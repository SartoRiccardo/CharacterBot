from modules.data_getter import *
from modules.data_manager import modify
from modules.chat_utils import bold, markdown

async def run(client, ctx, args, parameters):
    msgs = {
        'already_assigned': 'You are already assigned to ' + bold('{}') + '!',
        'usage': 'Usage: ' + markdown('>>char take (char)'),
        'invalid_param': 'Invalid parameter: {}.',
        'success': 'You are now ' + bold('{}') + '!'
    }

    if not in_range(parameters['char'], args):
        await client.say(msgs['usage'])
        return

    user, server = ctx.message.author, ctx.message.server.id
    user_char = get_user_character(server, user)
    if user_char is not None:
        await client.say(msgs['already_assigned'].format(user_char))
        return

    character = ' '.join(args[parameters['char']:])
    char_data = get_character_info(server, character)
    if len(char_data) == 0:
        await client.say(msgs['invalid_param'].format(character))
        return

    name_index = get_columns(server).index('name')
    table = get_dict_keys(char_data)[0]

    condition = 'UPDATE {} SET taken_by="{}" WHERE name="{}"'.format(table, user, char_data[table][name_index])
    modify(server, condition)

    await client.say(msgs['success'].format(char_data[table][name_index]))
    await client.change_nickname(user, char_data[table][name_index])
    if 'discord_role' in get_tables(server):
        discord_role = get_tables(server).index('discord_role')
        await client.give_role(user, char_data[table][discord_role])