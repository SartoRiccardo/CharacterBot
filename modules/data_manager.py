import json
import sqlite3
from contextlib import closing
from modules.data_getter import get_CharacterBot_path, get_columns, get_server_data, get_table_names

def delete_character(ctx, character):
    pass


def create_table(ctx, name):
    pass


def delete_table(ctx, table):
    pass


def update_template(ctx, columns):  #FIXME REFACTOR
    def reformat_table(t):
        c.execute('DROP TABLE IF EXISTS temp')
        conn.commit()

        current_columns = get_columns(ctx)
        command = 'ALTER TABLE {} RENAME TO temp'.format(t)
        c.execute(command)
        conn.commit()

        command = 'CREATE TABLE {} (name TEXT, taken_by TEXT'.format(t)
        for col in columns:
            command += ', {} TEXT'.format(col)
        command += ')'
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

        for col in columns:
            if col not in current_columns:
                command = 'UPDATE {} SET {}="N/A"'.format(t, col)
                c.execute(command)
                conn.commit()

        command = 'DROP TABLE temp'
        c.execute(command)
        conn.commit()

    id = ctx.message.server.id
    if id not in get_server_data():
        register_server(id)
    db_dir = get_CharacterBot_path() + '/data/' + id + '.db'
    conn = sqlite3.connect(db_dir)

    with closing(conn.cursor()) as c:
        tables = get_table_names(c)
        for t in tables:
            reformat_table(t)

    servers_dir = get_CharacterBot_path() + '/files/servers.json'
    with open(servers_dir, 'r') as jsonFile:
        data = json.load(jsonFile)

    data[id] = ["name", "taken_by"] + list(columns)

    with open(servers_dir, 'w') as jsonFile:
        json.dump(data, jsonFile)


def register_server(id):
    servers = get_server_data()
    servers[id] = ["name", "taken_by"]
    path = get_CharacterBot_path() + '/files/servers.json'
    with open(path, 'w') as jsonFile:
        json.dump(servers, jsonFile)

def modify(ctx, condition):
    server = ctx.message.server.id
    conn = sqlite3.connect(get_CharacterBot_path() + '/data/{}.db'.format(server))

    with closing(conn.cursor()) as c:
        c.execute(condition.replace('UPDATE ', 'UPDATE t'))
        conn.commit()

    conn.close()

def insert(ctx, condition):
    server = ctx.message.server.id
    conn = sqlite3.connect(get_CharacterBot_path() + '/data/{}.db'.format(server))

    with closing(conn.cursor()) as c:
        print(condition.replace('INSERT INTO ', 'INSERT INTO t'))
        c.execute(condition.replace('INSERT INTO ', 'INSERT INTO t'))
        conn.commit()

    conn.close()

def delete_char(ctx, condition):
    server = ctx.message.server.id
    conn = sqlite3.connect(get_CharacterBot_path() + '/data/{}.db'.format(server))

    with closing(conn.cursor()) as c:
        print(condition.replace('DELETE FROM ', 'DELETE FROM t'))
        c.execute(condition.replace('DELETE FROM ', 'DELETE FROM t'))
        conn.commit()

    conn.close()

