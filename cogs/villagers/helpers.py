import string
from math import sqrt

EMS = '<:emerald:1156624279857811457>'
EBOOK = '<:ebook:1158537467482341487>'
VALID_CHARS = set(string.ascii_letters + string.digits + " '.:-")


async def add_enchants(con, villager_name, enchant_list):
    # Takes list of dicts, each representing an enchant, with keys 'name', 'level', 'cost'
    # Returns output
    out = []  # To build output
    priority_list = await get_priority_list(con)
    replaced_villagers = []  # To check for if still contributing a best after update
    for enchant_data in enchant_list:
        enchant_name = enchant_data['name']
        level = enchant_data['level']
        cost = enchant_data['cost']
        # Add trade to db
        trade_id = await con.fetchval('INSERT INTO trades (villager_name, enchant_name, level, cost) '
                                      'VALUES ($1, $2, $3, $4) '
                                      'RETURNING id', villager_name, enchant_name, level, cost)

        # Check if new enchant
        result = await con.fetchval('SELECT 1 FROM best_enchants WHERE name = $1 FOR UPDATE',
                                    enchant_name)
        if result is None:  # Is a new enchant, so will be best for level and rate
            await con.execute('INSERT INTO best_enchants (name, best_level, best_rate) '
                              'VALUES ($1, $2, $2)', enchant_name, trade_id)
            if enchant_name in priority_list:
                out.append(
                    f'!! **[{string.capwords(enchant_name)} {level}]** is a new **PRIORITY** enchant!\n\n')
            else:
                out.append(f'! **[{string.capwords(enchant_name)} {level}]** is a new enchant!\n\n')
            continue

        # Not a new enchant. Perform comparisons
        is_best_level, cur_level_villager, lvl_output = await check_best_level(con, enchant_name, level, cost)
        out.append(lvl_output)
        is_best_rate, cur_rate_villager, rate_output = await check_best_rate(con, enchant_name, level, cost)
        out.append(rate_output)

        # Update best_enchants, record any villagers whose trades got bested
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

    return out


def create_enchant_data_string(record, enchant_name):
    # record is a dict of the enchant dict
    same_trade = record['same_trade']
    best_level = record['best_level']
    best_rate_level = record['best_rate_level']
    best_rate_cost = record['best_rate_cost']
    res = [f"{EBOOK}**[{string.capwords(enchant_name)} {best_level}]** "
           f"{record['best_level_cost']}{EMS} --> **{record['best_level_villager']}**"]
    if not same_trade:
        scaled_cost = int(get_rate(best_rate_level, best_rate_cost) * get_lvl_1(best_level))
        res.append(f" \\|\\| best rate: **[{string.capwords(enchant_name)} {best_rate_level}]** "
                   f"{best_rate_cost}{EMS} (Scaled {scaled_cost}{EMS}) --> **{record['best_rate_villager']}**")
    return ''.join(res)


def create_villager_data_string(records, villager_name):
    # records is a list of trade records
    enchants = []
    for trade in records:  # Will have a trade record per slot
        is_best_level = trade['is_best_level']
        is_best_rate = trade['is_best_rate']
        enchant_text = f"{EBOOK}**[{string.capwords(trade['enchant_name'])} {trade['level']}]** {trade['cost']}{EMS}"
        best_text = ''
        if is_best_level and is_best_rate:
            best_text = ' (BEST LEVEL/RATE)'
        elif is_best_level:
            best_text = ' (BEST LEVEL)'
        elif is_best_rate:
            best_text = ' (BEST RATE)'
        enchants.append(f'{enchant_text}{best_text}')
    return f"**<{villager_name}>** \\|\\| " + ', '.join(enchants)


def match_villager(villager_name, villagers):
    if villager_name in villagers:
        return villager_name
    for test_villager_name in villagers:
        if test_villager_name.startswith(villager_name):
            return test_villager_name
    return False


def match_enchant(enchant_name, enchants):
    if enchant_name in enchants:
        return enchant_name
    for test_enchant_name in enchants:
        if test_enchant_name.startswith(enchant_name):
            return test_enchant_name
    for test_enchant_name in enchants:
        if enchant_name in test_enchant_name:
            return test_enchant_name
    return False


def get_enchant_name(text: str):
    split = text.split()
    if split[-1].isnumeric():
        if len(split) == 1:
            return False
        return ' '.join(split[:-1])
    else:
        return ' '.join(split)


