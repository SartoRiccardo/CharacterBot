from modules.data_getter import *
from modules.chat_utils import *

async def run(client, ctx, args):
    character = ' '.join(args)
    special_columns = ('thumbnail', 'discord_role')

    info = get_character_info(ctx, character)
    attributes = list(get_columns(ctx))

    msg = ''
    table = get_dict_keys(info)[0]
    for i in range(1, len(attributes)):
        if attributes[i] not in special_columns:
            row = bold(attributes[i][0].upper() + attributes[i][1:] + ': ').replace('_', ' ')
            row += info[table][i][0].upper() + info[table][i][1:] + '\n'
            msg += row

    e = get_embed(info[table][0][0].upper() + info[table][0][1:], msg, discord.Colour(0x68d4bb))  # .blue())
    if 'thumbnail' in attributes:
        e.set_thumbnail(info[attributes.index('img')])
    await client.say('Like this character? Use {} to become them!'.format(bold('>>char take ' + info[table][0])), embed=e)