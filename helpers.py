import os
from pathlib import Path
from dotenv import load_dotenv
from cogs import EXTENSIONS


def read_env():
    if not Path('.env').is_file():
        with open('.env', 'w') as file:
            file.write('# Tokens\n'
                       'DISCORD_TOKEN=\n\n'
                       '# Settings\n'
                       'BOT_PREFIX=\n\n'
                       '# Postgres\n'
                       'PG_DATABASE=\n'
                       'PG_USER=\n'
                       'PG_PASSWORD=')
        print('Generated .env file, stopping')
        quit()
    load_dotenv()


def get_extension(text):
    # If extension is not found, see if it's short for one that does exist
    if text in EXTENSIONS:
        return text
    for extension in EXTENSIONS:
        if extension.startswith(text):
            return extension
    return None


def get_discord_token():
    return os.getenv('DISCORD_TOKEN')

def get_bot_prefix():
    return os.getenv('BOT_PREFIX')

def get_pg_login():
    return {'database': os.getenv('PG_DATABASE'), 'user': os.getenv('PG_USER'), 'password': os.getenv('PG_PASSWORD')}
