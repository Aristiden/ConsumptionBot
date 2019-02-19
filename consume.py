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
        self.consumers.append(consumer.nick)
        self.consumers = list(set(self.consumers))

    def remove_consumer(self, consumer):
        if (consumer == client.user):
            return
        self.consumers.remove(consumer.nick)

    def print_consumption(self):
        to_ret = "Consume at " + self.time + "\n"
        to_ret += "Consumers: " + (", ".join(self.consumers) if len(self.consumers) > 0 else "No one yet")
        if self.location != "":
            to_ret += "\nLocation: " + self.location
        if self.comment != "":
            to_ret += "\n" + self.comment
        return to_ret

    def add_message(self, message):
        self.message = message

consumptions = []

CONSUME_EMOJI = "mao"

def get_consumption_by_message(message):
    for con in consumptions:
        if message.id == con.message.id:
            return con
    return None

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('!consume'):
        if '@' in message.content:
            msg = "Hey don't do that"
            await client.send_message(message.channel, msg)
            return
        args = message.content.split()[1:]
        if (len(args) == 0 or args[0] == "help"):
            msg = "Consumption syntax: !consume <time> [location] [comment]"
            await client.send_message(message.channel, msg)
        else:
            consumptions.append(Consumption([str(message.author.nick)], args[0], location=(args[1] if len(args) >= 2 else ""), comment = (" ".join(args[2:]) if len(args) >= 3 else "")))
            msg = consumptions[-1].print_consumption()
            consumptions[-1].add_message(await client.send_message(message.channel, msg))
            emoji = discord.utils.get(client.get_all_emojis(), name=CONSUME_EMOJI)
            await client.add_reaction(consumptions[-1].message, emoji)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_reaction_add(reaction, user):
    print("rteaction")
    if user == client.user:
        return
    if reaction.message.author == client.user:
        print("in in")
        consumption = get_consumption_by_message(reaction.message)
        if consumption == None:
            return
        emoji = discord.utils.get(client.get_all_emojis(), name=CONSUME_EMOJI)
        print(reaction.emoji == emoji)
        if reaction.emoji == emoji:
            consumption.add_consumer(user)
            await client.edit_message(consumption.message, consumption.print_consumption())

@client.event
async def on_reaction_remove(reaction, user):
    if user == client.user:
        return
    if reaction.message.author == client.user:
        print("in in")
        consumption = get_consumption_by_message(reaction.message)
        if consumption == None:
            return
        emoji = discord.utils.get(client.get_all_emojis(), name=CONSUME_EMOJI)
        print(reaction.emoji == emoji)
        if reaction.emoji == emoji:
            consumption.remove_consumer(user)
            await client.edit_message(consumption.message, consumption.print_consumption())

client.run(TOKEN)
print("hi")