def get_enchant_level(text: str):
    split = text.split()
    if split[-1].isnumeric():
        if len(split) == 1:
            return False
        return int(split[-1])
    else:
        return 1


def create_enchant_list(input_list):
    # Takes list of string inputs '{cost} {enchant_name}' and returns a list of each item turned into a dict
    # This approach is taken rather than just returning a dictionary with name: data pairs because there can be dupes
    enchant_list = []
    for split in [x.split() for x in input_list]:
        if len(split) < 2:
            return False
        if not split[0].isnumeric():
            return False
        cost = int(split[0])
        enchant_name = get_enchant_name(' '.join(split[1:]))
        if not valid_name(enchant_name):
            return False
        level = get_enchant_level(' '.join(split[1:]))
        enchant_list.append({'name': enchant_name, 'level': level, 'cost': cost})
    return enchant_list


def get_lvl_1(level):
    return 2**(level-1)


def get_rate(level, cost):
    # cost per lvl 1. Lower is better
    return cost / get_lvl_1(level)


async def check_best_level(con, enchant_name, level, cost):
    # Assumes enchant already exists
    result = await con.fetchrow('SELECT level, villager_name, cost FROM best_enchants JOIN trades '
                                'ON best_enchants.best_level = trades.id '
                                'WHERE best_enchants.name = $1', enchant_name)
    best_level = result['level']
    best_level_cost = result['cost']
    villager_name = result['villager_name']
    formatted_enchant = string.capwords(enchant_name)
    if level > best_level:
        return (True, villager_name, f"! **[{formatted_enchant} {level}]** is a new highest level! "
                                     f"(prev: **[{formatted_enchant} {best_level}]** --> {villager_name})\n")
    elif level == best_level and get_rate(level, cost) < get_rate(best_level, best_level_cost):
        return (True, villager_name, f"~! **[{formatted_enchant} {level}]** is not a higher level but is a "
                                     f"better rate for the best level ({cost}{EMS}) compared to prev ({best_level_cost}{EMS}) "
                                     f"--> {villager_name}\n")
    else:
        return (False, villager_name, f"**[{formatted_enchant} {level}]** is not a higher level " 
                                      f"(cur: **[{formatted_enchant} {best_level}]** --> {villager_name})\n")


async def check_best_rate(con, enchant_name, level, cost):
    # Assumes enchant already exists
    level_result = await con.fetchrow('SELECT level FROM best_enchants JOIN trades '
                                      'ON best_enchants.best_level = trades.id '
                                      'WHERE best_enchants.name = $1', enchant_name)
    rate_result = await con.fetchrow('SELECT level, villager_name, cost FROM best_enchants JOIN trades '
                                     'ON best_enchants.best_rate = trades.id '
                                     'WHERE best_enchants.name = $1', enchant_name)
    best_level = level_result['level']
    highest_level = max(level, best_level)
    best_rate_level = rate_result['level']
    best_rate_cost = rate_result['cost']
    cur_cost = int(get_lvl_1(highest_level) * get_rate(best_rate_level, best_rate_cost))  # In terms of highest level
    new_cost = int(get_lvl_1(highest_level) * get_rate(level, cost))
    scaling = level != best_level
    villager_name = rate_result['villager_name']
    formatted_enchant = string.capwords(enchant_name)
    out = []
    if new_cost < cur_cost:
        out.append(f"! **[{formatted_enchant} {level}]** {cost}{EMS} is a new best rate! " 
                   f"(prev: **[{formatted_enchant} {best_rate_level}]** {best_rate_cost}{EMS} "
                   f"--> {villager_name})")
        if scaling:
            out.append(f" <Scaled> (prev {cur_cost}{EMS}) vs (new {new_cost}{EMS}) for "
                       f"**[{formatted_enchant} {highest_level}]**")
        out.append('\n')
        return True, villager_name, ''.join(out)
    elif new_cost == cur_cost and level > best_rate_level:
        return (True, villager_name, f"~! **[{formatted_enchant} {level}]** {cost}{EMS} is the same as the best rate but is a " 
                                     f"better level compared to prev of " 
                                     f"**[{formatted_enchant} {best_rate_level}]** --> {villager_name}\n")
    else:
        out.append(f"**[{formatted_enchant} {level}]** {cost}{EMS} is not a better rate "
                   f"(cur: **[{formatted_enchant} {best_rate_level}]** {best_rate_cost}{EMS} --> {villager_name})")
        if scaling:
            out.append(f" <Scaled> (cur {cur_cost}{EMS}) vs (new {new_cost}{EMS}) for "
                       f"**[{formatted_enchant} {highest_level}]**")
        out.append('\n')
        return False, villager_name, ''.join(out)


