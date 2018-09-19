import json
import asyncio
import asyncpg
import config
from modules.misc_utils import *

credentials = {
    'user': config.USERNAME,
    'password': config.PASSWORD,
    'host': config.HOST,
    'database': config.DATABASE
}


async def start_database():
    global con
    con = await asyncpg.create_pool(**credentials)


def get_con():
    return con


async def get_prefix(server):
    try:
        query = f"SELECT prefix FROM servers WHERE server='{server}';"
        ret = dict((await get_con().fetch(query))[0])["prefix"]
        return ret

    except Exception:
        return '$'


async def get_tables(server, bk=False):
    """Return the server's tables or the server's backup if bk=True"""
    raw = await con.fetch("SELECT table_name FROM information_schema.tables "
                          "WHERE table_schema='public' "
                          "AND table_type='BASE TABLE';")

    condition = f"s{server}t"
    if bk:
        condition = f"bk{server}t"

    ret = []
    for r in raw:
        if condition in r["table_name"]:
            ret.append(r["table_name"].replace(condition, ''))

    dprint(ret)
    return ret


async def get_columns(server, bk=False):
    to_return = "template"
    if bk:
        to_return = "backup"
    query = f"SELECT {to_return} FROM servers WHERE server='{server}';"

    return dict((await get_con().fetch(query))[0])[to_return].split(" ")


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
        if len(info) > 0:
            ret = info[0]["name"]
            break

    return ret


async def fetch(server, table, to_return, *conditions, bk=False):
    """Return query's results from server's database"""
    if to_return == "all":
        query = f"SELECT * FROM s{server}t{table}"
    else:
        query = f"SELECT {to_return} FROM s{server}t{table}"

    if bk:
        query = query.replace("FROM s", "FROM bk")

    if len(conditions) != 0:
        query += f" WHERE {'AND'.join(list(conditions))}"

    query += ';'
    dprint(query)

    ret = await get_con().fetch(query)
    ret = [dict(r) for r in ret]

    return ret


async def get_server_data():
    """Return the contents of servers.json"""
    path = os.path.join(project_path, "files", "servers.json")
    with open(path, 'r') as jsonFile:
        ret = json.load(jsonFile)

    return ret