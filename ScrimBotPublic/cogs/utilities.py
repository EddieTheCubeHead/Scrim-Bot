
import discord
from discord.ext import commands, tasks
import asyncio

import main_methods
import scrim_methods
import elo_methods
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

        self.config_initialization(ctx)

        if self.server_config[str(ctx.guild.id)]["roles_setup"]:
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
        signup_embed = discord.Embed(title="Role signup", description="React with the games you play to get pingable roles for them.", color=int("0x00ff00", 16))
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
##                 command group for managing server settings
##
#################################################################################

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    @checks.settings_eligible()
    async def settings(self, ctx):

        self.config_initialization(ctx)

        lb_max = self.server_config[str(ctx.guild.id)]["lb_max"] or "Unlimited"
        lb_default = self.server_config[str(ctx.guild.id)]["lb_default"] or lb_max

        if self.server_config[str(ctx.guild.id)]["require_setup_permissions"]:
            require_setup_permissions = "True"
        else:
            require_setup_permissions = "False"

        if self.server_config[str(ctx.guild.id)]["guild_admin_is_bot_admin"]:
            guild_admin_is_bot_admin = "True"
        else:
            guild_admin_is_bot_admin = "False"

        prefix = self.server_config[str(ctx.guild.id)]["prefix"] or "/"

        if self.server_config[str(ctx.guild.id)]["games_is_whitelist"]:
            games_type = "Whitelisted games"
        else:
            games_type = "Blacklisted games"

        games = "\n".join(self.server_config[str(ctx.guild.id)]["games"]) or "None"

        if self.server_config[str(ctx.guild.id)]["delete_inactive"]:
            delete_inactive = self.server_config[str(ctx.guild.id)]["delete_time_mins"] or "20"
        else:
            delete_inactive = "Not enabled"

        if self.server_config[str(ctx.guild.id)]["delete_msgs_in_scrim"]:
            delete_msgs_in_scrim = "True"
        else:
            delete_msgs_in_scrim = "False"

        bot_guild_admins = "\n".join(self.server_config[str(ctx.guild.id)]["bot_guild_admins"]) or "None"
        bot_guild_moderators = "\n".join(self.server_config[str(ctx.guild.id)]["bot_guild_moderators"]) or "None"

        setting_embed = discord.Embed(title = "Current server settings", description = "Use '/**settings** _setting value_ to change a setting.")
        setting_embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url_as())
        setting_embed.add_field(name="Leaderboard default length", value=lb_default, inline=False)
        setting_embed.add_field(name="Leaderboard maximum length", value=lb_max, inline=False)
        setting_embed.add_field(name="Require bot moderator permissions to setup scrim", value=require_setup_permissions, inline=False)
        setting_embed.add_field(name="Guild admins have bot admin rights", value=guild_admin_is_bot_admin, inline=False)
        setting_embed.add_field(name=games_type, value=games, inline=False)
        setting_embed.add_field(name="Inactive scrim deletion", value=delete_inactive, inline=False)
        setting_embed.add_field(name="Delete messages in channels with active scrims", value=delete_msgs_in_scrim, inline=False)
        setting_embed.add_field(name="Guild's bot admins", value=bot_guild_admins, inline=False)
        setting_embed.add_field(name="Guild's bot moderators", value=bot_guild_moderators, inline=False)
        setting_embed.set_footer(text="Type '/help settings' for more information.")
        await ctx.send(embed = setting_embed)

    @settings.error
    async def settings_error(self, ctx, error):
        if isinstance(error, checks.NotSettingsEligible):
            return await scrim_methods.temporary_feedback(ctx, error)

#################################################################################
##
##                      /settings leaderboard_default
##
#################################################################################'

    @settings.command()
    async def leaderboard_default(self, ctx, value: int):
        self.config_initialization(ctx)
        self.server_config[str(ctx.guild.id)]["lb_default"] = value
        main_methods.save_server_configs(self.server_config)
        return await scrim_methods.temporary_feedback(ctx, f"Default length of leaderboards successfully set to {value}.")

#################################################################################
##
##                      /settings leaderboard_max
##
#################################################################################

    @settings.command()
    async def leaderboard_max(self, ctx, value: int):
        self.config_initialization(ctx)
        self.server_config[str(ctx.guild.id)]["lb_max"] = value
        main_methods.save_server_configs(self.server_config)
        return await scrim_methods.temporary_feedback(ctx, f"Maximum length of leaderboards successfully set to {value}.")

#################################################################################
##
##                      /settings delete_timer_scrims
##
#################################################################################

    @settings.command()
    async def delete_timer_scrims(self, ctx, value: int):
        self.config_initialization(ctx)
        self.server_config[str(ctx.guild.id)]["delete_time_mins"] = value
        main_methods.save_server_configs(self.server_config)
        return await scrim_methods.temporary_feedback(ctx, f"Idle scrim deletion delay successfully set to {value}.")

