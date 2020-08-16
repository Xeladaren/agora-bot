import discord
import config
import Minecraft
import asyncio

client = discord.Client()

def sendPlayerMsg(pseudo, msg):

    print("[INFO] say on discord : <"+pseudo+"> "+msg)

    webhook = discord.Webhook.from_url(config.webhookURL, adapter=discord.RequestsWebhookAdapter())
    webhook.send(msg, username=pseudo)


def startBot():
    client.run(config.token)

def sendBotMsg(msg):
    for channel in client.get_all_channels():
        if channel.name == config.channelName :
            future = asyncio.run_coroutine_threadsafe(channel.send(msg), client.loop)
            future.result()

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
