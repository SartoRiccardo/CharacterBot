import discord
import json
from discord.ext import commands
from modules.chat_utils import *
from modules.data_manager import *
from modules.data_initializer import *

def __init__():
    with open('config.json') as jsonFile:
        data = json.load(jsonFile)

        global TOKEN, client
        TOKEN = data['TOKEN']
        client = commands.Bot(command_prefix=data['prefix'])
        client.remove_command('help')

    with open('files/char_parameters.json') as jsonFile:
        global char_params
        char_params = json.load(jsonFile)


__init__()
@client.event
async def on_ready():
    await client.change_presence(game=discord.Game(name='>>char help'))

BR, TAB = '\n', '\t'


async def create_role(author, role_name, role_colour):
    role = await client.create_role(author.server, name=role_name, colour=role_colour)
    return role


@client.command(pass_context=True)
async def char(ctx, *args):
    def get_help_msg():
        command = '>>char '
        message = bold('Usage:') + BR
        message += bold(command + 'list (table) [all]') + ' - List all characters from the table' + BR
        message += bold(command + 'take (character)') + ' - Assign youself to a character' + BR
        message += bold(command + 'leave') + ' - Stop being your character' + BR
        message += bold(command + '(character)') + ' - Get info about the character' + BR
        return message


    async def char_list():  #FIXME Take away the role shit
        lp = char_params['list'] # lp = [l]ist [p]arameters. This goes for all other commands
        msgs = {
            'usage': 'Usage: ' + markdown('>>char list (table) [all]'),
            'invalid_param': 'Invalid parameter: ' + markdown('{}') + '. Correct parameters: ' + markdown('{}')
        }

        if not in_range(lp['table'], args):
            await client.say(msgs['usage'])
            return
        elif args[lp['table']] not in get_tables():
            await client.say(msgs['invalid_param'].format(args[lp['table']], get_tables()))
            return

        searcher = 'SELECT name FROM {}'.format(args[lp['table']])
        if in_range(lp['role'], args):
            if not args[lp['role']] == 'all':
                searcher += ' WHERE role="{}" AND taken_by="nobody"'.format(args[lp['role']])
        else:
            searcher += ' WHERE taken_by="nobody"'

        characters = fetch(searcher)
        msg = ''
        for c in characters:
            msg += markdown(c[0]) + BR
        await client.say('Use ' + markdown('>>char take (name)') + ' to become one of these characters!',
                         embed = get_embed('', msg, discord.Colour.blue()))


    async def char_take():
        tp = char_params['take']
        msgs = {
            'usage': 'Usage: ' + markdown('>>char take (char)'),
            'invalid_param': 'Invalid parameter: {}.',
            'success': 'You are now ' + bold('{}') + '!'
        }

        if not in_range(tp['char'], args):
            await client.say(msgs['usage'])
            return

        character = ' '.join(args[tp['char']:])
        char_data = get_character_info(character)
        if len(char_data) == 0:
            await client.say(msgs['invalid_param'].format(character))
            return

        user = ctx.message.author
        name_index = get_attributes().index('name')
        table = get_dict_keys(char_data)[0]

        condition = 'UPDATE {} SET taken_by="{}" WHERE name="{}"'.format(table, user, char_data[table][name_index])
        modify(condition)

        await client.say(msgs['success'].format(char_data[table][name_index]))
        await client.change_nickname(user, char_data[table][name_index])
        if 'discord_role' in get_tables():
            discord_role = get_tables().index('discord_role')
            await client.give_role(user, char_data[table][discord_role])


    async def char_leave():
        msgs = {
            'nobody_assigned': 'You don\'t have a character assigned!',
            'success': 'You aren\'t ' + bold('{}') + ' anymore!'
        }

        user = ctx.message.author
        user_char = get_user_character(user)
        if user_char is None:
            await client.say(msgs['nobody_assigned'])
            return

        table = get_dict_keys(get_character_info(user_char))[0]
        condition = 'UPDATE {} SET taken_by="nobody" WHERE taken_by="{}"'.format(table, user)
        modify(condition)

        await client.say(msgs['success'].format(user_char))
        await client.change_nickname(user, '')
        if 'discord_role' in get_tables():
            discord_role = get_tables().index('discord_role')
            await client.remove_roles(user, char_data[table][discord_role])


    async def char_status():
        character = ' '.join(args)
        special_columns = ('thumbnail', 'discord_role')

        info = get_character_info(character)
        attributes = list(get_attributes())
        attributes += ['role', 'taken_by']

        msg = ''
        table = get_dict_keys(info)[0]
        for i in range(1, len(attributes)):
            if attributes[i] not in special_columns:
                row = bold(attributes[i][0].upper() + attributes[i][1:] + ': ').replace('_', ' ')
                row += info[table][i][0].upper() + info[table][i][1:] + BR
                msg += row

        e = get_embed(info[table][0][0].upper() + info[table][0][1:], msg, discord.Colour(0x68d4bb))#.blue())
        if 'thumbnail' in attributes:
            e.set_thumbnail(info[attributes.index('img')])
        await client.say('Like this character? Use {} to become them!'.format(bold('>>char take ' + info[table][0])) ,embed=e)


    async def char_template():
        update_template(ctx, args[1:])
        await client.say("Template was updated!")


    async def char_add():
        pass


    try:
        if args[0] == 'list':
            await char_list()
        elif args[0] == 'take':
            await char_take()
        elif args[0] == 'leave':
            await char_leave()
        elif args[0] == 'template':
            await char_template()
        elif args[0] == 'add':
            await char_add()
        else:
            await char_status()
    except IndexError:
        await client.say(get_help_msg())


@client.command()
async def info():
    msg = 'A bot that turns users into their favourite characters! Check `>>help` for usage.' + BR
    msg += 'Developed by Trifo Reborn#1676'
    await client.say(msg)

@client.command(pass_context=True)
async def invitelink(ctx):
    await client.send_message(ctx.message.author, 'https://bit.ly/CharacterBotInvite')

@client.command()
async def help():
    msg = bold('>>char') + ' - For all your roleplaying needs' + BR
    msg += bold('>>info') + ' - Find out who made this bot' + BR
    msg += bold('>>invitelink') + ' - Add this bot to YOUR server!'
    await client.say(msg)


client.run(TOKEN)
