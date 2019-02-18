# Work with Python 3.6
import discord

TOKEN = 'NTQ3MTgxMDcxNjMzMDg4NTEy.D0zGKA.Z97_Zz1rm3cqdVCOdMrH_VT6TCc'

client = discord.Client()

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('!hello'):
        msg = 'Hello {0.author.mention}'.format(message)
        await client.send_message(message.channel, msg)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)
