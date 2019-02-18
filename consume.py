# Work with Python 3.6
import discord

TOKEN = 'NTQ3MTgxMDcxNjMzMDg4NTEy.D0zGKA.Z97_Zz1rm3cqdVCOdMrH_VT6TCc'

client = discord.Client()

class Consumption:

    def __init__(self, consumers, time, location="", comment=""):
        self.consumers = consumers
        self.time = time
        self.location = location
        self.comment = comment

    def add_consumer(self, consumer):
        if (consumer == client.user):
            return
        self.consumers.append(consumer.split('#')[0])

    def print_consumption(self):
        to_ret = "Consume @" + self.time + "\n"
        to_ret += "Consumers: " + " ".join(self.consumers)
        if self.location != "":
            to_ret += "\nLocation: " + self.location
        if self.comment != "":
            to_ret += "\n" + self.comment
        return to_ret

    def add_message(self, message):
        self.message = message

consumptions = []

CONSUME_EMOJI = discord.utils.get(client.get_all_emojis(), name="mao")

print(CONSUME_EMOJI)

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('!consume'):
        args = message.content.split()[1:]
        if (args[0] == "help"):
            msg = "Consumption syntax: !consume <time> [location] [comment]"
            await client.send_message(message.channel, msg)
        else:
            consumptions.append(Consumption([str(message.author).split('#')[0]], args[0], location=(args[1] if len(args) <= 2 else ""), comment = (" ".join(args[2:]) if len(args) <= 3 else "")))
            msg = consumptions[-1].print_consumption()
            consumptions[-1].add_message(await client.send_message(message.channel, msg))
            await client.add_reaction(consumptions[-1].message, CONSUME_EMOJI)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(TOKEN)
print("hi")
