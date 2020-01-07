import discord
from discord.ext import commands, tasks
import elo_methods

class HelpCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.group()
    async def help(self, ctx):
        if ctx.invoked_subcommand is None:

            txt = """This bot supports the following commands:

    '/scrim (game)' - setup a scrim of the specified game.
    '/lock' - lock the current players, if the scrim is full.
    '/teams' - automatically arrange and manage teams.
    '/predict' - generate a win probability prediction with the current teams.
    '/start' - start the scrim, once both teams are full.
    '/winner' - specify the winner of a scrim to both end the scrim and update internal elo.
    '/terminate' - forcefully end the current scrim. Only usable by admins.
    '/pick' - pick players if scrim is set to pick-up -mode.
    '/leaderboard' - view the leaderboard.
    '/elo' - initialize elo-ratings for players. Only available to server admins.
    '/update' - update the current list of games. Only available to server admins and only usable if no scrims are being setup or underway.

    To get more info of a specific command please type '/help (command)'. To get a list of supported games and their aliases, type '/help games'."""

            embed=discord.Embed(color=0x00ff00)
            embed.set_author(name="Scrimbot help")
            embed.add_field(name="General commands", value=txt, inline=True)

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

        try:
            await ctx.message.delete()
        except:
            pass
        await ctx.message.author.send(embed=embed)

    #'/help update':

    @help.command()
    async def update(self, ctx):

        txt = f"""Update the current list of games. This temporarily removes all supported games and so can only be used by server admins and can only be used if no scrims are being setup or underway."""

        embed=discord.Embed(color=0x00ff00)
        embed.set_author(name="Scrimbot help")
        embed.add_field(name="/update", value=txt, inline=True)

        try:
            await ctx.message.delete()
        except:
            pass
        await ctx.message.author.send(embed=embed)

def setup(client):
    client.add_cog(HelpCog(client))
