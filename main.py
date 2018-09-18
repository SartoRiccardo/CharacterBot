import json
import config
import discord
import asyncio
from discord.ext import commands
from modules.data_getter import get_user_character, get_character_info, start_database
from modules.data_manager import modify, pgdelete
from modules.misc_utils import get_dict_keys
from modules.chat_utils import *
from char import leave, list, take, status, template, add, delete, create, import_preset

VERSION = "0.9.1"
def __init__():
    with open('files/char_parameters.json') as jsonFile:
        global parameters
        parameters = json.load(jsonFile)

client = commands.Bot(command_prefix=">>")
client.remove_command('help')
__init__()

@client.event
async def on_ready():
    await client.change_presence(game=discord.Game(name='>>char help'))

@client.event
async def on_message(message):
    if '<@475707068196585473>' in message.content:
        await client.send_message(message.channel, 'I\'m CharacterBot! Type ' + markdown('>>help') + ' to get started!')

    await client.process_commands(message)

@client.event
async def on_member_remove(member):
    server = member.server.id
    char_name = get_user_character(server, member)
    if char_name is not None:
        table = get_dict_keys(get_character_info(server, char_name))[0]
        modify(server, 'UPDATE {} SET taken_by="nobody" WHERE name="{}"'.format(table, char_name))


BR, TAB = '\n', '\t'

@client.command(pass_context=True)
@commands.cooldown(1, 2, commands.BucketType.user)
async def char(ctx, *args):
    def get_help_msg():
        command = '>>char '
        message = bold('Usage:') + BR
        message += bold(command + 'list (table) [all]') + ' - List all characters from the table' + BR
        message += bold(command + 'take (character)') + ' - Assign youself to a character' + BR
        message += bold(command + 'leave') + ' - Stop being your character' + BR
        message += bold(command + '(character)') + ' - Get info about the character' + BR

        if ctx.message.author.server_permissions.administrator:
            message += BR
            message += bold(command + 'import (preset)') + ' - Import one of our pre-made databases' + BR
            message += bold(command + 'template (columns)') + ' - Update the template' + BR
            message += bold(command + 'create (table)') + ' - Create a new table' + BR
            message += bold(command + 'add (table) (character) (columns)') + ' - Update/Add a character to a table' + BR
            message += bold(command + 'del (table | character)') + ' - Delete a table/character'

        return message

    try:
        if args[0] == 'list':
            await list.run(client, ctx, args, parameters['list'])
        elif args[0] == 'take':
            await take.run(client, ctx, args, parameters['take'])
        elif args[0] == 'leave':
            await leave.run(client, ctx)
        elif args[0] == 'template':
            await template.run(client, ctx, args)
        elif args[0] == 'add':
            await add.run(client, ctx, args, parameters['add'])
        elif args[0] == 'del':
            await delete.run(client, ctx, args, parameters['delete'])
        elif args[0] == 'create':
            await create.run(client, ctx, args, parameters['create'])
        elif args[0] == 'import':
            await import_preset.run(client, ctx, args, parameters['import'])
        else:
            await status.run(client, ctx, args)
    except IndexError:
        await client.say(get_help_msg())


@client.command()
async def info():
    msg = ''
    msg += f'CharacterBot v{VERSION}' + BR
    msg += 'A bot that turns users into their favourite characters! Check `>>help` for usage.' + BR
    msg += 'Developed by Trifo Reborn'
    await client.say(msg)

@client.command(pass_context=True)
async def share(ctx):
    await client.send_message(ctx.message.author, 'https://bit.ly/CharacterBotInvite')

@client.command()
async def help():
    msg = bold('>>char') + ' - For all your roleplaying needs' + BR
    msg += bold('>>info') + ' - Info about this bot' + BR
    msg += bold('>>share') + ' - Add this bot to YOUR server'
    await client.say(msg)


@client.command(pass_context=True)
async def test(ctx):
    server = ctx.message.server.id
    user = ctx.message.author
    if user == "Trifo Reborn#1676":
        # Do stuff


        pass

loop = asyncio.get_event_loop()
loop.run_until_complete(start_database())
client.run(config.TOKEN)
