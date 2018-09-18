import discord
from modules.data_getter import *
from modules.data_manager import modify
from modules.chat_utils import bold, markdown

async def run(client, ctx, args, parameters):
    msgs = {
        "already_assigned": "You are already assigned to " + bold("{}") + '!',
        "usage": "Usage: " + markdown(">>char take (char)"),
        "invalid_param": "Invalid parameter: {}.",
        "unavailable": "That character is already taken.",
        "success": "You are now " + bold("{}") + '!'
    }

    if not in_range(parameters["char"], args):
        await client.say(msgs["usage"])
        return

    user, server = ctx.message.author, ctx.message.server.id
    user_char = await get_user_character(server, user)
    if user_char is not None:
        await client.say(msgs["already_assigned"].format(user_char))
        return

    character = ' '.join(args[parameters["char"]:])
    char_data = await get_character_info(server, character)
    if char_data == {}:
        await client.say(msgs["invalid_param"].format(character))
        return

    if char_data["taken_by"] != "nobody":
        await client.say(msgs["unavailable"])
        return

    table, name = char_data["table"], char_data["name"]

    await modify(server, table, f"taken_by='{user}'", f"name='{name}'")

    await client.say(msgs["success"].format(name))
    if "discord_role" in await get_columns(server):
        role = discord.utils.get(ctx.message.server.roles, name=char_data["discord_role"])
        if role in ctx.message.server.roles:
            await client.add_roles(user, role)
    await client.change_nickname(user, name)