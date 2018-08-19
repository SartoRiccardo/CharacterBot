import json
import sqlite3
from contextlib import closing
from modules.misc_utils import *


def get_tables(ctx):
    server = ctx.message.server.id
    conn = sqlite3.connect(get_CharacterBot_path() + '/data/{}.db'.format(server))

    with closing(conn.cursor()) as c:
        c.execute('SELECT name FROM sqlite_master WHERE type="table"')
        raw = c.fetchall()
    conn.close()

    ret = [t[0][1:] for t in raw]
    return ret


def get_columns(ctx):
    server = ctx.message.server.id
    with open(get_CharacterBot_path() + '/files/servers.json', 'r') as jsonFile:
        ret = json.load(jsonFile)[str(server)]

    return ret


def add_table(ctx, table):
    with open(get_CharacterBot_path() + '/files/tables.json', 'r') as jsonFile:
        data = json.load(jsonFile)

    data['tables'].append(table)
    server = ctx.message.server.id
    conn = sqlite3.connect(get_CharacterBot_path() + '/data/{}.db'.format(server))

    with closing(conn.cursor()) as c:
        command = 'CREATE TABLE IF NOT EXISTS t{} ('.format(table)
        for param in data['columns']:
            command += '{} TEXT, '.format(param)
        command += ',role TEXT,taken_by TEXT)'
        c.execute(command)

    conn.close()
    data = sorted(data)

    with open(get_CharacterBot_path() + '/files/tables.json', 'r') as jsonFile:
        json.dumps(data, jsonFile)


def get_character_info(ctx, character):
    server = ctx.message.server.id
    conn = sqlite3.connect(get_CharacterBot_path() + '/data/{}.db'.format(server))

    with closing(conn.cursor()) as c:
        ret = {}
        tables = get_tables(ctx)
        for t in tables:
            c.execute('SELECT * FROM t{} WHERE LOWER(name)=LOWER("{}")'.format(t, character))
            info = c.fetchall()
            if len(info) > 0:
                ret[t] = info[0]
                break

    conn.close()
    return ret


def get_user_character(ctx):
    user = ctx.message.author
    server = ctx.message.server.id
    conn = sqlite3.connect(get_CharacterBot_path() + '/data/{}.db'.format(server))

    with closing(conn.cursor()) as c:
        ret = None
        tables = get_tables(ctx)
        for t in tables:
            c.execute('SELECT name FROM t{} WHERE taken_by="{}"'.format(t, user))
            info = c.fetchall()
            if len(info) > 0:
                ret = info[0][0]
                break

    conn.close()
    return ret


def fetch(ctx, condition):
    server = ctx.message.server.id
    conn = sqlite3.connect(get_CharacterBot_path() + '/data/{}.db'.format(server))

    with closing(conn.cursor()) as c:
        c.execute(condition.replace('FROM ', 'FROM t'))
        ret = c.fetchall()

    conn.close()
    return ret

def modify(ctx, condition):
    server = ctx.message.server.id
    conn = sqlite3.connect(get_CharacterBot_path() + '/data/{}.db'.format(server))

    with closing(conn.cursor()) as c:
        c.execute(condition.replace('UPDATE ', 'UPDATE t'))
        conn.commit()

    conn.close()