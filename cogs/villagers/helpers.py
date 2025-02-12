import string
from .data import DB

EMS = '<:emerald:1156624279857811457>'
EBOOK = '<:ebook:1158537467482341487>'
VALID_CHARS = set(string.ascii_letters + string.digits + " '.:")


def create_enchant_data_string(record, enchant_name):
    # record is a dict of the enchant dict
    same_trade = record['same_trade']
    best_level = record['best_level']
    best_rate_level = record['best_rate_level']
    best_rate_cost = record['best_rate_cost']
    res = [f"**[{string.capwords(enchant_name)} {best_level}]** "
           f"{record['best_level_cost']}{EMS} --> **{record['best_level_villager']}**"]
    if not same_trade:
        scaled_cost = int(get_rate(best_rate_level, best_rate_cost) * get_lv1(best_level))
        res.append(f" \\|\\| best rate: **[{string.capwords(enchant_name)} {best_rate_level}]** "
                   f"{best_rate_cost}{EMS} (Scaled {scaled_cost}{EMS}) --> **{record['best_rate_villager']}**")
    return ''.join(res)


def create_villager_data_string(records, villager_name):
    # records is a list of trade records
    enchants = []
    for trade in records:  # Will have a trade record per slot
        is_best_level = trade['is_best_level']
        is_best_rate = trade['is_best_rate']
        enchant_text = f"**[{string.capwords(trade['enchant_name'])} {trade['level']}]** {trade['cost']}{EMS}"
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
            return villager_name
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


def get_lv1(level):
    return 2**(level-1)


def get_rate(level, cost):
    # cost per lvl 1. Lower is better
    return cost / get_lv1(level)


async def check_best_level(con, enchant_name, level, cost):
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
    cur_cost = int(get_lv1(highest_level) * get_rate(best_rate_level, best_rate_cost))  # In terms of highest level
    new_cost = int(get_lv1(highest_level) * get_rate(level, cost))
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


async def get_villager_data(con, villager_name):
    result = await con.fetch("""SELECT t.enchant_name, t.level, t.cost, 
                             CASE WHEN t.id = e.best_level THEN TRUE ELSE FALSE END AS is_best_level, 
                             CASE WHEN t.id = e.best_rate THEN TRUE ELSE FALSE END AS is_best_rate 
                             FROM trades t 
                             LEFT JOIN best_enchants e ON t.enchant_name = e.name 
                             WHERE villager_name = $1 
                             ORDER BY slot""", villager_name)
    return result


async def get_villager_list(con):
    result = await con.fetch('SELECT DISTINCT villager_name FROM trades')
    sorted_villagers = sorted([record['villager_name'] for record in result])
    return sorted_villagers


async def get_enchant_list(con):
    result = await con.fetch('SELECT DISTINCT name FROM best_enchants ORDER BY name')
    sorted_enchants = sorted([record['name'] for record in result])
    return sorted_enchants


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


def sorted_dict(dictionary):
    return dict(sorted(dictionary.items()))


def valid_name(name):
    return all([c in VALID_CHARS for c in name])
