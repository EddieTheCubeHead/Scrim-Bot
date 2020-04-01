
import discord
from discord.ext import commands, tasks
import asyncio

import main_methods
import scrim_methods
import checks

class UtilitiesCog(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.server_config = main_methods.get_server_configs()
        self.emoji_games = {}

        game_dict = main_methods.get_game_config()
        for category in game_dict["Games"]:
            for game in game_dict["Games"][category]:
                self.emoji_games.update({game : game_dict["Games"][category][game]["dispname"]})

#################################################################################
##
##   /setup_roles for automated and interactive setup of the bot's role system
##
#################################################################################

    @commands.command()
    @commands.guild_only()
    @checks.guild_admin()
    async def setup_roles(self, ctx):

        #getting all the games
        game_dict = main_methods.get_game_config()

        #check for the interactive creation and recognising the correct user
        def check(message):
            return (message.channel == ctx.message.channel
                    and message.author == ctx.message.author)

        if str(ctx.guild.id) not in self.server_config:
            #default server settings
            self.server_config[str(ctx.guild.id)] = {"lb_default": 25,
                                                     "roles_setup": False,
                                                     "role_signup_message": None,
                                                     "require_setup_permissions": False,
                                                     "bot_guild_admins": [],
                                                     "prefix": None,
                                                     "bot_guild_moderators": [],
                                                     "games_is_whitelist": False,
                                                     "games": [],
                                                     "delete_inactive": True,
                                                     "delete_time_mins": 20,
                                                     "delete_msgs_in_scrim": True}


        elif self.server_config[str(ctx.guild.id)]["roles_setup"]:
            query_msg = await ctx.send(f"This server already has a role signup system setup. If you want to run the setup again to update the roles, answer 'yes', if not, answer anything else.")
            try:
                response_msg = await self.client.wait_for('message', timeout=20.0, check = check)
                await query_msg.delete()
            except asyncio.TimeoutError:
                return await scrim_methods.temporary_feedback(ctx, "Request timed out.", delay = 20.0)

            if response_msg.content.lower() != "yes":
                await response_msg.delete()
                return await scrim_methods.temporary_feedback(ctx, "Operation cancelled", delay = 20.0)
            await response_msg.delete()

        new_role_count = 0
        overwrite_count = 0
        new_emoji_count = 0
        emoji_overwrites = 0

        #counting new and old roles and emojis for the interactive messages
        for category in game_dict["Games"]:
            for game in game_dict["Games"][category]:
                new_role_count += 1
                new_emoji_count += 1
                if game in list(emoji.name for emoji in ctx.guild.emojis):
                    emoji_overwrites += 1
                for role in ctx.message.guild.roles:
                    if str(role) == game_dict["Games"][category][game]["dispname"]:
                        overwrite_count += 1
                        break
        new_role_count -= overwrite_count
        new_emoji_count -= emoji_overwrites

        if new_role_count == 0:
            query_msg = await ctx.send(f"All games alredy have a role. Overwriting old roles is recommended. If you want to do it answer 'yes', if no, answer anything else.")
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
                force_overwrite = (response_msg.content.lower() == "yes")
                await response_msg.delete()
            else:
                force_overwrite = False

        extra_string = ""
        if emoji_overwrites:
            extra_string = f" and reuse {emoji_overwrites} existing ones"
        query_msg = await ctx.send(f"Do you want to create a signup system for the roles? This will create {new_emoji_count} new emojis on the server{extra_string}. " + 
                                    f"This will also create a signup channel if one does not already exist and post a message on that channel. " + 
                                    f"If you want to do this, answer 'yes', if not, answer anything else.")

        try:
            response_msg = await self.client.wait_for('message', timeout=20.0, check = check)
            await query_msg.delete()
        except asyncio.TimeoutError:
            return await scrim_methods.temporary_feedback(ctx, "Request timed out.", delay = 20.0)
        create_signup_system = (response_msg.content.lower() == "yes")
        await response_msg.delete()

        emojis = {}
        
        #creating all the necessary roles and emotes
        for category in game_dict["Games"]:
            for game in game_dict["Games"][category]:

                #check server-specific gamebans
                if ((self.server_config[str(ctx.guild.id)]["games_is_whitelist"] and game not in self.server_config[str(ctx.guild.id)]["games"]) or
                   (not self.server_config[str(ctx.guild.id)]["games_is_whitelist"] and game in self.server_config[str(ctx.guild.id)]["games"])):
                    continue

                #role creation
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

                #emoji creation
                if create_signup_system and game not in list(emoji.name for emoji in ctx.guild.emojis):
                    with open(f"emoji_pics/{game}.png", "rb") as emoji_image:
                        emojis.update({game_dict["Games"][category][game]["dispname"] : await ctx.message.guild.create_custom_emoji(name = game, image = emoji_image.read())})
                elif create_signup_system:
                    for emoji in ctx.guild.emojis:
                        if emoji.name == game:
                            emojis.update({game_dict["Games"][category][game]["dispname"] : emoji})
                            break

        if not create_signup_system:
            return await scrim_methods.temporary_feedback(ctx, "Roles setup. Did not setup automated signup channel as requested.")

        #setting up the signup message embed
        signup_embed = discord.Embed(title="Role signup", description="React with the games you play to get pingable roles for them.", color=int("0x008709", 16))
        signup_embed.set_author(name="ScrimBot", icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Fxemoji_u1F3AE.svg/512px-Fxemoji_u1F3AE.svg.png")
        signup_embed.set_footer(text="Tip: If you are stuck with a role after this message was reset, just react with that role again and remove the reaction.")
        for game in emojis:
            signup_embed.add_field(name = game, value = str(emojis[game]))


        if ("scrimbot-role-signup" in list(channel.name for channel in ctx.guild.channels)) and (not self.server_config[str(ctx.guild.id)]["role_signup_message"]):
            for channel in ctx.guild.channels:
                if channel.name == "scrimbot-role-signup":
                    signup_message = await channel.send(embed = signup_embed)
                    feedback = "Role signup channel already exists. Signup message missing, a new one was created."

        elif "scrimbot-role-signup" in list(channel.name for channel in ctx.guild.channels) and self.server_config[str(ctx.guild.id)]["role_signup_message"]:
            for channel in ctx.guild.channels:
                if channel.name == "scrimbot-role-signup":
                    signup_message = await channel.fetch_message(self.server_config[str(ctx.guild.id)]["role_signup_message"])
                    await signup_message.edit(embed = signup_embed)
                    feedback = "Role signup channel and message already exist. Updated the message."

        else:
            for category in ctx.guild.categories:
                if category.name == "SCRIMBOT ROLE SIGNUP":
                    signup_category = category
                    break
            else:
                signup_category = await ctx.guild.create_category(name = "SCRIMBOT ROLE SIGNUP", reason = "ScrimBot: setting up role signup system.")

            signup_channel = await ctx.guild.create_text_channel(name = "scrimbot-role-signup", category = signup_category, reason = "ScrimBot: setting up role signup system.")
            signup_message = await signup_channel.send(embed=signup_embed)
            feedback = "Created a channel and a message for role signup."

        await signup_message.clear_reactions()
        for game in emojis:
            await signup_message.add_reaction(str(emojis[game]))
        self.server_config[str(ctx.guild.id)]["role_signup_message"] = signup_message.id
        self.server_config[str(ctx.guild.id)]["roles_setup"] = True

        main_methods.save_server_configs(self.server_config)
        return await scrim_methods.temporary_feedback(ctx, feedback)

    @setup_roles.error
    async def setup_roles_error(self, ctx, error):
        if isinstance(error, checks.NotServerAdmin):
            return await scrim_methods.temporary_feedback(ctx, error)

#################################################################################
##
##      update all cogs and the game list and reset the bot
##
#################################################################################

    @commands.command()
    @checks.bot_admin_global()
    async def update(self, ctx):
    
        for scrim in scrim_methods.Scrim.instances:
            if scrim.phase != "no scrim":
                return await scrim_methods.temporary_feedback(ctx, "Cannot update while a scrim is underway.")

        else:
            if elo_methods.Game.get_games(main_methods.get_game_config()):
                await scrim_methods.temporary_feedback(ctx, "Successfully updated games.", delete=False)
            else:
                await scrim_methods.temporary_feedback(ctx, "Couldn't update games.", delete=False)

            try:
                initial_extensions = main_methods.get_cogs()
                for ext in initial_extensions:
                    client.reload_extension(ext)
                await scrim_methods.temporary_feedback(ctx, "Successfully updated commands.")
            except:
                await scrim_methods.temporary_feedback(ctx, "Couldn't update commands.")

            scrim_methods.Scrim.setup_instances(client)
            scrim_methods.Scrim.participators.clear()

    @update.error
    async def update_error(self, ctx, error):
        if isinstance(error, checks.NotBotAdminGlobal):
            return await scrim_methods.temporary_feedback(ctx, error)

#################################################################################
##
##      listeners for the role signup system
##
#################################################################################

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if str(ctx.guild.id) in self.server_config:
            if self.server_config[str(ctx.guild.id)]["role_signup_message"] and ctx.channel.name == "scrimbot-role-signup" and not ctx.author.bot:
                await ctx.delete()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, react):
        user = self.client.get_guild(react.guild_id).get_member(react.user_id)

        if user.bot:
            return False
        #the cascading if-clauses here are to prevent key errors with dictionaries and null keys
        if str(react.guild_id) in self.server_config:
            if self.server_config[str(react.guild_id)]["role_signup_message"]:
                if react.message_id == self.server_config[str(react.guild_id)]["role_signup_message"]:
                    if react.emoji.name in self.emoji_games:
                        if self.emoji_games[react.emoji.name] not in list(role.name for role in user.roles):
                            for role in self.client.get_guild(react.guild_id).roles:
                                if role.name == self.emoji_games[react.emoji.name]:
                                    await user.add_roles(role)
                                    return

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, react):
        user = self.client.get_guild(react.guild_id).get_member(react.user_id)

        if user.bot:
            return False
        #the cascading if-clauses here are to prevent key errors with dictionaries and null keys
        if str(react.guild_id) in self.server_config:
            if self.server_config[str(react.guild_id)]["role_signup_message"]:
                if react.message_id == self.server_config[str(react.guild_id)]["role_signup_message"]:
                    if react.emoji.name in self.emoji_games:
                        if self.emoji_games[react.emoji.name] in list(role.name for role in user.roles):
                            for role in self.client.get_guild(react.guild_id).roles:
                                if role.name == self.emoji_games[react.emoji.name]:
                                    await user.remove_roles(role)
                                    return


def setup(client):
    client.add_cog(UtilitiesCog(client))