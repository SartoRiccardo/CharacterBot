import json
import sqlite3
from contextlib import closing
from modules.data_manager import get_CharacterBot_path

def add_character(ctx, table, *args):
    pass


def delete_character(ctx, character):
    pass


def create_table(ctx, name):
    pass


def delete_table(ctx, table):
    pass


def update_template(ctx, columns):
    def reformat_table(t, columns):
        c.execute('DROP TABLE IF EXISTS temp')
        conn.commit()

        current_columns = get_columns(t, c)
        command = 'ALTER TABLE {} RENAME TO temp'.format(t)
        c.execute(command)
        conn.commit()

        command = 'CREATE TABLE {} (name TEXT, taken_by TEXT'.format(t)
        for col in columns:
            command += ', {} TEXT'.format(col)
        command += ')'
        c.execute(command)
        conn.commit()

        for col in columns:
            if col not in current_columns:
                command = 'UPDATE {} SET {}="N/A"'.format(t, col)
                c.execute(command)
                conn.commit()

        command = 'INSERT INTO {} (name, taken_by'.format(t)
        for col in columns:
            if col in current_columns:
                command += ', {}'.format(col)
        command += ') SELECT name, taken_by'
        for col in columns:
            if col in current_columns:
                command += ', {}'.format(col)
        command += ' FROM temp'
        c.execute(command)
        conn.commit()

        command = 'DROP TABLE temp'
        c.execute(command)
        conn.commit()

    id = ctx.message.server.id
    if id not in get_data():
        register_server(id)
    db_dir = get_CharacterBot_path() + "/files/characters.db"
    #db_dir = get_CharacterBot_path() + '/data/' + str(id) + '.db'
    conn = sqlite3.connect(db_dir)

    with closing(conn.cursor()) as c:
        tables = get_table_names(c)
        for t in tables:
            print(t)
            reformat_table(t, columns)

    servers_dir = get_CharacterBot_path() + '/files/servers.json'
    with open(servers_dir, 'r') as jsonFile:
        data = json.load(jsonFile)

    data[id] = ["name", "taken_by"] + list(columns)

    with open(servers_dir, 'w') as jsonFile:
        print(data)
        json.dump(data, jsonFile)


def get_table_names(cursor):
    cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
    raw = cursor.fetchall()  # gives list of tuples with one element

    ret = []
    for raw_name in raw:
        ret.append(raw_name[0])

    return ret

def get_columns(table, cursor):
    cursor.execute('PRAGMA table_info({})'.format(table))
    raw = cursor.fetchall()

    ret = []
    for raw_col in raw:
        ret.append(raw_col[1])

    return ret

def register_server(id):
    servers = get_data()
    print('THESE ARE THE SERVERS:',servers)
    servers[str(id)] = ["name", "taken_by"]
    path = get_CharacterBot_path() + '/files/servers.json'
    with open(path, 'w') as jsonFile:
        json.dump(servers, jsonFile)


def get_data():
    path = get_CharacterBot_path() + '/files/servers.json'
    with open(path, 'r') as jsonFile:
        ret = json.load(jsonFile)

    return ret