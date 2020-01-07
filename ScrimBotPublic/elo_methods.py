#################################################################################
##
##                           elo-module for scrim bot
##
#################################################################################

import json
import math
import os
import shutil
import datetime

class Game:

    """Superclass for all registered games for the bot.
    
variables:
name -- the name the game is referenced in code.
dispname -- the name that is displayed in scrims.
icon -- the icon that is displayerd in scrims.
color -- the color thatis displayed in scrims (default: 0xffffff=white)
alias -- the aliases game can be called with in commands.
players -- a dictionary of all players' statistics
options -- a dictionary of options for TBA features

class variables:
instances -- tracks all instances of Game and it's subclasses"""

    instances = []

    def __init__(self, name, dispname, icon, color=0xffffff, **alias):

        self.name = name
        self.dispname = dispname
        self.color = color
        self.icon = icon
        self.alias = alias
        self.players = {}
        self.options = {}
        self.instances.append(self)

        for option in self.options:
            pass

    def safesave(self, saved_stats, file_name=None):

        """Save specified stats.
        
arguments:
saved_stats -- a dictionary to be saved
file_name -- a name for the saved file (default: file_name=saved_stats)"""

        file_name = file_name or saved_stats
        savedr = f"{os.getcwd()}/data/{self.name}"
        backupdr = f"{os.getcwd()}/backups/{self.name}"
        timestmp = datetime.datetime.now()
        date = timestmp.strftime("%Y_%m_%d-%H_%M_%S")
        file = f"{backupdr}/{file_name}_{date}.json"
        with open(file, "w") as outfile:
            json.dump(getattr(self, saved_stats), outfile)
        
        shutil.copy2(file, f"{savedr}/{file_name}.json")

        backups = []

        for backup_file in os.listdir(backupdr):
            if backup_file[:len(file_name)] == file_name:
                backups.append(backup_file)
                backups.sort(reverse=True)

        else:
            for redundant_file in backups[99:]:
                os.remove(f"{backupdr}/{redundant_file}")


    def load(self, on_startup=False):

        """Load elo stats and options for self.
        
attributes:
on_startup -- declares if function is called with bot startup (default: False)"""

        main = os.getcwd()
        try:
            with open(f"{main}/data/{self.name}/elo.json", "r") as player_stats:
                self.players = json.load(player_stats)
        except:
            if on_startup:
                print(f"{self.dispname} couldn't load elo")
        else:
            if on_startup:
                print(f"{self.dispname} loaded elo")

        try:
            with open(f"{main}/data/{self.name}/options.json", "r") as options:
                self.options = json.load(options)
        except:
            if on_startup:
                print(f"{self.dispname} couldn't load options")
        else:
            if on_startup:
                print(f"{self.dispname} loaded options")


    def addelo(self, player_id, elo=1800):

        """Add elo stats for a player.
        
arguments:
player_id -- id of a discord.member -object
elo -- starting rank for member (default: 1800)

returns True if succesful and False if unsuccesful"""

        if str(player_id) in self.players:
            return False
        
        self.players[str(player_id)] = {
            'elo': int(elo),
            'wins': 0,
            'losses': 0,
            'errs': 0,
            'initialelo': elo
        }

        self.safesave("players", "elo")
            
        return True

    def addoption(self, name, dispname, category, *choices, lock=0):

        """Future proofing for map, side, etc. selection. Description TBA"""

        self.options[name] = {
            'dispname': dispname,
            'category': category,
            'choices': choices,
            'lock': 0
        }

        self.safesave("options")

    def editoption(self, name, dispname=None, category=None, choices=None, lock=None):

        """Future proofing for map, side, etc. selection. Description TBA"""

        for option in self.options:
            if name == option:
                self.options[name]['dispname'] = dispname or self.options[name]['dispname'],
                self.options[name]['category'] = category or self.options[name]['category'],
                self.options[name]['choices'] = choices or self.options[name]['choices'],
                self.options[name]['lock'] = lock or self.options[name]['lock']

    def removeoption(self, name):

        """Future proofing for map, side, etc. selection. Description TBA"""

        for option in self.options:
            if name == option:
                self.options.pop[option]

    @classmethod
    def get_games(self, config, *, on_startup=False):

        """Load supported games from given config

keyword attributes:
on_startup -- declares if function is called with bot startup (default: False)
    
Returns True"""

        for game in self.instances:
            del game

        self.instances.clear()

        for subclass in self.__subclasses__():
            subclass.instances.clear()

        for team_game in config["Games"]["Team"]:
            aliases = []
            aliases.append(team_game)
            for alias in range(len(config["Games"]["Team"][team_game]["alias"])):
                aliases.append(config["Games"]["Team"][team_game]["alias"][alias])
            vars()[team_game] = Team(config["Games"]["Team"][team_game]["playerreq"], team_game, config["Games"]["Team"][team_game]["dispname"], config["Games"]["Team"][team_game]["icon"], int(config["Games"]["Team"][team_game]["colour"], 16), *aliases)

        for ffa_game in config["Games"]["FFA"]:
            aliases = []
            aliases.append(ffa_game)
            for alias in range(len(config["Games"]["FFA"][ffa_game]["alias"])):
                aliases.append(config["Games"]["FFA"][ffa_game]["alias"][alias])
            vars()[ffa_game] = FFA(config["Games"]["FFA"][ffa_game]["maxplayers"], ffa_game, config["Games"]["FFA"][ffa_game]["dispname"], config["Games"]["FFA"][ffa_game]["icon"], int(config["Games"]["FFA"][ffa_game]["colour"], 16), *aliases)

        for game in self.instances:
            game.load(on_startup)

        return True

