from analyzertools import analyzer, loader
import discord
from db import SqlLiteDom
import env_variables


client = discord.Client()
@client.event
async def on_ready():
    try:
        dom = SqlLiteDom(env_variables.dbFilename())
        loader.storeAndIncrement(dom)
        channelIds = dom.getChannels()
        message = analyzer.craftMessageSince(dom, 1)
        for channelId in channelIds:
            await client.get_channel(channelId[0]).send(message)
    finally:
        await client.close()
    
client.run(env_variables.token())