
import discord
from discord.ext import commands, tasks
import re

import main_methods
import scrim_methods

class UtilitiesCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.guild_only()
    async def setup_roles(self, ctx):
        if ctx.message.author.guild_permissions.administrator == False:
            return await scrim_methods.temporary_feedback(ctx, "You need to be an administrator to do that.")

        game_dict = main_methods.get_game_config()
        server_config = main_methods.get_server_configs()

        new_role_count = 0
        overwrite_count = 0

        for category in game_dict["Games"]:
            for game in game_dict["Games"][category]:
                nenew_role_count += 1
                for role in ctx.message.guild.roles:
                    if str(role) == game_dict["Games"][category][game]["dispname"]:
                        overwrite_count += 1

        new_role_count -= overwrite_count

        def check(message):
            return (message.channel == ctx.message.channel
                    and message.author == ctx.message.author)

        query_msg = await ctx.send(f"This will create {new_role_count} new roles on the server. If you want to proceed answer 'yes', if not answer anything else.")

        try:
            response_msg = await self.client.wait_for('message', timeout=20.0, check = check)
            await query_msg.delete()
        except asyncio.TimeoutError:
            return await scrim_methods.temporary_feedback(ctx, "Request timed out.", delay = 20.0)

        if response_msg.content.lower() != "yes":
            await response_msg.delete()
            return await scrim_methods.temporary_feedback(ctx, "Operation cancelled", delay = 20.0)
        await response_msg.delete()

        if overwrite_count:
            query_msg = await ctx.send(f"Found {overwrite_count} conflicting roles. Overwriting old roles is recommeneded. If you want to do it answer 'yes', if no, answer anything else.")

            try:
                response_msg = await self.client.wait_for('message', timeout = 20.0, check = check)
                await query_msg.delete()
            except asyncio.TimeoutError:
                return await scrim_methods.temporary_feedback(ctx, "Request timed out.", delay = 20.0)

            if response_msg.content.lower() == "yes":
                force_overwrite = True
            else:
                force_overwrite = False
            await response_msg.delete()

        else:
            force_overwrite = False
        
        for category in game_dict["Games"]:
            for game in game_dict["Games"][category]:
                for role in ctx.message.guild.roles:
                    if str(role) == game_dict["Games"][category][game]["dispname"]:
                        if force_overwrite:
                            await ctx.message.guild.get_role(role.id).delete(reason = "ScrimBot: overwriting old roles while setting up roles for games.")
                            continue
                        else:
                            break
                else:
                    await ctx.message.guild.create_role(name = game_dict["Games"][category][game]["dispname"],
                                                        #getting the hex values of the color from the game dictionary's color value:
                                                        colour = discord.Color.from_rgb(int(game_dict["Games"][category][game]["colour"][2:4], 16),
                                                                                        int(game_dict["Games"][category][game]["colour"][4:6], 16),
                                                                                        int(game_dict["Games"][category][game]["colour"][6:], 16)),
                                                        mentionable = True,
                                                        reason = "ScrimBot: Setting up roles for games")

        if "scrimbot-role-signup" in list(map(channel.name, channel in ctx.guild.channels)):
            return await ctx.send(ctx, "Role signup channel already exists,")




def setup(client):
    client.add_cog(UtilitiesCog(client))