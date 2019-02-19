# Work with Python 3.6
import discord

with open('token.txt', 'r') as f:
    TOKEN = f.read().strip()

client = discord.Client()

class Command:

    def on_message(self, message):
        pass

    def on_reaction_add(self, reaction, user):
        pass

    def on_reaction_remove(self, reaction, user):
        pass

class Consume(Command):

    async def on_message(self, message):
        if message.author == client.user:
            return

        if message.content.startswith('!consume') and (message.channel.name == 'consumption' or message.channel.name == 'bot-testing'):
            if '@' in message.content:
                msg = "Hey don't do that"
                await client.send_message(message.channel, msg)
                return
            args = message.content.split()[1:]
            if (len(args) == 0 or args[0] == "help"):
                msg = "Consumption syntax: !consume <time> [location] [comment]"
                await client.send_message(message.channel, msg)
            else:
                consumptions.append(Consumption(message.author, args[0], location=(args[1] if len(args) >= 2 else ""), comment = (" ".join(args[2:]) if len(args) >= 3 else "")))
                msg = consumptions[-1].print_consumption()
                consumptions[-1].add_message(await client.send_message(message.channel, msg))
                emoji = discord.utils.get(client.get_all_emojis(), name=CONSUME_EMOJI)
                late_emoji = discord.utils.get(client.get_all_emojis(), name=LATE_EMOJI)
                await client.add_reaction(consumptions[-1].message, emoji)
                await client.add_reaction(consumptions[-1].message, late_emoji)
                await client.delete_message(message)

    async def on_reaction_add(self, reaction, user):
        if user == client.user:
            return

        if reaction.message.author == client.user:
            consumption = get_consumption_by_message(reaction.message)
            if consumption == None:
                return
            emoji = discord.utils.get(client.get_all_emojis(), name=CONSUME_EMOJI)
            late_emoji = discord.utils.get(client.get_all_emojis(), name=LATE_EMOJI)
            cancel_emoji = discord.utils.get(client.get_all_emojis(), name=CANCEL_EMOJI)
            if reaction.emoji == emoji:
                if user == consumption.author:
                    if consumption.author not in consumption.consumers:
                        consumption.add_consumer(user)
                    await client.remove_reaction(consumption.message, emoji, client.user)
                else:
                    consumption.add_consumer(user)
                    await client.edit_message(consumption.message, consumption.print_consumption())
            elif reaction.emoji == late_emoji:
                consumption.add_late_consumer(user)
                if len(consumption.lates) > 0:
                    await client.remove_reaction(consumption.message, late_emoji, client.user)
                await client.edit_message(consumption.message, consumption.print_consumption())
            elif reaction.emoji == cancel_emoji and user == consumption.author:
                await client.delete_message(consumption.message)
                consumptions.remove(consumption)
                
    async def on_reaction_remove(self, reaction, user):
        if user == client.user:
            return

        if reaction.message.author == client.user:
            consumption = get_consumption_by_message(reaction.message)
            if consumption == None:
                return
            emoji = discord.utils.get(client.get_all_emojis(), name=CONSUME_EMOJI)
            late_emoji = discord.utils.get(client.get_all_emojis(), name=LATE_EMOJI)
            if reaction.emoji == emoji:
                if user == consumption.author:
                    await client.add_reaction(consumption.message, emoji)
                consumption.remove_consumer(user)
                await client.edit_message(consumption.message, consumption.print_consumption())
            elif reaction.emoji == late_emoji:
                consumption.remove_late_consumer(user)
                if len(consumption.lates) == 0:
                    await client.add_reaction(consumption.message, late_emoji)
                await client.edit_message(consumption.message, consumption.print_consumption())

class CollegeChants:

    async def on_message(self, message):
        if message.author == client.user:
            return

        msg = ""
        if message.content.upper().startswith('!ENGR'):
            msg = "BETTER THAN. YOU ARE."
        elif message.content.upper().startswith('!CMNS'):
            msg = "C-M. N-S. WE ARE. THE BEST."
        elif message.content.upper().startswith('!BSOS'):
            msg = "WHAT KIND OF SAUCE? B-SAUCE"
        elif message.content.upper().startswith('!ARHU'):
            msg = "i have no idea"

        if msg != "":
            await client.send_message(message.channel, msg)

class Consumption:

    def __init__(self, author, time, location="", comment=""):
        self.author = author
        self.consumers = [author]
        self.time = time
        self.location = location
        self.comment = comment
        self.lates = []

    def add_consumer(self, consumer):
        if (consumer == client.user):
            return
        self.consumers.append(consumer)
        self.consumers = list(set(self.consumers))

    def add_late_consumer(self, consumer):
        if consumer == client.user:
            return
        self.lates.append(consumer)

    def remove_late_consumer(self, consumer):
        if consumer == client.user:
            return
        self.lates.remove(consumer)

    def remove_consumer(self, consumer):
        if (consumer == client.user):
            return
        self.consumers.remove(consumer)

    def print_consumption(self):
        to_ret = "Consume at " + self.time + "\n"
        to_ret += "Consumers: " + (", ".join([con.display_name for con in self.consumers]) if len(self.consumers) > 0 else "No one yet")
        if len(self.lates) != 0:
            to_ret += "\nLate Consumers: " + ", ".join([late.display_name for late in self.lates])
        if self.location != "":
            to_ret += "\nLocation: " + self.location
        if self.comment != "":
            to_ret += "\n" + self.comment
        return to_ret

    def add_message(self, message):
        self.message = message

consumptions = []

CONSUME_EMOJI = "mao"
LATE_EMOJI = "daddyloh"
CANCEL_EMOJI = "downmao"

consume_command = Consume()
chants = CollegeChants()

def get_consumption_by_message(message):
    for con in consumptions:
        if message.id == con.message.id:
            return con
    return None

@client.event
async def on_message(message):
    await consume_command.on_message(message)
    await chants.on_message(message)
    
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_reaction_add(reaction, user):
    await consume_command.on_reaction_add(reaction, user)
    
@client.event
async def on_reaction_remove(reaction, user):
    await consume_command.on_reaction_remove(reaction, user)
    
client.run(TOKEN)
