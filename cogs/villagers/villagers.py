import string
import asyncio
from discord.ext import commands
from cogs.villagers.helpers import create_enchant_data_string, create_villager_data_string, \
    create_enchant_list, get_enchant_list, get_villager_list, get_villager_data, match_enchant, match_villager,\
    check_best_level, check_best_rate, check_villager, get_priority_list, get_enchant_data,\
    get_enchant_best_level, get_enchant_best_rate, valid_name, EMS, EBOOK
from cogs.villagers.views import Pages, EnchantPages, VillagerPages, PageView
from cogs.villagers import enchanting


class Villagers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        print(f'{self.__class__.__name__} cog loaded!')

    async def cog_unload(self):
        print(f'{self.__class__.__name__} cog unloaded!')

    @commands.command()
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.guild)
    async def help(self, ctx):
        await ctx.send('**Commands:**\n'
                       '- list\n'
                       '- find <enchant>\n'
                       '- findlist <text>\n'
                       '- check <cost> <enchant>, ..\n'
                       '- villagers\n'
                       '- villager <villager_name>\n'
                       '- add <villager name>, <cost1 enchant1>, <c2 e2>, <c3 e3>\n'
                       '- rename <villager name>, <new villager name>\n'
                       '- remove <villager name>\n'
                       '- priority (add/remove <enchant_name>)\n'
                       '- scale cost:level new_level')

    @commands.command()
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.guild)
    async def add(self, ctx, *, text: str.lower):
        # ex: add bob, 10 ash destroyer, 5 mending, 7 supreme sharpness 5
        # Names are forced lowercase no excess whitespace, enchant names are automatically adjusted during print

        args = ' '.join(text.split())  # Sanitize whitespace
        parsed = args.split(', ')  # ie [bob, 10 ash destroyer, 5 mending, 7 supreme sharpness 5]
        if len(parsed) < 2:
            await ctx.send('Need at least one trade. Format args like: <name>, <cost1> <enchant1> ...')
            return

        # Validate name
        villager_name = parsed[0]
        if not valid_name(villager_name):
            await ctx.send('Villager name invalid')
            return

        async with self.bot.pg_pool.acquire() as con:
            async with con.transaction():
                # Check if villager exists already
                result = await con.fetchval('SELECT 1 FROM trades WHERE villager_name = $1 LIMIT 1 FOR UPDATE', villager_name)
                if result is not None:
                    await ctx.send('Villager name already in use')
                    return

                # Validate & format enchants
                if not (enchant_list := create_enchant_list(parsed[1:])):  # Get list of dicts representing enchants
                    await ctx.send('Invalid input')
                    return

                # Iterate over enchants, perform comparisons, and update data
                out = []  # To compile output at the end
                slot = 0
                priority_list = await get_priority_list(con)
                replaced_villagers = []  # To check for if still contributing a best after update
                for enchant_data in enchant_list:
                    enchant_name = enchant_data['name']
                    level = enchant_data['level']
                    cost = enchant_data['cost']
                    slot += 1
                    # Add trade to db
                    trade_id = await con.fetchval('INSERT INTO trades (villager_name, slot, enchant_name, level, cost) '
                                                 'VALUES ($1, $2, $3, $4, $5) '
                                                 'RETURNING id', villager_name, slot, enchant_name, level, cost)
                    # Check if new enchant
                    result = await con.fetchval('SELECT 1 FROM best_enchants WHERE name = $1 LIMIT 1 FOR UPDATE', enchant_name)
                    if result is None:  # Is a new enchant
                        await con.execute('INSERT INTO best_enchants (name, best_level, best_rate) '
                                          'VALUES ($1, $2, $2)', enchant_name, trade_id)
                        if enchant_name in priority_list:
                            out.append(f'!! **[{string.capwords(enchant_name)} {level}]** is a new **PRIORITY** enchant!\n\n')
                        else:
                            out.append(f'! **[{string.capwords(enchant_name)} {level}]** is a new enchant!\n\n')
                        continue

                    # Not a new enchant. Perform comparisons
                    is_best_level, cur_level_villager, lvl_output = await check_best_level(con, enchant_name, level, cost)
                    out.append(lvl_output)
                    is_best_rate, cur_rate_villager, rate_output = await check_best_rate(con, enchant_name, level, cost)
                    out.append(rate_output)

                    if is_best_level:
                        await con.execute('UPDATE best_enchants SET best_level = $1 '
                                          'WHERE name = $2', trade_id, enchant_name)
                        if cur_level_villager not in replaced_villagers and cur_level_villager != villager_name:
                            replaced_villagers.append(cur_level_villager)
                    if is_best_rate:
                        await con.execute('UPDATE best_enchants SET best_rate = $1 '
                                          'WHERE name = $2', trade_id, enchant_name)
                        if cur_rate_villager not in replaced_villagers and cur_rate_villager != villager_name:
                            replaced_villagers.append(cur_rate_villager)
                    out.append('\n')
                out.append(f'Successfully added villager **{villager_name}**!\n')

                for replaced_villager in replaced_villagers:
                    if not await check_villager(con, replaced_villager):
                        out.append(f'**{replaced_villager}** no longer contributes any bests\n')

        await ctx.send(''.join(out))

    @commands.command()
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.guild)
    async def rename(self, ctx, *, text: str.lower):
        # ex: rename bob, bob2
        args = ' '.join(text.split())  # Sanitize whitespace
        parsed = args.split(', ')  # List of args
        if len(parsed) != 2:
            await ctx.send('Format like rename <villager_name>, <new_villager_name>')
            return
        villager_name = parsed[0]
        new_villager_name = parsed[1]
        async with self.bot.pg_pool.acquire() as con:
            async with con.transaction():
                # Check if villager exists already
                result = await con.fetchval('SELECT 1 FROM trades WHERE villager_name = $1 LIMIT 1 FOR UPDATE', villager_name)
                if result is None:
                    await ctx.send('Villager not found')
                    return
                # Check if new name already exists
                result = await con.fetchval('SELECT 1 FROM trades WHERE villager_name = $1 LIMIT 1', new_villager_name)
                if result is not None:
                    await ctx.send('That name is already in use')
                    return
                if not valid_name(new_villager_name):
                    await ctx.send('New villager name invalid')
                    return
                await con.execute('UPDATE trades '
                                  'SET villager_name = $1 WHERE villager_name = $2', new_villager_name, villager_name)
        await ctx.send(f'Successfully renamed **{villager_name}** to **{new_villager_name}**!')

    @commands.command()
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.guild)
    async def remove(self, ctx, *, text: str.lower):
        # ex: remove bob
        villager_name = ' '.join(text.split())  # Sanitize whitespace
        out = []
        async with self.bot.pg_pool.acquire() as con:
            async with con.transaction():
                result = await get_villager_data(con, villager_name)
                if not result:
                    await ctx.send('Villager not found')
                    return
                if not await check_villager(con, villager_name):  # If villager has no bests, can delete without other updates
                    await con.execute('DELETE FROM trades WHERE villager_name = $1', villager_name)
                    await ctx.send(f'Successfully deleted **{villager_name}**')
                    return
                # Systematically find the replacement for each best the villager has
                for trade in result:
                    enchant_name = trade['enchant_name']
                    level = trade['level']
                    cost = trade['cost']
                    is_best_level = trade['is_best_level']
                    is_best_rate = trade['is_best_rate']
                    if not await con.fetchval('SELECT 1 FROM best_enchants WHERE name = $1 LIMIT 1', enchant_name):
                        continue  # Was already deleted from a duplicate enchant on this villager as no replacements found
                    if is_best_level:
                        if not (lvl_trade := await get_enchant_best_level(con, enchant_name, villager_name)):
                            # No villager with this enchant is left
                            await con.execute('DELETE FROM best_enchants WHERE name = $1', enchant_name)
                            out.append(f"Removed **[{string.capwords(enchant_name)}]** as no other villager found with it\n")
                            continue
                        new_id = lvl_trade['id']
                        new_level = lvl_trade['level']
                        new_cost = lvl_trade['cost']
                        new_villager = lvl_trade['villager_name']
                        await con.execute('UPDATE best_enchants '
                                          'SET best_level = $1 WHERE name = $2', new_id, enchant_name)
                        print('help1')
                        out.append(f"Replaced best level of **[{string.capwords(enchant_name)} {level}]** {cost}{EMS} "
                                   f"with **[{string.capwords(enchant_name)} {new_level}]** {new_cost}{EMS} "
                                   f"--> **{new_villager}**\n")
                    if is_best_rate:
                        rate_trade = await get_enchant_best_rate(con, enchant_name, villager_name)
                        new_id = rate_trade['id']
                        new_level = rate_trade['level']
                        new_cost = rate_trade['cost']
                        new_villager = rate_trade['villager_name']
                        await con.execute('UPDATE best_enchants '
                                          'SET best_rate = $1 WHERE name = $2', new_id, enchant_name)
                        print('help2')
                        out.append(
                            f"Replaced best rate of **[{string.capwords(enchant_name)} {level}]** {cost}{EMS} "
                            f"with **[{string.capwords(enchant_name)} {new_level}]** {new_cost}{EMS} "
                            f"--> **{new_villager}**\n\n")
                await con.execute('DELETE FROM trades WHERE villager_name = $1', villager_name)
        out.append(f'Successfully deleted **{villager_name}**\n')
        await ctx.send(''.join(out))

    @commands.command(aliases=['enchants'])
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.guild)
    async def list(self, ctx):
        # ex: list
        result = await self.bot.pg_pool.fetch("""SELECT e.name AS enchant_name,
                                                 e.best_level = e.best_rate AS same_trade,
                                                 level_trade.villager_name AS best_level_villager, 
                                                 level_trade.level AS best_level, 
                                                 level_trade.cost AS best_level_cost,
                                                 rate_trade.villager_name AS best_rate_villager,
                                                 rate_trade.level AS best_rate_level,
                                                 rate_trade.cost AS best_rate_cost
                                                 FROM best_enchants as e
                                                 LEFT JOIN trades AS level_trade ON e.best_level = level_trade.id
                                                 LEFT JOIN trades AS rate_trade ON e.best_rate = rate_trade.id
                                                 ORDER BY e.name""")
        if not result:
            await ctx.send('There are no enchants')
            return
        enchants = {}
        for enchant in result:
            enchant_name = enchant['enchant_name']
            enchants.update({enchant_name: {'same_trade': enchant['same_trade'],
                                            'best_level_villager': enchant['best_level_villager'],
                                            'best_level': enchant['best_level'],
                                            'best_level_cost': enchant['best_level_cost'],
                                            'best_rate_villager': enchant['best_rate_villager'],
                                            'best_rate_level': enchant['best_rate_level'],
                                            'best_rate_cost': enchant['best_rate_cost']}})
        pages = EnchantPages(enchants)
        view = PageView(pages)
        view.author = ctx.author
        view.message = await ctx.send(pages.get_current_page_text(), view=view)

    @commands.command(aliases=['f'])
    @commands.cooldown(rate=1, per=1, type=commands.BucketType.guild)
    async def find(self, ctx, *, text: str.lower):
        # ex: find ash destroyer
        enchant_name = ' '.join(text.split())  # Sanitize whitespace
        if not enchant_name:  # Should be caught by missing arg anyways
            await ctx.send('Must provide enchant name, like `find ash destroyer`')
            return
        async with self.bot.pg_pool.acquire() as con:
            enchant_list = await get_enchant_list(con)
            if not enchant_list:
                await ctx.send('There are no enchants')
                return
            if not (enchant_name := match_enchant(enchant_name, enchant_list)):
                await ctx.send('Enchant not found')
                return
            result = await get_enchant_data(con, enchant_name)
        await ctx.send(create_enchant_data_string(result, enchant_name))

    @commands.command(aliases=['fl', 'findl'])
    @commands.cooldown(rate=1, per=2, type=commands.BucketType.guild)
    async def findlist(self, ctx, *, text: str.lower):
        # ex: findlist adv
        enchant_name = ' '.join(text.split())  # Sanitize whitespace
        async with self.bot.pg_pool.acquire() as con:
            enchants = await get_enchant_list(con)
            if not enchants:
                await ctx.send('There are no enchants')
                return
            enchant_list = []
            if enchant_name in enchants:
                enchant_list.append(enchant_name)
            for test_enchant_name in enchants:
                if test_enchant_name.startswith(enchant_name) or enchant_name in test_enchant_name:
                    enchant_list.append(test_enchant_name)
            if not enchant_list:
                await ctx.send('Nothing found')
                return
            result = await self.bot.pg_pool.fetch("""SELECT e.name AS enchant_name,
                                                     e.best_level = e.best_rate AS same_trade,
                                                     level_trade.villager_name AS best_level_villager, 
                                                     level_trade.level AS best_level, 
                                                     level_trade.cost AS best_level_cost,
                                                     rate_trade.villager_name AS best_rate_villager,
                                                     rate_trade.level AS best_rate_level,
                                                     rate_trade.cost AS best_rate_cost
                                                     FROM best_enchants as e
                                                     LEFT JOIN trades AS level_trade ON e.best_level = level_trade.id
                                                     LEFT JOIN trades AS rate_trade ON e.best_rate = rate_trade.id
                                                     WHERE e.name = ANY($1)
                                                     ORDER BY e.name""", enchant_list)
        enchants = {}
        for enchant in result:
            enchant_name = enchant['enchant_name']
            enchants.update({enchant_name: {'same_trade': enchant['same_trade'],
                                            'best_level_villager': enchant['best_level_villager'],
                                            'best_level': enchant['best_level'],
                                            'best_level_cost': enchant['best_level_cost'],
                                            'best_rate_villager': enchant['best_rate_villager'],
                                            'best_rate_level': enchant['best_rate_level'],
                                            'best_rate_cost': enchant['best_rate_cost']}})
        pages = EnchantPages(enchants)
        view = PageView(pages)
        view.author = ctx.author
        view.message = await ctx.send(pages.get_current_page_text(), view=view)

    @commands.command()
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.guild)
    async def villager(self, ctx, *, text: str.lower):
        # ex: villager bob
        villager_name = ' '.join(text.split())  # Sanitize whitespace
        if not villager_name or not valid_name(villager_name):  # First part should be caught by missing arg anyways
            await ctx.send('Invalid name')
            return
        async with self.bot.pg_pool.acquire() as con:
            villagers = await get_villager_list(con)
            if not villagers:
                await ctx.send('There are no villagers')
                return
            if not (villager_name := match_villager(villager_name, villagers)):
                await ctx.send('Villager not found')
                return
            result = await get_villager_data(con, villager_name)
        await ctx.send(create_villager_data_string(result, villager_name))

    @commands.command(aliases=['v'])
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.guild)
    async def villagers(self, ctx):
        # ex: villagers
        result = await self.bot.pg_pool.fetch("""SELECT t.villager_name, t.enchant_name, t.level, t.cost, 
                                              CASE WHEN t.id = e.best_level THEN TRUE ELSE FALSE END AS is_best_level, 
                                              CASE WHEN t.id = e.best_rate THEN TRUE ELSE FALSE END AS is_best_rate 
                                              FROM trades t 
                                              LEFT JOIN best_enchants e ON t.enchant_name = e.name 
                                              ORDER BY villager_name, slot""")
        if not result:
            await ctx.send('There are no villagers')
            return
        villagers = {}
        for trade in result:
            villager_name = trade['villager_name']
            if villager_name not in villagers:
                villagers.update({villager_name: []})
            villagers[villager_name].append({'enchant_name': trade['enchant_name'], 'level': trade['level'],
                                             'cost': trade['cost'], 'is_best_level': trade['is_best_level'],
                                             'is_best_rate': trade['is_best_rate']})
        unused_villagers = []
        for villager_name, data in villagers.items():
            has_best = False
            for trade in data:
                if trade['is_best_level'] or trade['is_best_rate']:
                    has_best = True
            if not has_best:
                unused_villagers.append(villager_name)
        pages = VillagerPages(villagers, unused_villagers)
        view = PageView(pages)
        view.author = ctx.author
        view.message = await ctx.send(pages.get_current_page_text(), view=view)

    @commands.group(invoke_without_command=True, aliases=['p', 'prio'])
    async def priority(self, ctx):
        # List of owned priority enchants with locations
        async with self.bot.pg_pool.acquire() as con:
            priority_list = await get_priority_list(con)
            if not priority_list:
                await ctx.send('There are no priority enchants set')
                return
            result = await self.bot.pg_pool.fetch("""SELECT e.name AS enchant_name,
                                                     e.best_level = e.best_rate AS same_trade,
                                                     level_trade.villager_name AS best_level_villager, 
                                                     level_trade.level AS best_level, 
                                                     level_trade.cost AS best_level_cost,
                                                     rate_trade.villager_name AS best_rate_villager,
                                                     rate_trade.level AS best_rate_level,
                                                     rate_trade.cost AS best_rate_cost
                                                     FROM best_enchants as e
                                                     LEFT JOIN trades AS level_trade ON e.best_level = level_trade.id
                                                     LEFT JOIN trades AS rate_trade ON e.best_rate = rate_trade.id
                                                     WHERE e.name = ANY($1)
                                                     ORDER BY e.name""", priority_list)
        if not result:
            await ctx.send('No priority enchants found')
            return
        enchants = {}
        for enchant in result:
            enchant_name = enchant['enchant_name']
            enchants.update({enchant_name: {'same_trade': enchant['same_trade'],
                                            'best_level_villager': enchant['best_level_villager'],
                                            'best_level': enchant['best_level'],
                                            'best_level_cost': enchant['best_level_cost'],
                                            'best_rate_villager': enchant['best_rate_villager'],
                                            'best_rate_level': enchant['best_rate_level'],
                                            'best_rate_cost': enchant['best_rate_cost']}})
        pages = EnchantPages(enchants, keys_per_page=20)
        view = PageView(pages)
        view.author = ctx.author
        view.message = await ctx.send(pages.get_current_page_text(), view=view)

    @priority.command(name='list', aliases=['l'])
    async def priority_list(self, ctx):
        # List of priority enchant names
        async with self.bot.pg_pool.acquire() as con:
            enchant_list = await get_enchant_list(con)
            priority_list = await get_priority_list(con)
        if not priority_list:
            await ctx.send('There are no priority enchants set')
            return
        priority_enchants = {}
        for enchant_name in priority_list:
            if enchant_name in enchant_list:
                priority_enchants.update({enchant_name: f'**(OWNED)** {string.capwords(enchant_name)}'})
            else:
                priority_enchants.update({enchant_name: f'{string.capwords(enchant_name)}'})
        pages = Pages(priority_enchants, keys_per_page=20)
        view = PageView(pages)
        view.author = ctx.author
        view.message = await ctx.send(pages.get_current_page_text(), view=view)

    @priority.command(name='add')
    async def priority_add(self, ctx, *, text: str.lower):
        # Allow line-separated lists
        lines = text.split('\n')
        enchant_list = []
        async with self.bot.pg_pool.acquire() as con:
            priority_list = await get_priority_list(con)
            for line in lines:
                enchant_name = ' '.join(line.split())  # Sanitize whitespace
                if not valid_name(enchant_name):
                    await ctx.send('Invalid input')
                    return
                if enchant_name not in priority_list and enchant_name not in enchant_list:
                    enchant_list.append(enchant_name)
            if not enchant_list:
                await ctx.send('All listed enchants are already in priority list')
                return
            await con.execute("""INSERT INTO priority (name) 
                              SELECT * FROM UNNEST($1::text[])""", enchant_list)
        await ctx.send('Successfully added enchant(s) to priority list')

    @priority.command(name='remove')
    async def priority_remove(self, ctx, *, text: str.lower):
        enchant_name = ' '.join(text.split())  # Sanitize whitespace
        async with self.bot.pg_pool.acquire() as con:
            priority_list = await get_priority_list(con)
            if enchant_name not in priority_list:
                await ctx.send('That enchant is not on the list')
                return
            await con.execute('DELETE FROM priority WHERE name = $1', enchant_name)
        await ctx.send('Successfully removed enchant from priority list')

    @priority.command(name='clear')
    async def priority_clear(self, ctx):
        def msg_check(message):  # Wait for message meeting this criteria to handle as a response
            return message.author == ctx.author and message.channel == ctx.channel

        async with self.bot.pg_pool.acquire() as con:
            priority_list = await get_priority_list(con)
            if not priority_list:
                await ctx.send('There are no priority enchants set')
                return
            await ctx.send("Are you sure you'd like to ERASE the priority list? (y/n)")

            # wait_for returns first event that satisfies check (message event in this case)
            try:
                response = await self.bot.wait_for('message', check=msg_check, timeout=10)
            except asyncio.TimeoutError:
                await ctx.send('Timed out')
                return

            content = response.content.lower()
            if content in {'y', 'yes'}:
                await con.execute('DELETE FROM priority')
                await ctx.send(f'Priority list cleared. Deleted {len(priority_list)} value(s)')
            elif content in {'n', 'no'}:
                await ctx.send('Cancelled')
            else:
                await ctx.send('Invalid response. Cancelling')

    @commands.command()
    @commands.cooldown(rate=1, per=2, type=commands.BucketType.guild)
    async def check(self, ctx, *, text: str.lower):
        # ex: check bob, 10 ash destroyer, 5 mending, 7 supreme sharpness 5

        split = text.split()
        args = ' '.join(split)  # Sanitize whitespace
        parsed = args.split(', ')  # ie [10 ash destroyer, 5 mending, 7 supreme sharpness 5]
        if not parsed:
            await ctx.send('Need at least one trade. Format args like: <cost1> <enchant1>, ...')
            return
        # Validate & format enchants
        if not (enchant_list := create_enchant_list(parsed)):  # Get list of dicts representing enchants
            await ctx.send('Invalid input')
            return

        async with self.bot.pg_pool.acquire() as con:
            # Iterate over enchants and perform comparisons
            out = []  # To compile output at the end
            priority_list = await get_priority_list(con)
            replaced_villagers = {}  # To check for if still contributing a best after update
            for enchant_data in enchant_list:
                enchant_name = enchant_data['name']
                level = enchant_data['level']
                cost = enchant_data['cost']
                # Check if new enchant
                result = await con.fetchval('SELECT 1 FROM best_enchants WHERE name = $1 LIMIT 1', enchant_name)
                if result is None:  # Is a new enchant
                    if enchant_name in priority_list:
                        out.append(f'!! **[{string.capwords(enchant_name)} {level}]** is a new **PRIORITY** enchant!\n\n')
                    else:
                        out.append(f'! **[{string.capwords(enchant_name)} {level}]** is a new enchant!\n\n')
                    continue

                # Not a new enchant. Perform comparisons
                is_best_level, cur_level_villager, lvl_output = await check_best_level(con, enchant_name, level, cost)
                out.append(lvl_output)
                is_best_rate, cur_rate_villager, rate_output = await check_best_rate(con, enchant_name, level, cost)
                out.append(rate_output)

                if is_best_level:
                    if cur_level_villager not in replaced_villagers:
                        villager_bests = await check_villager(con, cur_level_villager)
                        print(f'{villager_bests=}')
                        replaced_villagers.update({cur_level_villager: villager_bests - 1})
                        print(f'Created.. {replaced_villagers=}')
                    else:
                        replaced_villagers[cur_level_villager] -= 1
                        print(f'Updated.. {replaced_villagers=}')
                if is_best_rate:
                    if cur_rate_villager not in replaced_villagers:
                        villager_bests = await check_villager(con, cur_rate_villager)
                        print(f'{villager_bests=}')
                        replaced_villagers.update({cur_rate_villager: villager_bests - 1})
                        print(f'Created.. {replaced_villagers=}')
                    else:
                        replaced_villagers[cur_rate_villager] -= 1
                        print(f'Updated.. {replaced_villagers=}')
                out.append('\n')

            for replaced_villager in replaced_villagers:
                if replaced_villagers[replaced_villager] < 1:  # No bests remaining
                    out.append(f'**{replaced_villager}** would no longer contribute any bests\n')
        
        await ctx.send(''.join(out))

    @commands.command()
    async def scale(self, ctx, base: str, new_level: str):
        if ':' not in base:
            await ctx.send('Format args like (the text part is optional).. <cost>ems:lvl<level> lvl<new_level>')
            return
        cost, level = base.split(':')
        cost = cost.replace('ems', '')
        level = level.replace('lvl', '').replace('lv', '')
        new_level = new_level.replace('lvl', '').replace('lv', '')
        if not (cost.isnumeric() and level.isnumeric() and new_level.isnumeric()):
            await ctx.send('Invalid inputs, use integers')
            return
        cost = int(cost)
        level = int(level)
        new_level = int(new_level)
        if not level > 0 or not new_level > 0:
            await ctx.send('Error: cannot use 0')
            return

        if new_level >= level:
            mult = 2 ** (new_level - level)
            await ctx.send(f'It would cost {cost * mult}{EMS} ({mult}{EBOOK}) to go from '
                           f'**Level {level}** to **Level {new_level}**')
        else:  # Scaling down to a lower level
            mult = 2 ** (level - new_level)
            new_cost = cost / mult
            new_cost_text = str(int(new_cost)) if new_cost.is_integer() else f'{new_cost:.2f}'
            await ctx.send(f'{EBOOK} **Level {level}** @ {cost}{EMS} = '
                           f'{mult}x [{EBOOK} **Level {new_level}** @ {new_cost_text}{EMS}]')

    @commands.command()
    async def enchant(self, ctx, *, text: str.lower):
        tags = ['helmet', 'chestplate', 'chestplate_noheating', 'chestplate_berserk', 'leggings', 'boots',
                'boots_noheating', 'javelin']
        if text == 'help':
            await ctx.send(f"This command outputs a guide on efficiently enchanting items and "
                           f"where to get the enchants from your villagers\n"
                           f"Usage: **enchant <tag>**\n"
                           f"- Go in order top-to-bottom\n"
                           f"- Numbers in brackets [] represent level cost\n"
                           f"- Shown villager goes by best level available, notes level if level is lower than needed\n"
                           f"- 'DNH' = Do Not Have enchant\n"
                           f"Enchant guide tags: {tags}")
        elif text in tags:
            tag_func = getattr(enchanting, text + '_tag')
            async with self.bot.pg_pool.acquire() as con:
                await ctx.send(await tag_func(con))
        else:
            await ctx.send("Invalid tag. Use 'enchant help' for help")

async def setup(bot):
    await bot.add_cog(Villagers(bot))