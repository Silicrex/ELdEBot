import os
import json
from pathlib import Path
from dotenv import load_dotenv


def get_discord_token():
    if not Path('.env').is_file():
        with open('.env', 'w') as file:
            file.write('# Tokens\nDISCORD_TOKEN=')
        print('Generated .env file, stopping')
        quit()
    load_dotenv()
    return os.getenv('DISCORD_TOKEN')
