#################################################################################
##
##                          scrimbot main module
##                              dev 1.1.0
##
#################################################################################

import discord
from discord.ext import tasks, commands

import scrim_methods
import elo_methods
import main_methods
import checks

import logging
import os

#setup client

client = commands.Bot(command_prefix = main_methods.get_prefix)
client.remove_command("help")

#setup logging

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='scrim_bot.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

for extension in main_methods.get_cogs():
    client.load_extension(extension)
    print(f"Using cog '{extension[5:]}'")

@client.event
async def on_ready():
    scrim_methods.Scrim.setup_instances(client)
    elo_methods.Game.get_games(main_methods.get_game_config(), on_startup=True)
    print(f"Bot is ready.\nRunning in {os.getcwd()}.\nCurrent admins: {' '.join(list(map(str, main_methods.get_configs()['admins'])))}")
 
#################################################################################
###################################--TOKEN--#####################################
#################################################################################

client.run(main_methods.get_configs()["key"])

#################################################################################
###########--Eetu "EddieTheCubeHead" Asikainen, all rights reserved--############
#################################################################################