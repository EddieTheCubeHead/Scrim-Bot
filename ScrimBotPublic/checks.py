import discord
from discord.ext import commands, tasks

import main_methods
import scrim_methods

#################################################################################
##
##This module houses all the different custom checks the bot utilizes, as well as
##the custom errors the checks raise. Might see a small rewrite as I learn more
##about how checks and error handling work and what are the best practices to use
##with them.
##
#################################################################################

# all unique errors: might condense these into less errors when I get a
# better understanding on the whole checks-system and error handling with
# the API
class InadequatePermissions(commands.CheckFailure):
    pass

class NotBotAdminGlobal(commands.CheckFailure):
    pass

class NotBotAdminLocal(commands.CheckFailure):
    pass

class NotServerAdmin(commands.CheckFailure):
    pass

class NotScrimMaster(commands.CheckFailure):
    pass

class NotSettingsEligible(commands.CheckFailure):
    pass

def scrim_eligible():
    """Check if the user has permissions to setup scrims on this server."""
    async def predicate(ctx):
        server_config = main_methods.get_server_configs()
        if str(ctx.guild.id) in server_config:
            if (server_config[str(ctx.guild.id)]["require_setup_permissions"] and
               (ctx.author.id not in server_config[str(ctx.guild.id)]["bot_guild_moderators"] and
               ctx.author.id not in server_config[str(ctx.guild.id)]["bot_guild_admins"] and
               not ctx.author.guild_permissions.administrator)):
                raise InadequatePermissions("This server requires special permissions for scrim management. Please contact the server owner if you feel like you should be able to manage scrims on the server.")
        return True
    return commands.check(predicate)

def bot_admin_global():
    """Check if the user is a global bot admin."""
    async def predicate(ctx):
        config = main_methods.get_configs()
        if str(ctx.author.id) not in config["admins"]:
            raise NotBotAdminGlobal("This command requires you to have global bot admin permissions. If you feel like the command should require lesser permissions, or you should have global bot admin permissions, plese contact EddieTheCubeHead.")
        return True
    return commands.check(predicate)

def bot_admin_local():
    """Check if the user is a local bot admin."""
    async def predicate(ctx):
        server_config = main_methods.get_server_configs()
        config = main_methods.get_configs()
        if str(ctx.guild.id) in server_config:
            if (ctx.author.id in server_config[str(ctx.guild.id)]["bot_guild_admins"] or
                server_config[str(ctx.guild.id)]["guild_admin_is_bot_admin"] and  ctx.message.author.guild_permissions.administrator or
                ctx.message.author.id == ctx.guild.owner.id):
                return True
        raise NotBotAdminLocal("This command requires you to have bot admin permissions on this server. If you feel like you should have the permissions, please contact the server owner.")
    return commands.check(predicate)

def guild_admin():
    """Check if the user has admin permissions on the server."""
    async def predicate(ctx):
        if ctx.message.author.guild_permissions.administrator:
            return True
        raise NotServerAdmin("This command requires you to have server admin permissions.")
    return commands.check(predicate)

def scrim_master():
    """Check if the user is the person who setup the scrim in ctx."""
    async def predicate(ctx):
        scrim = await scrim_methods.get_scrim(ctx)
        if ctx.message.author != scrim.master:
            raise NotScrimMaster("Only the person who set up the scrim or is a bot admin can manage it.")
        return True
    return commands.check(predicate)

def settings_eligible():
    """Check if the user has permissions to manage settings on the server."""
    async def predicate(ctx):
        server_config = main_methods.get_server_configs()
        if str(ctx.guild.id) in server_config: 
            if (server_config[str(ctx.guild.id)]["guild_admin_is_bot_admin"] and
                (ctx.message.author.guild_permissions.administrator or
                ctx.message.author.id in server_config[str(ctx.guild.id)]["bot_guild_admins"])):
                return True
            elif ctx.message.author.id in server_config[str(ctx.guild.id)]["bot_guild_admins"]:
                return True
        elif ctx.message.author.guild_permissions.administrator:
            return True
        raise NotSettingsEligible("You do not have required permissions to manage server settings.")
    return commands.check(predicate)