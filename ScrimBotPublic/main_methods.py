import json
import os

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
