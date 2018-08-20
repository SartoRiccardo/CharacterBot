import discord
from modules.data_getter import *
from modules.data_manager import modify
from modules.chat_utils import bold

async def run(client, ctx):
    msgs = {
        'nobody_assigned': 'You don\'t have a character assigned!',
        'success': 'You aren\'t ' + bold('{}') + ' anymore!'
    }

    user, server = ctx.message.author, ctx.message.server.id
    user_char = get_user_character(server, user)
    char_data = get_character_info(server, user_char)
    if user_char is None:
        await client.say(msgs['nobody_assigned'])
        return

    table = get_dict_keys(char_data)[0]
    condition = 'UPDATE {} SET taken_by="nobody" WHERE taken_by="{}"'.format(table, user)
    modify(server, condition)

    await client.say(msgs['success'].format(user_char))
    if 'discord_role' in get_columns(server):
        role_index = get_columns(server).index('discord_role')
        role = discord.utils.get(ctx.message.server.roles, name=char_data[table][role_index])
        if role in ctx.message.server.roles:
            await client.remove_roles(user, role)
    await client.change_nickname(user, '')