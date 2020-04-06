import discord
from discord.ext import commands, tasks

import elo_methods
import scrim_methods
import main_methods
import checks

class EloCog(commands.Cog):
    def __init__(self, client):
        self.client = client

###n#############################################################################
##
##                a command to set an elo-ranking for a player
##
#################################################################################

    @commands.command()
    @commands.guild_only()
    @checks.bot_admin_local()
    async def elo(self, ctx, user_name, init_game, elo):
        if 0 > int(elo) or int(elo) > 4000:
            return await scrim_methods.temporary_feedback(ctx, "Please specify a value between 1 and 4000")
        elif ctx.message.author.guild_permissions.administrator == False and ctx.message.author.id != "162882518381494272":
            return await scrim_methods.temporary_feedback(ctx, "You need admin permissions to do that.")
        for member in ctx.message.guild.members:
            if member.display_name == user_name:
                for game in elo_methods.Game.instances:
                    if init_game in game.alias['alias']:
                        if game.addelo(member.id, elo):
                            return await scrim_methods.temporary_feedback(ctx, f"Succesfully added elo statistics for {user_name}.")
                        else:
                            return await scrim_methods.temporary_feedback(ctx, f"{user_name} already has elo statistics.")
        else:
            return await scrim_methods.temporary_feedback(ctx, f"Couldn't find member {user_name}.")

    @elo.error
    async def elo_error(self, ctx, error):
        if isinstance(error, checks.NotBotAdminLocal):
            return await scrim_methods.temporary_feedback(ctx, error)

#################################################################################
##
##     a command to display leaderboard of a given statistic in a given game
##
#################################################################################

    @commands.command(aliases=['lb','scoreboard','sb'])
    @commands.guild_only()
    async def leaderboard(self, ctx, stat_game=None, stat="elo", length=None):
        if not stat_game:
            return await scrim_methods.temporary_feedback(ctx, "Please specify a game. Type '/help games' for a list of all supported games.")

        if length:
            try:
                length = int(length)
            except:
                return await scrim_methods.temporary_feedback(ctx, "Please specify length as a whole number.")
        else:
            try:
                length = int(stat)
                stat = "elo"
            except:
                pass

        for game in elo_methods.Game.instances:
            if stat_game in game.alias['alias']:
                stat_game = game
                break
        else:
            return await scrim_methods.temporary_feedback(ctx, f"Couldn't find the game '{stat_game}'. Type '/help games' for a list of all supported games.")

        leaderboard = {}

        if not length:
            try:
                length = main_methods.get_server_configs()[str(ctx.message.guild.id)]["lb_default"]
            except:
                length = 25

        try:
            max = main_methods.get_server_configs()[str(ctx.message.guild.id)]["lb_max"]
        except:
            max = 100

        if stat in ("elo", "wins", "losses"):


            for player_id in game.players:
                for member in ctx.message.guild.members:
                    if str(member.id) == player_id:
                        leaderboard[member.display_name] = int(game.players[player_id][stat])
                        break

        elif stat in ("winloss"):

            for player_id in game.players:
                for member in ctx.message.guild.members:
                    if str(member.id) == player_id:
                        if game.players[player_id]['losses'] > 0:
                            leaderboard[member.display_name] = float(round(game.players[player_id]['wins']/(game.players[player_id]['losses']+game.players[player_id]['wins'])*100,2))
                            break
                        elif game.players[player_id]['wins'] > 0:
                            leaderboard[member.display_name] = 100
                            break

        elif stat in ("games"):

            for player_id in game.players:
                for member in ctx.message.guild.members:
                    if str(member.id) == player_id:
                        leaderboard[member.display_name] = int(game.players[player_id]['wins']+game.players[player_id]['losses'])
                        break
                

        elif stat in ("plusminus", "+-"):

            for player_id in game.players:
                for member in ctx.message.guild.members:
                    if str(member.id) == player_id:
                        leaderboard[member.display_name] = int(game.players[player_id]['wins']-game.players[player_id]['losses'])

        else:
            return await scrim_methods.temporary_feedback(ctx, f"Couldn't find the stat '{stat}'. Type '/help leaderboard' for help.")

        embedprint = ""
        counter = 0

        #sort the leaderboard
        for key, value in sorted(leaderboard.items(), key=lambda name: name[1], reverse=True):
            embedprint += (f"{key}: {value}")
            if stat in ("winloss"):
                embedprint += "%\n"
            else:
                embedprint += "\n"

            counter += 1
            if (length and length <= counter) or (max and max <= counter):
                break


        lb = discord.Embed(color=stat_game.color)
        lb.set_author(name=f"{stat_game.dispname} leaderboard", icon_url=f"{stat_game.icon}")
        lb.add_field(name=f"Sorted by {stat}", value=embedprint)
    
        await ctx.send(embed=lb)
        await ctx.message.delete()


def setup(client):
    client.add_cog(EloCog(client))
