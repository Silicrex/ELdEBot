import string
from discord.ext import commands
from .data import DB, save
from .helpers import get_enchant_data_string, get_villager_data_string, get_enchant_name, get_enchant_list,\
    check_best_level, check_best_rate, check_villager, replace_best_level, replace_best_rate, sorted_dict,\
    get_enchant_best_level, get_enchant_best_rate, valid_name, EMS, EBOOK
from .views import EnchantPages, VillagerPages, PageView
from . import enchanting


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

    @commands.command(aliases=['enchants'])
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.guild)
    async def list(self, ctx):
        # ex: list
        # Assumes data is pre-sorted
        enchants = DB['enchants']
        if not enchants:
            await ctx.send('There are no enchants')
            return
        pages = EnchantPages(enchants)
        view = PageView(pages)
        view.author = ctx.author
        view.message = await ctx.send(pages.get_current_page_text(), view=view)

    @commands.command(aliases=['f'])
    @commands.cooldown(rate=1, per=1, type=commands.BucketType.guild)
    async def find(self, ctx, *, text: str.lower):
        # ex: find ash destroyer
        if not (enchant_name := get_enchant_name(text)):
            await ctx.send('Invalid enchant name')
            return
        enchants = DB['enchants']
        if enchant_name not in enchants:
            found = False
            for test_enchant_name in enchants:
                if test_enchant_name.startswith(enchant_name):
                    enchant_name = test_enchant_name
                    found = True
                    break
            if not found:
                await ctx.send('Enchant not found')
                return
        await ctx.send(get_enchant_data_string(enchant_name))

    @commands.command(aliases=['fl', 'findl'])
    @commands.cooldown(rate=1, per=2, type=commands.BucketType.guild)
    async def findlist(self, ctx, *, text: str.lower):
        # ex: findlist adv
        if not valid_name(text):
            await ctx.send('Invalid enchant name')
            return
        enchants = DB['enchants']
        enchant_list = []
        for enchant_name in enchants:
            if enchant_name.startswith(text):
                enchant_list.append(enchant_name)
        if not enchant_list:
            await ctx.send('Nothing found')
            return
        pages = EnchantPages({k: enchants[k] for k in enchant_list})
        view = PageView(pages)
        view.author = ctx.author
        view.message = await ctx.send(pages.get_current_page_text(), view=view)

    @commands.command()
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.guild)
    async def check(self, ctx, *, text: str.lower):
        # ex: check 10 fire aspect 2, 30 education 3
        args = text.split()
        enchants = DB['enchants']
        priority = DB['priority']
        if len(args) < 2:
            await ctx.send('Missing required argument(s)')
            return
        parsed = ' '.join(args).split(', ')  # ie ["10", "infinity,", "5", "mending"] -> ["10 infinity", "5 mending"]
        if not (enchant_list := get_enchant_list(parsed)):
            await ctx.send('Invalid input')
            return
        res = []
        for enchant_data in enchant_list:
            enchant_name = enchant_data['name']
            level = enchant_data['level']
            cost = enchant_data['cost']
            if enchant_name not in enchants:
                if enchant_name in priority:
                    res.append(f'!! **[{string.capwords(enchant_name)} {level}]** is a new **PRIORITY** enchant!\n\n')
                    continue
                else:
                    res.append(f'! **[{string.capwords(enchant_name)} {level}]** is a new enchant!\n\n')
                    continue
            res.append(check_best_level(enchant_name, level, cost)[1])
            res.append(check_best_rate(enchant_name, level, cost)[1])
        await ctx.send(''.join(res))

    @commands.command()
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.guild)
    async def villagers(self, ctx):
        # ex: villagers
        villagers = DB['villagers']
        if not villagers:
            await ctx.send('There are no villagers')
            return
        unused_villagers = []
        for villager_name in villagers:
            if not check_villager(villager_name):
                unused_villagers.append(villager_name)
        pages = VillagerPages(villagers, unused_villagers)
        view = PageView(pages)
        view.author = ctx.author
        view.message = await ctx.send(pages.get_current_page_text(), view=view)

    @commands.command()
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.guild)
    async def villager(self, ctx, *, villager_name: str.lower):
        if not valid_name(villager_name):
            await ctx.send('Invalid name')
            return
        villagers = DB['villagers']
        if villager_name not in villagers:
            found = False
            for test_villager_name in villagers:
                if test_villager_name.startswith(villager_name):
                    villager_name = test_villager_name
                    found = True
                    break
            if not found:
                await ctx.send('Villager not found')
                return
        await ctx.send(get_villager_data_string(villager_name))

    @commands.command()
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.guild)
    async def add(self, ctx, *, text: str.lower):
        # ex: add bob, 10 ash destroyer, 5 mending, 7 supreme sharpness 5
        # Names are forced lowercase, enchant names are automatically adjusted during print

        args = text.split()
        res = []
        # Process input
        if len(args) < 7:
            await ctx.send('Missing required argument(s)')
            return
        parsed = ' '.join(args).split(', ')  # ie [bob, 10 ash destroyer, 5 mending, 7 supreme sharpness 5]
        if len(parsed) != 4:
            await ctx.send('Format args like: <name>, <cost1> <enchant1>, <cost2> <enchant2>, <cost3> <enchant3>')
            return
        villagers = DB['villagers']
        enchants = DB['enchants']
        priority = DB['priority']
        villager_name = parsed[0]

        # Validate name
        if villager_name in villagers:
            await ctx.send('Villager name already in use')
            return
        elif not valid_name(villager_name):
            await ctx.send('Villager name invalid')
            return

        # Validate & format enchants
        if not (enchant_list := get_enchant_list(parsed[1:])):  # Get list of dicts representing enchants
            await ctx.send('Invalid input')
            return

        # Iterate over enchants, perform comparisons, and update data
        villagers[villager_name] = {}
        villager = villagers[villager_name]
        replaced_villagers = []  # To check for if still contributing a best after update
        new_enchant = False
        for enchant_data in enchant_list:
            enchant_name = enchant_data['name']
            level = enchant_data['level']
            cost = enchant_data['cost']
            full_enchant_name = f"{enchant_name} {level}"
            if full_enchant_name not in villager:  # In case duplicate on same villager
                villager.update({full_enchant_name: {'is_best_level': False, 'is_best_rate': False, 'cost': cost}})
                # False is a default value

            # New enchant
            if enchant_name not in enchants:
                if enchant_name in priority:
                    res.append(f'!! **[{string.capwords(enchant_name)} {level}]** is a new **PRIORITY** enchant!\n\n')
                else:
                    res.append(f'! **[{string.capwords(enchant_name)} {level}]** is a new enchant!\n\n')
                new_enchant = True
                enchants.update({enchant_name: {
                    'best_level': {'villager_name': villager_name, 'level': level, 'cost': cost},
                    'best_rate': {'villager_name': villager_name, 'level': level, 'cost': cost}
                }})
                villager[full_enchant_name]['is_best_level'] = True
                villager[full_enchant_name]['is_best_rate'] = True
                continue

            is_best_level, best_level_output = check_best_level(enchant_name, level, cost)
            res.append(best_level_output)
            is_best_rate, best_rate_output = check_best_rate(enchant_name, level, cost)
            res.append(best_rate_output)
            if is_best_level:
                villager[full_enchant_name]['is_best_level'] = True
                prev_villager = replace_best_level(villager_name, enchant_name, level, cost)
                if prev_villager not in replaced_villagers and prev_villager != villager_name:
                    replaced_villagers.append(prev_villager)
            if is_best_rate:
                villager[full_enchant_name]['is_best_rate'] = True
                prev_villager = replace_best_rate(villager_name, enchant_name, level, cost)
                if prev_villager not in replaced_villagers and prev_villager != villager_name:
                    replaced_villagers.append(prev_villager)
            res.append('\n')
        res.append(f'Successfully added villager **{villager_name}**!\n')

        for replaced_villager in replaced_villagers:
            if not check_villager(replaced_villager):
                res.append(f'**{replaced_villager}** no longer contributes any bests\n')

        if new_enchant:
            DB['enchants'] = sorted_dict(enchants)
        DB['villagers'] = sorted_dict(villagers)

        await ctx.send(''.join(res))
        save()

    @commands.command()
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.guild)
    async def rename(self, ctx, *, text: str.lower):
        args = text.split()
        villagers = DB['villagers']
        enchants = DB['enchants']
        parsed = ' '.join(args).split(', ')
        if len(parsed) != 2:
            await ctx.send('Format like rename <villager_name>, <new_villager_name>')
            return
        villager_name = parsed[0]
        new_villager_name = parsed[1]
        if villager_name not in villagers:
            await ctx.send('Villager not found')
            return
        if new_villager_name in villagers:
            await ctx.send('That name is already in use')
            return
        elif not valid_name(new_villager_name):
            await ctx.send('New villager name invalid')
            return
        villagers[new_villager_name] = villagers[villager_name]
        for full_enchant_name, data in villagers[villager_name].items():
            enchant_name = get_enchant_name(full_enchant_name)
            if data['is_best_level']:
                enchants[enchant_name]['best_level']['villager_name'] = new_villager_name
            if data['is_best_rate']:
                enchants[enchant_name]['best_rate']['villager_name'] = new_villager_name
        villagers.pop(villager_name)
        await ctx.send(f'Successfully renamed **{villager_name}** to **{new_villager_name}**!')
        save()

    @commands.command()
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.guild)
    async def remove(self, ctx, *, text: str.lower):
        args = text.split()
        res = []
        villager_name = ' '.join(args)
        villagers = DB['villagers']
        if villager_name not in villagers:
            await ctx.send('Villager not found')
            return
        other_villager_names = [x for x in villagers if x != villager_name]
        enchants = DB['enchants']
        if not check_villager(villager_name):  # If villager has no bests, can delete without other updates
            villagers.pop(villager_name)
            await ctx.send(f'Successfully deleted **{villager_name}**')
            save()
            return
        # Systematically find the replacement for each best the villager has
        for full_enchant_name, data in villagers[villager_name].items():
            enchant_name = get_enchant_name(full_enchant_name)
            if enchant_name not in enchants:  # Was already deleted from a duplicate enchant type on this villager
                continue
            if data['is_best_level']:
                if not (level_res := get_enchant_best_level(other_villager_names, enchant_name)):
                    enchants.pop(enchant_name)  # No villager with this enchant is left
                    res.append(f"Removed **[{string.capwords(enchant_name)}]** as no other villager found with it\n")
                    continue
                enchants[enchant_name]['best_level'] = level_res
                new_villager_name = level_res['villager_name']
                new_full_enchant_name = f"{enchant_name} {level_res['level']}"
                villagers[new_villager_name][new_full_enchant_name]['is_best_level'] = True
                res.append(f"Replaced best level of **[{string.capwords(full_enchant_name)}]** {data['cost']}{EMS} "
                           f"with **[{string.capwords(enchant_name)} {level_res['level']}]** {level_res['cost']}{EMS} "
                           f"--> **{level_res['villager_name']}**\n")
            if data['is_best_rate']:
                rate_res = get_enchant_best_rate(other_villager_names, enchant_name)
                new_villager_name = rate_res['villager_name']
                new_full_enchant_name = f"{enchant_name} {rate_res['level']}"
                villagers[new_villager_name][new_full_enchant_name]['is_best_rate'] = True
                enchants[enchant_name]['best_rate'] = rate_res
                res.append(f"Replaced best rate of **[{string.capwords(full_enchant_name)}]** {data['cost']}{EMS} "
                           f"with **[{string.capwords(enchant_name)} {rate_res['level']}]** {rate_res['cost']}{EMS} "
                           f"--> **{rate_res['villager_name']}**\n")
        villagers.pop(villager_name)
        res.append(f'Successfully deleted **{villager_name}**\n')
        save()
        await ctx.send(''.join(res))

    @commands.group(invoke_without_command=True, aliases=['p', 'prio'])
    async def priority(self, ctx):
        enchants = DB['enchants']
        priority = DB['priority']
        if not enchants:
            await ctx.send('There are no enchants')
            return
        res = []
        for enchant_name in enchants:
            if enchant_name in priority:
                res.append(get_enchant_data_string(enchant_name))
        if res:
            res.insert(0, '**Priority Enchants Owned:**')
            await ctx.send('\n'.join(res))
        else:
            await ctx.send('No priority enchants owned')

    @priority.command(name='list')
    async def priority_list(self, ctx):
        enchants = DB['enchants']
        priority = DB['priority']
        res = []
        for enchant_name in priority:
            owned = '**(OWNED)** ' if enchant_name in enchants else ''
            res.append(f'{owned}{string.capwords(enchant_name)}')
        body = '\n'.join(res)
        await ctx.send(f'**Priority Enchant List:**\n{body}')

    @priority.command(name='add')
    async def priority_add(self, ctx, *, enchant_name: str.lower):
        if not valid_name(enchant_name):
            await ctx.send('Invalid input (note priority enchants do not take level)')
            return
        priority = DB['priority']
        if enchant_name in priority:
            await ctx.send('That item is already on the list')
            return
        priority.append(enchant_name)
        DB['priority'] = sorted(priority)
        save()
        await ctx.send('Successfully added item to priority list')

    @priority.command(name='remove')
    async def priority_remove(self, ctx, *, enchant_name: str.lower):
        if not valid_name(enchant_name):
            await ctx.send('Invalid input (note priority enchants do not take level)')
            return
        priority = DB['priority']
        if enchant_name not in priority:
            await ctx.send('That item is not on the list')
            return
        priority.remove(enchant_name)
        save()
        await ctx.send('Successfully removed item from priority list')

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
        tags = ['helmet', 'chestplate', 'chestplate_heating', 'chestplate_berserk', 'leggings', 'boots',
                'boots_heating']
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
            await ctx.send(tag_func())
        else:
            await ctx.send("Invalid tag. Use 'enchant help' for help")
