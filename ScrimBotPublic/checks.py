import discord
from discord.ext import commands, tasks

import main_methods
import scrim_methods


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
    async def predicate(ctx):
        config = main_methods.get_configs()
        if str(ctx.author.id) not in config["admins"]:
            raise NotBotAdminGlobal("This command requires you to have global bot admin permissions. If you feel like the command should require lesser permissions, or you should have global bot admin permissions, plese contact EddieTheCubeHead.")
        return True
    return commands.check(predicate)

def bot_admin_local():
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
    async def predicate(ctx):
        if ctx.message.author.guild_permissions.administrator:
            return True
        raise NotServerAdmin("This command requires you to have server admin permissions.")
    return commands.check(predicate)

def scrim_master():
    async def predicate(ctx):
        scrim = await scrim_methods.get_scrim(ctx)
        if ctx.message.author != scrim.master:
            raise NotScrimMaster("Only the person who set up the scrim or is a bot admin can manage it.")
        return True
    return commands.check(predicate)

def settings_eligible():
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