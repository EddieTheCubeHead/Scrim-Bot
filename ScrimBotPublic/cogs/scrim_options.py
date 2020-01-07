
import discord
from discord.ext import commands, tasks
import scrim_methods
import option_methods

class OptionsCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.guild_only()
    async def options(self, ctx):
        current = await scrim_methods.get_scrim(ctx, check_master=True)
        if not current:
            return None
        for counter, option in enumerate(current.options, 1):
            option_embed = discord.Embed(title=option.name, color=current.game.color)
            option_embed.add_field(name="Choices", value="\n".join(option.choices))
            if counter == len(current.options):
                option_embed.set_footer(text="Please specify how you wish to set options.\nSee '/help options' for a complete list of possibilities.")
            current.option_embeds[option.name] = {await ctx.send(embed=option_embed)}


def setup(client):
    client.add_cog(OptionsCog(client))
