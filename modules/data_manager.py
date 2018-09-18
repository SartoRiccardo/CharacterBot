import json
import asyncio
import asyncpg
from modules.misc_utils import *
from modules.data_getter import get_columns, get_server_data, get_tables, get_character_info, get_con

async def create_table(server, name): #OK
    """Create a table in server's database"""
    query = f"CREATE TABLE IF NOT EXISTS s{server}t{name}" \
            "(name TEXT, taken_by TEXT"

    columns = await get_columns(server)
    for col in columns[2:]:
        query += f",{col} TEXT"
    query += ');'

    await get_con().execute(query)


async def delete_table(server, table): #OK
    """Delete table in server's database"""
    query = f"DROP TABLE IF EXISTS s{server}t{table}"
    await get_con().execute(query)


async def update_template(server, columns):  #FIXME REFACTOR
    """Replace server's template with columns"""
    async def reformat_table(t):
        current_columns = await get_columns(server)
        query = f"ALTER TABLE {t} RENAME TO hold;"
        await get_con().execute(query)

        query = f"CREATE TABLE {t}(name TEXT, taken_by TEXT"
        for col in columns:
            query += f", {col} TEXT"
        query += ");"
        await get_con().execute(query)

        # Inserts into the new table the old data if possible
        query = f"INSERT INTO {t}(name, taken_by"
        for col in columns:
            if col in current_columns:
                query += f", {col}"
        query += ') SELECT name, taken_by'
        for col in columns:
            if col in current_columns:
                query += f", {col}"
        query += " FROM hold;"
        await get_con().execute(query)

        # Inserts "N/A" where data isn't present
        for col in columns:
            if col not in current_columns:
                query = f"UPDATE {t} SET {col}='N/A'"
                await get_con().execute(query)

        await get_con().execute("DROP TABLE hold;")


    tables = await get_tables(server)
    for t in tables:
        await reformat_table(f"s{server}t{t}")

    servers_dir = project_path + '/files/servers.json'
    with open(servers_dir, 'r') as jsonFile:
        data = json.load(jsonFile)

    data[server] = ["name", "taken_by"] + list(columns)

    with open(servers_dir, 'w') as jsonFile:
        json.dump(data, jsonFile)

async def modify(server, table, to_modify, *conditions): #OK
    """Modify server's database using condition"""
    query = f"UPDATE s{server}t{table} SET {to_modify}"
    if len(conditions) != 0:
        query += f" WHERE {'AND'.join(list(conditions))}"
    query += ';'

    await get_con().execute(query)


async def insert(server, table, values): #OK
    """Insert condition in server's database"""
    query = f"INSERT INTO s{server}t{table} VALUES("
    for v in values:
        query += f"'{v}', "
    query = query[:-2] + ");"

    await get_con().execute(query)

async def pgdelete(server, table, *conditions): #OK
    """Deletes a character from server's database"""
    query = f"DELETE FROM s{server}t{table}"
    if len(conditions) != 0:
        query += f" WHERE {'AND'.join(list(conditions))}"
    query += ';'

    await get_con().execute(query)

