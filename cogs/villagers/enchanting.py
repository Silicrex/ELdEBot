import string
from .helpers import get_enchant_name, get_enchant_level, get_enchant_data, EMS


async def estring(con, full_enchant_name):
    full_enchant_name = full_enchant_name.lower()
    enchant_name = get_enchant_name(full_enchant_name)
    enchant_level = get_enchant_level(full_enchant_name)
    result = await get_enchant_data(con, enchant_name)
    if result:
        best_level = result['best_level']
        cost = result['best_level_cost']
        villager_name = result['best_level_villager']
        if enchant_level == result['best_level']:
            return f'**{string.capwords(full_enchant_name)}** ({cost}{EMS} @ {villager_name})'
        else:  # Lower level owned
            return f"**{string.capwords(full_enchant_name)}** (<Lvl {best_level}> {cost}{EMS} @ {villager_name})"
    else:
        return f'**{string.capwords(full_enchant_name)}** (N/A)'


async def helmet_tag(con):
    return (f"**Helmet Enchantment Guide**\n"
            f"Total XP: 1314, Total Levels: 68\n"
            f"(1 -> 2 -> 2 -> 2)\n\n"
            f"**[4]** {await estring(con, 'Rune: Revival 2')} + {await estring(con, 'Advanced Mending')}\n"
            f"**[3]** {await estring(con, 'Combat Medic 3')} + {await estring(con, 'Unbreaking 3')}\n"
            f"**[2]** {await estring(con, 'Respiration 3')} + {await estring(con, 'Aqua Affinity')}\n"
            f"**[16]** Item + {await estring(con, 'Advanced Protection 4')}\n"
            f"**[14]** Item + **<Rune: Revival 2 + Advanced Mending>**\n"
            f"**[13]** Item + **<Combat Medic 3 + Unbreaking 3>**\n"
            f"**[16]** Item + **<Respiration 3 + Aqua Affinity>**\n\n")


async def chestplate_tag(con):
    return (f"**Chestplate Enchantment Guide**\n"
            f"Total XP: 1540, Total Levels: 69\n"
            f"(1 -> 1 -> 2 -> 2)\n\n"
            f"**[3]** {await estring(con, 'Rune: Revival 2')} + {await estring(con, 'Unbreaking 3')}\n"
            f"**[1]** {await estring(con, 'Advanced Mending')} + {await estring(con, 'Heating')}\n"
            f"**[20]** Item + {await estring(con, 'Strengthened Vitality 5')}\n"
            f"**[17]** Item + {await estring(con, 'Advanced Protection 4')}\n"
            f"**[15]** Item + **<Rune: Revival 2 + Unbreaking 3>**\n"
            f"**[3]** Item + **<Advanced Mending + Heating>**\n\n"
            f"Notes: Heating assumes hyperthermia immunity")


async def leggings_tag(con):
    return (f"**Leggings Enchantment Guide**\n"
            f"Total XP: 882, Total Levels: 50\n"
            f"(1 -> 2 -> 2 -> 1)\n\n"
            f"**[1]** {await estring(con, 'Rune: Revival 2')} + {await estring(con, 'Heating')}\n"
            f"**[2]** {await estring(con, 'Agility 2')} + {await estring(con, 'Mending')}\n"
            f"**[16]** Item + {await estring(con, 'Advanced Protection 4')}\n"
            f"**[11]** Item + **<Rune: Revival 2 + Heating>**\n"
            f"**[10]** Item + **<Agility 2 + Mending>**\n"
            f"**[10]** Item + **<Unbreaking 3>**\n\n"
            f"Notes: Heating assumes hyperthermia immunity")


async def boots_tag(con):
    return (f"**Boots Enchantment Guide**\n"
            f"Total XP: 1601, Total Levels: 79\n"
            f"(1 -> 2 -> 3 -> 2)\n\n"
            f"**[4]** {await estring(con, 'Rune: Revival 2')} + {await estring(con, 'High Jump 2')}\n"
            f"**[3]** {await estring(con, 'Light Weight 3')} + {await estring(con, 'Unbreaking 3')}\n"
            f"**[3]** **<Light Weight 3 + Unbreaking 3>** + {await estring(con, 'Mending')}\n"
            f"**[4]** {await estring(con, 'Underwater Strider 3')} + {await estring(con, 'Double Jump')}\n"
            f"**[16]** Item + {await estring(con, 'Advanced Protection 4')}\n"
            f"**[14]** Item + **<Rune: Revival 2 + High Jump 2>**\n"
            f"**[17]** Item + **<Light Weight 3 + Unbreaking 3 + Mending>**\n"
            f"**[18]** Item + **<Underwater Strider 3 + Double Jump>**\n\n"
            f"Notes: Heating assumes hyperthermia immunity")
