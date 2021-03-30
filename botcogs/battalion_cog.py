from discord.ext import commands
from analyzertools import analyzer
from main_bot import hasPermissions

class BattalionCog(commands.Cog):
    def __init__(self, bot, dom):
        self.bot = bot
        self.dom = dom

    @commands.check(hasPermissions)
    async def listBattalions(self):
        self.dom.listBattalions()

    @commands.command(pass_context=True)
    @commands.check(hasPermissions)
    async def createBattalion(self, ctx, *args):


    @commands.command(pass_context=True)
    @commands.check(hasPermissions)
    async def showBattalion(self, ctx):
        users = self.dom.getUsers()
        if (len(users) == 0):
            await ctx.send("Theres no one in the battalion???")
        else:
            await ctx.send(users)


    @commands.command(pass_context=True)
    @commands.check(hasPermissions)
    async def enlist(self, ctx, username):
        await ctx.send('Validating User')
        try:
            users = self.dom.getUsers()
            for user in users:
                if user[0] == username:
                    await ctx.send('Username already exists in users. Are you sure you meant to enlist %s.' % username)
                    return
            query = analyzer.queryBfTracker(username)['data']
            # if(query == None):
            #    await ctx.send('Unable to find user in battlefield tracker. Are you sure you meant to enlist %s' % username)
            dom.enlistUser(username)
            reply = """ User %s added to list of users. Current list of users: %s """ % (username, dom.getUsers())
            await ctx.send(reply)
        except Exception as e:
            print(e)
            await ctx.send("Something went wrong while trying to enlist user %s." % username)