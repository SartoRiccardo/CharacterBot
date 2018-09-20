from modules.misc_utils import *
from modules.data_manager import *
from modules.data_getter import get_tables
import os
import csv
from asyncpg.exceptions import DuplicateColumnError
from io import StringIO


# TODO: Use Postgres instead of files because blocking is a thing
async def import_db(server, preset):  # FIXME
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


def get_presets():
    """Return a list of all .txt files in the presets folder"""
    ret = []

    for file in os.listdir(os.path.join(project_path, "presets")):
        if file[-4:] == ".txt":
            ret.append(file[:-4])

    return ret


async def load_file_preset(server, link):
    """Load the contents of fin"""
    raw_data = (await get_file_content(link)).decode("utf-8")
    reader = csv.reader(StringIO(raw_data))

    await backup(server)
    dprint("Backed Up!")

    for t in await get_tables(server):
        await delete_table(server, t)

    current_table = None
    is_table_name = False
    template = None
    names = []
    try:
        for row in reader:
            is_template = is_table_name
            is_table_name = True

            for nothing in row[1:]:
                if nothing != " " and nothing != "":
                    is_table_name = False
                    break

            if is_table_name:
                current_table = row[0]
                if len(current_table) == 0 or " " in current_table:
                    raise SyntaxError("csv_invalid_table_name")
                await create_table(server, current_table)
                continue

            if is_template:
                if not contains(row, ["name", "taken_by"]):
                    raise SyntaxError("csv_no_name_taken_by")
                if template is None:
                    template = row
                    await update_template(server, row[2:])
                continue

            if current_table is None or current_table == "":
                raise SyntaxError("csv_no_table_name")

            if row[0] in names:
                raise SyntaxError("csv_duplicate_char_name")

            names.append(row[0])
            await insert(server, current_table, row)

    except DuplicateColumnError:
        await load_backup(server)
        raise SyntaxError("csv_duplicate_column_name")

    except SyntaxError as e:
        await load_backup(server)
        raise SyntaxError(str(e))

    dprint("Deleting")
    await delete_backup(server)
