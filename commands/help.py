import copy
import discord
from discord.ext import commands
from modules.data_getter import get_prefix
from modules.chat_utils import get_embed

reactions = ("◀", "⏹", "▶")
help_messages = (
            get_embed("Index",
                      "Page 1: Index\n"
                      "Page 2: Roleplay Commands\n"
                      "Page 3: Config Commands\n"
                      "Page 4: Misc Commands\n",
                      discord.Colour(0x546e7a)),
            get_embed("Roleplay Commands", "", discord.Colour(0x546e7a)),
            get_embed("Config Commands", "", discord.Colour(0x546e7a)),
            get_embed("Misc Commands", "", discord.Colour(0x546e7a)),
        )
fields = [
    [],
    (
        ("{}take", "Become a character"),
        ("{}leave", "Stop being your current character"),
        ("{}list, {}catalogue", "List the contents of a table"),
        ("{}char", "Display a character's info")
    ),
    (
        ("{}import, {}load", "Import your .csv database or a preset"),
        ("{}download", "Download your server's data"),
        ("{}create", "Make a new table"),
        ("{}add", "Add (or modify, if it already exists) a new character"),
        ("{}del, {}delete", "Delete a table or a character"),
        ("{}template, {}columns", "Modify the columns"),
        ("In depth guide for configuring your server:", "https://bit.ly/CharacterBotSetup")
    ),
    (
        ("{}invite, {}share", "Get the bot's invite link"),
        ("{}info", "General info about the bot"),
        ("{}prefix", "Change the bot's prefix"),
        ("{}help", "Display this message")
    )
]


class Help:
    def __init__(self, client):
        self.client = client

    async def on_reaction_add(self, reaction, user):
        message = reaction.message
        emoji = reaction.emoji
        if message.author.id == "491581230962442242" \
                and user.id != "491581230962442242" \
                and emoji in reactions:
            await self.client.remove_reaction(message, emoji, user)

            if emoji == "⏹":
                await self.client.delete_message(message)
                return

            page_number = int(message.content[-1])-1
            page_number += reactions.index(emoji)-1
            if not 0 <= page_number < len(help_messages):
                return

            prefix = await get_prefix(message.server.id)
            page = copy.copy(help_messages[page_number])
            for f in fields[page_number]:
                page.add_field(name=f[0].replace("{}", prefix),
                               value=f[1],
                               inline=False)

            await self.client.edit_message(message, new_content=f"Page {page_number+1}", embed=page)


    @commands.command(pass_context=True)
    async def help(self, ctx):
        help_msg = await self.client.say("Page 1", embed=help_messages[0])
        for r in reactions:
            await self.client.add_reaction(help_msg, r)


def setup(client):
    client.add_cog(Help(client))
