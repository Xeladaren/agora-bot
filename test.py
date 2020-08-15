import discord
import aiohttp
import time
import asyncio

import config

client = discord.Client()

@client.event
async def on_message(message):
#    print("Author : ", message.author)
#    print("Type : ", message.type)
#    print("Channel : ", message.channel)
#    print("Content : ", message.content)

#    for attachment in message.attachments :
#        print("Attachment : ", attachment)

    msg = "["+message.channel.name+"]<"+message.author.name+"> "+message.content
    print(msg)

    if not message.author.bot :
        if message.content == "Bonjour" :
            sendMsg = "Coucou " + message.author.mention
            await message.channel.send(sendMsg)

async def runCli() :
    print("login")
    await client.login(config.token, bot=True)
    print("connect")
    await client.connect(reconnect=True)


loop = asyncio.get_event_loop()
loop.run_until_complete(runCli())

webhook = discord.Webhook.from_url(config.webhookURL, adapter=discord.RequestsWebhookAdapter())
webhook.send('Hello World', username='Xeladaren')
