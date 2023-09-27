import discord
from helpers import get_discord_token
from custom_bot import CustomBot


def main():
    # Intents
    intents = discord.Intents.default()
    intents.message_content = True
    intents.dm_messages = False

    # Bot setup
    discord_token = get_discord_token()
    bot = CustomBot(command_prefix='$', intents=intents, case_insensitive=True, help_command=None)
    bot.run(discord_token)


if __name__ == '__main__':
    main()
