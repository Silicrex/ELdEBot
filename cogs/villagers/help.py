import discord


async def get_help_embed(command):
    help_dict = get_help_dict()
    if arg not in help_dict:
        embed = discord.Embed(
            title='Invalid command/subcommand',
            color=0xFFE900
        )
        return embed
    value = help_dict[arg]
    aliases_text = f"\n**Aliases:** {', '.join(value['alias'])}" if value['alias'] else ''
    embed = discord.Embed(
        title=value['title'],
        description=f"{value['description']}\n\n"
                    f"**Example:** {value['example']}"
                    f"{aliases_text}",
        color=0x00AD25
    )
    return embed