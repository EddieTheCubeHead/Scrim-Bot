import discord
from discord.ext import commands, tasks


import elo_methods
import scrim_methods
import main_methods

import os
import json
import itertools
import random
import asyncio
import checks

#################################################################################
##
##The most important cog of the bot. Houses the commands and listeners that deal
##with setting up and managing scrims.
##
#################################################################################

class ScrimCog(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.tick_active_scrims.start()
        self.delete_idle_scrims.start()

#################################################################################
##
##The main user interface consists of reacting to messages to join scrims and teams.
##
##These two listeners check for reactions the main message of a scrim instances
##and perform needed actions for the player list.
##
#################################################################################

    @commands.Cog.listener()
    async def on_reaction_add(self, react, user):

        current = await scrim_methods.get_scrim(react)
        if not current:
            return None

        if user.bot == True or react.message.id != current.message.id:
            return None

#################################################################################
##
##                              joining the scrim
##
#################################################################################

        if current.phase == "setup":

            # joining as a player

            if react.emoji == "\U0001F3AE": #video game controller

                if user in current.participators:
                    await react.remove(user)
                    return None
                else:
                    current.add_user(user)

                if len(current.players) < current.game.playerreq:

                    current.embed.set_field_at(0, name="**Players**", value=current.get_formatted_members("players"), inline=True)
                    current.embed.description = f"Looking for players. Need {current.game.playerreq-len(current.players)} more."
                    await current.message.edit(embed=current.embed)
                    return None

                else:

                    current.embed.set_field_at(0, name="**Players** _(full)_", value=current.get_formatted_members("players"), inline=True)
                    current.embed.description = f"{current.game.playerreq} players present. Type '/lock' to lock the current players."
                    await current.message.edit(embed=current.embed)
                    return None

            #joining as a spectator
        
            elif react.emoji == "\U0001F441": #eye

                if user in current.participators:
                    await react.remove(user)
                    return None
                else:
                    current.add_user(user, "spectators")

                current.embed.set_field_at(1, name="**Spectators**", value=current.get_formatted_members("spectators"), inline=True)
                await current.message.edit(embed=current.embed)

#################################################################################
##
##                                 joining teams
##
#################################################################################
            
        elif current.phase == "locked":

            if react.emoji == "1\u20E3": #keycap 1

                if user not in current.players or len(current.team1) >= current.game.playerreq/2:
                    await react.remove(user)
                    return None

                current.move_to(user, "team1")

                current.embed.set_field_at(0, name="**Unassigned players**", value=current.get_formatted_members("players"), inline=True)
                if len(current.team1) == current.game.playerreq/2:
                    current.embed.set_field_at(3, name="**Team 1** _(full)_", value=current.get_formatted_members("team1"), inline=True)
                else:
                    current.embed.set_field_at(3, name="**Team 1**", value=current.get_formatted_members("team1"), inline=True)
                await current.message.edit(embed=current.embed)

            elif react.emoji == "2\u20E3": #keycap 2

                if user not in current.players or len(current.team2) == current.game.playerreq/2:
                    await react.remove(user)
                    return None

                current.move_to(user, "team2")

                current.embed.set_field_at(0, name="**Unassigned players**", value=current.get_formatted_members("players"), inline=True)
                if len(current.team2) == current.game.playerreq/2:
                    current.embed.set_field_at(4, name="**Team 2** _(full)_", value=current.get_formatted_members("team2"), inline=True)
                else:
                    current.embed.set_field_at(4, name="**Team 2**", value=current.get_formatted_members("team2"), inline=True)
                await current.message.edit(embed=current.embed)

            #update embed for further instructions if both teams are full
            if len(current.team1) == len(current.team2) == current.game.playerreq/2:
                current.embed.description = "The teams are ready. Write '/start' to start the scrim."
                await current.message.edit(embed=current.embed)
            
#################################################################################
##
##                              choosing captains
##
#################################################################################

        elif current.phase == "caps":

            if react.emoji == "\U0001F451": #crown emoji for captains

                if user not in current.players or len(current.caps) > 2:
                    await react.remove(user)
                    return None

                else:
                    current.move_to(user, "caps")

                    current.embed.set_field_at(0, name="**Unassigned players**", value=current.get_formatted_members("players"), inline=True)
                    current.embed.set_field_at(3, name="**Team 1**", value=current.get_formatted_members("team1"), inline=True)
                    current.embed.set_field_at(4, name="**Team 2**", value=current.get_formatted_members("team2"), inline=True)
                    await current.message.edit(embed=current.embed)

        else:
            return None

#################################################################################
##
##Second half of handling the reaction UI: removing players from scrim/teams/etc.
##
#################################################################################

    @commands.Cog.listener()
    async def on_reaction_remove(self, react, user):

        current = await scrim_methods.get_scrim(react)
        if not current:
            return None

        if current.phase == "no scrim":
            return None
        if user.bot == True or react.message.id != current.message.id:
            return None

#################################################################################
##
##                              leaving the scrim
##
#################################################################################

        if current.phase == "setup":

            #leaving players

            if react.emoji == "\U0001F3AE": #video game controller

                if user not in current.players:
                    return None

                current.remove_user(user)

                if len(current.players) >= current.game.playerreq:
                    current.embed.set_field_at(0, name="**Players** _(full)_", value=current.get_formatted_members("players"), inline=True)
                    current.embed.description = f"{current.game.playerreq} players present. Type '/lock' to lock the current players."
                else:
                    current.embed.set_field_at(0, name="**Players**", value=current.get_formatted_members("players"), inline=True)
                    if len(current.players) > 0:
                        current.embed.description = f"Looking for players. Need {current.game.playerreq-len(current.players)} more."
                    else:
                        current.embed.description = "Looking for players."  
                await current.message.edit(embed=current.embed)

            #leaving spectators

            elif react.emoji == "\U0001F441": #eye

                if user not in current.spectators:
                    return None

                current.remove_user(user)

                current.embed.set_field_at(1, name="**Spectators**", value=current.get_formatted_members("spectators"), inline=True)
                await current.message.edit(embed=current.embed)

#################################################################################
##
##                              leaving a team
##
#################################################################################

        elif current.phase == "locked":

            #leaving team 1

            if react.emoji == "1\u20E3": #keycap 1

                if user not in current.team1:
                    return None

                current.move_to(user)

                current.embed.set_field_at(0, name="**Unassigned players**", value=current.get_formatted_members("players"), inline=True)
                current.embed.set_field_at(3, name="**Team 1**", value=current.get_formatted_members("team1"), inline=True)
                await current.message.edit(embed=current.embed)
 
            #leaving team 2

            elif react.emoji == "2\u20E3":

                if user not in current.team2:
                    return None

                current.move_to(user)

                current.embed.set_field_at(0, name="**Unassigned players**", value=current.get_formatted_members("players"), inline=True)
                current.embed.set_field_at(4, name="**Team 2**", value=current.get_formatted_members("team2"), inline=True)
                await current.message.edit(embed=current.embed)
            
            #if teams were full before removing a player, update embed
            if current.embed.description == "The teams are ready. Write '/start' to start the scrim.":
                current.embed.description = "Players locked. Use reactions for manual team selection or type '**/teams** _random/balanced/balancedrandom_' to define teams automatically. (Defaults to random)"
                await current.message.edit(embed=current.embed)
            
#################################################################################
##
##                              leaving captains
##
#################################################################################

        elif current.phase == "caps":

            if react.emoji == "\U0001F451": #crown
            
                if user not in current.caps:
                    return None

                current.move_to(user)
                current.embed.set_field_at(0, name="**Unassigned players**", value=current.get_formatted_members("players"), inline=True)
                current.embed.set_field_at(3, name="**Team 1**", value=current.get_formatted_members("team1"), inline=True)
                current.embed.set_field_at(4, name="**Team 2**", value=current.get_formatted_members("team2"), inline=True)
                await current.message.edit(embed=current.embed)
            
#################################################################################
##
##                      Command for setting up a scrim
##
#################################################################################
        
    @commands.command(aliases=['s'])
    @commands.guild_only()
    @checks.scrim_eligible()
    async def scrim(self, ctx, game=None, dont_delete=None):

        current = await scrim_methods.get_scrim(ctx)
        if not current:
            return None

        elif not game:
            return await scrim_methods.temporary_feedback(ctx, "Please specify a game. Type '/help games' for a list of all supported games.")
        
        elif current.phase != "no scrim":
            return await scrim_methods.temporary_feedback(ctx, "Cannot setup more than one scrim at a time.")

        for team_game in elo_methods.Team.instances:
            if game in team_game.alias['alias']:
                if current.server:
                    if (current.server["games_is_whitelist"] == 0) and (team_game.dispname in current.server["games"]):
                        return await scrim_methods.temporary_feedback(ctx, f"The game '{game}' is not allowed on this server.")
                    elif (current.server["games_is_whitelist"] == 1) and (team_game.dispname not in current.server["games"]):
                        return await scrim_methods.temporary_feedback(ctx, f"The game '{game}' is not allowed on this server.")
                game = team_game
                break

        else:
            return await scrim_methods.temporary_feedback(ctx, f"Couldn't find the game '{game}'. Type '/help games' for a list of all supported games.")

        await current.reset()

        if dont_delete:
            current.dont_delete = True

        current.game = game
        current.get_options()
        current.phase = "setup"
        current.master = ctx.message.author
        current.embed = discord.Embed(title="Status", description="Looking for players.", color=current.game.color)
        current.embed.set_author(name=f"{current.game.dispname} scrim", icon_url=f"{current.game.icon}")
        current.embed.add_field(name="**Players**", value="_empty_", inline=True)
        current.embed.add_field(name="**Spectators**", value="_empty_", inline=True)
        current.embed.set_footer(text=f"To join players react \U0001F3AE To join spectators react \U0001F441")
        current.message = await ctx.send(embed=current.embed)
        await ctx.message.delete()
        await current.message.add_reaction(emoji = "\U0001F3AE")    #video game controller
        await current.message.add_reaction(emoji = "\U0001F441")    #eye

        # ping the correct role, if the setting is enabled
        if current.server:
            if current.server["ping_game_role"]:
                for role in ctx.guild.roles:
                    if role.name == current.game.dispname:
                        ping = role.mention
                        return await scrim_methods.temporary_feedback(ctx, ping, delay=180)
                return await scrim_methods.temporary_feedback(ctx, "Couldn't find a role for the game of the current scrim.")

    @scrim.error
    async def scrim_error(self, ctx, error):
        if isinstance(error, checks.InadequatePermissions):
            return await scrim_methods.temporary_feedback(ctx, error)

#################################################################################
##
##             Command for pinging the role of the scrim's game
##
#################################################################################

    @commands.command()
    @commands.cooldown(1, 180, commands.BucketType.channel)
    @commands.guild_only()
    async def ping(self, ctx):
        current = await scrim_methods.get_scrim(ctx)
        if not current:
            return None

        if current.server:
            print(current.server)

        elif not current.server or not current.server["roles_setup"]:
            return await scrim_methods.temporary_feedback(ctx, "Pinging for players is only supported on servers that have setup the role system.")

        elif current.phase != "setup":
            return await scrim_methods.temporary_feedback(ctx, "You can only ping users if there is a scrim currently looking for players.")

        for role in ctx.guild.roles:
            if role.name == current.game.dispname:
                ping = role.mention
                return await scrim_methods.temporary_feedback(ctx, ping, delay=180)
        return await scrim_methods.temporary_feedback(ctx, "Couldn't find a role for the game of the current scrim.")

    @ping.error
    async def ping_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            return await scrim_methods.temporary_feedback(ctx, "Command on cooldown.")

#################################################################################
##
##                   Command for locking a scrim's players
##
#################################################################################

    @commands.command(aliases=['l'])
    @commands.guild_only()
    @checks.scrim_master()
    async def lock(self, ctx):

        current = await scrim_methods.get_scrim(ctx)
        if not current:
            return None

        if current.phase != "setup":
            return await scrim_methods.temporary_feedback(ctx, "You cannot do that now.")

        if current.message == None or len(current.players) < current.game.playerreq:
            if current.message == None:
                return await scrim_methods.temporary_feedback(ctx, "No scrim to lock.")
            else:
                return await scrim_methods.temporary_feedback(ctx, f"You don't have enough players to lock the scrim. {current.game.playerreq-len(current.players)} more needed.")

        else:
            current.phase = "locked"
            current.embed.description = "Players locked. Use reactions for manual team selection or type '**/teams** _random/balanced/balancedrandom_' to define teams automatically."
            current.players = current.players[:current.game.playerreq] #remove extra players
            current.player_backup = set(current.players)

            await current.message.clear_reactions()   
            await current.message.add_reaction("1\u20E3")   #keycap 1
            await current.message.add_reaction("2\u20E3")   #keycap 2

            current.embed.set_field_at(0, name="**Unassigned players**", value=current.get_formatted_members("players"), inline=True)
            current.embed.add_field(name="------------------------------------------------------------", value="------------------------------------------------------------", inline=False)
            current.embed.add_field(name="**Team 1**", value="_empty_", inline=True)
            current.embed.add_field(name="**Team 2**", value="_empty_", inline=True)
            current.embed.set_footer(text="React 1️⃣ to join team one or 2️⃣ to join team two.")
            await current.message.edit(embed=current.embed)
            await ctx.message.delete()

    @lock.error
    async def lock_error(self, ctx, error):
        if isinstance(error, checks.NotScrimMaster):
            return await scrim_methods.temporary_feedback(ctx, error)

#################################################################################
##
##teams -group let's participators automate assignment of team baced on a criteria
##
#################################################################################
        
    @commands.group(aliases=['t','team'])
    @commands.guild_only()
    @checks.scrim_master()
    async def teams(self, ctx):

        if ctx.invoked_subcommand is None:
            current = await scrim_methods.get_scrim(ctx)
            if not current:
                return None
            return await scrim_methods.temporary_feedback(ctx, "Invalid subcommand for command 'teams'. Please  type '/help teams' for a list of commands.")

    @teams.error
    async def teams_error(self, ctx, error):
        if isinstance(error, checks.NotScrimMaster):
            return await scrim_methods.temporary_feedback(ctx, error)
        
#################################################################################
##
##                       random assigns teams by random
##
#################################################################################
    
    @teams.command(aliases=['random', 'r', 's'])
    async def shuffle(self, ctx):

        current = await scrim_methods.get_scrim(ctx)
        if not current:
            return None

        if current.phase not in ["locked", "caps", "pickup1", "pickup2"]:
            return await scrim_methods.temporary_feedback(ctx, "Cannot do that right now.")

        current.clear_teams()

        for p in current.players:

            if (bool(random.getrandbits(1)) == True and len(current.team1) < current.game.playerreq/2) or len(current.team2) == current.game.playerreq/2:
                current.team1.append(p)
            else:
                current.team2.append(p)

        current.players.clear()

        current.embed.set_field_at(0, name="**Unassigned players**", value="_empty_", inline=True)
        current.embed.set_field_at(3, name="**Team 1** _(full)_", value=current.get_formatted_members("team1"), inline=True)
        current.embed.set_field_at(4, name="**Team 2** _(full)_", value=current.get_formatted_members("team2"), inline=True)
        current.embed.description="The teams are ready. Write '/start' to start the scrim."
        current.embed.set_footer(text="Type '/teams clear' to clear teams")
        await current.message.edit(embed=current.embed)
        await current.message.clear_reactions()
        await ctx.message.delete()

#################################################################################
##
##pickup let's players assign two caps by criteria and let captains pick players
##
#################################################################################

    @teams.command(aliases=['pug'])
    async def pickup(self, ctx, cap="balanced", order="fair"):

        current = await scrim_methods.get_scrim(ctx)
        if not current:
            return None

        if current.phase != "locked":
            return await scrim_methods.temporary_feedback(ctx, "You cannot do that now.")

        if cap not in ("random", "choose", "balanced"):
            return await scrim_methods.temporary_feedback(ctx, "Please specify the assignment of captains as 'random', 'choose' or 'balanced'. Type '/help pickup' for more help.")

        if order != "fair" and order != "classic":
            return await scrim_methods.temporary_feedback(ctx, "Please specify the picking order as either 'fair' or 'classic'. Type '/help pickup' for more help.")
        
        current.clear_teams()


        #assigning captains by random
    
        if cap == "random":

            for i in range(2):
                c = random.choice(current.players)
                current.caps.append(c)
                current.players.remove(c)

            current.team1.append(current.caps[0])
            current.team2.append(current.caps[1])

            await current.message.clear_reactions()
            current.phase = "pickup1"
            current.embed.description = f"Picking underway. Team 1 starts. {len(current.players)} players left to pick."
            current.embed.set_footer(text="Captains, use '/pick @user' to pick players on your turn.")


        #assigning captains by elo

        elif cap == "balanced":

            await current.set_missing_elos(ctx)

            highest_elo = 0
            second_elo = 0

            for player in current.players:

                if current.game.players[str(player.id)]['elo'] > highest_elo:
                    current.caps.insert(0, player)
                    second_elo = highest_elo
                    highest_elo = current.game.players[str(player.id)]['elo']
                elif current.game.players[str(player.id)]['elo'] > second_elo:
                    current.caps.insert(1, player)
                    second_elo = current.game.players[str(player.id)]['elo']

                if len(current.caps) > 2:
                    current.caps.pop()

            current.team1.append(current.caps[1])
            current.team2.append(current.caps[0])
            current.players.remove(current.caps[1])
            current.players.remove(current.caps[0])

            await current.message.clear_reactions()
            current.phase = "pickup1"
            current.embed.description = f"Picking underway. Team 1 starts. {len(current.players)} players left to pick."
            current.embed.set_footer(text="Captains, use '/pick @user' to pick players on your turn.")


        #letting players choose captains
        
        elif cap == "choose":
        
            current.phase = "caps"
            current.embed.description = "Setting up a pick-up game. Waiting for players to choose captains."
            current.embed.set_footer(text="React \U0001F451 to become a captain.")
            await current.message.clear_reactions()
            await current.message.add_reaction("\U0001F451")
        
        current.embed.set_field_at(0, name="**Unassigned players**", value=current.get_formatted_members("players"), inline=True)
        current.embed.set_field_at(3, name="**Team 1**", value=current.get_formatted_members("team1"), inline=True)
        current.embed.set_field_at(4, name="**Team 2**", value=current.get_formatted_members("team2"), inline=True)
        await current.message.edit(embed=current.embed)
        await ctx.message.delete()

        #wait until both teams have captains
        while len(current.team1) == 0 or len(current.team2) == 0:
            await asyncio.sleep(2)
        
        if current.phase == "caps":
            current.phase = "pickup1"
            current.embed.description = f"Picking underway. Team 1 starts. {len(current.players)} players left to pick."
            current.embed.set_footer(text="Captains, use '/pick @user' to pick players on your turn.")
            await current.message.clear_reactions()
            await current.message.edit(embed=current.embed)
        
        #run a loop assigning picking turns for captains
        while len(current.players) != 0 and order == "fair":
            await asyncio.sleep(0.2)
            if len(current.team1) > len(current.team2):
                if current.phase == "pickup1":
                    current.phase = "pickup2"
                    current.embed.description = f"Picking underway. Team 2 is picking. {len(current.players)} players left to pick."

            elif len(current.team2) > len(current.team1):
                if current.phase == "pickup2":
                    current.phase = "pickup1"
                    current.embed.description = f"Picking underway. Team 1 is picking. {len(current.players)} players left to pick."

            elif current.phase == "pickup1":
                current.embed.description = f"Picking underway. Team 1 is picking. {len(current.players)} players left to pick."

            else:
                current.embed.description = f"Picking underway. Team 2 is picking. {len(current.players)} players left to pick."

            await current.message.edit(embed=current.embed)

        while len(current.players) != 0 and order == "classic":
            await asyncio.sleep(0.5)
            if len(current.team1) > len(current.team2):
                current.phase = "pickup2"
                current.embed.description = f"Picking underway. Team 2 is picking. {len(current.players)} players left to pick."

            else:
                current.phase = "pickup1"
                current.embed.description = f"Picking underway. Team 1 is picking. {len(current.players)} players left to pick."

            await current.message.edit(embed=current.embed)
        
        current.embed.set_field_at(0, name="**Unassigned players**", value="_empty_", inline=True)
        current.embed.set_field_at(3, name="**Team 1** _(full)_", value=current.get_formatted_members("team1"), inline=True)
        current.embed.set_field_at(4, name="**Team 2** _(full)_", value=current.get_formatted_members("team2"), inline=True)
        current.embed.description = "The teams are ready. Write '/start' to start the scrim."
        current.embed.set_footer(text="Type '/teams clear' to clear teams")
        await current.message.edit(embed=current.embed)

#################################################################################
##
##     assign the most balanced teams possible based on players' elo-ratings
##
#################################################################################

    @teams.command(aliases=['b'])
    async def balanced(self, ctx):
    
        current = await scrim_methods.get_scrim(ctx)
        if not current:
            return None

        if current.phase not in ["locked", "caps", "pickup1", "pickup2"]:
            return await scrim_methods.temporary_feedback(ctx, "You cannot do that now.")

        current.clear_teams()
        if not await current.set_missing_elos(ctx):
            return await scrim_methods.temporary_feedback(ctx, "Error when assigning missing elo values to players.")
    

        #get a list of ALL possible team combinations for team 1
        teamcomps = list(itertools.combinations(current.players, int(current.game.playerreq/2)))
        closest_winprob = 2
        dummy_team1 = []
        dummy_team2 = []
        # balanced and balancedrandom have been constantly making problems when
        # encountering a bug. Dummies aim to fix the bot breaking completely if
        # the function encounters a problem.
    
        for team in teamcomps:

            #combinations returns tuples. For ease of use, this creates a list from a tuple
            tester_team = []
            for player in team:
                tester_team.append(player)

            dummy_team2 = list(set(current.players).difference(tester_team))

            winprob = current.game.winprob(tester_team, dummy_team2)

            if abs(winprob-0.5) < abs(closest_winprob-0.5):
                closest_winprob = winprob

                dummy_team1.clear()
                dummy_team1 = tester_team
                        
        dummy_team2 = list(set(current.players).difference(dummy_team1))

        if not (len(dummy_team1) == len(dummy_team2) and set(dummy_team1+dummy_team2) == current.player_backup):
            current.clear_teams()
            return await scrim_methods.temporary_feedback(ctx, "Unexpected error when assigning teams.")

        current.team1 = dummy_team1
        current.team2 = dummy_team2
    
        current.players.clear()
        current.embed.set_field_at(0, name="**Unassigned players**", value="_empty_", inline=True)
        current.embed.set_field_at(3, name="**Team 1** _(full)_", value=current.get_formatted_members("team1"), inline=True)
        current.embed.set_field_at(4, name="**Team 2** _(full)_", value=current.get_formatted_members("team2"), inline=True)
        current.embed.description = "The teams are ready. Write '/start' to start the scrim."
        current.embed.set_footer(text="Type '/teams clear' to clear teams")
        await current.message.edit(embed=current.embed)
        await current.message.clear_reactions()
        await ctx.message.delete()

#################################################################################
##
##       assign random, but balanced teams based on players' elo ratings.
##
#################################################################################

    @teams.command(aliases=['br','balancedrand','brand'])
    async def balancedrandom(self, ctx, threshold=5):

        current = await scrim_methods.get_scrim(ctx)
        if not current:
            return None

        if current.phase not in ["locked", "caps", "pickup1", "pickup2"]:
            return await scrim_methods.temporary_feedback(ctx, "You cannot do that now.")

        if not 0 < int(threshold) <= 50:
            return await scrim_methods.temporary_feedback(ctx, "Threshold out of limits. Please give a value between 1 and 50.")

        current.clear_teams()
        if not await current.set_missing_elos(ctx):
            return await scrim_methods.temporary_feedback(ctx, "Error when assigning missing elo values to players.")

        teamcomps = list(itertools.combinations(current.players, int(current.game.playerreq/2)))
        threshold /= 100
        candidates = []
        smallest_three = []
        values = []
        dummy_team1 = []
        dummy_team2 = []
        # balanced and balancedrandom have been constantly making problems when
        # encountering a bug. Dummies aim to fix the bot breaking completely if
        # the function encounters a problem.
    
        for team in teamcomps:
            tester_team = []
            for player in team:
                tester_team.append(player)
            dummy_team2 = list(set(current.players).difference(tester_team))

            winprob = current.game.winprob(tester_team, dummy_team2)

            if len(values) < 3:
                smallest_three.insert(0, tester_team)
            elif winprob <= values[2]:
                smallest_three.insert(2, tester_team)
                smallest_three.remove(smallest_three[3])

            values.append(winprob)
            values.sort()

            if abs(winprob-0.5) < threshold:
                candidates.append(tester_team)

        if len(candidates) >= len(smallest_three):
            dummy_team1 = random.choice(candidates)
        else:
            dummy_team1 = random.choice(smallest_three)
                        
        dummy_team2 = list(set(current.players).difference(dummy_team1))
        
        if not (len(dummy_team1) == len(dummy_team2) and set(dummy_team1+dummy_team2) == current.player_backup):
            current.clear_teams()
            return await scrim_methods.temporary_feedback(ctx, "Unexpected error when assigning teams.")

        current.team1 = dummy_team1
        current.team2 = dummy_team2

        current.players.clear()
        current.embed.set_field_at(0, name="**Unassigned players**", value="_empty_", inline=True)
        current.embed.set_field_at(3, name="**Team 1** _(full)_", value=current.get_formatted_members("team1"), inline=True)
        current.embed.set_field_at(4, name="**Team 2** _(full)_", value=current.get_formatted_members("team2"), inline=True)
        current.embed.description = "The teams are ready. Write '/start' to start the scrim."
        current.embed.set_footer(text="Type '/teams clear' to clear teams")
        await current.message.edit(embed=current.embed)
        await current.message.clear_reactions()
        await ctx.message.delete()


#################################################################################
##
##           a command to let captains pick players in a pickup game
##
#################################################################################

    @commands.command(aliases=['p'])
    @commands.guild_only()
    async def pick(self, ctx, user=None):

        current = await scrim_methods.get_scrim(ctx)
        if not current:
            return None

        elif current.phase != "pickup1" and current.phase != "pickup2":
            return await scrim_methods.temporary_feedback(ctx, "You cannot do that now.")

        elif ctx.message.author not in current.caps:
            return await scrim_methods.temporary_feedback(ctx, "You need to be a captain to pick players.")

        elif len(ctx.message.mentions) > 1 and user != "random":
            return await scrim_methods.temporary_feedback(ctx, "Please specify only one player.")

        elif len(ctx.message.mentions) < 1 and user != "random":
            return await scrim_methods.temporary_feedback(ctx, "Please specify a player.")
        
        elif user != "random" and ctx.message.mentions[0] not in current.players:
            return await scrim_methods.temporary_feedback(ctx, f"Didn't find player {ctx.message.mentions[0].display_name} in available players.")
    
        elif ctx.message.author in current.team1 and current.phase == "pickup1":
            if user == "random":
                random_player = random.choice(current.players)

                current.team1.append(random_player)
                current.players.remove(random_player)
            else:

                current.team1.append(ctx.message.mentions[0])
                current.players.remove(ctx.message.mentions[0])
                
        elif ctx.message.author in current.team2 and current.phase == "pickup2":
            if user == "random":
                p = random.choice(current.players)

                current.team2.append(p)
                current.players.remove(p)

            else:

                current.team2.append(ctx.message.mentions[0])
                current.players.remove(ctx.message.mentions[0])

        else:
            return await sm.temporary_feedback(ctx, "It's not your turn to pick!")

        current.embed.set_field_at(0, name="**Unassigned players**", value=current.get_formatted_members("players"), inline=True)
        current.embed.set_field_at(3, name="**Team 1**", value=current.get_formatted_members("team1"), inline=True)
        current.embed.set_field_at(4, name="**Team 2**", value=current.get_formatted_members("team2"), inline=True)
        await current.message.edit(embed=current.embed)
        await ctx.message.delete()

#################################################################################
##
##  a command that generates a win probability prediction for the current teams
##
#################################################################################

    @commands.command(aliases=['odds'])
    @commands.guild_only()
    async def predict(self, ctx):

        current = await scrim_methods.get_scrim(ctx)
        if not current:
            return None
    
        if current.phase not in ["locked", "caps", "pickup1", "pickup2", "underway"]:
            return await scrim_methods.temporary_feedback(ctx, "I need full teams to make a prediction.")
        
        elif len(current.team1) != current.game.playerreq/2 or len(current.team2) != current.game.playerreq/2:
            return await scrim_methods.temporary_feedback(ctx, "I need full teams to make a prediction.")

        else:
            winprob = current.game.winprob(current.team1, current.team2)
            if round(winprob ,2) == 0.50:
                return await scrim_methods.temporary_feedback(ctx, "I predict both teams having a 50% chance of winning.", delay = 20.0)

            elif winprob > 0.50:
                return await scrim_methods.temporary_feedback(ctx, f"I predict team 1 having a {round(winprob*100, 1)}% chance of winning.", delay = 20.0)

            elif winprob < 0.50:
                return await scrim_methods.temporary_feedback(ctx, f"I predict team 2 having a {round((1-winprob)*100, 1)}% chance of winning.", delay = 20.0)

#################################################################################
##
##                  a command to clear players from both teams
##
#################################################################################

    @teams.command(aliases=['c', 'empty', 'e'])
    async def clear(self, ctx):

        current = await scrim_methods.get_scrim(ctx)
        if not current:
            return None

        if current.phase not in ["locked", "caps", "pickup1", "pickup2"]:
            return await scrim_methods.temporary_feedback(ctx, "You cannot do that now.")

        current.clear_teams()
        current.phase = "locked"
        current.embed.description = "Players locked. Use reactions for manual team selection or type '**/teams** _random/balanced/balancedrandom_' to define teams automatically."
        current.embed.set_field_at(0, name="**Unassigned players**", value=current.get_formatted_members("players"), inline=True)
        current.embed.set_field_at(3, name="**Team 1**", value="_empty_", inline=True)
        current.embed.set_field_at(4, name="**Team 2**", value="_empty_", inline=True)
        current.embed.set_footer(text="React 1️⃣ to join team one or 2️⃣ to join team two.")
        await current.message.clear_reactions()
        await current.message.add_reaction("1\u20E3")   #keycap 1
        await current.message.add_reaction("2\u20E3")   #keycap 2
        await current.message.edit(embed=current.embed)
        await ctx.message.delete()

#################################################################################
##
##               a command to start a scrim if both teams are full
##
#################################################################################

    @commands.command()
    @commands.guild_only()
    @checks.scrim_master()
    async def start(self, ctx, voice="voice"):

        current = await scrim_methods.get_scrim(ctx)
        if not current:
            return None

        check = 0
    
        if (len(current.team1) or len(current.team2)) != current.game.playerreq/2:
            return await scrim_methods.temporary_feedback(ctx, "I need both teams to be full to start a scrim.")
           
        elif (current.phase not in ["locked", "caps", "pickup1", "pickup2"]):
            return await scrim_methods.temporary_feedback(ctx, "You cannot do that now.")

        if voice in ("voice", "withvoice", "v") and len(current.voice) >= 2:

            for p in current.team1:
                if p.voice == None:
                    break
                elif p.voice.channel:
                    if p.voice.channel.guild == ctx.message.guild:
                        pass
                    else:
                        break
                else:
                    break
                
            else:
                check += 1
                current.embed.description = "Scrim underway."
                footertemp = "Good luck, have fun! Declare the winner with '**/winner** _team1/team2_'"

            for p in current.team2:
                if p.voice == None:
                    break
                elif p.voice.channel:
                    if p.voice.channel.guild == ctx.message.guild:
                        pass
                    else:
                        break
                else:
                    break

            else:
                check += 1
                current.embed.description = "Scrim underway."
                footertemp = "Good luck, have fun! Declare the winner with '**/winner** _team1/team2_'"

            if check < 2:
            
                current.embed.description = "Starting scrim: waiting for all players to join voice channels."
                footertemp = "Players please join a voice channel to start the game."
                current.phase = "voice"
                check = 0

            current.embed.remove_field(0)
            current.embed.set_field_at(2, name="**Team 1**", value=current.get_formatted_members("team1"), inline=True)
            current.embed.set_field_at(3, name="**Team 2**", value=current.get_formatted_members("team2"), inline=True)
            current.embed.set_footer(text=footertemp)
            await current.message.edit(embed=current.embed)
            await ctx.message.delete()
            
            #wait for all players to be in a voice channel before moving players
            #to avoic errors
            while check < 2:
                check = 0
                await asyncio.sleep(2)
                for p in current.team1:
                    if p.voice == None:
                        break
                    elif p.voice.channel != None:
                        if p.voice.channel.guild == ctx.message.guild:
                            pass
                        else:
                            break
                    else:
                        break

                else:
                    check += 1
                
                for p in current.team2:
                    if p.voice == None:
                        break
                    elif p.voice.channel != None:
                        if p.voice.channel.guild == ctx.message.guild:
                            pass
                        else:
                            break
                    else:
                        break
                else:
                    check += 1
                    

 
            current.embed.description = "Scrim underway."
            footertemp = "Good luck, have fun! Declare the winner with '**/winner** _team1/team2_'"
            current.embed.set_footer(text=footertemp)
            await current.message.edit(embed=current.embed)
                
            current.phase = "underway"
            for player in current.team1:
                await player.move_to(current.voice[0], reason="Setting up a scrim.")

            for player in current.team2:
                await player.move_to(current.voice[1], reason="Setting up a scrim.")

            if len(current.voice) >= 3:
                for spectator in current.spectators:
                    if spectator.voice:
                        await spectator.move_to(current.voice[2], reason="Setting up a scrim.")
                

        elif voice in ("novoice", "no", "n") or len(current.voice) < 2:

            current.phase = "underway"
            current.embed.description = "Scrim underway."
            footertemp = "Good luck, have fun! Declare the winner with '**/winner** _team1/team2_'"
            current.embed.set_footer(text=footertemp)
            current.embed.remove_field(0)
            current.embed.set_field_at(2, name="**Team 1**", value=current.get_formatted_members("team1"), inline=True)
            current.embed.set_field_at(3, name="**Team 2**", value=current.get_formatted_members("team2"), inline=True)
            current.embed.set_footer(text=footertemp)
            await current.message.edit(embed=current.embed)
            await ctx.message.delete()
        
        else:
            return await scrim_methods.temporary_feedback(ctx, "Unknown value for voice (voice/novoice).")

    @start.error
    async def start_error(self, ctx, error):
        if isinstance(error, checks.NotScrimMaster):
            return await scrim_methods.temporary_feedback(ctx, error)
        
#################################################################################
##
##    a command to declare a winner and simultaneously update elo statistics
##
#################################################################################

    @commands.command(aliases=['victor', 'win', 'end', 'w', 'v', 'e'])
    @commands.guild_only()
    @checks.scrim_master()
    async def winner(self, ctx, winner, update_elo="True"):

        current = await scrim_methods.get_scrim(ctx)
        if not current:
            return await scrim_methods.temporary_feedback(ctx, "You cannot do that on this channel.")

        if current.phase != "underway":
            return await scrim_methods.temporary_feedback(ctx, "You cannot do that now.")
    

        if winner not in ("team1", "1", "t1", "team2", "2", "t2"):
            return await scrim_methods.temporary_feedback(ctx, "Pleace specify a winner ('team1' or 'team2').")

        elif winner in  ("team1", "1", "t1"):
            winner = "Team 1"
            if update_elo == "True":
                current.game.editstat(current.team1, current.team2)
        else:
            winner = "Team 2"
            if update_elo == "True":
                current.game.editstat(current.team2, current.team1)

        current.embed.description = f"Scrim over. {winner} won. Congratulations!"
        footertemp = "gg wp"
        current.embed.remove_field(0)
        current.embed.remove_field(0)
        current.embed.set_footer(text=footertemp)
        await current.message.edit(embed=current.embed)
        await ctx.message.delete()
    
        await current.reset()

    @winner.error
    async def winner_error(self, ctx, error):
        if isinstance(error, checks.NotScrimMaster):
            return await scrim_methods.temporary_feedback(ctx, error)
    
#################################################################################
##
##            a command to forcefully terminate the current scrim
##
#################################################################################

    @commands.command()
    @commands.guild_only()
    @commands.check_any(checks.bot_admin_local(), checks.scrim_master())
    async def terminate(self, ctx):

        current = await scrim_methods.get_scrim(ctx)
        if not current:
            return await scrim_methods.temporary_feedback(ctx, "You cannot do that on this channel.")
    
        if ctx.message.author.guild_permissions.administrator == False and ctx.message.author.id != "162882518381494272" and current.master != ctx.message.author:
            return await scrim_methods.temporary_feedback(ctx, "You need admin permissions to use that command.")

        if current.phase == "no scrim":
            return await scrim_methods.temporary_feedback(ctx, "No scrim to terminate.")

        current.embed.description = f"Scrim terminated"
        footertemp = "f"
        current.embed.clear_fields()
        current.embed.set_footer(text=footertemp)
        await current.message.edit(embed=current.embed)
        await ctx.message.delete()
        await current.message.clear_reactions()

        await current.reset()

    @terminate.error
    async def terminate_error(self, ctx, error):
        if isinstance(error, commands.errors.CheckAnyFailure):
            return await scrim_methods.temporary_feedback(ctx, "Only bot admins and the owner of the scrim can terminate a scrim.")

#################################################################################
##
##      a few loops for deleting idle scrims, an event for deleting messages
##      in a channel with an active scrim and a command to post notes that
##      won't get deleted
##
#################################################################################

    @tasks.loop(minutes=1)
    async def tick_active_scrims(self):
        for scrim in scrim_methods.Scrim.instances:
            scrim.last_interaction += 1

    @tasks.loop(minutes=1)
    async def delete_idle_scrims(self):
        for scrim in scrim_methods.Scrim.instances:

            if scrim.dont_delete:
                return None
            if scrim.server:
                if scrim.server["delete_inactive"] and scrim.last_interaction > scrim.server["delete_time_mins"] and scrim.phase == "setup":
                    scrim.embed.description = f"Scrim terminated"
                    footertemp = "f"
                    scrim.embed.clear_fields()
                    scrim.embed.set_footer(text=footertemp)
                    await scrim.message.edit(embed=scrim.embed)
                    await scrim.message.clear_reactions()
                    await scrim.reset()
                    return None

            elif scrim.last_interaction > 20 and scrim.phase == "setup":
                scrim.embed.description = f"Scrim terminated"
                footertemp = "f"
                scrim.embed.clear_fields()
                scrim.embed.set_footer(text=footertemp)
                await scrim.message.edit(embed=scrim.embed)
                await scrim.message.clear_reactions()
                await scrim.reset()
                return None

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.author.bot:
            return None

        await asyncio.sleep(5)
        current = await scrim_methods.get_scrim(ctx, send_feedback=False)
        if not current or current.phase == "no scrim":
            return None
        try:
            await ctx.delete()
        except:
            pass

    @commands.command()
    @commands.guild_only()
    async def note(self, ctx, *contents):
        current = await scrim_methods.get_scrim(ctx)
        if not current:
            return None

        embed = discord.Embed(title=f"Note", description=f"{' '.join(contents)}", color=current.game.color)
        embed.set_author(name=ctx.message.author.display_name, icon_url=ctx.message.author.avatar_url)
        note_msg = await ctx.send(embed=embed)
        current.notes.append(note_msg)
        await ctx.message.delete()


def setup(client):
    client.add_cog(ScrimCog(client))
