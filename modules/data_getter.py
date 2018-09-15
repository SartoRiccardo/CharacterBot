import json
import asyncio
import asyncpg
import config
import sqlite3
from contextlib import closing
from modules.misc_utils import *

credentials = {
    'user': config.USERNAME,
    'password': config.PASSWORD,
    'host': config.HOST,
    'database': config.DATABASE
}
con = None
async def start_database():
    global con
    con = await asyncpg.create_pool(**credentials)

def get_con():
    return con



async def get_tables(server):
    """Return the server's tables"""
    raw = await con.fetch("SELECT table_name FROM information_schema.tables "
                          "WHERE table_schema='public' "
                          "AND table_type='BASE TABLE';")

    ret = []
    for r in raw:
        if f"s{server}t" in r["table_name"]:
            ret.append(r["table_name"].replace(f"s{server}t", ''))

    print()
    return ret


async def get_columns(server):
    """Return name, taken_by and the rest of the template"""
    with open(os.path.join(project_path,
                      "files",
                      "servers.json"), 'r') as jsonFile:
        ret = json.load(jsonFile)[server]

    return ret


async def get_character_info(server, character):
    """Return dict containing the character's info"""
    ret = {}
    tables = await get_tables(server)
    for t in tables:
        info = await con.fetch(f"SELECT * FROM s{server}t{t} WHERE LOWER(name)=LOWER('{character}')")
        if len(info) > 0:
            ret = dict(info[0])
            ret["table"] = t
            break

    return ret


async def get_user_character(server, user):
    """Return the character assigned to the user, None if nothing is found"""
    ret = None
    tables = await get_tables(server)
    for t in tables:
        info = await fetch(server, t, "name", f"taken_by='{user}'")
        print(info)
        if len(info) > 0:
            ret = info[0][0]
            break

    return ret


async def fetch(server, table, to_return, *conditions):
    """Return condition's results from server's database"""
    if to_return == "all":
        query = f"SELECT * FROM s{server}t{table}"
    else:
        query = f"SELECT {to_return} FROM s{server}t{table}"

    if len(conditions) != 0:
        query += f" WHERE {'AND'.join(list(conditions))}"

    query += ';'

    return tuple(await get_con().fetch(query))

async def get_server_data():
    """Return the contents of servers.json"""
    path = os.path.join(project_path, "files", "servers.json")
    with open(path, 'r') as jsonFile:
        ret = json.load(jsonFile)

    return ret