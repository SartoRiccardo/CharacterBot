from modules.data_getter import *
from modules.chat_utils import *
from discord.errors import HTTPException
import discord

async def run(client, ctx, args):
    character = ' '.join(args)
    special_columns = ('taken_by', 'thumbnail', 'img' 'discord_role')

    info = get_character_info(ctx, character)
    attributes = list(get_columns(ctx))

    msg = ''
    table = get_dict_keys(info)[0]
    for i in range(1, len(attributes)):
        if attributes[i] not in special_columns:
            row = bold(attributes[i][0].upper() + attributes[i][1:] + ': ').replace('_', ' ')
            row += info[table][i][0].upper() + info[table][i][1:] + '\n'
            msg += row

    e = get_embed(table + ' - ' + info[table][0], msg, discord.Colour(0x546e7a))
    e.add_field(name='Taken By:', value=info[table][attributes.index('taken_by')])
    if 'thumbnail' in attributes:
        e.set_thumbnail(url=info[table][attributes.index('thumbnail')])
    if 'img' in attributes:
        e.set_image(url=info[table][attributes.index('img')])
    if 'discord_role' in attributes:
        role = discord.utils.get(ctx.message.server.roles, name=info[table][attributes.index('discord_role')])
        if role is not None:
            e.colour = role.colour

    try:
        await client.say('Like this character? Use {} to become them!'.format(bold('>>char take ' + info[table][0])), embed=e)
    except HTTPException:
        e.set_thumbnail(url='')
        e.set_image(url='')
        await client.say('Like this character? Use {} to become them!'.format(bold('>>char take ' + info[table][0])), embed=e)
