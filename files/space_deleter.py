f = open("raw_characters.txt", "r")
data = f.read()
f.close()

for i in range(100):
    data = data.replace('; ', ';')
    data = data.replace(';\t', ';')
    data = data.replace(' ;', ';')
    data = data.replace('\t;', ';')

f = open("raw_characters.txt", "w")
f.write(data)
f.close()
