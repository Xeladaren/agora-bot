import discord
import config
import Minecraft

client = discord.Client()

def senPlayerMsg(pseudo, msg):
    webhook = discord.Webhook.from_url(config.webhookURL, adapter=discord.RequestsWebhookAdapter())
    webhook.send(msg, username=pseudo)

def startBot():
    client.run(config.token)

@client.event
async def on_message(message):

    if not message.author.bot :

        if message.channel.name == config.channelName:

            guildMember = message.guild.get_member(message.author.id)

            pseudo = guildMember.name
            if guildMember.nick :
                pseudo = guildMember.nick

            msg = message.content

            Minecraft.sayOnChat(pseudo, msg)
