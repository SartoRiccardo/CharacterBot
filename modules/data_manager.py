import os
import json
import sqlite3
from contextlib import closing


def get_dict_keys(dict):
    ret = list(dict.keys())
    return ret


def get_CharacterBot_path():
    ret = os.path.dirname(os.path.abspath(__file__))
    ret = str.join('/', ret.split('/')[:-1])
    return ret


def get_tables():
    with open(get_CharacterBot_path() + '/files/tables.json') as jsonFile:
        ret = json.load(jsonFile)['tables']

    return ret


def get_attributes():
    with open(get_CharacterBot_path() + '/files/tables.json') as jsonFile:
        ret = json.load(jsonFile)['columns']

    return ret


def add_table(table):
    with open(get_CharacterBot_path() + '/files/tables.json', 'r') as jsonFile:
        data = json.load(jsonFile)

    data['tables'].append(table)
    conn = sqlite3.connect(get_CharacterBot_path() + '/files/characters.db')

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


def get_character_info(character):
    conn = sqlite3.connect(get_CharacterBot_path() + '/files/characters.db')

    with closing(conn.cursor()) as c:
        ret = {}
        tables = get_tables()
        for t in tables:
            c.execute('SELECT * FROM t{} WHERE LOWER(name)=LOWER("{}")'.format(t, character))
            info = c.fetchall()
            if len(info) > 0:
                ret[t] = info[0]
                break

    conn.close()
    return ret


def get_user_character(user):
    conn = sqlite3.connect(get_CharacterBot_path() + '/files/characters.db')

    with closing(conn.cursor()) as c:
        ret = None
        tables = get_tables()
        for t in tables:
            c.execute('SELECT name FROM t{} WHERE taken_by="{}"'.format(t, user))
            info = c.fetchall()
            if len(info) > 0:
                ret = info[0][0]
                break

    conn.close()
    return ret


def fetch(condition):
    conn = sqlite3.connect(get_CharacterBot_path() + '/files/characters.db')

    with closing(conn.cursor()) as c:
        c.execute(condition.replace('FROM ', 'FROM t'))
        ret = c.fetchall()

    conn.close()
    return ret

def modify(condition):
    conn = sqlite3.connect(get_CharacterBot_path() + '/files/characters.db')

    with closing(conn.cursor()) as c:
        c.execute(condition.replace('UPDATE ', 'UPDATE t'))
        conn.commit()

    conn.close()


def in_range(i, list):
    return i in range(len(list))