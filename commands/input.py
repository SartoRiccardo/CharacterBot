import aiohttp
import discord
from discord.ext import commands
from modules.preset_manager import import_db, get_presets, load_file_preset
from modules.misc_utils import *
from modules.data_manager import *
from modules.data_getter import get_character_info, get_tables, get_columns, get_prefix

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
            "usage": "Usage: `{}add (table) (character) {}`",
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
        prefix = await get_prefix(server)

        if pa.index("character") >= len(args) or len(args[pa.index("parameters"):]) != len(await get_columns(server))-2:
            template = ''
            for c in (await get_columns(server))[2:]:
                template += f"({c}) "
            await self.client.say(msgs["usage"].format(prefix, template))
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
            correct_cmd = f"{prefix}add {char_data['table']} {char}"
            for p in args[pa.index("parameters"):]:
                correct_cmd += f" {p}"

            await self.client.say(msgs["already_exists"].format(char_data["table"], correct_cmd))
            return

        # Character exists and the table is correct
        await pgdelete(server, table, f"name='{char}'")

        values = [char, "nobody"]
        for p in args[parameters["add"]:]:
            values.append(p)

        await insert(server, table, values)
        await self.client.say(msgs["success_modified"].format(char))

    @commands.command(pass_context=True)
    async def create(self, ctx, *args):
        msgs = {
            "usage": "Usage: `{}create (table)`",
            "insufficient_permissions": "You don't have the permissions to do that!",
            "already_exists": "**{}** already exists! Try using `{}list {}` to see who's there!",
            "spaces": "You can't use spaces in your table name!\nTry using: `{}`",
            "success": "Table **{}** successfully created!"
        }

        # Check if has the permissions to do that
        if not ctx.message.author.server_permissions.administrator:
            await self.client.say(msgs["insufficient_permissions"])
            return

        # Check if there's any arguments
        prefix = await get_prefix(ctx.message.server.id)
        if len(args) == 0:
            await self.client.say(msgs["usage"].format(prefix))
            return

        pc = parameters["create"]
        to_create = args[pc.index("table")]

        # Checks if there are spaces in the table name
        if len(args[pc.index("table"):]) > 1 or ' ' in to_create:
            snake_case = []
            for i in range(pc.index("table"), len(args)):
                snake_case += args[i].split(' ')

            await self.client.say(msgs["spaces"].format('_'.join(snake_case)))
            return

        server = ctx.message.server.id

        # Check if the table already exists
        if to_create in await get_tables(server):
            await self.client.say(msgs["already_exists"].format(to_create, prefix, to_create))
            return

        await create_table(server, to_create)
        await self.client.say(msgs["success"].format(to_create))

    @commands.command(pass_context=True, aliases=["del"])
    async def delete(self, ctx, to_delete=""):
        msgs = {
            "usage": "Usage: `{}del (table | character)`",
            "insufficient_permissions": "You don't have the permissions to do that!",
            "not_found": "Didn't find anything with the name: **{}**",
            "confirmation": "You are about to delete a whole table. Type `yes` to continue",
            "success": "**{}** successfully deleted!",
            "failure": "Did not delete **{}**"
        }

        if not ctx.message.author.server_permissions.administrator:
            await self.client.say(msgs["insufficient_permissions"])
            return

        server = ctx.message.server.id
        prefix = await get_prefix(server)
        if to_delete == "":
            await self.client.say(msgs["usage"].format(prefix))
            return

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
    async def load(self, ctx, preset=None):
        msgs = {
            "usage": "Usage: `{}import [preset]``[file]`",
            "insufficient_permissions": "You don't have the permissions to do that",
            "nonexistent": "The preset **{}** doesn't exist!",
            "list_presets": "Do `{}import list` to see what's available!",
            "confirmation": "All of your current characters will be deleted. Type `yes` to continue",
            "success": "Successfully imported **{}**!",
            "failure": "Did not import **{}**",
            "not_csv_file": "Unsupported file type.\n"
                            "Export your Excel/LibreOffice table into `.csv`",
            "csv_no_name_taken_by": "Your file doesn't have a `name` and/or `taken_by` column.",
            "csv_no_table_name": "Your table doesn't have a name.",

            "csv_invalid_table_name": "Your table name can't contain spaces",
            "csv_duplicate_column_name": "Your table has two or more columns with the same name",
            "csv_duplicate_char_name": "Your table has two or more characters with the same `name`. "
                                        "This counts for different tables as well!",
            "download_example": "Check out the template with `{}download example` if you're confused!",
        }

        if not ctx.message.author.server_permissions.administrator:
            await self.client.say(msgs["insufficient_permissions"])
            return

        prefix = await get_prefix(ctx.message.server.id)

        if preset is None and ctx.message.attachments == [] or \
                preset is not None and preset.lower() == "list":
            available_presets = get_presets()
            msg = "Available presets: "
            for p in available_presets:
                msg += f"`{p}` "
            msg += f"\nYou can also just write `{prefix}import` and attach a csv file to it"

            prefix = await get_prefix(ctx.message.server.id)

            await self.client.say(msgs["usage"].format(prefix) + '\n' + msg)
            return

        if preset is None and ctx.message.attachments != []:
            link = ctx.message.attachments[0]["url"]
            if link[-4:] != ".csv":
                await self.client.say(msgs["not_csv_file"])
                return

            try:
                await load_file_preset(ctx.message.server.id, link)
                await self.client.say(msgs["success"].format(ctx.message.attachments[0]["filename"]))
            except SyntaxError as e:
                output = msgs[str(e)]
                if str(e)[:4] == "csv":
                    output += '\n' + msgs["download_example"]
                await self.client.say(output)

            return

        await self.client.say(msgs["confirmation"])
        response = await self.client.wait_for_message(author=ctx.message.author, timeout=30)
        try:
            if response is not None and response.clean_content.lower() == "yes":
                server = ctx.message.server.id
                await import_db(server, preset)
                await self.client.say(msgs["success"].format(preset))
            else:
                await self.client.say(msgs["failure"].format(preset))

        except SyntaxError as e:
            await self.client.say(msgs[str(e)].format(preset) + '\n'
                                  + msgs["list_presets"].format(prefix))

    @commands.command(pass_context=True)
    async def template(self, ctx, *args):
        msgs = {
            "insufficient_permissions": "You don't have the permissions to do that!",
            "confirmation": "You are about to modify the template. Type `yes` to go through with it.",
            "success": "Template was updated!",
            "space_in_arg": "You can't put spaces in the template! "
                            "Try using underscores (_) instead!"
        }

        if not ctx.message.author.server_permissions.administrator:
            await self.client.say(msgs["insufficient_permissions"])
            return

        await self.client.say(msgs["confirmation"])
        response = await self.client.wait_for_message(author=ctx.message.author, timeout=30)

        if response is None or response.clean_content.lower() != "yes":
            return

        try:
            await update_template(ctx.message.server.id, args)
            await self.client.say(msgs["success"])
        except SyntaxError as e:
            await self.client.say(msgs[str(e)])


def setup(client):
    client.add_cog(Input(client))
