import sqlite3

conn = sqlite3.connect('characters.db')
c = conn.cursor()

def get_data(path):
	raw_characters = open(path, 'r')
	data = raw_characters.read()
	raw_characters.close()
	return data

def make_db(name):
	def delete():
		c.execute('DELETE FROM {}'.format(name))

	c.execute('CREATE TABLE IF NOT EXISTS {}(name TEXT, role TEXT, user TEXT)'.format(name))
	delete()

def put_in_db(db, name, role):
	c.execute('INSERT INTO {} VALUES("{}", "{}", "Nobody")'.format(db, name, role))

data = get_data('raw_characters.txt').strip().split('\n')

for row in data:
	if ';' not in row:
		current_db = row
		make_db(current_db)
	else:
		name, role = row.split(';')
		put_in_db(current_db, name, role)

conn.commit()
c.close()
conn.close()
