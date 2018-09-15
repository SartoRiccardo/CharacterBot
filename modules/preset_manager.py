from modules.misc_utils import project_path, get_lines
from modules.data_manager import update_template, create_table, delete_table, insert
from modules.data_getter import get_tables
import os

# TODO: Use Postgres instead of files because blocking is a thing
async def import_db(server, preset):   #FIXME
    """Copy preset into server's database"""
    available_presets = get_presets()

    preset = preset.lower()
    if preset not in available_presets:
        raise SyntaxError('nonexistent')

    path = os.path.join(os.path.join(project_path, "presets", f"{preset}.txt"))
    lines = get_lines(path)
    with open(path, 'r') as f:
        data = f.read().strip().split('\n')

    template = data[0].strip().split(';')
    await update_template(server, template)

    for t in await get_tables(server):
        await delete_table(server, t)

    for i in range(1, lines):
        if ';' not in data[i]:
            table = data[i].strip()
            await create_table(server, table)

        else:
            row = data[i].strip().split(';')

            values = [row[0], "nobody"]
            for j in range(1, len(row)):
                values.append(row[j])

            await insert(server, table, values)

def get_presets(): #OK
    """Return a list of all .txt files in the presets folder"""
    ret = []

    for file in os.listdir(os.path.join(project_path, "presets")):
        if file[-4:] == ".txt":
            ret.append(file[:-4])

    return ret