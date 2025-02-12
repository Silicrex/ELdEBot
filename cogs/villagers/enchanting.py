import string
from .helpers import get_enchant_name, get_enchant_level, get_enchant_data, EMS


async def estring(con, full_enchant_name):
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
        return f'**{string.capwords(full_enchant_name)}** (DNH)'


async def helmet_tag(con):
    return (f"**Helmet Enchantment Guide**\n"
            f"Total XP: 776, Total Levels: 44\n"
            f"(1 -> 2 -> 3)\n\n"
            f"**[2]** {await estring(con, 'respiration 3')} + {await estring(con, 'aqua affinity')}\n"
            f"**[2]** {await estring(con, 'unbreaking 3')} + {await estring(con, 'mending')}\n"
            f"**[2]** **<Unbreaking 3 + Mending>** + {await estring(con, 'heating')}\n"
            f"**[16]** Item + {await estring(con, 'advanced protection 4')}\n"
            f"**[10]** Item + **<Respiration 3 + Aqua Affinity>**\n"
            f"**[12]** Item + **<Unbreaking 3 + Mending + Heating>**\n\n"
            f"Notes: Heating only if hyperthermia immune otherwise skip it")


async def chestplate_tag(con):
    return (f"**Chestplate Enchantment Guide**\n"
            f"Total XP: 1201, Total Levels: 51\n"
            f"(1 -> 2 -> 2)\n\n"
            f"**[1]** {await estring(con, 'advanced protection 4')} + {await estring(con, 'heating')}\n"
            f"**[2]** {await estring(con, 'unbreaking 3')} + {await estring(con, 'mending')}\n"
            f"**[20]** Item + {await estring(con, 'strengthened vitality 5')}\n"
            f"**[19]** Item + **<Advanced Protection 4 + Heating>**\n"
            f"**[9]** Item + **<Unbreaking 3 + Mending>**\n\n"
            f"Notes: Heating is for hyperthermia-immune builds, use enchant chestplate_noheating otherwise")


async def chestplate_noheating_tag(con):
    return (f"**Chestplate (no Heating) Enchantment Guide**\n"
            f"Total XP: 1150, Total Levels: 48\n"
            f"(1 -> 2 -> 1)\n\n"
            f"**[2]** {await estring(con, 'unbreaking 3')} + {await estring(con, 'mending')}\n"
            f"**[20]** Item + {await estring(con, 'strengthened vitality 5')}\n"
            f"**[7]** Item + **<Unbreaking 3 + Mending>**\n"
            f"**[19]** Item + {await estring(con, 'advanced protection 4')}\n\n")



async def chestplate_berserk_tag(con):
    return (f"**Chestplate (Inner Berserk & Heating) Enchantment Guide**\n"
            f"Total XP: 2131, Total Levels: 73\n"
            f"(1 -> 2 -> 3)\n\n"
            f"**[3]** {await estring(con, 'advanced protection 4')} + {await estring(con, 'unbreaking 3')}\n"
            f"**[2]** {await estring(con, 'inner berserk 4')} + {await estring(con, 'mending')}\n"
            f"**[2]** **<Inner Berserk 4 + Mending>** + {await estring(con, 'heating')}\n"
            f"**[20]** Item + {await estring(con, 'strengthened vitality 5')}\n"
            f"**[21]** Item + **<Advanced Protection 4 + Unbreaking 3>**\n"
            f"**[25]** Item + **<Inner Berserk 4 + Mending + Heating>**\n\n"
            f"Notes: Heating only if hyperthermia immune, Inner Berserk is optional and not very useful")


async def leggings_tag(con):
    return (f"**Leggings Enchantment Guide**\n"
            f"Total XP: 728, Total Levels: 42\n"
            f"(1 -> 2 -> 3)\n\n"
            f"**[2]** {await estring(con, 'agility 2')} + {await estring(con, 'evasion')}\n"
            f"**[2]** {await estring(con, 'unbreaking 3')} + {await estring(con, 'mending')}\n"
            f"**[2]** **<Unbreaking 3 + Mending>** + {await estring(con, 'heating')}\n"
            f"**[16]** Item + {await estring(con, 'advanced protection 4')}\n"
            f"**[8]** Item + **<Agility 2 + Evasion>**\n"
            f"**[12]** Item + **<Unbreaking 3 + Mending + Heating>**\n\n"
            f"Notes: Heating only if hyperthermia immune otherwise skip it")


