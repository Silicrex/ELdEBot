import string
from .helpers import get_enchant_name, get_enchant_level, get_enchant_data, EMS
import discord


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
    embed = discord.Embed(color=0xcd3242, title='Helmet Enchantment Guide')
    embed.description = (f"Total XP: 1314, Total Levels: 68\n"
            f"(1 -> 2 -> 2 -> 2)\n\n"
            f"**[4]** {await estring(con, 'Rune: Revival 2')} + {await estring(con, 'Advanced Mending')}\n"
            f"**[3]** {await estring(con, 'Combat Medic 3')} + {await estring(con, 'Unbreaking 3')}\n"
            f"**[2]** {await estring(con, 'Respiration 3')} + {await estring(con, 'Aqua Affinity')}\n"
            f"**[16]** Item + {await estring(con, 'Advanced Protection 4')}\n"
            f"**[14]** Item + **<Rune: Revival 2 + Advanced Mending>**\n"
            f"**[13]** Item + **<Combat Medic 3 + Unbreaking 3>**\n"
            f"**[16]** Item + **<Respiration 3 + Aqua Affinity>**\n\n")
    return embed


async def chestplate_tag(con):
    embed = discord.Embed(color=0xcd3242, title='Chestplate Enchantment Guide')
    embed.description = (f"Total XP: 1540, Total Levels: 69\n"
            f"(1 -> 1 -> 2 -> 2)\n\n"
            f"**[3]** {await estring(con, 'Rune: Revival 2')} + {await estring(con, 'Unbreaking 3')}\n"
            f"**[1]** {await estring(con, 'Advanced Mending')} + {await estring(con, 'Heating')}\n"
            f"**[20]** Item + {await estring(con, 'Strengthened Vitality 5')}\n"
            f"**[17]** Item + {await estring(con, 'Advanced Protection 4')}\n"
            f"**[15]** Item + **<Rune: Revival 2 + Unbreaking 3>**\n"
            f"**[3]** Item + **<Advanced Mending + Heating>**\n\n"
            f"Notes: Heating assumes hyperthermia immunity")
    return embed


async def leggings_tag(con):
    embed = discord.Embed(color=0xcd3242, title='Leggings Enchantment Guide')
    embed.description = (f"Total XP: 882, Total Levels: 50\n"
            f"(1 -> 2 -> 2 -> 1)\n\n"
            f"**[1]** {await estring(con, 'Rune: Revival 2')} + {await estring(con, 'Heating')}\n"
            f"**[2]** {await estring(con, 'Agility 2')} + {await estring(con, 'Mending')}\n"
            f"**[16]** Item + {await estring(con, 'Advanced Protection 4')}\n"
            f"**[11]** Item + **<Rune: Revival 2 + Heating>**\n"
            f"**[10]** Item + **<Agility 2 + Mending>**\n"
            f"**[10]** Item + **<Unbreaking 3>**\n\n"
            f"Notes: Heating assumes hyperthermia immunity")
    return embed


