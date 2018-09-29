import discord
from discord.ext import commands
from modules.data_manager import modify, unregister_server
from modules.data_getter import get_user_character, get_character_info, get_columns, get_tables, fetch, get_prefix

parameters = {
    "take": ["character"]
}


class RolePlay:
    def __init__(self, client):
        self.client = client

    async def on_member_remove(self, member):
        server = member.server.id
        tables = await get_tables(server)

        for t in tables:
            await modify(server, t, "taken_by='nobody'", f"taken_by='{member}'")

    async def on_member_update(self, before, after):
        if str(before) == str(after):
            return

        server = after.server.id
        tables = await get_tables(server)
        for t in tables:
            await modify(server, t, f"taken_by='{after}'", f"taken_by='{before}'")

    async def on_server_leave(self, server):
        id = server.id

        tables = await get_tables(id)
        for t in tables:
            await delete_table(server, t)

        backup = await get_tables(id, bk=True)
        for b in backup:
            await delete_table(server, b, bk=True)

        await unregister_server(id)

    @commands.command(pass_context=True)
    async def take(self, ctx, *args):
        msgs = {
            "usage": "Usage: `{}take (char)`\nUse `{}list` to see who's available",
            "already_assigned": "You are already assigned to **{}**!",
            "invalid_param": "Invalid parameter: {}.",
            "unavailable": "That character is already taken.",
            "success": "You are now **{}**!"
        }

        pt = parameters["take"]
        user, server = ctx.message.author, ctx.message.server.id

        if pt.index("character") >= len(args):
            prefix = await get_prefix(server)
            await self.client.say(msgs["usage"].format(prefix, prefix))
            return

        user_char = await get_user_character(server, user)
        if user_char is not None:
            await self.client.say(msgs["already_assigned"].format(user_char))
            return

        character = ' '.join(args[pt.index("character"):])
        char_data = await get_character_info(server, character)
        if char_data == {}:
            await self.client.say(msgs["invalid_param"].format(character))
            return

        if char_data["taken_by"] != "nobody":
            await self.client.say(msgs["unavailable"])
            return

        table, name = char_data["table"], char_data["name"]

        await modify(server, table, f"taken_by='{user}'", f"name='{name}'")

        await self.client.say(msgs["success"].format(name))
        if "discord_role" in await get_columns(server):
            role = discord.utils.get(ctx.message.server.roles, name=char_data["discord_role"])
            if role in ctx.message.server.roles:
                await self.client.add_roles(user, role)
        await self.client.change_nickname(user, name)

    @commands.command(pass_context=True)
    async def leave(self, ctx):
        msgs = {
            "nobody_assigned": "You don't have a character assigned!",
            "success": "You aren't **{}** anymore!"
        }

        user, server = ctx.message.author, ctx.message.server.id
        user_char = await get_user_character(server, user)
        char_data = await get_character_info(server, user_char)
        if user_char is None:
            await self.client.say(msgs['nobody_assigned'])
            return

        table = char_data["table"]
        await modify(server, table, "taken_by='nobody'", f"taken_by='{user}'")

        await self.client.say(msgs['success'].format(user_char))
        if "discord_role" in await get_columns(server):
            role = discord.utils.get(ctx.message.server.roles, name=char_data["discord_role"])
            if role in ctx.message.server.roles:
                await self.client.remove_roles(user, role)
        await self.client.change_nickname(user, '')


def setup(client):
    client.add_cog(RolePlay(client))