class Team(Game):

    """Subclass of Game, for games where two teams play against each other.
    
variables:
playerreq -- the required numbe of players to play the game)
name -- the name the game will be referenced in code.
dispname -- the name that will be displayed in scrims.
icon -- the icon that will be displayerd in scrims.
color -- the color that will be displayed in scrims (default: 0xffffff=white)
alias -- the aliases game can be called with in commands.

class variables:
instances -- trakcs all instances of Team"""


    instances = []

    def __init__(self, playerreq, name, dispname, icon, color=0xffffff, *alias):

        self.playerreq = playerreq
        super().instances.append(self)
        super().__init__(name, dispname, icon, color, alias=alias)
    

    def editstat(self, win_team, lose_team):

        """When given a winning and losing team, updates their elo statistics for the game called from.
        
arguments:
win_team -- list of players in the winning team
lose_team -- list of players in the losing team"""

        winprob = self.winprob(win_team, lose_team)         #get win probability

        matchelo = 0                                        #small code snippet to get match avg elo
        for i in win_team:
            matchelo += self.players[str(i.id)]['elo']
        for i in lose_team:
            matchelo += self.players[str(i.id)]['elo']
        matchelo = matchelo/(len(win_team)+len(lose_team))
            
        for player in win_team:
            elo = self.players[str(player.id)]['elo']

            #  The algorith by which the elo is modified is as following:
            #  1: start with a base value of 50
            #  2: add 15 weighed by estimated win probability for player's team (-1<n<1)
            #  3: add 10 weighed by the difference between the player's elo and the average elo of the match (-1<n<1)

            self.players[str(player.id)]['elo'] = int(round(elo+(50+(2*(1-winprob)-1)*15+(matchelo-elo)/300),0))
            self.players[str(player.id)]['wins'] += 1

            for adversary in lose_team:
                try:
                    self.players[str(player.id)]['won_against'][str(adversary.id)] += 1
                except:
                    try:
                        self.players[str(player.id)]['won_against'][str(adversary.id)] = 1
                    except:
                        self.players[str(player.id)]['won_against'] =  {
                            str(adversary.id): 1
                        }
            for mate in win_team:
                if player == mate:
                    continue
                else:
                    try:
                        self.players[str(player.id)]['won_with'][str(mate.id)] += 1
                    except:
                        try:
                            self.players[str(player.id)]['won_with'][str(mate.id)] = 1
                        except:
                            self.players[str(player.id)]['won_with'] =  {
                                str(mate.id): 1
                            }

        for player in lose_team:
            elo = self.players[str(player.id)]['elo']
            self.players[str(player.id)]['elo'] = int(round(elo-(50-(2*winprob-1)*15-(matchelo-elo)/300),0))
            if self.players[str(player.id)]['elo'] <= 0:
                self.players[str(player.id)]['elo'] = 1
            self.players[str(player.id)]['losses'] += 1
            for adversary in win_team:
                try:
                    self.players[str(player.id)]['lost_against'][str(adversary.id)] += 1
                except:
                    try:
                        self.players[str(player.id)]['lost_against'][str(adversary.id)] = 1
                    except:
                        self.players[str(player.id)]['lost_against'] = {
                           str(adversary.id): 1
                        }
            for mate in lose_team:
                if player == mate:
                    continue
                else:
                    try:
                        self.players[str(player.id)]['lost_with'][str(mate.id)] += 1
                    except:
                        try:
                            self.players[str(player.id)]['lost_with'][str(mate.id)] = 1
                        except:
                            self.players[str(player.id)]['lost_with'] =  {
                                str(mate.id): 1
                            }
                        

        self.safesave("players", "elo")


    def winprob(self, team1, team2):

        """Gets estimated win probability for team 1 when given 2 teams.

arguments:
team1 -- list of players in team1
team2 -- list of players in team2

Returns estimated win probability, type: float, value n: 0<=n<=1."""

        elo1 = self.teamelo(team1)
        elo2 = self.teamelo(team2)
        return (1/(1+10**((elo2-elo1)/800)))

    def teamelo(self, team):

        """Gets a weighed elo value for a given team.

arguments:
team -- list of players

Returns elo value for team, type: int"""

        elos = []   #temporary list
        for player in team:
            elos.append(self.players[str(player.id)]['elo'])
        return (sum(elos)+math.sqrt((sum(elos)/len(elos))*max(elos)))/(len(elos)+1)

        #  The algorithm takes the mean of n+1 values, where n is the number of players in a team. 
        #  n of the taken values are the elo values for players in a team. 
        #  The last value is the geometric mean of two values:
        #  1: the elo of the highest ranked player
        #  2: the average elo of the team.
        #  This way the elo for a team skews towards the highest ranked player, but not by much.

