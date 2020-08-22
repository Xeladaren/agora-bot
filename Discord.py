import discord
import config
import Minecraft
import asyncio

client = discord.Client()

def sendPlayerMsg(pseudo, msg):

    print("[INFO] say on discord : <"+pseudo+"> "+msg)

    webhook = discord.Webhook.from_url(config.webhookURL, adapter=discord.RequestsWebhookAdapter())

    defaultHeadURL = "https://i.imgur.com/kHXRnzX.png" # steve head

    webhook.send(msg, username=pseudo, avatar_url=defaultHeadURL)


def startBot():
    client.run(config.token)

def sendBotMsg(msg):
    future = asyncio.run_coroutine_threadsafe(__sendBotMsg(msg), client.loop)

async def __sendBotMsg(msg):
    for channel in client.get_all_channels():
        if channel.name == config.channelName :
                await channel.send(msg)
                await __updateTopic(channel)

async def __updateTopic(channel, playersInfo=None):
    print("[INFO] update channel topic")
    if playersInfo == None:
        playersInfo = Minecraft.getPlayersList()

    if playersInfo != None :
        topic = ""
        if playersInfo["count"] > 1:
            topic += "Joueurs en ligne "
        else:
            topic += "Joueur en ligne "

        topic += str(playersInfo["count"])
        topic += "/"
        topic += str(playersInfo["max"])
        topic += config.channelTopicSufix

        print("[INFO] new topic on (", channel.name, ") :", topic)

        out = await channel.edit(topic=topic)
        print("channel edit return :", out)

async def parseCommands(message) :
    print("[INFO] discord command :", message.content)
    command = message.content.split(" ")

    if ( "list" in command or "liste" in command ) and message.channel.name == config.channelName:
        playersList = Minecraft.getPlayersList()
        msg = "Il y a "+str(playersList["count"])
        if playersList["count"] > 1:
            msg += " joueurs "
        else :
            msg += " joueur "
        msg += "connecté sur "+str(playersList["max"])

        if playersList["count"] > 0 :
            msg += " : \n"

        for player in playersList["list"] :
            msg += "\t - "+player+"\n"

        await message.channel.send(msg)
        await __updateTopic(message.channel, playersInfo=playersList)

@client.event
async def on_message(message):

    if not message.author.bot :

        if client.user in message.mentions:
            await parseCommands(message)

        elif message.channel.name == config.channelName:

            guildMember = message.guild.get_member(message.author.id)

            pseudo = guildMember.name
            if guildMember.nick :
                pseudo = guildMember.nick

            for msgLine in message.content.split("\n") :
                Minecraft.sayOnChat(pseudo, msgLine)