async def check_villager(con, villager_name):
    # Returns number of bests a villager has. Level/rate counted separated. If none, returns 0
    return await con.fetchval("""SELECT COUNT(DISTINCT level_trade.id) + COUNT(DISTINCT rate_trade.id) AS total_bests 
                                 FROM best_enchants 
                                 LEFT JOIN trades as level_trade ON best_enchants.best_level = level_trade.id 
                                 AND level_trade.villager_name = $1
                                 LEFT JOIN trades as rate_trade ON best_enchants.best_rate = rate_trade.id 
                                 AND rate_trade.villager_name = $1""", villager_name)


async def get_redundant_villagers(con):
    # Checks all villagers and returns a list of any that are not contributing any bests
    # For each trade, checks if its villager has any trades that are a best. There is some redundancy due to lack
    # of a villagers table, but not enough for it to seem worthwhile to create one just for this purpose
    result = await con.fetch("""SELECT DISTINCT t1.villager_name FROM trades t1
                                WHERE NOT EXISTS (
                                    SELECT 1 FROM trades t2
                                    WHERE t2.villager_name = t1.villager_name AND id IN (
                                        SELECT best_level FROM best_enchants
                                        UNION
                                        SELECT best_rate FROM best_enchants
                                    )
                                )""")
    return [record['villager_name'] for record in result]


async def get_villager_data(con, villager_name):
    result = await con.fetch("""SELECT t.enchant_name, t.level, t.cost, 
                             CASE WHEN t.id = e.best_level THEN TRUE ELSE FALSE END AS is_best_level, 
                             CASE WHEN t.id = e.best_rate THEN TRUE ELSE FALSE END AS is_best_rate 
                             FROM trades t 
                             LEFT JOIN best_enchants e ON t.enchant_name = e.name 
                             WHERE villager_name = $1 
                             ORDER BY t.id""", villager_name)
    return result


async def get_villager_enchants(con, villager_name):
    # Returns a list of enchants a villager has, ordered by trade id
    result = await con.fetch("""SELECT enchant_name FROM trades WHERE villager_name = $1 ORDER BY id""", villager_name)
    return [record['enchant_name'] for record in result]


async def get_villager_list(con):
    result = await con.fetch('SELECT DISTINCT villager_name FROM trades ORDER BY villager_name')
    return [record['villager_name'] for record in result]


async def get_enchant_list(con):
    result = await con.fetch('SELECT DISTINCT enchant_name FROM trades ORDER BY enchant_name')
    return [record['enchant_name'] for record in result]


async def get_enchant_data(con, enchant_name):
    result = await con.fetchrow("""SELECT e.best_level = e.best_rate AS same_trade,
                                   level_trade.villager_name AS best_level_villager, 
                                   level_trade.level AS best_level, 
                                   level_trade.cost AS best_level_cost,
                                   rate_trade.villager_name AS best_rate_villager,
                                   rate_trade.level AS best_rate_level,
                                   rate_trade.cost AS best_rate_cost
                                   FROM best_enchants as e
                                   LEFT JOIN trades AS level_trade ON e.best_level = level_trade.id
                                   LEFT JOIN trades AS rate_trade ON e.best_rate = rate_trade.id
                                   WHERE e.name = $1""", enchant_name)
    return result


async def get_priority_list(con):
    result = await con.fetch('SELECT DISTINCT name FROM priority ORDER BY name')
    return [record['name'] for record in result]


async def get_enchant_best_level(con, enchant_name, blacklisted=''):
    # Returns None or a dict representing new best trade
    # Blacklisted is to exclude a villager's own trades when deleting it
    trades = await con.fetch('SELECT id, villager_name, level, cost '
                             'FROM trades WHERE enchant_name = $1 AND villager_name != $2', enchant_name, blacklisted)
    best_trade_id = None
    best_level = 0
    best_cost = float('inf')
    new_villager = None
    for trade in trades:
        t_id, level, cost = trade['id'], trade['level'], trade['cost']
        if level > best_level or level == best_level and cost < best_cost:
            best_trade_id = t_id
            best_level = level
            best_cost = cost
            new_villager = trade['villager_name']
    if best_trade_id:
        return {'id': best_trade_id, 'villager_name': new_villager, 'level': best_level, 'cost': best_cost}
    else:
        return None