async def boots_tag(con):
    return (f"**Boots Enchantment Guide**\n"
            f"Total XP: 2067, Total Levels: 91\n"
            f"(1 -> 2 -> 4 -> 2)\n\n"
            f"**[3]** {await estring(con, 'advanced feather falling 4')} + {await estring(con, 'unbreaking 3')}\n"
            f"**[4]** {await estring(con, 'light weight 3')} + {await estring(con, 'high jump 2')}\n"
            f"**[1]** {await estring(con, 'mending')} + {await estring(con, 'heating')}\n"
            f"**[5]** **<Light Weight 3 + High Jump 2>** + **<Mending + Heating>**\n"
            f"**[4]** {await estring(con, 'underwater strider 3')} + {await estring(con, 'double jump')}\n"
            f"**[16]** Item + {await estring(con, 'advanced protection 4')}\n"
            f"**[21]** Item + **<Advanced Feather Falling 4 + Unbreaking 3>**\n"
            f"**[19]** Item + **<Light Weight 3 + High Jump 2 + Mending + Heating>**\n"
            f"**[18]** Item + **<Underwater Strider 3 + Double Jump>**\n\n"
            f"Notes: Heating is for hyperthermia-immune builds, use enchant boots_noheating otherwise")


async def boots_noheating_tag(con):
    return (f"**Boots (no Heating) Enchantment Guide**\n"
            f"Total XP: 1972, Total Levels: 87\n"
            f"(1 -> 2 -> 3 -> 2)\n\n"
            f"**[2]** {await estring(con, 'advanced feather falling 4')} + {await estring(con, 'mending')}\n"
            f"**[4]** {await estring(con, 'light weight 3')} + {await estring(con, 'high jump 2')}\n"
            f"**[4]** **<Light Weight 3 + High Jump 2>** + {await estring(con, 'unbreaking 3')}\n"
            f"**[4]** {await estring(con, 'underwater strider 3')} + {await estring(con, 'double jump')}\n"
            f"**[16]** Item + {await estring(con, 'advanced protection 4')}\n"
            f"**[20]** Item + **<Advanced Feather Falling 4 + Mending>**\n"
            f"**[19]** Item + **<Light Weight 3 + High Jump 2 + Unbreaking 3>**\n"
            f"**[18]** Item + **<Underwater Strider 3 + Double Jump>**\n\n")


async def javelin_tag(con):
    return (f"**Javelin Enchantment Guide**\n"
            f"Total XP: 1635, Total Levels: 84\n"
            f"(1 -> 2 -> 4 -> 2)\n\n"
            f"**[4]** {await estring(con, 'lucky throw 3')} + {await estring(con, 'advanced mending')}\n"
            f"**[4]** {await estring(con, 'hydrodynamic')} + {await estring(con, 'supercharge 2')}\n"
            f"**[3]** {await estring(con, 'propulsion 3')} + {await estring(con, 'unbreaking 3')}\n"
            f"**[8]** **<Hydrodynamic + Supercharge 2>** + **<Propulsion 3 + Unbreaking 3>**\n"
            f"**[4]** {await estring(con, 'razors edge 5')} + {await estring(con, 'expanse 2')}\n"
            f"**[12]** Item + {await estring(con, 'return 3')}\n"
            f"**[12]** Item + **<Lucky Throw 3 + Advanced Mending>**\n"
            f"**[20]** Item + **<Hydrodynamic + Supercharge 2 + Propulsion 3 + Unbreaking 3>**\n"
            f"**[17]** Item + **<Razors Edge 5 + Expanse 2>**\n\n")



