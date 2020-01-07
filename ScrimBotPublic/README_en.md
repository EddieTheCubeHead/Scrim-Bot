###############################################################################

                             scrimbot beta0.9.8
							      07.11.2019

###############################################################################

							about the documentation

###############################################################################

The bot has been and still is mainly a learning opportunity for me and so the
documentation is mainly meant as sort of a hybrid between funcional docs and
a personal project diary.

###############################################################################

							  current functions

###############################################################################

A discord bot for setting up friendly scrims, or friendly matches where predecided 
teams play against each other, among the members of a server. The bot creates
an embed message serving as the main user interface with the '/setup (game)'
-command. The bot gets supported games from the .games json file and displays
correct logo, name etc. based on the info on the file. Based on the game, the 
bot keeps track of how many more players need to join. Joining as a spectator is
also supported, although for now this feature is just future proofing.

Once the required number of players has been reached the players and spectators
can be locked with '/lock'. This enables setting up the two teams. You can either
manually setup teams with the reaction UI, or use one of the many supported
automatic or semi-automatic commands to setup a team.

The commands for teams selection all start with '/teams' after that you can specify
the criteria by which the teams are decided by. '/teams shuffle' is the most self-
esplanatory method, literally shuffling the current players into two teams.
'/teams balanced' takes advantage of the integrated elo-system, going through all
team combinations and choosing the one that has the winrate prediction closest to
50% for either team. '/teams balancedrandom (thershold)' is almost the same as 
balanced, but users can specify a threshold (default=5) and the bot takes a random
team combination which winrate prediction falls within the treshold of 50%, so that
the default thershold yield winrates between 45% and 55%. If the players don't like
the current teams, '/teams clear' moves all players back to unassigned.

With the '/teams pickup' the scrim can be transformed into a pickup game. By default
the captains are assigned as two of the highest ranked players. But the way captains
are chosen can be changed with '/teams pickup (criteria)' as either 'choose' or 'random',
both of which should be self-explanatory. Once the captains have been chosen they can
pick players from the unassigned players pool with '/pick' and mentioning the desired
player. The picking order is ABBAABBA ('fair') by default, but can also be changed
with an argument, so that '/teams pickup choose classic' let's you choose two captains,
that pick players in the classic ABABABAB order. '/teams clear' resets the pickup game
back into the default team selection process.

Once the teams are ready, the command '/start' starts the scrim. If the channel the 
scrim is setup in is in a category that also has voice channels "Team 1" and "Team 2",
the bot will wait for all players to join some voice channel (this is to prevent errors)
and then move the teams to correct voice channels. This behavior can be prevented by 
adding a "novoice" -argument to the start command ('/start novoice'). Regardless of
the voice channel behaviour, the start command also updates the embed and makes team
manipulation impossible.

Once the scrim is played, the command '/winner (team1/team2)' ends the scrim and
updates the elo statistics for all participators. If players don't wish to update
the statistics it can be prevented with adding another argument to the command.

The bot can be updated with '/update'. This will update the internal game list
and the cog-modules. This can bee useful if the server wishes to play a game
that is not currently supported, or for developement purposes.

###############################################################################

							elo-system and commands

###############################################################################

The matchmaking system of the bot is based upon the elo system used in chess.
The default estimated winrate for both teams is calculated identically to
chess winrate calculations, but the way a team's elo is calculated isn't a straight
up average of the team's players' elo values. The algorith for calculating a team's
elo is as follows:

1: get the geometric mean of the team's highest ranked player and the team's average elo
2: get the average of the elo of team's players' and the value calculated in step one

This way a team's elo skews a little towards the highest ranked player. Based on
testing with a group of roughly 20 players with widely varying skill levels this
yields consistently balanced teams.

To set an elo value for a player, an user with bot admin permissions can use 
'/elo (player) (game) (value)'. Bot admin list can be found in .configs -file, but
currently only contains the developer id. A command to add global, or server specific
admins is planned and will be implemented at some point.

All members of a server can see the elo statistics for all members of the server
with '/leaderboard (game) (statistic)'.

###############################################################################

                                   ideas

