import discord
import config
import Minecraft
import asyncio
import json

client = discord.Client()

def sendPlayerMsg(pseudo, msg):

    print("[INFO] say on discord : <"+pseudo+"> "+msg)

    webhook = discord.Webhook.from_url(config.webhookURL, adapter=discord.RequestsWebhookAdapter())

    defaultHeadURL = "https://i.imgur.com/kHXRnzX.png" # steve head

    playersDBFile = open('playersDB.json', 'r')
    playersDB = json.loads(playersDBFile.read())
    playersDBFile.close()

    for playerData in playersDB :
        if playerData['minecraft-pseudo'] == pseudo :
            if playerData['minecraft-head-url'] != "":
                defaultHeadURL = playerData['minecraft-head-url']

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

    if "help" in command :
        msg = "Les commandes disponibles sont :\n"
        msg += "\n**help** : affiche cette aide."

        if message.channel.name == config.channelName :
            msg += "\n**list** : affiche la liste des joueurs connecté."
            msg += "\n**stats** : affiche les stats serveur."

        await message.channel.send(msg)

    elif "list" in command and message.channel.name == config.channelName:
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

    elif "stats" in command and message.channel.name == config.channelName :
        servStat = Minecraft.serverStat()

        msg = "Serveur status :\n"

        if servStat["alive"]:
            msg += "**Minecraft** : ON\n"
            if (servStat["tps1m"] != -1) and (servStat["tps5m"] != -1) and (servStat["tps15m"] != -1):
                msg += "**Minecraft TPS** : "+str(servStat["tps1m"])+"(1m) "+str(servStat["tps5m"])+"(5m) "+str(servStat["tps15m"])+"(15m)\n"
        else :
            msg += "**Minecraft** : OFF\n"

        if (servStat["cpuUse"] != -1):
            msg += "**Utilisation CPU** : "+str(servStat["cpuUse"])+" %\n"

        if (servStat["memUse"] != -1) and (servStat["memTot"] != -1):
            msg += "**Utilisation Memoire** : "+str(round(servStat["memUse"] / 10**9, 2))+" Go / "+str(round(servStat["memTot"] / 10**9, 2))+" Go\n"

        if (servStat["diskUse"] != -1) and (servStat["diskTot"] != -1):
            msg += "**Utilisation Disque** : "+str(round(servStat["diskUse"] / 10**9, 2))+" Go / "+str(round(servStat["diskTot"] / 10**9, 2))+" Go\n"

        await message.channel.send(msg)

    elif "debug" in command :
        for member in message.channel.members :
            print(member.name, member.nick)


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
