import json
import discord
from discord.ext import commands
from modules.chat_utils import *
from char import leave, list, take, status, template, add, delete, create, import_preset

def __init__():
    with open('config.json') as jsonFile:
        data = json.load(jsonFile)

        global TOKEN, client
        TOKEN = data['TOKEN']
        client = commands.Bot(command_prefix=data['prefix'])
        client.remove_command('help')

    with open('files/char_parameters.json') as jsonFile:
        global parameters
        parameters = json.load(jsonFile)


__init__()
@client.event
async def on_ready():
    await client.change_presence(game=discord.Game(name='>>char help'))

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
    msg += 'CharacterBot v0.9' + BR
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


client.run(TOKEN)