class FFA(Game):

    """Subclass of Game, for games where all players play against each other.
    
variables:
maxplayers -- the maximum players allowed for the game, if 0 set to None
name -- the name the game will be referenced in code.
dispname -- the name that will be displayed in scrims.
icon -- the icon that will be displayerd in scrims.
color -- the color that will be displayed in scrims (default: 0xffffff=white)
alias -- the aliases game can be called with in commands.

class variables:
instances -- tracks all instances of FFA"""

    instances = []

    def __init__(self, maxplayers, name, dispname, icon, color=0xffffff, *alias):
        self.maxplayers = maxplayers
        if self.maxplayers == 0:
            self.maxplayers = None
        super().instances.append(self)
        super().__init__(name, dispname, icon, color, alias=alias)

class Versus(Game):

    """Subclass of Game, for 1 on 1 games.
    
variables:
name -- the name the game will be referenced in code.
dispname -- the name that will be displayed in scrims.
icon -- the icon that will be displayerd in scrims.
color -- the color that will be displayed in scrims (default: 0xffffff=white)
alias -- the aliases game can be called with in commands.

class variables:
instancess -- tracks all instances of Versus"""

    instances = []

    def __init__(self, name, dispname, icon, color=0xffffff, *alias):
        super().instances.append(self)
        super().__init__(name, dispname, icon, color, alias=alias)





    

    


    
