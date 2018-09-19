import os
import csv
import discord
from discord.ext import commands
from discord.errors import HTTPException
from modules.misc_utils import get_dict_keys, project_path
from modules.chat_utils import get_embed, first_upper, bold, strikethrough
from modules.data_getter import fetch, get_tables, get_character_info, get_user_character, get_columns

parameters = {
    "char": ["character"],
    "list": ["table"]
}


class Output:
    def __init__(self, client):
        self.client = client

    @commands.command(pass_context=True)
    async def char(self, ctx, *args):
        character = ' '.join(args)
        special_columns = ('taken_by', 'thumbnail', 'img' 'discord_role', 'table')
        server = ctx.message.server.id

        info = await get_character_info(server, character)
        attributes = get_dict_keys(info)

        if "table" not in attributes:
            return

        output = ''
        for a in attributes:
            if a not in special_columns and info[a] != "N/A":
                row = bold(f"{first_upper(a).replace('_', ' ')}: ") + first_upper(info[a])
                output += row + '\n'

        e = get_embed(f"{first_upper(info['table'])} - {info['name']}", output, discord.Colour(0x546e7a))
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
            await self.client.say(f"Like this character? Use `>>take {info['name']}` to become them!", embed=e)
        except HTTPException:
            e.set_thumbnail(url='')
            e.set_image(url='')
            await self.client.say(f"Like this character? Use `>>take {info['name']}` to become them!", embed=e)

    @commands.command(pass_context=True, aliases=["list"])
    async def catalogue(self, ctx, *args):
        msgs = {
            "usage": "Usage: `>>list (table)`",
            "invalid_param": "Error: Table `{}` doesn't exist"
        }

        pl = parameters["list"]
        server = ctx.message.server.id

        if pl.index("table") >= len(args):
            await self.client.say(msgs['usage'])
            return

        t = args[pl.index("table")].lower()
        if t not in await get_tables(server):
            tables = ''
            for t in await get_tables(server):
                tables += f"`{t}`"

            await self.client.say(msgs['invalid_param'].format(args[pl.index("table")], tables))
            return

        characters = await fetch(server, t, "name")
        characters = [c["name"] for c in characters]

        output = ''
        for c in characters:
            formatted_c = bold(c)
            taken_by = (await fetch(server, t, "taken_by", f"name='{c}'"))[0]["taken_by"]
            if taken_by != "nobody":
                formatted_c = strikethrough(formatted_c)
            output += f"{formatted_c}\n"

        await self.client.say(f"Use `>>char take (name)` to become one of these characters!",
                              embed=get_embed(first_upper(t), output, discord.Colour(0x546e7a)))

    @commands.command(pass_context=True, aliases=["export"])
    async def download(self, ctx, example=None):
        if not ctx.message.author.server_permissions.administrator:
            await self.client.say("You don't have the permissions to do that!")
            return

        if example == "example":
            fout = os.path.join(project_path, "files", "example.csv")
            await self.client.send_file(ctx.message.channel, fout)
            return

        server = ctx.message.server.id
        tables = await get_tables(server)
        columns = await get_columns(server)

        path = os.path.join(project_path, "files", f"{server}.csv")
        with open(path, "w+") as fout:
            writer = csv.writer(fout)

            for t in tables:
                row = [t]
                row += [' ' for i in range(len(columns)-1)]
                writer.writerow(row)
                writer.writerow(columns)

                data = await fetch(server, t, "all")
                for d in data:
                    row = []
                    for c in columns:
                        row.append(d[c])

                    writer.writerow(row)

        await self.client.send_file(ctx.message.channel, path, filename="Server Data.csv")

        os.remove(path)


def setup(client):
    client.add_cog(Output(client))