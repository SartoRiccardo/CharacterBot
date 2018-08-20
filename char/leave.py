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
    await client.change_nickname(user, '')
    if 'discord_role' in get_tables(server):
        discord_role = get_tables(server).index('discord_role')
        await client.remove_roles(user, char_data[table][discord_role])