async def get_enchant_best_rate(con, enchant_name, blacklisted=''):
    # Returns None or a replacement trade id
    trades = await con.fetch('SELECT id, villager_name, level, cost '
                             'FROM trades WHERE enchant_name = $1 AND villager_name != $2', enchant_name, blacklisted)
    best_trade_id = None
    best_level = 0
    best_cost = None
    best_rate = float('inf')  # Lower is better
    new_villager = None
    for trade in trades:
        t_id, level, cost = trade['id'], trade['level'], trade['cost']
        new_rate = get_rate(level, cost)
        if new_rate < best_rate or new_rate == best_rate and level > best_level:
            best_trade_id = t_id
            best_level = level
            best_cost = cost
            new_villager = trade['villager_name']
    if best_trade_id:
        return {'id': best_trade_id, 'villager_name': new_villager, 'level': best_level, 'cost': best_cost}
    else:
        return None


async def update_enchant_bests(con, enchant_name):
    # Assumes enchant_name is in trades
    lvl_trade = await get_enchant_best_level(con, enchant_name)
    rate_trade = await get_enchant_best_rate(con, enchant_name)
    if lvl_trade is None or rate_trade is None:  # Shouldn't ever be the case
        raise RuntimeError(f"update_enchant_bests() called with invalid enchant {enchant_name}")
    lvl_id = lvl_trade['id']
    rate_id = rate_trade['id']

    # Check if has a best_enchants entry already
    best_exists = await con.fetchval('SELECT 1 FROM best_enchants WHERE name = $1 LIMIT 1 FOR UPDATE', enchant_name)
    if not best_exists:  # If not, create one
        await con.execute('INSERT INTO best_enchants (name, best_level, best_rate) '
                          'VALUES ($1, $2, $3)', enchant_name, lvl_id, rate_id)
    else:
        # Handle lvl, ignore if same value is already there
        await con.execute('UPDATE best_enchants SET best_level = $1 '
                          'WHERE name = $2 AND best_level IS DISTINCT FROM $1', lvl_id, enchant_name)
        # Handle rate, ignore if same value is already there
        await con.execute('UPDATE best_enchants SET best_rate = $1 '
                          'WHERE name = $2 AND best_rate IS DISTINCT FROM $1', rate_id, enchant_name)


async def rebuild_best_enchants(con):
    await con.execute('LOCK TABLE trades IN ACCESS EXCLUSIVE MODE')
    await con.execute('TRUNCATE TABLE best_enchants')
    enchant_list = await get_enchant_list(con)
    for enchant_name in enchant_list:
        await update_enchant_bests(con, enchant_name)


def diff_best_enchants(old, new):
    # Compares the snapshot of best_enchants from before and after a rebuild. Returns a summary of changes found
    # Start by restructuring both to an easier form to work with.
    # Using tuples since we're only comparing and don't need the specific information
    old_snapshot = {record['name']: (record['best_level'], record['best_rate']) for record in old}
    new_snapshot = {record['name']: (record['best_level'], record['best_rate']) for record in new}

    if old_snapshot == new_snapshot:
        return 'No changes found'

    lost_enchants = old_snapshot.keys() - new_snapshot.keys()
    new_enchants = new_snapshot.keys() - old_snapshot.keys()
    changed_enchants = {name for name in old_snapshot.keys() & new_snapshot.keys() if old_snapshot[name] != new_snapshot[name]}

    return (f"Lost enchants ({len(lost_enchants)}): {', '.join(lost_enchants)}\n"
            f"New enchants ({len(new_enchants)}): {', '.join(new_enchants)}\n"
            f"Changed enchants ({len(changed_enchants)}): {', '.join(changed_enchants)}")


def level_to_xp(level):
    if level <= 16:
        return level ** 2 + 6 * level
    elif level <= 31:
        return 2.5 * level ** 2 - 40.5 * level + 360
    else:  # level ≥ 32
        return 4.5 * level ** 2 - 162.5 * level + 2220


def xp_to_level(xp):
    if xp <= 352:  # level 0-16
        return sqrt(xp + 9) - 3
    elif xp <= 1507:  # level 17-31
        return 81/10 + sqrt(2/5 * (xp - 7839/40))
    else:  # xp > 1507, level 32+
        return 325/18 + sqrt(2/9 * (xp - 54215/72))


def sorted_dict(dictionary):
    return dict(sorted(dictionary.items()))


def valid_name(name):
    return all([c in VALID_CHARS for c in name])
