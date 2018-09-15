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
    t = args[parameters['table']].lower()
    if t not in await get_tables(server):
        tables = ''
        for t in await get_tables(server):
            tables += markdown(t).lower() + ' '
        await client.say(msgs['invalid_param'].format(args[parameters['table']], tables))
        return


    if in_range(parameters['role'], args):
        characters = await fetch(server, t, "name", "taken_by='nobody'")
    else:
        characters = await fetch(server, t, "name")

    msg = ''
    for c in characters:
        msg += markdown(c[0]) + '\n'
    await client.say(f"Use {markdown('>>char take (name)')} to become one of these characters!",
               embed=get_embed(t[0].upper()+t[1:].lower(), msg, discord.Colour(0x546e7a)))