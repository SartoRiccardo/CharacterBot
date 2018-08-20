import discord
from modules.data_getter import *
from modules.chat_utils import markdown, get_embed

async def run(client, ctx, args, parameters):
    msgs = {
        'usage': 'Usage: ' + markdown('>>char list (table) [all]'),
        'invalid_param': 'Invalid parameter: ' + markdown('{}') + '. Correct parameters: {}'
    }

    if not in_range(parameters['table'], args):
        await client.say(msgs['usage'])
        return

    server = ctx.message.server.id
    table = get_correct_table(server, args[parameters['table']])
    if table not in get_tables(server):
        tables = ''
        for t in get_tables(server):
            tables += markdown(t).lower() + ' '
        await client.say(msgs['invalid_param'].format(args[parameters['table']], tables))
        return


    searcher = 'SELECT name FROM {}'.format(table)
    if in_range(parameters['role'], args):
        searcher += ' WHERE taken_by="nobody"'

    characters = fetch(server, searcher)
    msg = ''
    for c in characters:
        msg += markdown(c[0]) + '\n'
    await client.say('Use ' + markdown('>>char take (name)') + ' to become one of these characters!',
               embed=get_embed(table, msg, discord.Colour(0x546e7a)))