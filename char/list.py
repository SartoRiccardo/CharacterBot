import discord
from modules.data_getter import *
from modules.chat_utils import markdown, get_embed

async def run(client, ctx, args, parameters):
    msgs = {
        'usage': 'Usage: ' + markdown('>>char list (table) [all]'),
        'invalid_param': 'Invalid parameter: ' + markdown('{}') + '. Correct parameters: ' + markdown('{}')
    }

    if not in_range(parameters['table'], args):
        await client.say(msgs['usage'])
        return
    elif args[parameters['table']] not in get_tables(ctx):
        await client.say(msgs['invalid_param'].format(args[parameters['table']], get_tables(ctx)))
        return

    searcher = 'SELECT name FROM {}'.format(args[parameters['table']])
    if in_range(parameters['role'], args):
        searcher += ' WHERE taken_by="nobody"'

    characters = fetch(ctx, searcher)
    msg = ''
    for c in characters:
        msg += markdown(c[0]) + '\n'
    await client.say('Use ' + markdown('>>char take (name)') + ' to become one of these characters!',
               embed=get_embed('', msg, discord.Colour.blue()))