#################################################################################
##
##                      /settings scrim_permissions
##
#################################################################################

    @settings.command()
    async def scrim_permissions(self, ctx, value: bool):
        self.config_initialization(ctx)
        self.server_config[str(ctx.guild.id)]["require_setup_permissions"] = value
        main_methods.save_server_configs(self.server_config)
        return await scrim_methods.temporary_feedback(ctx, f"Scrim setup requiring permissions successfully set to {value}.")

#################################################################################
##
##                      /settings guild_bot_admin
##
#################################################################################

    @settings.command()
    async def guild_bot_admin(self, ctx, value: bool):
        self.config_initialization(ctx)
        self.server_config[str(ctx.guild.id)]["guild_admin_is_bot_admin"] = value
        main_methods.save_server_configs(self.server_config)
        return await scrim_methods.temporary_feedback(ctx, f"Server admins automatically having bot admin permissions on the server successfully set to {value}.")

#################################################################################
##
##                      /settings delete_idle_scrims
##
#################################################################################

    @settings.command()
    async def delete_idle_scrims(self, ctx, value: bool):
        self.config_initialization(ctx)
        self.server_config[str(ctx.guild.id)]["delete_inactive"] = value
        main_methods.save_server_configs(self.server_config)
        return await scrim_methods.temporary_feedback(ctx, f"Automatically deleting idle scrims on the server successfully set to {value}.")

#################################################################################
##
##                      /settings scrim_delete_messages
##
#################################################################################

    @settings.command()
    async def scrim_delete_messages(self, ctx, value: bool):
        self.config_initialization(ctx)
        self.server_config[str(ctx.guild.id)]["delete_msgs_in_scrim"] = value
        main_methods.save_server_configs(self.server_config)
        return await scrim_methods.temporary_feedback(ctx, f"Automatically deleting messages on channels with active scrims successfully set to {value}.")

#################################################################################
##
##                      /settings prefix
##
#################################################################################

    @settings.command()
    async def prefix(self, ctx, value):
        self.config_initialization(ctx)
        self.server_config[str(ctx.guild.id)]["prefix"] = value
        main_methods.save_server_configs(self.server_config)
        return await scrim_methods.temporary_feedback(ctx, f"Server bot prefix successfully set to '{value}'.")

#################################################################################
##
##                      /settings games_is_whitelist
##
#################################################################################

    @settings.command()
    async def games_is_whitelist(self, ctx, value: bool):
        self.config_initialization(ctx)
        self.server_config[str(ctx.guild.id)]["games_is_whitelist"] = value
        main_methods.save_server_configs(self.server_config)
        if value:
            text = "Server game list set to whitelist."
        else:
            text = "Server game list set to blacklist."
        return await scrim_methods.temporary_feedback(ctx, text)

#################################################################################
##
##                      /settings ping_created_scrim
##
#################################################################################

    @settings.command()
    async def ping_created_scrim(self, ctx, value: bool):
        self.config_initialization(ctx)
        self.server_config[str(ctx.guild.id)]["ping_game_role"] = value
        main_methods.save_server_configs(self.server_config)
        return await scrim_methods.temporary_feedback(ctx, f"Pinging the scrim's game on scrim setup successfully set to '{value}'.")

#################################################################################
##
##                      /settings admin -group
##
#################################################################################

    @settings.group(invoke_without_command=True)
    async def admin(self, ctx):
        return await scrim_methods.temporary_feedback(ctx, "Invalid use of command '/settings admin'. Use '/settings admin _add/remove/clear_' to manipulate server admins.")

    @admin.command()
    async def add(self, ctx, members: commands.Greedy[discord.Member]):
        self.config_initialization(ctx)
        admin_list = self.server_config[str(ctx.guild.id)]["bot_guild_admins"]
        for member in members:
            if member.id not in admin_list:
                admin_list.append(member.id)
                await scrim_methods.temporary_feedback(ctx, f"Added {member.display_name} as bot admin", delete=False)
            else:
                await scrim_methods.temporary_feedback(ctx, f"User {member.display_name} is already a bot admin", delete=False)
        self.server_config[str(ctx.guild.id)]["bot_guild_admins"] = admin_list
        main_methods.save_server_configs(self.server_config)
        await ctx.message.delete()
        return

    @admin.command()
    async def remove(self, ctx, members: commands.Greedy[discord.Member]):
        self.config_initialization(ctx)
        admin_list = self.server_config[str(ctx.guild.id)]["bot_guild_admins"]
        for member in members:
            if member.id in admin_list:
                admin_list.remove(member.id)
                await scrim_methods.temporary_feedback(ctx, f"Removed {member.display_name} from bot admins", delete=False)
            else:
                await scrim_methods.temporary_feedback(ctx, f"User {member.display_name} is not a bot admin", delete=False)
        self.server_config[str(ctx.guild.id)]["bot_guild_admins"] = admin_list
        main_methods.save_server_configs(self.server_config)
        await ctx.message.delete()
        return

    @admin.command()
    async def clear(self, ctx):
        self.config_initialization(ctx)
        self.server_config[str(ctx.guild.id)]["bot_guild_admins"] = []
        return await scrim_methods.temporary_feedback(ctx, "Cleared the server admin list.")

