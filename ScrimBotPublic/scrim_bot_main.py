#################################################################################
##
##                          scrimbot main module
##                              beta 0.9.8
##
#################################################################################

import discord
from discord.ext import tasks, commands

import scrim_methods
import elo_methods
import main_methods

import discord
import logging
import os

#setup client

client = commands.Bot(command_prefix = "/")
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

@client.command()
async def update(ctx):
    if ctx.message.author.id not in main_methods.get_configs()["admins"]:
        try:
            if ctx.message.author.guild_permissions.administrator == False :
                return await scrim_methods.temporary_feedback(ctx, "You need admin permissions to do that.")
        except:
            pass
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


 
#################################################################################
###################################--TOKEN--#####################################
#################################################################################

client.run(main_methods.get_configs()["key"])

#################################################################################
###########--Eetu "EddieTheCubeHead" Asikainen, all rights reserved--############
#################################################################################