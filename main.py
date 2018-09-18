import config
import discord
import asyncio
from modules.data_getter import start_database
from modules.chat_utils import get_embed
from discord.ext import commands

VERSION = "0.10.0"
client = commands.Bot(command_prefix=">>")
client.remove_command('help')


@client.event
async def on_ready():
    await client.change_presence(game=discord.Game(name='>>char help'))


@client.event
async def on_message(message):
    if '<@475707068196585473>' in message.content:
        await client.send_message(message.channel,
                                  f"I'm CharacterBot! "
                                  f"Type {markdown('>>help')} to get started!")

    await client.process_commands(message)


@commands.command()
async def info():
    msg = f"""CharacterBot v{VERSION}
A bot that helps users role play! Check `>>help` for usage.
Developed by Trifo Reborn"""
    await self.client.say(msg)


@commands.command(pass_context=True, aliases=["invite"])
async def share(ctx):
    await self.client.send_message(ctx.message.author, "https://bit.ly/CharacterBotInvite")


@client.command(pass_context=True)
async def help(ctx):
    output = get_embed("CharacterBot Help", '', discord.Colour(0x546e7a))

    output.add_field(name=">>take (character)",
                     value="Become the character you chose",
                     inline=False)
    output.add_field(name=">>leave",
                     value="Leave your current character",
                     inline=False)
    output.add_field(name=">>list (table)",
                     value="List all the characters in a table",
                     inline=False)
    output.add_field(name=">>char (character)",
                     value="Display a character's info",
                     inline=False)

    if ctx.message.author.server_permissions.administrator:
        output.add_field(name=">>import (preset)",
                         value="Load a preset",
                         inline=False)
        output.add_field(name=">>create (table)",
                         value="Make a new empty table",
                         inline=False)
        output.add_field(name=">>add (table) (character) (args)",
                         value="Add a character to a table",
                         inline=False)
        output.add_field(name=">>del (table | character)",
                         value="Delete a character or a table",
                         inline=False)
        output.add_field(name=">>template (args)",
                         value="Update the template",
                         inline=False)

    output.add_field(name=">>invite",
                     value="Get the bot's invite link",
                     inline=False)
    output.add_field(name=">>info",
                     value="General information about the bot",
                     inline=False)
    output.add_field(name=">>help",
                     value="Display this message",
                     inline=False)

    await client.send_message(ctx.message.author, '', embed=output)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_database())

    extensions = ["commands.input", "commands.output", "commands.roleplay"]
    for e in extensions:
        client.load_extension(e)

    client.run(config.TOKEN)
