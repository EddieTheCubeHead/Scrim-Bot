
import discord
from discord.ext import commands, tasks

class UtilitiesCog(commands.Cog):
    def __init__(self, client):
        self.client = client



def setup(client):
    client.add_cog(UtilitiesCog(client))