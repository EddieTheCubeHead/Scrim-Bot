import discord
from discord.ext import commands, tasks
import elo_methods
import main_methods
import option_methods
import json

class Scrim:

    """Class that houses the information of a single scrim.
    
variables:
message -- the discord message the main scrim is tied to
embed -- the embed in the main message
game -- the game the scrim is setup as, instance of elo_methods.Game
phase -- declares the scrim's current phase
players -- a list of players in the scrim
team1 -- a list of team1 of the scrim
team2 -- a list of team2 of the scrim
spectators -- a list of spectators of the scrim
caps -- a list of captains of the scrim
voice -- a list ofvoice channels in the main channel's category
options -- a list of options the scrim has, saved as objects (see options_methods)
last_interaction -- task loops since last interaction
notes -- note messages connected to the current scrim
option_embeds -- a list of embed messages if displaying options

class variables:
instances -- tracks all instances of Scrim
participators -- tracks all participators in all scrims"""

    instances = []
    participators = []

    def __init__(self, id, passtru, *, message=None, embed=None, game=None, phase="no scrim", master=None):
        self.id = id
        self.message = message
        self.embed = embed
        self.game = game
        self.phase = phase
        self.master = master
        self.players = []
        self.team1 = []
        self.team2 = []
        self.spectators = []
        self.caps = []
        self.voice = []
        self.options = []
        self.last_interaction = 0
        self.notes = []
        self.option_embeds = {}
        self.instances.append(self)
        if passtru.category:
            if passtru.category.voice_channels:
                for v in passtru.category.voice_channels:
                    self.voice.append(v)

    async def reset(self):

        """Reset all information in self."""

        self.message = None
        self.embed = None
        self.game = None
        self.phase = "no scrim"
        self.master = None
        for p in self.players:
            try:
                Scrim.participators.remove(p)
            except:
                pass
        for p in self.team1:
            try:
                Scrim.participators.remove(p)
            except:
                pass
        for p in self.team2:
            try:
                Scrim.participators.remove(p)
            except:
                pass
        for p in self.spectators:
            try:
                Scrim.participators.remove(p)
            except:
                pass
        self.players.clear()
        self.team1.clear()
        self.team2.clear()
        self.spectators.clear()
        self.caps.clear()
        self.options.clear()
        self.last_interaction = 0
        for note in self.notes:
            await note.delete()
        self.notes.clear()
        await self.delete_option_embeds()
        self.option_embeds = {}

    def get_options(self):
        if not self.game:
            return None
        for option in self.game.options:
            if self.game.options[option]["category"] == "pick_one":
                temp_option = option_methods.Pick_One(self.game.options[option]["dispname"], self.game.options[option]["choices"])
            elif self.game.options[option]["category"] == "side":
                temp_option = option_methods.Side(self.game.options[option]["dispname"], self.game.options[option]["choices"])
            self.options.append(temp_option)

    async def delete_option_embeds(self):
        for message in self.option_embeds.values():
            await message.delete()

    def get_formatted_members(self, group):

        """Get a list of a scrim's players formatted for displaying in an embed.

attributes:
group -- players, team1, team2 or spectators

returns a string with the players' display names."""

        if not vars(self)[group]:
            return "_empty_"

        else:

            player_names = []
            formatted_players = ""

            for captain in self.caps:
                if captain in vars(self)[group]:
                    formatted_players = captain.display_name + " _(captain)_"

                    if len(vars(self)[group]) > 1:
                        formatted_players = formatted_players + "\n"

            for player in vars(self)[group]:
                if player in self.caps:
                    continue
                else:
                    player_names.append(player.display_name)

            formatted_players = formatted_players + '\n'.join(player_names)

            return formatted_players

    def clear_teams(self):

        """Clears both teams for a given scrim and moves all players to unassigned."""

        for player in self.team1:
            self.team1.remove(player)
            self.players.append(player)

        for player in self.team2:
            self.team2.remove(player)
            self.players.append(player)

        self.caps.clear()

    def move_to(self, player, destination="players"):
    
        """Moves a given player to the given group of players.
    
attributes:
player -- a player in the given scrim
destination -- str team1, team2, caps or players (default: players)"""

        if destination[:4] == "team":
            vars(self)[destination].append(player)
            self.players.remove(player)
            return True

        elif destination == "caps":
            if len(self.caps) >= 2:
                return False
            self.caps.append(player)
            if len(self.team1) == 0:
                self.team1.append(player)
            else:
                self.team2.append(player)
            self.players.remove(player)
            return True

        elif player in self.caps:
            self.caps.remove(player)

        if player in self.team1:
            self.team1.remove(player)
            self.players.append(player)
            return True

        elif player in self.team2:
            self.team2.remove(player)
            self.players.append(player)
            return True

        else:
            return False

    def add_user(self, user, group="players"):

        """Add a player or a spectator to the scrim.
        
attributes:
user -- discord
group -- str players or spectators

returns True is successful, False if not"""

        if user in self.participators:
            return False

        else:
            vars(self)[group].append(user)
            self.participators.append(user)

    def remove_user(self, user):

        if user not in self.participators:
            return False

        if user in self.players:
            self.players.remove(user)
            self.participators.remove(user)
            return True

        if user in self.spectators:
            self.spectators.remove(user)
            self.participators.remove(user)
            return True
    
    def set_missing_elos(self):

        for player in self.team1 + self.team2:
            if player.id not in self.players:
                self.game.addelo(player.id, 1800)

    @classmethod
    def setup_instances(self, client):

        """Setup instances of Scrim for every eligible channel in client."""

        for c in client.get_all_channels():
            if str(c.type) == "text" and c.name[:5] == "scrim":
                vars()[c.id] = Scrim(c.id, c)

async def temporary_feedback(ctx, msg, *, delay=8.0, delete=True):

    """Send a temporary message and delete it after a specified delay.
    
arguments:
ctx -- context, has to have a message-attribute or be a message
msg -- temporary message to send
    
keyword arguments:
delay -- delay for temporary message deletion (default 8.0)
delete -- deletes context message if True (default True)
    
returns None"""

    tempmsg = await ctx.send(msg)
    if delete:
        try:
            await ctx.message.delete()
        except:
            pass
    await tempmsg.delete(delay=delay)
    return None

async def get_scrim(ctx, *, check_master=False, send_feedback=True):

        """Get the instance of Scrim associated with context's (ctx) channel.
        
arguments:
ctx -- context message or reaction

keyword arguments:
check_master -- bool, if True, checks if context author is the master of the current scrim. (default: False)

returns an instance of scrim if successful, None if it failed to find a scrim or a master."""

        if isinstance(ctx, discord.Message):
            ctx_id = ctx.channel.id
        else:
            ctx_id = ctx.message.channel.id

        for channel in Scrim.instances:
            try:
                if ctx_id == channel.id:
                    if check_master and (ctx.message.author != channel.master and ctx.message.author.id not in main_methods.get_configs()["admins"]):
                        if send_feedback:
                            return await temporary_feedback(ctx, "Only the person who set up the scrim or is a bot admin can manage it.")
                        else:
                            return None
                    else:
                        channel.last_interaction = 0
                        return channel
            except:
                pass
        else:
            if isinstance(ctx, discord.Reaction):
                return None
            elif send_feedback:
                return await temporary_feedback(ctx, "You cannot do that on this channel.")
