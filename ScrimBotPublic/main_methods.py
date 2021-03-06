import json
import os

import scrim_methods

#################################################################################
##
##Some general methods. Used to be more closely related to the main-file. Will
##most probably be renamed once I get enough energy to think of a good name.
##
#################################################################################

def get_configs():

    """Gets the config dictionary, from the file 'config'."""

    with open(".config.json", "r") as config_file:
        configs = json.load(config_file)

    return configs

def get_game_config():

    """Gets the game dictionary, from the file '.games'."""

    with open(".games.json", "r") as game_file:
        games = json.load(game_file)

    return games

def get_cogs():

    """Get all cogs associated with the bot as a list of file locations."""

    cog_files = []

    for cog in os.listdir("cogs"):
        if cog[-3:] == ".py":
            cog_files.append("cogs."+cog[:-3])

    return cog_files

def get_server_configs():

    """Get config files for all servers. Returns a dict of the configs."""

    with open(".servers.json", "r") as server_file:
        config_dict = json.load(server_file)

    return config_dict

def save_server_configs(config : dict):

    """Saves the given dict as the bot's config file for servers."""

    with open(".servers.json", "w") as server_file:
        json.dump(config, server_file)

    for scrim in scrim_methods.Scrim.instances:
        scrim.update_server()

async def get_prefix(bot, ctx_msg):

    """The prefix-getter of the bot. Returns '/' by default or the guild specific prefix if a guild has one"""

    servers = get_server_configs()
    if ctx_msg.guild and str(ctx_msg.guild.id) in servers:
        return servers[str(ctx_msg.guild.id)]["prefix"] or "/"
    return "/"

def get_cooldown(ctx):
    server_configs = get_server_configs()
    if str(ctx.guild.id) in server_configs:
        return server_configs[str(ctx.guild.id)]["ping_cooldown_seconds"]
    return 120
