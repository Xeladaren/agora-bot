import discord
import config

def senPlayerMsg(pseudo, msg):
    webhook = discord.Webhook.from_url(config.webhookURL, adapter=discord.RequestsWebhookAdapter())
    webhook.send(msg, username=pseudo)
