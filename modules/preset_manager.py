from modules.misc_utils import get_CharacterBot_path
from modules.data_manager import update_template, create_table, delete_table, insert
from modules.data_getter import get_tables
import os

def import_db(ctx, preset):
    available_presets = get_presets()

    preset = preset.lower()
    if preset not in available_presets:
        raise SyntaxError('nonexistent')

    path = get_CharacterBot_path() + '/presets/{}.txt'.format(preset)
    lines = get_lines(path)
    with open(path, 'r') as f:
        data = f.read().strip().split('\n')

    template = data[0].strip().split(';')
    update_template(ctx, template)

    for t in get_tables(ctx):
        delete_table(ctx, t)

    for i in range(1, lines):
        if ';' not in data[i]:
            table = data[i].strip()
            create_table(ctx, table)

        else:
            row = data[i].strip().split(';')
            cmd = 'INSERT INTO {} VALUES("{}", "nobody"'.format(table, row[0])
            for j in range(1, len(row)):
                cmd += ', "{}"'.format(row[j])
            cmd += ')'
            insert(ctx, cmd)


def get_lines(path):
    with open(path, 'r') as f:
        ret = len(f.read().strip().split('\n'))

    return ret


def get_presets():
    ret = os.listdir(get_CharacterBot_path() + '/presets')

    to_remove = []
    for i in range(len(ret)):
        if not ret[i][-4:] == '.txt':
            to_remove.append(ret[i])
    for rm in to_remove:
        ret.remove(rm)

    ret = [p[:-4] for p in ret]
    return ret