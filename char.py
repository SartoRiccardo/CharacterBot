import discord
from discord.ext import commands

extensions = ["input", "roleplay"]

class Char():
    def __init__(self, client):
        self.client = client
#        try:
 #           for e in extensions:
  #              client.load_extension(e)
   #     except Exception as e:
    #        print(e)

    @commands.group(pass_context=True, invoke_without_command=True)
    async def char(self, ctx):
        # status command
        pass



def setup(client):
    client.add_cog(Char(client))