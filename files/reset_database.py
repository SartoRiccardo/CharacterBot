import sqlite3

conn = sqlite3.connect('characters.db')
c = conn.cursor()

NAME, EN_NAME, JP_NAME, SEX, ROLE, DECKS = [i for i in range(6)]

def get_data(path):
    raw_characters = open(path, 'r')
    data = raw_characters.read()
    raw_characters.close()
    return data

def make_db(db_name):
    c.execute('CREATE TABLE IF NOT EXISTS {} (name TEXT, en_name TEXT, jp_name TEXT, sex TEXT, role TEXT, decks TEXT, user TEXT)'.format(db_name))
    c.execute('DELETE FROM {}'.format(db_name))

def put_in_db(db):
    c.execute('INSERT INTO {} VALUES("{}", "{}", "{}", "{}", "{}", "{}", "Nobody")'.format(db, char[NAME], char[EN_NAME], char[JP_NAME], char[SEX], char[ROLE], char[DECKS]))

data = get_data('raw_characters.txt').split('\n')
characters = []
for row in data:
    if len(row) > 0 and row[0] == '#':
        continue

    if ';' not in row:
        if len(characters) > 0:
            for char in sorted(characters):
                put_in_db(current_db)

        if not row == '':
            current_db = row
            make_db(current_db)
            characters = []
    else:
        characters.append(row.split(';'))

conn.commit()
c.close()
conn.close()
