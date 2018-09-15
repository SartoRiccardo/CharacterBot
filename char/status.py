from modules.data_getter import *
from modules.chat_utils import *
from modules.misc_utils import first_upper
from discord.errors import HTTPException
import discord

async def run(client, ctx, args):
    character = ' '.join(args)
    special_columns = ('taken_by', 'thumbnail', 'img' 'discord_role', 'table')

    server = ctx.message.server.id
    info = await get_character_info(server, character)
    tables = get_dict_keys(info)

    attributes = await get_columns(server)

    msg = ''
    try:
        t = info["table"]
    except KeyError:
        return

    for k in tables:
        if k not in special_columns:
            row = bold(f"{first_upper(k).replace('_', ' ')}: ") + first_upper(info[k])
            msg += row + '\n'

    e = get_embed(f"{t} - {info['name']}", msg, discord.Colour(0x546e7a))
    e.add_field(name='Taken By:', value=info['taken_by'])
    if 'thumbnail' in attributes:
        e.set_thumbnail(url=info['thumbnail'])
    if 'img' in attributes:
        e.set_image(url=info['img'])
    if 'discord_role' in attributes:
        role = discord.utils.get(ctx.message.server.roles, name=info['discord_role'])
        if role is not None:
            e.colour = role.colour

    try:
        await client.say(f"Like this character? Use {bold('>>char take ' + info['name'])} to become them!", embed=e)
    except HTTPException:
        e.set_thumbnail(url='')
        e.set_image(url='')
        await client.say(f"Like this character? Use {bold('>>char take ' + info['name'])} to become them!", embed=e)
