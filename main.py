import config
import discord
import asyncio
from discord.ext import commands
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
async def prefix(ctx, newprefix=None):
    if not ctx.message.author.server_permissions.administrator:
        await client.say("You don't have the permissions to do that!")
        return

    current_prefix = await get_prefix(ctx.message.server.id)
    if newprefix is None:
        await client.say(f"Usage: `{current_prefix}prefix (newprefix)")
        return

    await change_prefix(ctx.message.server.id, newprefix.replace("'", "''").replace('"', '""'))
    await client.say(f"Prefix changed to {newprefix}")


@client.command(pass_context=True)
async def info(ctx):
    prefix = await get_prefix(ctx.message.server.id)
    msg = f"""CharacterBot v{VERSION}
A bot that helps users role play! Check `{prefix}help` for usage.
GitHub Repository: https://bit.ly/CharacterBotGit"""
    await client.say(msg)


@client.command(pass_context=True, aliases=["invite"])
async def share(ctx):
    await client.send_message(ctx.message.author, "https://bit.ly/2NXNMJn")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_database())
    loop.run_until_complete(start_servers_data())

    extensions = ["commands.input", "commands.output", "commands.roleplay", "commands.help"]
    for e in extensions:
        client.load_extension(e)

    client.run(config.TOKEN)