###############################################################################

  -map, side, first pick etc. selection
  -Votes for the mvp and the saltiest player after a game.
  -fill -argument for the '/teams' -command
  -A feature for subscribing to a certain game on a certain server
  -A feature for setting up all the needed channels with one adming command

###############################################################################

                                version history

###############################################################################

  beta 0.9.8 -- 5.11.2019
	-Cleaning up the code with better commenting, docstings, more readable variable
	names, more functions etc.
	-Assigning a master user to every scrim to prevent running conflicting commands
	simultaneously. Bot admins can still manage all the scrims

  beta 0.9.7b -- 31.10.2019

	-Cogs -implementation left some functions tied to the Scrim-class homeless.
	These have been moved to the scrim_methods module.
		-elo_module renamed to elo_methods to preserver the naming scheme
		-This fixed a bug in '/update' that wiped out all supported games

  beta 0.9.7 -- 31.10.2019
	
	-Implementing the cogs system.
		-elo, scrim and help cog creation
			-the corresponding code has been moved to these modules
		-update command updated to reload all cogs
			-no need to restart the bot when making small updates
	-small bugfixes
		-'/leaderboard (game) games' not sorting correctly
	-implementing temporary_feedback to the temporary messages still missing it


  beta 0.9.6 -- 30.10.2019

	-Adding the config -file
	-Moving the list of games from the main module to config
		-implementing get_games and /update
	-Changing pickup ganes from display_name -based to @user -based
	-Bug fixes for pickup games



  beta 0.9.5 -- 29.10.2019

	-Streamlining user commands and updating /help to resemble the new commands
	-Support for multiple scrims on the same server with individual voice channels
	-'/leaderboard' -cleanup
		-sorting problems caused by incorrect cariable types fixed
		-excess dictionaries needed because of these variable types removed
	-Small code cleanup
		-Function for recognizing a channel and getting the corresponding Scrim
		instance
		-Temporary messages got their own function
		-Pruned excess prints used for testing
	-Other minor bugfixes



  beta 0.9.4 -- 24.10.2019

	-Support for multiple simultaneous scrims on multiple servers
		-every channel with a name starting with "scrim" can host one scrim at a time



  beta 0.9.3 -- 23.10.2019

	-Better file handling and backups



  beta 0.9.2 -- 17.10.2019

	-Small bugfixes for bugs that popped up in 0.9.0



  beta 0.9.1 -- 16.10.2019

	-Updating all the documentation to resemble the current state of the project



  beta 0.9.0 -- 16.10.2019

	-Small rewrite to remove all global variables. Implemented the Scrim -class
	to host all required information for a scrim.


  beta 0.8.2 -- 15.10.2019

	-'/help' -rewrite
	-'leaderboard' bugfixes
	-'/scrim teams pickup balanced' -implementation with elo
	-'/pick random' -implementation



  beta 0.8.1 -- 14.10.2019

	-/leaderboard (game) (statistic)



  beta 0.8.0 -- 11.10.2019

	-elo -implementation
		-/scrim teams balanced
		-/scrim teams balancedrandom
		-/elo (player) (game) (value)



  v 0.7.0 -- 10.10.2019

	-elo-module implementation. Functionality stayed the same



  v 0.6.0 -- 9.10.2019

	-/scrim teams pickup -implementation
	-reaction UI for caps="choose"
	-/pick (user)



  v 0.5.0 -- 9.10.2019

	-/scrim start



  v 0.4.2 -- 8.10.2019

	-creating documentation
	-some cleaning up



  v 0.4.1 -- 8.10.2019

	-removing excess lists
		-participators' diplay name and id can be called from the member object



  v 0.4.0 -- 8.10.2019

	-/scrim teams random- and /scrim teams clear -implementation
	-/scrim teams -implementation



  v 0.3.1 -- 7.10.2019

	-/scrim lock reaction UI



  v 0.3.0 -- 7.10.2019

	-/scrim lock



  v 0.2.0 -- 7.10.2019

	-/scrim setup reactíon UI



  v 0.1.0 -- 7.10.2019

	-/scrim setup



###############################################################################

							some sources used:

###############################################################################

https://discordpy.readthedocs.io/en/latest/api.html
https://gist.github.com/EvieePy/d78c061a4798ae81be9825468fe146be
countless one page articles on all imaginable python functions

