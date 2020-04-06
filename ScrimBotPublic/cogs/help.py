import discord
from discord.ext import commands, tasks
import elo_methods

class HelpCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.group()
    async def help(self, ctx):
        if ctx.invoked_subcommand is None:

            txt = """The bot supports the following commands for managing scrims:

'/scrim (game)' - setup a scrim of the specified game.
'/lock' - lock the current players, if the scrim is full.
'/teams' - automatically arrange and manage teams.
'/predict' - generate a win probability prediction with the current teams.
'/start' - start the scrim, once both teams are full.
'/winner' - specify the winner of a scrim to both end the scrim and update internal elo.
'/terminate' - forcefully end the current scrim. Only usable by admins.
'/pick' - pick players if scrim is set to pick-up -mode."""

            txt_2 = """The bot supports the following commands for utility and settings:

'/leaderboard' - view the leaderboard.
'/elo' - initialize elo-ratings for players. Only available to server admins.
'/update' - update the current list of games. Only available to global bot admins.
'/settings' - view and change the bot's settings for the server. Only available to admins.      
'/setup_roles' - setup a role system for the supported games. Only available to admins."""

            embed=discord.Embed(color=0x00ff00)
            embed.set_author(name="Scrimbot help")
            embed.add_field(name="Scrim management commands", value=txt, inline=False)
            embed.add_field(name="Utility commands", value=txt_2, inline=False)
            embed.set_footer(text="To get more info of a specific command please type '/help (command)'. To get a list of supported games and their aliases, type '/help games'.")

            try:
                await ctx.message.delete()
            except:
                pass
            await ctx.message.author.send(embed=embed)

    #'/help scrim':

    @help.command()
    async def scrim(self, ctx):

        txt = f"""Setup a scrim by typing '/scrim _game_'. Aliases: 's'

        To get a list of supported games and their aliases, type '/help games'."""

        embed=discord.Embed(color=0x00ff00)
        embed.set_author(name="Scrimbot help")
        embed.add_field(name="/scrim", value=txt, inline=True)
        embed.set_footer(text="To get more info of a specific command please type '/help (command)'. To get a list of supported games and their aliases, type '/help games'.")

        try:
            await ctx.message.delete()
        except:
            pass
        await ctx.message.author.send(embed=embed)

    #'/help lock':

    @help.command()
    async def lock(self, ctx):

        txt = f"""Once there are enough players in a scrim, type '/lock' to lock the players and start team selection. Aliases: 'l'"""

        embed=discord.Embed(color=0x00ff00)
        embed.set_author(name="Scrimbot help")
        embed.add_field(name="/lock", value=txt, inline=True)
        embed.set_footer(text="To get more info of a specific command please type '/help (command)'. To get a list of supported games and their aliases, type '/help games'.")

        try:
            await ctx.message.delete()
        except:
            pass
        await ctx.message.author.send(embed=embed)

    #'/help teams':

    @help.command()
    async def teams(self, ctx):

        txt = f"""Once players are locked, you can either use reactions to select teams manually, or ask the bot to arrange teams automatically. '/teams _criteria_' lets you arrange the teams according to specified criteria. Aliases: 't'. Supports the following criteria:
    
        'shuffle' - Completely random teams. Aliases: 's', 'random', 'r'.
        'balanced' - Finds the most balanced teams according to the internal elo system. Aliases: 'b'.
        'balancedrandom (threshold)' - Arranges mostly balanced teams. The treshold specifies how many percent units estimated win probability can differ from 50%. Aliases: 'br'.
        'pickup' - Lets you choose players by letting captains pick their desired players. Type '/help pickup' for more information. Aliases: 'pug'.
        'clear' - Clears both teams and moves all players to unassigned players. Aliases: 'c', 'empty', 'e'."""

        embed=discord.Embed(color=0x00ff00)
        embed.set_author(name="Scrimbot help")
        embed.add_field(name="/teams", value=txt, inline=True)
        embed.set_footer(text="To get more info of a specific command please type '/help (command)'. To get a list of supported games and their aliases, type '/help games'.")

        try:
            await ctx.message.delete()
        except:
            pass
        await ctx.message.author.send(embed=embed)

    #'/help predict':

    @help.command()
    async def predict(self, ctx):

        txt = f"""You can ask the bot to predic the win probability of the current teams with '/predict'. Requires both teams to be full."""

        embed=discord.Embed(color=0x00ff00)
        embed.set_author(name="Scrimbot help")
        embed.add_field(name="/predict", value=txt, inline=True)
        embed.set_footer(text="To get more info of a specific command please type '/help (command)'. To get a list of supported games and their aliases, type '/help games'.")

        try:
            await ctx.message.delete()
        except:
            pass
        await ctx.message.author.send(embed=embed)

    #'/help start':

    @help.command()
    async def start(self, ctx):

        txt = f"""Once both teams are full, type '/start (novoice)' to start the game. If you wish to start the game without moving players add the 'novoice' -argument (aliases: 'no', 'n'). Without the argument, the command waits for all the players to join any voice channel and then moves then to specified channels, if available."""

        embed=discord.Embed(color=0x00ff00)
        embed.set_author(name="Scrimbot help")
        embed.add_field(name="/start", value=txt, inline=True)
        embed.set_footer(text="To get more info of a specific command please type '/help (command)'. To get a list of supported games and their aliases, type '/help games'.")

        try:
            await ctx.message.delete()
        except:
            pass
        await ctx.message.author.send(embed=embed)

    #'/help winner':

    @help.command()
    async def winner(self, ctx):

        txt = f"""Once the scrim has been played, you can end the scrim and update the internal elo statistics with '/winner (team1/1 or team2/2)'. Aliases: 'w'."""

        embed=discord.Embed(color=0x00ff00)
        embed.set_author(name="Scrimbot help")
        embed.add_field(name="/winner", value=txt, inline=True)
        embed.set_footer(text="To get more info of a specific command please type '/help (command)'. To get a list of supported games and their aliases, type '/help games'.")

        try:
            await ctx.message.delete()
        except:
            pass
        await ctx.message.author.send(embed=embed)

    #'/help terminate':

    @help.command()
    async def terminate(self, ctx):

        txt = f"""Admins can terminate the scrim prematurely with '/terminate'."""

        embed=discord.Embed(color=0x00ff00)
        embed.set_author(name="Scrimbot help")
        embed.add_field(name="/terminate", value=txt, inline=True)
        embed.set_footer(text="To get more info of a specific command please type '/help (command)'. To get a list of supported games and their aliases, type '/help games'.")

        try:
            await ctx.message.delete()
        except:
            pass
        await ctx.message.author.send(embed=embed)

    #'/help pick/pickup':

    @help.command(aliases=['pickup'])
    async def pick(self, ctx):

        txt = """'/pickup (criteria)' makes the game a pickup game. Has the following criteria:

    'random': Assign captains by random.
    'choose': Let the players choose the captains themselves.
    'balanced': Assign two highest ranked players as captains. Lower ranked one starts picking.
    
    You can also define the picking order as 'fair' or 'classic'. Classic is the traditional format where captains take turns, while in fair, starting team picks once and then teams pick players in pairs of two. The format for this is:
    '/teams pickup (criteria) (fair/classic)'. Defaults to 'fair'.

    Once captains have been selected Team1 starts picking. '/pick @player' lets a captain pick a player of their choice on their turn. They can also choose to use '/pick random' to pick an ussagined player by random."""

        embed=discord.Embed(color=0x00ff00)
        embed.set_author(name="Scrimbot help")
        embed.add_field(name="Pick-up games", value=txt, inline=True)
        embed.set_footer(text="To get more info of a specific command please type '/help (command)'. To get a list of supported games and their aliases, type '/help games'.")

        try:
            await ctx.message.delete()
        except:
            pass
        await ctx.message.author.send(embed=embed)

    #'/help leaderboard/elo':

    @help.command(aliases=['leaderboard'])
    async def elo(self, ctx):

        txt = """Besides playing games, you can manipulate the internal elo-system with two commands:

    '/elo (member) (game) (rating)': Lets you set an elo rating for a member. Only available to server admins.
    '/leaderboard (game) (stat)': Shows a leaderboard of the specified game's specified stat. Stats are 'elo', 'wins', 'losses', 'winloss', 'plusminus' and 'games'.
    
    Please write '/help games' for a full list of supported games and their aliases."""

        embed=discord.Embed(color=0x00ff00)
        embed.set_author(name="Scrimbot help")
        embed.add_field(name="Leaderboard and elo-system", value=txt, inline=True)
        embed.set_footer(text="To get more info of a specific command please type '/help (command)'. To get a list of supported games and their aliases, type '/help games'.")

        try:
            await ctx.message.delete()
        except:
            pass
        await ctx.message.author.send(embed=embed)

    #'/help games':

    @help.command()
    async def games(self, ctx):

        txt = "The games this bot supports currently, and their aliases are:\n\n"

        for g in elo_methods.Game.instances:
            txt += f"**{g.dispname}** aliases: _{', '.join(g.alias['alias'])}_\n"

        embed=discord.Embed(color=0x00ff00)
        embed.set_author(name="Scrimbot help")
        embed.add_field(name="Supported games", value=txt, inline=True)
        embed.set_footer(text="To get more info of a specific command please type '/help (command)'. To get a list of supported games and their aliases, type '/help games'.")

        try:
            await ctx.message.delete()
        except:
            pass
        await ctx.message.author.send(embed=embed)

    #'/help update':

    @help.command()
    async def update(self, ctx):

        txt = f"""Update the current list of games. This temporarily removes all supported games and so can only be used by bot admins and can only be used if no scrims are being setup or underway."""

        embed=discord.Embed(color=0x00ff00)
        embed.set_author(name="Scrimbot help")
        embed.add_field(name="/update", value=txt, inline=True)
        embed.set_footer(text="To get more info of a specific command please type '/help (command)'. To get a list of supported games and their aliases, type '/help games'.")

        try:
            await ctx.message.delete()
        except:
            pass
        await ctx.message.author.send(embed=embed)

    # '/help settings':
    @help.command()
    async def settings(self, ctx):

        txt = f"""Server admins can configure the settings of their server to their liking with the '/settings _category value_'-command. To view a server's settings, you can use just '/settings'.

To change the bot's prefix on the server you can use the following command:
'/settings prefix _prefix_'"""

        txt_2 = """The following commands take a positive whole number as their argument:
        
'leaderboard_default' - Give the default length for the '/leaderboard' -command. Default 25, 0 means unlimited.
'leaderboard_max' - Give the maximum allowed length for the '/leaderboard' -command. Default 100, 0 means unlimited.
'delete_timer_scrims' - Give the time in minutes the bot waits before deleting an idle scrim. Default 20."""

        txt_3 = """The following commands take a boolean truth value as their argument. Many variations work, such as 'true', 'false', 'yes' and 'no':
        
'scrim_permissions' - Change if setting up a scrim should require special permissions. If false, anyone can setup a scrim. If true, only server admins and server bot moderators and admins can setup scrims. Default 'false'.
'guild_bot_admin' - Change if guild admins should also have admin rights for the bot. Server owner has bot admin rights regardless of this setting. Default 'true'.
'scrim_delete_messages' - Change if messages in channels with active scrims are automatically deleted. Default 'true'.
'delete_idle_scrims' - Change if unlocked scrims that are idle for too long are automatically deleted. Default 'true'.
'games_whitelist' - Change if the guild is a whitelist instead of a blacklist. Default 'false'.
'ping_created_scrim' - Change if new scrims automatically ping the role of their game. Default 'false'."""

        txt_4 = """The following commands manipulate the special rights of the bot's users on your server. All but the clear commands take most forms of user identification for specifying a member to target, but a mention is recommended. You can add permissions to as many users as you want at once.

'admin add' - Add bot admins to the server. Server bot admins can change the bot's settings and terminate scrims.
'admin remove' - Remove bot admins.
'admin clear' - Removes all added bot admins. Might leave you in a situation where only the server owner has bot admin rights. Use with care.
'moderator add' - Add bot moderators to the server. Bot moderators don't have any other special rights, but they can setup scrims even if special permissions to setup scrims on a server are enabled.
'moderator remove' - Remove bot moderators.
'moderator clear' - Removes all bot moderators."""

        embed=discord.Embed(color=0x00ff00)
        embed.set_author(name="Scrimbot help")
        embed.add_field(name="/settings", value=txt, inline=False)
        embed.add_field(name="Numeric settings", value=txt_2, inline=False)
        embed.add_field(name="Boolean settings", value=txt_3, inline=False)
        embed.add_field(name="Permission manipulation", value=txt_4, inline=False)
        embed.set_footer(text="To get more info of a specific command please type '/help (command)'. To get a list of supported games and their aliases, type '/help games'.")

        try:
            await ctx.message.delete()
        except:
            pass
        await ctx.message.author.send(embed=embed)

def setup(client):
    client.add_cog(HelpCog(client))
