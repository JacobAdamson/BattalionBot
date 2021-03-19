#!/usr/bin/python3
from discord.ext.commands import Bot
from discord.ext import commands
import env_variables
from db import SqlLiteDom
import task
import datetime
from pytz import timezone

client = Bot(description="My Cool Bot", command_prefix="!", )

filename = env_variables.dbFilename()
dom = SqlLiteDom(filename)

@client.event
async def on_ready():
    #dom.getUsers()
    print('We have logged in as {0.user}'.format(client))

### PERMISSIONS CHECKS ###
async def hasPermissions(ctx):
    return ctx.message.author.id == 693962849717846147 or ctx.message.author.guild_permissions.administrator

async def isSysAdmin(ctx):
    return ctx.message.author.id == 693962849717846147

async def isAdmin(ctx):
    return ctx.message.author.guild_permissions.administrator

### BATTALION COMMANDS ###
@client.command(pass_context=True)
@commands.check(hasPermissions)
async def showBattalion(ctx):
    users = dom.getUsers()
    if(len(users) == 0):
        await ctx.send("Theres no one in the battalion???")
    else:
        await ctx.send(users)

@client.command(pass_context=True)
@commands.check(hasPermissions)
async def enlist(ctx, username):
    await ctx.send('Validating User')
    try:   
        users = dom.getUsers()
        for user in users:
            if user[0] == username:
                await ctx.send('Username already exists in users. Are you sure you meant to enlist %s.' % username)
                return
        query = task.queryBfTracker(username)['data']
        #if(query == None):
        #    await ctx.send('Unable to find user in battlefield tracker. Are you sure you meant to enlist %s' % username)
        dom.enlistUser(username)
        reply = """ User %s added to list of users. Current list of users: %s """ % (username, dom.getUsers())
        await ctx.send(reply)
    except Exception as e:
        print(e)
        await ctx.send("Something went wrong while trying to enlist user %s." % username)

@client.command(pass_context=True)
@commands.check(hasPermissions)
async def discharge(ctx, username):
    dom.dischargeUser(username)
    reply = """ User %s removed from list of users. Current list of users: %s """ % (username, dom.getUsers()) 
    await ctx.send(reply)

### DATA CONTROLS ###
@client.command(pass_context=True, name="sync-data")
@commands.check(hasPermissions)
async def syncData(ctx):
    await ctx.send('syncing data for users in battalion')
    task.storeAndIncrement(dom)
    await ctx.send(dom.getUsers())

@client.command(pass_context=True)
@commands.check(hasPermissions)
async def indicies(ctx, *args):
    indicies = dom.getIndicies()
    formattedIndicies = list(
        map(lambda index: (index[0], 
            timezone('UTC').localize(datetime.datetime.fromtimestamp(index[1])).astimezone(timezone('US/Pacific')).strftime("%m/%d/%Y, %H:%M:%S")
            ), indicies)
        )
    await ctx.send(formattedIndicies)

@client.command(pass_context=True)
@commands.check(hasPermissions)
async def getDupeCount(ctx):
    dupeCount = dom.getDupeCount()
    await ctx.send(dupeCount)

@client.command(pass_context=True)
@commands.check(hasPermissions)
async def report(ctx, *args):
    if(len(args) == 0):     
        await ctx.send("Showing Frag Report Since Last Interval")
        report = task.craftLastMessage(dom)
    elif(len(args) == 1):
        since = int(args[0])
        await ctx.send("Showing Frag Report Over Last %s Intervals" % since)
        report = task.craftMessageSince(dom, since)
    elif(len(args) == 2):
        prev = int(args[0])
        cur = int(args[1])
        report = task.craftMessage(dom, prev, cur)
        await ctx.send("Showing Frag Report Between Intervals %s and %s" % (prev, cur))
    await ctx.send(report)

### CHANNEL COMMANDS ###
@client.command(pass_context=True)
@commands.check(hasPermissions)
async def broadcast(ctx):
    channelIds = dom.getChannels()
    await ctx.send("trying to send message to %s channels" % len(channelIds))
    for channelId in channelIds:
        try:
            await client.get_channel(channelId[0]).send("Sending message via on demand messanger to channel with id %s"  % channelId)
        except:
            await ctx.send("message send failed for channel with id %s" % channelId)

@client.command(pass_context=True, name="send-here")
@commands.check(hasPermissions)
async def sendHere(ctx):
    channel = ctx.channel.id
    dom.registerChannel(channel)
    await ctx.send("channel registered for discord server")

@client.command(pass_context=True, name="clear-channels")
@commands.check(hasPermissions)
async def clearChannels(ctx):
    dom.clearChannels()
    channels = dom.getChannels()
    await ctx.send("Channels cleared, current channels %s" % channels)

### SERVER COMMANDS ###
@client.command(pass_context=True, name="setup-server")
@commands.check(hasPermissions)
async def setup_server(ctx):
    #Create Channels - Reports + Stats Channel
    #Create Roles
    #guild = ctx.guild
    #await guild.create_role(name="")
    await ctx.send("Not Implemented Yet")

### SYS-ADMIN COMMANDS ###
@client.command(pass_context=True)
@commands.check(isSysAdmin)
async def init(ctx):
    await ctx.send("Resetting database")
    dom.createDatabaseTables()
    users = dom.getUsers()
    await ctx.send("Database reset, current users: %s" + users)    

@client.command(pass_context = True)
async def whoami(ctx):
    if ctx.message.author.guild_permissions.administrator:
        msg = "You're an admin {0.author.mention}".format(ctx.message)  
        await ctx.send(msg)
    else:
        msg = "You're an average joe {0.author.mention}".format(ctx.message)  
        await ctx.send(msg)

client.run(env_variables.token())