#################################################################################
##
##                      /settings moderator -group
##
#################################################################################

    @settings.group(invoke_without_command=True)
    async def moderator(self, ctx):
        return await scrim_methods.temporary_feedback(ctx, "Invalid use of command '/settings moderator'. Use '/settings moderator _add/remove/clear_' to manipulate server moderators.")

    @moderator.command()
    async def add(self, ctx, members: commands.Greedy[discord.Member]):
        self.config_initialization(ctx)
        moderator_list = self.server_config[str(ctx.guild.id)]["bot_guild_moderators"]
        for member in members:
            if member.id not in moderator_list:
                moderator_list.append(member.id)
                await scrim_methods.temporary_feedback(ctx, f"Added {member.display_name} as bot moderator.", delete=False)
            else:
                await scrim_methods.temporary_feedback(ctx, f"User {member.display_name} is already a bot moderator.", delete=False)
        self.server_config[str(ctx.guild.id)]["bot_guild_moderators"] = moderator_list
        main_methods.save_server_configs(self.server_config)
        await ctx.message.delete()
        return

    @moderator.command()
    async def remove(self, ctx, members: commands.Greedy[discord.Member]):
        self.config_initialization(ctx)
        moderator_list = self.server_config[str(ctx.guild.id)]["bot_guild_moderators"]
        for member in members:
            if member.id in moderator_list:
                moderator_list.remove(member.id)
                await scrim_methods.temporary_feedback(ctx, f"Removed {member.display_name} from bot moderators.", delete=False)
            else:
                await scrim_methods.temporary_feedback(ctx, f"User {member.display_name} is not a bot moderator.", delete=False)
        self.server_config[str(ctx.guild.id)]["bot_guild_moderators"] = moderator_list
        main_methods.save_server_configs(self.server_config)
        await ctx.message.delete()
        return

    @moderator.command()
    async def clear(self, ctx):
        self.config_initialization(ctx)
        self.server_config[str(ctx.guild.id)]["bot_guild_moderators"] = []
        return await scrim_methods.temporary_feedback(ctx, "Cleared the server moderator list.")


#################################################################################
##
##                            /settings gamelist -group
##
#################################################################################

    @settings.group(invoke_without_command=True)
    async def gamelist(self, ctx):
        return await  scrim_methods.temporary_feedback(ctx, "Invalid use of command '/settings gamelist'. Use '/settings gamelist _add/remove/clear_ to manipulate the games white/blacklist.")

    @gamelist.command()
    async def add(self, ctx, game_name):
        self.config_initialization(ctx)

        for game in elo_methods.Game.instances:
            if game_name in game.alias['alias']:
                if game.dispname in self.server_config[str(ctx.guild.id)]["games"]:
                    return await scrim_methods.temporary_feedback(ctx, f"The game {game.dispname} is already on the games list.")
                self.server_config[str(ctx.guild.id)]["games"].append(game.dispname)
                main_methods.save_server_configs(self.server_config)
                return await scrim_methods.temporary_feedback(ctx, f"Added game {game.dispname} to the games list.")

    @gamelist.command()
    async def remove(self, ctx, game_name):
        self.config_initialization(ctx)

        for game in elo_methods.Game.instances:
            if game_name in game.alias['alias']:
                if game.dispname not in self.server_config[str(ctx.guild.id)]["games"]:
                    return await scrim_methods.temporary_feedback(ctx, f"The game {game.dispname} is not on the games list.")
                self.server_config[str(ctx.guild.id)]["games"].remove(game.dispname)
                main_methods.save_server_configs(self.server_config)
                return await scrim_methods.temporary_feedback(ctx, f"Removed game {game.dispname} from the games list.")

    @gamelist.command()
    async def clear(self, ctx):
        self.config_initialization(ctx)
        self.server_config[str(ctx.guild.id)]["games"].clear()
        return await scrim_methods.temporary_feedback(ctx, "Cleared the games list.")



#################################################################################
##
##       a command to update all cogs and the game list and reset the bot
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
        if ctx.guild and str(ctx.guild.id) in self.server_config:
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

    def config_initialization(self, ctx):
        if str(ctx.guild.id) in self.server_config:
            return
        else:
            self.server_config[str(ctx.guild.id)] = {"lb_default": 25,
                                                     "lb_max": 100,
                                                     "roles_setup": False,
                                                     "role_signup_message": None,
                                                     "require_setup_permissions": False,
                                                     "guild_admin_is_bot_admin": True,
                                                     "bot_guild_admins": [],
                                                     "prefix": None,
                                                     "bot_guild_moderators": [],
                                                     "games_is_whitelist": False,
                                                     "games": [],
                                                     "delete_inactive": True,
                                                     "delete_time_mins": 20,
                                                     "delete_msgs_in_scrim": True,
                                                     "ping_game_role": False,
                                                     "ping_cooldown_seconds": 120}


def setup(client):
    client.add_cog(UtilitiesCog(client))