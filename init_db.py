import asyncio
import asyncpg
from helpers import read_env, get_pg_login

# This script assumes the empty database already exists, and will populate it with the table schemas.
# It uses the information provided in the .env file

read_env()
pg_login = get_pg_login()

# Table structures
TABLE_SQL = """
CREATE TABLE IF NOT EXISTS trades (
    id serial PRIMARY KEY,
    villager_name text NOT NULL,
    enchant_name text NOT NULL,
    level smallint NOT NULL,
    cost smallint NOT NULL
);

CREATE TABLE IF NOT EXISTS best_enchants (
    name text PRIMARY KEY,
    best_level integer REFERENCES trades(id) NOT NULL,
    best_rate integer REFERENCES trades(id) NOT NULL
);

CREATE TABLE IF NOT EXISTS priority (
    name text PRIMARY KEY
);
"""


async def create_tables():
    con = await asyncpg.connect(**pg_login)
    try:
        await con.execute(TABLE_SQL)
        print('Tables generated successfully (or already exist)')
    except Exception as e:
        print(e)
    finally:
        await con.close()


if __name__ == '__main__':
    asyncio.run(create_tables())
