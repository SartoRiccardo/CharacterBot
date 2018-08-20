import json
import sqlite3
from contextlib import closing
from modules.misc_utils import *


def get_tables(server):
    """Return the server's tables"""
    conn = sqlite3.connect(get_CharacterBot_path() + '/data/{}.db'.format(server))

    with closing(conn.cursor()) as c:
        c.execute('SELECT name FROM sqlite_master WHERE type="table"')
        raw = c.fetchall()
    conn.close()

    ret = [t[0][1:] for t in raw]
    return ret


def get_columns(server):
    """Return name, taken_by and the rest of the template"""
    with open(get_CharacterBot_path() + '/files/servers.json', 'r') as jsonFile:
        ret = json.load(jsonFile)[server]

    return ret


def add_table(server, table):
    """Add a table to the server's database"""
    with open(get_CharacterBot_path() + '/files/tables.json', 'r') as jsonFile:
        data = json.load(jsonFile)

    data['tables'].append(table)
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


def get_character_info(server, character):
    """Return {table: (rows)}, {} if nothing is found"""
    conn = sqlite3.connect(get_CharacterBot_path() + '/data/{}.db'.format(server))

    with closing(conn.cursor()) as c:
        ret = {}
        tables = get_tables(server)
        for t in tables:
            c.execute('SELECT * FROM t{} WHERE LOWER(name)=LOWER("{}")'.format(t, character))
            info = c.fetchall()
            if len(info) > 0:
                ret[t] = info[0]
                break

    conn.close()
    return ret


def get_user_character(server, user):
    """Return the character assigned to the user, None if nothing is found"""
    conn = sqlite3.connect(get_CharacterBot_path() + '/data/{}.db'.format(server))

    with closing(conn.cursor()) as c:
        ret = None
        tables = get_tables(server)
        for t in tables:
            c.execute('SELECT name FROM t{} WHERE taken_by="{}"'.format(t, user))
            info = c.fetchall()
            if len(info) > 0:
                ret = info[0][0]
                break

    conn.close()
    return ret


def fetch(server, condition):
    """Return condition's results from server's database"""
    conn = sqlite3.connect(get_CharacterBot_path() + '/data/{}.db'.format(server))

    with closing(conn.cursor()) as c:
        c.execute(condition.replace('FROM ', 'FROM t'))
        ret = c.fetchall()

    conn.close()
    return ret

def get_server_data():
    """Return the contents of servers.json"""
    path = get_CharacterBot_path() + '/files/servers.json'
    with open(path, 'r') as jsonFile:
        ret = json.load(jsonFile)

    return ret

def get_correct_table(server, t):
    """Return case-sensitive table or None"""
    conn = sqlite3.connect(get_CharacterBot_path() + '/data/{}.db'.format(server))

    ret = None
    with closing(conn.cursor()) as c:
        for correct_t in get_tables(server):
            print(t, correct_t)
            if t.lower() == correct_t.lower():
                ret = correct_t
                break

    conn.close()
    return ret