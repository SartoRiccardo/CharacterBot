import discord
from discord.ext import commands
from modules.preset_manager import import_db, get_presets
from modules.misc_utils import *
from modules.data_manager import delete_table, pgdelete, update_template, create_table, insert
from modules.data_getter import get_character_info, get_tables, get_columns

parameters = {
    "create": ["table"],
    "add": ["table", "character", "parameters"]
}


class Input:
    def __init__(self, client):
        self.client = client

    @commands.command(pass_context=True)
    async def add(self, ctx, *args):
        msgs = {
            "usage": "Usage: `>>add (table) (character) {}`",
            "insufficient_permissions": "You don't have the permissions to do that!",
            "invalid_table": "Invalid table: `{}`",
            "already_exists": "Character already exists in table `{}`\nTo modify that character's info, use `{}`",
            "success_added": "Successfully added **{}** into **{}**",
            "success_modified": "Successfully modified **{}**'s data!"
        }

        if not ctx.message.author.server_permissions.administrator:
            await self.client.say(msgs["insufficient_permissions"])
            return

        pa = parameters["add"]
        server = ctx.message.server.id

        if pa.index("character") >= len(args) or len(args[pa.index("parameters"):]) != len(await get_columns(server))-2:
            template = ''
            for c in (await get_columns(server))[2:]:
                template += f"({c}) "
            await self.client.say(msgs["usage"].format(template))
            return

        table = args[pa.index("table")].lower()

        if table not in await get_tables(server):
            await self.client.say(msgs["invalid_table"].format(args[pa.index("table")]))
            return

        char = args[pa.index("character")]
        char_data = await get_character_info(server, char)
        if char_data == {}:  # Character doesn't exist
            values = [char, "nobody"]
            for p in args[pa.index("parameters"):]:
                values.append(p)

            await insert(server, table, values)
            await self.client.say(msgs["success_added"].format(char, table))
            return

        if table != char_data["table"]:  # Character exists in another table
            correct_cmd = f">>char add {char_data['table']} {char}"
            for p in args[pa.index("parameters"):]:
                correct_cmd += f" {p}"

            await self.client.say(msgs["already_exists"].format(char_data["table"], correct_cmd))
            return

        # Character exists and the table is correct
        await pgdelete(server, table, f"name='{char}'")

        values = [char, "nobody"]
        for p in args[parameters["args"]:]:
            values.append(p)

        await insert(server, table, values)
        await self.client.say(msgs["success_modified"].format(char))

    @commands.command(pass_context=True)
    async def create(self, ctx, *args):
        msgs = {
            "usage": "Usage: `>>char create (table)`",
            "insufficient_permissions": "You don't have the permissions to do that!",
            "already_exists": "**{}** already exists! Try using `>>char list {}` to see who's there!",
            "spaces": "You can't use spaces in your table name!\nSuggestions: `{}` `{}`",
            "success": "Table **{}** successfully created!"
        }

        # Check if has the permissions to do that
        if not ctx.message.author.server_permissions.administrator:
            await self.client.say(msgs["insufficient_permissions"])
            return

        # Check if there's any arguments
        if len(args) == 0:
            await self.client.say(msgs["usage"])
            return

        pc = parameters["create"]
        to_create = args[pc.index("table")]

        # Checks if there are spaces in the table name
        if len(args[pc.index("table"):]) > 1 or ' ' in to_create:
            camel_case, snake_case = [], []
            for i in range(pc.index("table"), len(args)):
                camel_case += args[i].split(' ')
                snake_case += args[i].split(' ')

            camel_case = [camel_case[i][0].upper() + camel_case[i][1:] for i in range(len(camel_case))]
            camel_case[0] = camel_case[0].lower()

            await self.client.say(msgs["spaces"].format(''.join(camel_case), '_'.join(snake_case)))
            return

        server = ctx.message.server.id

        # Check if the table already exists
        if to_create in await get_tables(server):
            await self.client.say(msgs["already_exists"].format(to_create, to_create))
            return

        await create_table(server, to_create)
        await self.client.say(msgs["success"].format(to_create))

    @commands.command(pass_context=True, aliases=["del"])
    async def delete(self, ctx, to_delete=""):
        msgs = {
            "usage": "Usage: `>>del (table | character)`",
            "insufficient_permissions": "You don't have the permissions to do that!",
            "not_found": "Didn't find anything with the name: **{}**",
            "confirmation": "You are about to delete a whole table. Type `yes` to continue",
            "success": "**{}** successfully deleted!",
            "failure": "Did not delete **{}**"
        }

        if not ctx.message.author.server_permissions.administrator:
            await self.client.say(msgs["insufficient_permissions"])
            return

        if to_delete == "":
            await self.client.say(msgs["usage"])

        server = ctx.message.server.id
        char_info = await get_character_info(server, to_delete)

        # It's a table
        if to_delete in await get_tables(server):
            await self.client.say(msgs["confirmation"])
            response = await self.client.wait_for_message(author=ctx.message.author, timeout=30)

            if response is not None and response.clean_content == "yes":
                await delete_table(server, to_delete)
                await self.client.say(msgs["success"].format(to_delete))
            else:
                await self.client.say(msgs["failure"].format(to_delete))

        # It's a character
        elif char_info != {}:
            await pgdelete(server, char_info["table"], f"LOWER(name)=LOWER('{to_delete}')")
            await self.client.say(msgs["success"].format(to_delete))

        else:
            await self.client.say(msgs["not_found"].format(to_delete))

    @commands.command(pass_context=True, aliases=["import"])
    async def load(self, ctx, preset):
        msgs = {
            "insufficient_permissions": "You don't have the permissions to do that",
            "nonexistent": "The preset **{}** doesn't exist!\n"
                           "Do `>>import list` to see what's available!",
            "confirmation": "All of your current characters will be deleted. Type `yes` to continue",
            "success": "Successfully imported **{}**!",
            "failure": "Did not import **{}**"
        }

        if not ctx.message.author.server_permissions.administrator:
            await self.client.say(msgs["insufficient_permissions"])
            return

        if preset.lower() == "list":
            available_presets = get_presets()
            msg = "Available presets: "
            for p in available_presets:
                msg += f"`{p}` "
            await self.client.say(msg)
            return

        await self.client.say(msgs["confirmation"])
        response = await self.client.wait_for_message(author=ctx.message.author, timeout=30)
        try:
            if response is not None and response.clean_content == "yes":
                server = ctx.message.server.id
                await import_db(server, preset)
                await self.client.say(msgs["success"].format(preset))
            else:
                await self.client.say(msgs["failure"].format(preset))

        except SyntaxError as e:
            await self.client.say(msgs[str(e)].format(preset))

    @commands.command(pass_context=True)
    async def template(self, ctx, *args):
        if ctx.message.author.server_permissions.administrator:
            await update_template(ctx.message.server.id, args[1:])
            await self.client.say("Template was updated!")
        else:
            await self.client.say("You don't have the permissions to do that!")


def setup(client):
    client.add_cog(Input(client))
