import json
import asyncio
import asyncpg
from modules.misc_utils import *
from modules.data_getter import get_columns, get_server_data, get_tables, get_character_info, fetch, get_con


async def start_servers_data():
    await get_con().execute("CREATE TABLE IF NOT EXISTS servers"
                            "(server TEXT, template TEXT, backup TEXT, prefix TEXT);")


async def create_table(server, name, bk=False):
    """Create a table in server's database"""
    query = f"CREATE TABLE IF NOT EXISTS s{server}t{name}" \
            "(name TEXT, taken_by TEXT"
    if bk:
        query = f"CREATE TABLE IF NOT EXISTS bk{server}t{name}" \
                "(name TEXT, taken_by TEXT"

    columns = await get_columns(server)
    for col in columns[2:]:
        query += f",{col} TEXT"
    query += ');'

    await get_con().execute(query)


async def delete_table(server, table, bk=False):
    """Delete table in server's database"""
    query = f"DROP TABLE IF EXISTS s{server}t{table};"
    if bk:
        query = f"DROP TABLE IF EXISTS bk{server}t{table};"

    dprint(query)
    await get_con().execute(query)


async def update_template(server, columns):
    async def reformat_table(t):
        await get_con().execute("DROP TABLE IF EXISTS hold;")

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

    servers = await get_con().fetch("SELECT server FROM servers;")
    servers = [dict(s)["server"] for s in servers]
    if server not in servers:
        await register_server(server)

    for c in columns:
        if ' ' in c:
            raise SyntaxError("space_in_arg")

    tables = await get_tables(server)
    for t in tables:
        await reformat_table(f"s{server}t{t}")

    template = ["name", "taken_by"] + list(columns)
    query = f"UPDATE servers SET template='{' '.join(template)}' WHERE server='{server}'"
    await get_con().execute(query)


async def register_server(server):
    if len(await get_con().fetch(f"SELECT server FROM servers WHERE server='{server}'")) == 0:
        query = f"INSERT INTO servers VALUES({server}, 'name taken_by', 'N/A', '$');"
        await get_con().execute(query)


async def change_prefix(server, newprefix):
    query = f"UPDATE servers SET prefix='{newprefix}' WHERE server='{server}'"
    await get_con().execute(query)


async def modify(server, table, to_modify, *conditions):
    """Modify server's database using condition"""
    query = f"UPDATE s{server}t{table} SET {to_modify}"
    if len(conditions) != 0:
        query += f" WHERE {'AND'.join(list(conditions))}"
    query += ';'

    await get_con().execute(query)


async def insert(server, table, values, bk=False):
    """Insert condition in server's database"""
    query = f"INSERT INTO s{server}t{table} VALUES("
    if bk:
        query = f"INSERT INTO bk{server}t{table} VALUES("

    for v in values:
        v = v.replace("'", "''")
        query += f"'{v}', "
    query = query[:-2] + ");"

    await get_con().execute(query)


async def pgdelete(server, table, *conditions):
    """Deletes a character from server's database"""
    query = f"DELETE FROM s{server}t{table}"
    if len(conditions) != 0:
        query += f" WHERE {'AND'.join(list(conditions))}"
    query += ';'

    await get_con().execute(query)


async def backup(server):
    """Back up the data under bk{server}t{table}"""
    await delete_backup(server)

    columns = await get_columns(server)
    tables = await get_tables(server)
    for t in tables:
        await create_table(server, t, bk=True)

        for info in await fetch(server, t, "all"):
            values = []
            for c in columns:
                values.append(info[c])
            await insert(server, t, values, bk=True)

    query = f"UPDATE servers SET backup='{' '.join(columns)}' WHERE server='{server}';"
    await get_con().execute(query)


async def delete_backup(server):
    """Delete all tables under the bk{server}t{table} name"""
    backups = await get_tables(server, bk=True)
    for b in backups:
        await delete_table(server, b, bk=True)

    query = f"UPDATE servers SET backup='N/A' WHERE server='{server}';"
    await get_con().execute(query)


async def load_backup(server):
    """Load the backup"""
    dprint("Load backup start")
    bkcolumns = await get_columns(server, bk=True)
    if bkcolumns == "N/A":
        raise ValueError("no_backup")

    dprint("Backup present")
    bkcolumns.remove("name")
    bkcolumns.remove("taken_by")
    await update_template(server, bkcolumns)

    dprint("Deleting tables")
    tables = await get_tables(server)
    for t in tables:
        await delete_table(server, t)
    dprint("Tables deleted")

    bkcolumns.insert(0, "taken_by")
    bkcolumns.insert(0, "name")
    bktables = await get_tables(server, bk=True)
    for t in bktables:
        await create_table(server, t)

        for info in await fetch(server, t, "all", bk=True):
            values = []
            for c in bkcolumns:
                values.append(info[c])

            await insert(server, t, values)

    dprint("Backup loaded")