async def boots_tag(con):
    embed = discord.Embed(color=0xcd3242, title='Boots Enchantment Guide')
    embed.description = (f"Total XP: 1601, Total Levels: 79\n"
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
    return embed


async def longbow_tag(con):
    embed = discord.Embed(color=0xcd3242, title='Longbow Enchantment Guide')
    embed.description = (f"Total XP: 2802, Total Levels: 111\n"
            f"(1 -> 2 -> 4 -> 3)\n\n"
            f"**[4]** {await estring(con, 'Rune: Arrow Piercing 4')} + {await estring(con, 'Multishot 4')}\n"
            f"**[4]** {await estring(con, 'Adept 3')} + {await estring(con, 'Infinity')}\n"
            f"**[2]** {await estring(con, 'Unbreaking 3')} + {await estring(con, 'Range')}\n"
            f"**[7]** **<Adept 3 + Infinity>** + **<Unbreaking 3 + Range>**\n"
            f"**[4]** {await estring(con, 'Rapid Fire 2')} + {await estring(con, 'Advanced Mending')}\n"
            f"**[5]** **<Rapid Fire 2 + Advanced Mending>** + {await estring(con, 'Supreme Flame')}\n"
            f"**[20]** Item + {await estring(con, 'Advanced Power 5')}\n"
            f"**[22]** Item + **<Rune: Arrow Piercing 4 + Multishot 4>**\n"
            f"**[21]** Item + **<Adept 3 + Infinity + Unbreaking 3 + Range>**\n"
            f"**[22]** Item + **<Rapid Fire 2 + Advanced Mending + Supreme Flame>**\n\n"
            f"Notes: Can swap Multishot/Splitshot")
    return embed

async def cursededge_tag(con):
    embed = discord.Embed(color=0xcd3242, title='Cursed Edge Nunchaku Enchantment Guide')
    embed.description = (f"Total XP: 15959, Total Levels: 420\n"
            f"(1 -> 2 -> 4 -> 4 -> 3, reset, 1 -> 2 -> 4 -> 4 -> 3)\n\n"
            f"**[10]** {await estring(con, 'Rune: Piercing Capabilities 4')} + {await estring(con, 'Advanced Sharpness 5')}\n"
            f"**[6]** {await estring(con, 'Subject P.E. 5')} + {await estring(con, 'Adept 3')}\n"
            f"**[4]** {await estring(con, 'Smite 5')} + {await estring(con, 'Lifesteal 2')}\n"
            f"**[11]** **<Subject P.E. 5 + Adept 3>** + **<Smite 5 + Lifesteal 2>**\n"
            f"**[6]** {await estring(con, 'Spell Breaker 5')} + {await estring(con, 'Counter Attack 3')}\n"
            f"**[2]** {await estring(con, 'Vampirism 2')} + {await estring(con, 'Mending')}\n"
            f"**[8]** **<Spell Breaker 5 + Counter Attack 3>** + **<Vampirism 2 + Mending>**\n"
            f"**[4]** {await estring(con, 'Disorienting Blade 4')} + {await estring(con, 'Curse of Possession')}\n"
            f"**[4]** **<Disorienting Blade 4 + Curse of Possession>** + {await estring(con, 'Unbreaking 3')}\n"
            f"**[12]** {await estring(con, 'Advanced Looting 3')} + {await estring(con, 'Arc Slash 3')}\n"
            f"""**[8]** {await estring(con, "Sol's Blessing 5")} + {await estring(con, 'Unsheathing 2')}\n"""
            f"**[2]** {await estring(con, 'Purging Blade 5')} + {await estring(con, 'Parry')}\n"
            f"**[9]** **<Sol's Blessing 5 + Unsheathing 2>** + **<Purging Blade 5 + Parry>**\n"
            f"**[6]** {await estring(con, 'Cursed Edge 5')} + {await estring(con, 'Combo 3')}\n"
            f"**[2]** {await estring(con, 'Luck Magnification 2')} + {await estring(con, 'True Strike')}\n"
            f"**[8]** **<Cursed Edge 5 + Combo 3>** + **<Luck Magnification 2 + True Strike>**\n"
            f"**[4]** {await estring(con, 'Fiery Edge 2')} + {await estring(con, 'Atomic Deconstructor 2')}\n"
            f"**[5]** **<Fiery Edge 2 + Atomic Deconstructor 2>** + **<Unreasonable 2>**\n"
            f"**[32]** Item + {await estring(con, 'Mortalitas 8')}\n"
            f"**[28]** Item + **<Rune: Piercing Capabilities 4 + Advanced Sharpness 5>**\n"
            f"**[31]** Item + **<Subject PE 5 + Adept 3 + Smite 5 + Lifesteal 2>**\n"
            f"**[32]** Item + **<Spell Breaker 5 + Counter Attack 3 + Vampirism 2 + Mending>**\n"
            f"**[33]** Item + **<Disorienting Blade 4 + Curse of Possession + Unbreaking 3>**\n"
            f"**[10]** Item + **Upgraded Potentials**\n"
            f"**[20]** Item + {await estring(con, 'Swifter Slashes 5')}\n"
            f"**[26]** Item + **<Advanced Looting 3 + Arc Slash 3>**\n"
            f"**[31]** Item + **<Sol's Blessing 5 + Unsheathing 2 + Purging Blade 5 + Parry>**\n"
            f"**[32]** Item + **<Cursed Edge 5 + Combo 3 + Luck Magnification 2 + True Strike>**\n"
            f"**[34]** Item + **<Fiery Edge 2 + Atomic Deconstructor 2 + Unreasonable 2>**")
    return embed
