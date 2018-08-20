from modules.misc_utils import get_CharacterBot_path, get_lines
from modules.data_manager import update_template, create_table, delete_table, insert
from modules.data_getter import get_tables
import os

def import_db(server, preset):
    """Copy preset into server's database"""
    available_presets = get_presets()

    preset = preset.lower()
    if preset not in available_presets:
        raise SyntaxError('nonexistent')

    path = get_CharacterBot_path() + '/presets/{}.txt'.format(preset)
    lines = get_lines(path)
    with open(path, 'r') as f:
        data = f.read().strip().split('\n')

    template = data[0].strip().split(';')
    update_template(server, template)

    for t in get_tables(server):
        delete_table(server, t)

    for i in range(1, lines):
        if ';' not in data[i]:
            table = data[i].strip()
            create_table(server, table)

        else:
            row = data[i].strip().split(';')
            cmd = 'INSERT INTO {} VALUES("{}", "nobody"'.format(table, row[0])
            for j in range(1, len(row)):
                cmd += ', "{}"'.format(row[j])
            cmd += ')'
            insert(server, cmd)

def get_presets():
    """Return a list of all .txt files in the presets folder"""
    ret = os.listdir(get_CharacterBot_path() + '/presets')

    to_remove = []
    for i in range(len(ret)):
        if not ret[i][-4:] == '.txt':
            to_remove.append(ret[i])
    for rm in to_remove:
        ret.remove(rm)

    ret = [p[:-4] for p in ret]
    return ret