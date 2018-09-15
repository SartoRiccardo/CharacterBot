from modules.chat_utils import markdown, bold
from modules.data_getter import get_tables, get_character_info
from modules.data_manager import get_columns, insert, pgdelete
from modules.misc_utils import in_range, get_dict_keys

async def run(client, ctx, args, parameters):
    msgs = {
        "insufficient_permissions": "You don't have the permissions to do that!",
        "invalid_table": "Invalid table: {}",
        "already_exists": "Character already exists in table " + markdown("{}") + '\n'
                          "To modify that character's info, use " + markdown("{}"),
        "invalid_parameters": "Invalid parameters. This is what you should put:\n{}",
        "usage" : "Usage: " + markdown(">>char add (table) (character) (parameters)"),
        "success_added": "Successfully added " + bold("{}") + " into " + bold("{}"),
        "success_modified": "Successfully modified " + bold("{}") + "'s data!"
    }

    if not ctx.message.author.server_permissions.administrator:
        await client.say(msgs["insufficient_permissions"])
        return

    if not in_range(parameters["char"], args):
        await client.say(msgs["usage"])
        return

    server = ctx.message.server.id
    table = args[parameters["table"]].lower()
    if table not in await get_tables(server):
        await client.say(msgs["invalid_table"].format(args[parameters["table"]]))
        return

    if not len(args)-1 == len(await get_columns(server)):
        template = ''
        for c in (await get_columns(server))[2:]:
            template += markdown(c) + ' '
        await client.say(msgs["invalid_parameters"].format(template))
        return

    char = args[parameters["char"]]
    char_data = await get_character_info(server, char)
    if char_data == {}:
        values = [char, "nobody"]
        for p in args[parameters["args"]:]:
            values.append(p)

        await insert(server, table, values)
        await client.say(msgs["success_added"].format(char, table))
        return

    if table != char_data["table"]:
        correct_cmd = f">>char add {char_data['table']} {char}"
        for p in args[parameters["args"]:]:
            correct_cmd += f" {p}"

        await client.say(msgs["already_exists"].format(get_dict_keys(char_data)[0], correct_cmd))
        return

    await pgdelete(server, table, f"name='{char}'")

    values = [char, "nobody"]
    for p in args[parameters["args"]:]:
        values.append(p)

    await insert(server, table, values)
    await client.say(msgs["success_modified"].format(char))