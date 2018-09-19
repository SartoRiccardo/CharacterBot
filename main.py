import config
import discord
import asyncio
from discord.ext import commands
from modules.chat_utils import get_embed
from modules.data_manager import start_servers_data, register_server, change_prefix
from modules.data_getter import start_database, get_prefix

VERSION = "1.0.0"
client = commands.Bot(command_prefix='$')
client.remove_command('help')


@client.event
async def on_ready():
    for s in client.servers:
        await register_server(s.id)

    await client.change_presence(game=discord.Game(name='Ping me for info!'))


@client.event
async def on_server_join(server):
    await register_server(server.id)


@client.event
async def on_message(message):
    prefix = await get_prefix(message.server.id)

    if '<@475707068196585473>' in message.content:
        await client.send_message(message.channel,
                                  f"I'm CharacterBot! "
                                  f"Type `{prefix}help` to get started!")

    content = message.content
    if content[:len(prefix)] == prefix:
        content = '$' + content[len(prefix):]
        message.content = content
        await client.process_commands(message)


@client.command(pass_context=True)
async def prefix(ctx, newprefix):
    if not ctx.message.author.server_permissions.administrator:
        await client.say("You don't have the permissions to do that!")
        return

    await change_prefix(ctx.message.server.id, newprefix.replace("'", "''").replace('"', '""'))
    await client.say(f"Prefix changed to {newprefix}")


@client.command()
async def info():
    msg = f"""CharacterBot v{VERSION}
A bot that helps users role play! Check `>>help` for usage.
Developed by Trifo Reborn"""
    await client.say(msg)


@client.command(pass_context=True, aliases=["invite"])
async def share(ctx):
    await client.send_message(ctx.message.author, "https://bit.ly/CharacterBotInvite")


@client.command(pass_context=True)
async def help(ctx):
    p = await get_prefix(ctx.message.server.id)

    output = get_embed("CharacterBot Help", '', discord.Colour(0x546e7a))

    output.add_field(name=f"{p}take (character)",
                     value="Become the character you chose",
                     inline=False)
    output.add_field(name=f"{p}leave",
                     value="Leave your current character",
                     inline=False)
    output.add_field(name=f"{p}list (table)",
                     value="List all the characters in a table",
                     inline=False)
    output.add_field(name=f"{p}char (character)",
                     value="Display a character's info",
                     inline=False)

    if ctx.message.author.server_permissions.administrator:
        output.add_field(name=f"{p}import (preset)",
                         value="Load a preset",
                         inline=False)
        output.add_field(name=f"{p}create (table)",
                         value="Make a new empty table",
                         inline=False)
        output.add_field(name=f"{p}add (table) (character) (args)",
                         value="Add a character to a table",
                         inline=False)
        output.add_field(name=f"{p}del (table | character)",
                         value="Delete a character or a table",
                         inline=False)
        output.add_field(name=f"{p}template (args)",
                         value="Update the template",
                         inline=False)

    output.add_field(name=f"{p}invite",
                     value="Get the bot's invite link",
                     inline=False)
    output.add_field(name=f"{p}info",
                     value="General information about the bot",
                     inline=False)
    output.add_field(name=f"{p}help",
                     value="Display this message",
                     inline=False)

    await client.send_message(ctx.message.author, '', embed=output)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_database())
    loop.run_until_complete(start_servers_data())

    extensions = ["commands.input", "commands.output", "commands.roleplay"]
    for e in extensions:
        client.load_extension(e)

    client.run(config.TOKEN)
