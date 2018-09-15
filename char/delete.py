from modules.chat_utils import markdown, bold
from modules.misc_utils import in_range
from modules.data_manager import delete_table, pgdelete
from modules.data_getter import get_character_info, get_tables

async def run(client, ctx, args, parameters):
    msgs = {
        "usage": "Usage: " + markdown(">>char del (table | character)"),
        "insufficient_permissions": "You don't have the permissions to do that!",
        "not_found": "Didn't find anything with the name: " + bold("{}"),
        "confirmation": "You are about to delete a whole table. Type " + markdown("yes") + " to continue",
        "success": bold("{}") + " successfully deleted!",
        "failure": "Did not delete " + bold("{}"),
    }

    if not ctx.message.author.server_permissions.administrator:
        await client.say(msgs["insufficient_permissions"])
        return

    if not in_range(parameters["to_delete"], args):
        await client.say(msgs["usage"])

    server = ctx.message.server.id
    to_delete = args[parameters["to_delete"]]
    char_info = await get_character_info(server, to_delete)

    # It's a table
    if to_delete in await get_tables(server):
        await client.say(msgs["confirmation"])
        response = await client.wait_for_message(author=ctx.message.author, timeout = 30)

        if response is not None and response.clean_content == "yes":
            await delete_table(server, to_delete)
            await client.say(msgs["success"].format(to_delete))
        else:
            await client.say(msgs["failure"].format(to_delete))

    # It's a character
    elif char_info != {}:
        await pgdelete(server, char_info["table"], f"LOWER(name)=LOWER('{to_delete}')")
        await client.say(msgs["success"].format(to_delete))

    else:
        await client.say(msgs["not_found"].format(to_delete))