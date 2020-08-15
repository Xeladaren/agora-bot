import discord
import aiohttp
import time
import asyncio
import os
import _thread
import config



def checkFile():

    fileMTime = 0

    while True :
        stat = os.stat("./test.log") # check si le fichier à été modifier.
        if fileMTime != stat.st_mtime :
            fileMTime = stat.st_mtime
            print("file modif !!")
        time.sleep(1)

client = discord.Client()
webhook = discord.Webhook.from_url(config.webhookURL, adapter=discord.RequestsWebhookAdapter())

_thread.start_new_thread(checkFile, ())

@client.event
async def on_message(message):

    msg = "["+message.channel.name+"]<"+message.author.name+"> "+message.content
    print(msg)

    guildMember = message.guild.get_member(message.author.id)

    if guildMember :
        print("Name : ", guildMember.name)
        print("Nick : ", guildMember.nick)

    if not message.author.bot :

        if message.content == "Salon" :
            sendMsg = ""
            for channel in message.guild.channels :
                sendMsg += channel.name + "\n"
            await message.channel.send(sendMsg)

        if message.content == "Bonjour" :
            sendMsg = "Coucou " + message.author.mention
            await message.channel.send(sendMsg)

        if message.channel.name == "chat-minecraft":
            pseudo = guildMember.name
            if guildMember.nick != None:
                pseudo = guildMember.nick

            webhook.send(message.content, username=pseudo)

client.run(config.token)
