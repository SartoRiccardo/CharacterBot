import discord
from modules.data_getter import *
from modules.data_manager import modify
from modules.chat_utils import bold

async def run(client, ctx):
    msgs = {
        "nobody_assigned": "You don't have a character assigned!",
        "success": "You aren't " + bold('{}') + " anymore!"
    }

    user, server = ctx.message.author, ctx.message.server.id
    user_char = await get_user_character(server, user)
    char_data = await get_character_info(server, user_char)
    if user_char is None:
        await client.say(msgs['nobody_assigned'])
        return

    table = char_data["table"]
    await modify(server, table, "taken_by='nobody'", f"taken_by='{user}'")

    await client.say(msgs['success'].format(user_char))
    if "discord_role" in await get_columns(server):
        role = discord.utils.get(ctx.message.server.roles, name=char_data["discord_role"])
        if role in ctx.message.server.roles:
            await client.remove_roles(user, role)
    await client.change_nickname(user, '')