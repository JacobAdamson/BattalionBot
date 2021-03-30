from discord.ext import commands
from analyzertools import analyzer
from pytz import timezone
import datetime
from analyzertools.analyzer_models import *


class AnalyzerCog(commands.Cog):
    def __init__(self, bot, dom):
        self.bot = bot
        self.dom = dom

    @commands.command(
        help="""Shows the indicies available for diffing.
                User data is only stored after they are enlisted""",
        pass_context=True
    )
    async def indicies(self, ctx):
        indicies = self.dom.getIndicies()
        formattedIndicies = list(
            map(lambda index: (index[0],
                               timezone('UTC').localize(datetime.datetime.fromtimestamp(index[1])).astimezone(
                                   timezone('US/Pacific')).strftime("%m/%d/%Y, %H:%M:%S")
                               ), indicies)
        )
        await ctx.send(formattedIndicies)

    #@commands.command(pass_context=True)
    async def report(self, ctx, *args):
        if len(args) == 0:
            await ctx.send("Showing Frag Report Since Last Interval")
            report = analyzer.craftLastMessage(self.dom)
        elif len(args) == 1:
            since = int(args[0])
            await ctx.send("Showing Frag Report Over Last %s Intervals" % since)
            report = analyzer.craftMessageSince(self.dom, since)
        elif len(args) == 2:
            prev = int(args[0])
            cur = int(args[1])
            report = analyzer.craftMessage(self.dom, prev, cur)
            await ctx.send("Showing Frag Report Between Intervals %s and %s" % (prev, cur))
        await ctx.send(report)

    @commands.command(
        help="""Generates a leaderboard for the users in the battalion. Select the keys for your leaderboard and up them in one quoted string. e.g. \"kills deaths timePlayed\"
                To get stats for a class do <class>.<stat> e.g. medic.kills. 
                You can get the ratio between 2 stats by putting a slash in-between them. 
                By default stats are pulled from tracker directly. To get stats in the last X days put a number after your query. 
                Available classes are: medic assault support recon ground tanker pilot and overall. 
                Overall is used by default. 
                Available stats are kills deaths scoreRound timePlayed damage assists shotsHit shotsTaken headshots revives revivesRecieved wins roundsPlayed and more.  
                Not all stats are available for all classes.""",
                brief = "Generates a leaderboard using provided keys",
                      pass_context=True)
    async def analyze(self, ctx, *args):
        if len(args) == 0:
            await ctx.send("You are required to pass in a query string")
        else:
            leaderboardString = args[0]
            leaderboardConfig = LeaderboardConfig.createFromString(leaderboardString, 20)
            joinedStat = None
            if len(args) == 1:
                await ctx.send("Generating Leaderboard From Live Data")
                joinedStat = analyzer.createLiveStat(self.dom)
            elif len(args) == 2:
                since = int(args[1])
                await ctx.send("Generating Leaderboard Over Last %s Intervals" % since)
                key = self.dom.getKey()
                joinedStat = self.dom.getFriendlyJoinedStat(key - since, key)
            elif len(args) == 3:
                prev = int(args[1])
                cur = int(args[2])
                await ctx.send("Generating Leaderboard Between Intervals %s and %s" % (prev, cur))
                joinedStat = self.dom.getFriendlyJoinedStat(prev, cur)
            else:
                await ctx.send("Invalid Number of Arguments. Up to three arguments allowed")
            leaderboard = analyzer.createLeaderboard(joinedStat, leaderboardConfig)
            await ctx.send("```" + leaderboard + "```")

