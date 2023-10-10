import string
from .data import DB
from .helpers import get_enchant_name, get_enchant_level, EMS


def estring(full_enchant_name):
    enchants = DB['enchants']
    enchant_name = get_enchant_name(full_enchant_name)
    enchant_level = get_enchant_level(full_enchant_name)
    if enchant_name in enchants:
        best_level = enchants[enchant_name]['best_level']
        cost = best_level['cost']
        villager_name = best_level['villager_name']
        if enchant_level == best_level['level']:
            return f'**{string.capwords(full_enchant_name)}** ({cost}{EMS} @ {villager_name})'
        else:  # Lower level owned
            return f"**{string.capwords(full_enchant_name)}** (<Lvl {best_level['level']}> {cost}{EMS} @ {villager_name})"
    else:
        return f'**{string.capwords(full_enchant_name)}** (DNH)'


def helmet_tag():
    return (f"**Helmet Enchantment Guide**\n"
            f"Total XP: 776, Total Levels: 44\n"
            f"(1 -> 2 -> 3)\n\n"
            f"**[2]** {estring('respiration 3')} + {estring('aqua affinity')}\n"
            f"**[2]** {estring('unbreaking 3')} + {estring('mending')}\n"
            f"**[2]** **<Unbreaking 3 + Mending>** + {estring('heating')}\n"
            f"**[16]** Item + {estring('advanced protection 4')}\n"
            f"**[10]** Item + **<Respiration 3 + Aqua Affinity>**\n"
            f"**[12]** Item + **<Unbreaking 3 + Mending + Heating>**\n\n"
            f"Notes: Heating only if hyperthermia immune otherwise skip it")


def chestplate_tag():
    return (f"**Chestplate Enchantment Guide**\n"
            f"Total XP: 1150, Total Levels: 48\n"
            f"(1 -> 2 -> 1)\n\n"
            f"**[2]** {estring('unbreaking 3')} + {estring('mending')}\n"
            f"**[20]** Item + {estring('strengthened vitality 5')}\n"
            f"**[7]** Item + **<Unbreaking 3 + Mending>**\n"
            f"**[19]** Item + {estring('advanced protection 4')}\n\n")


def chestplate_heating_tag():
    return (f"**Chestplate (Heating) Enchantment Guide**\n"
            f"Total XP: 1201, Total Levels: 51\n"
            f"(1 -> 2 -> 2)\n\n"
            f"**[1]** {estring('advanced protection 4')} + {estring('heating')}\n"
            f"**[2]** {estring('unbreaking 3')} + {estring('mending')}\n"
            f"**[20]** Item + {estring('strengthened vitality 5')}\n"
            f"**[19]** Item + **<Advanced Protection 4 + Heating>**\n"
            f"**[9]** Item + **<Unbreaking 3 + Mending>**\n\n"
            f"Notes: Heating is for hyperthermia-immune builds")


def chestplate_berserk_tag():
    return (f"**Chestplate (Inner Berserk & Heating) Enchantment Guide**\n"
            f"Total XP: 2131, Total Levels: 73\n"
            f"(1 -> 2 -> 3)\n\n"
            f"**[3]** {estring('advanced protection 4')} + {estring('unbreaking 3')}\n"
            f"**[2]** {estring('inner berserk 4')} + {estring('mending')}\n"
            f"**[2]** **<Inner Berserk 4 + Mending>** + {estring('heating')}\n"
            f"**[20]** Item + {estring('strengthened vitality 5')}\n"
            f"**[21]** Item + **<Advanced Protection 4 + Unbreaking 3>**\n"
            f"**[25]** Item + **<Inner Berserk 4 + Mending + Heating>**\n\n"
            f"Notes: Heating only if hyperthermia immune, Inner Berserk is optional and not very useful")


def leggings_tag():
    return (f"**Leggings Enchantment Guide**\n"
            f"Total XP: 728, Total Levels: 42\n"
            f"(1 -> 2 -> 3)\n\n"
            f"**[2]** {estring('agility 2')} + {estring('evasion')}\n"
            f"**[2]** {estring('unbreaking 3')} + {estring('mending')}\n"
            f"**[2]** **<Unbreaking 3 + Mending>** + {estring('heating')}\n"
            f"**[16]** Item + {estring('advanced protection 4')}\n"
            f"**[8]** Item + **<Agility 2 + Evasion>**\n"
            f"**[12]** Item + **<Unbreaking 3 + Mending + Heating>**\n\n"
            f"Notes: Heating only if hyperthermia immune otherwise skip it")


# def boots_tag():
#     return (f"**Boots Enchantment Guide**\n"
#             f"Total XP: 2067, Total Levels: 91\n"
#             f"(1 -> 2 -> 4 -> 1)\n\n"
#             f"**[3]** {estring('advanced feather falling 4')} + {estring('unbreaking 3')}\n"
#             f"**[4]** {estring('light weight 3')} + {estring('high jump 2')}\n"
#             f"**[1]** {estring('mending')} + {estring('heating')}\n"
#             f"**[5]** **<Light Weight 3 + High Jump 2>** + **<Mending + Heating>**\n"
#             f"**[4]** {estring('underwater strider 3')} + {estring('double jump')}\n"
#             f"**[16]** Item + {estring('advanced protection 4')}\n"
#             f"**[21]** Item + **<Advanced Feather Falling 4 + Unbreaking 3>**\n"
#             f"**[19]** Item + **<Light Weight 3 + High Jump 2 + Mending + Heating>**\n"
#             f"**[18]** Item + **<Underwater Strider 3 + Double Jump>**\n\n"
#             f"Notes: Heating is for hyperthermia-immune builds")


def boots_heating_tag():
    return (f"**Boots Enchantment Guide**\n"
            f"Total XP: 2067, Total Levels: 91\n"
            f"(1 -> 2 -> 4 -> 2)\n\n"
            f"**[3]** {estring('advanced feather falling 4')} + {estring('unbreaking 3')}\n"
            f"**[4]** {estring('light weight 3')} + {estring('high jump 2')}\n"
            f"**[1]** {estring('mending')} + {estring('heating')}\n"
            f"**[5]** **<Light Weight 3 + High Jump 2>** + **<Mending + Heating>**\n"
            f"**[4]** {estring('underwater strider 3')} + {estring('double jump')}\n"
            f"**[16]** Item + {estring('advanced protection 4')}\n"
            f"**[21]** Item + **<Advanced Feather Falling 4 + Unbreaking 3>**\n"
            f"**[19]** Item + **<Light Weight 3 + High Jump 2 + Mending + Heating>**\n"
            f"**[18]** Item + **<Underwater Strider 3 + Double Jump>**\n\n"
            f"Notes: Heating is for hyperthermia-immune builds")
