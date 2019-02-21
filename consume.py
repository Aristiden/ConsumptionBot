# Work with Python 3.6
import discord
import random
import cowsay
import re
import time
import asyncio
from pytz import timezone
from datetime import datetime
from io import StringIO
import sys

with open('token.txt', 'r') as f:
    TOKEN = f.read().strip()

client = discord.Client(max_messages=100)

class Command:

    async def on_message(self, message):
        pass

    async def on_reaction_add(self, reaction, user):
        pass

    async def on_reaction_remove(self, reaction, user):
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
                consumption = consumptions[-1]
                emoji = discord.utils.get(client.get_all_emojis(), name=CONSUME_EMOJI)
                late_emoji = discord.utils.get(client.get_all_emojis(), name=LATE_EMOJI)
                await client.add_reaction(consumptions[-1].message, emoji)
                await client.add_reaction(consumptions[-1].message, late_emoji)
                await client.delete_message(message)
                t = parse_time(args[0])
                await asyncio.sleep(t)
                consumers = consumption.get_consumers()
                msg = ""
                for consumer in consumers:
                    msg+="<@!"+consumer.id+"> "
                await client.send_message(message.channel, msg)

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
                else:
                    consumption.add_consumer(user)
                await client.edit_message(consumption.message, consumption.print_consumption())
                if user == consumption.author:
                    await client.remove_reaction(consumption.message, emoji, client.user)
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
                consumption.remove_consumer(user)
                if len(consumption.consumers) == 0:
                    await client.add_reaction(consumption.message, emoji)
                await client.edit_message(consumption.message, consumption.print_consumption())
            elif reaction.emoji == late_emoji:
                consumption.remove_late_consumer(user)
                if len(consumption.lates) == 0:
                    await client.add_reaction(consumption.message, late_emoji)
                await client.edit_message(consumption.message, consumption.print_consumption())

class CollegeChants(Command):

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

class Communism(Command):

    async def on_message(self, message):
        if message.author == client.user:
            return
        bad_words = list(REPLACEMENTS.keys())
        msg = ""
        for word in message.content.split():
            if word.lower() in bad_words:
                msg += "*" + REPLACEMENTS[word.lower()] + " "
        if msg != "":
            await client.send_message(message.channel, msg)

class RandomMao(Command):

    async def on_message(self, message):
        if message.author == client.user:
            return
        if random.random() < .05:
            emoji = discord.utils.get(client.get_all_emojis(), name="mao")
            await client.add_reaction(message, emoji)
        if random.random() < .05:
            await client.send_typing(message.channel)

class Cowsay(Command):

    async def on_message(self, message):
        if message.author == client.user:
            return
        if message.content.lower().startswith("!cowsay"):
            say =  " ".join(message.content.split()[1:])
            old_stdout = sys.stdout
            sys.stdout = mystdout = StringIO()
            cowsay.cow(say)
            sys.stdout = old_stdout
            msg = "```" + mystdout.getvalue() + "```"
            for i in range(len(msg)):
                if msg[i] == '/' and msg[i - 1] == '\\':
                    msg = msg[:i + 1] + '\\\n' + ((7 + (len(say) if len(say) < 49 else 49) - 2) * ' ') + msg[i + 1:]
                    break
            await client.send_message(message.channel, msg)

class Roll(Command):

    async def on_message(self, message):
        if message.author == client.user:
            return
        if message.content.lower().startswith("!roll"):
            try:
                try:
                    die_str = message.content.split()[1]
                except IndexError:
                    msg = "Syntax is !roll d<number>."
                    await client.send_message(message.channel, msg)
                    return
                if die_str[0] == 'd':
                    die_str = die_str[1:]
                die = int(die_str)
                if die < 1:
                    msg = die + " is not a die."
                else:
                    roll = random.randint(1, die)
                    msg = "It's " + str(roll) + "."
                    if roll == 1:
                        msg += " Sucks to be you."
                    elif roll == die:
                        msg += " Crit!"                    
            except ValueError:
                msg = "Please input a number next time."
            await client.send_message(message.channel, msg)

class Kenobi(Command):

    async def on_message(self, message):
        if message.author == client.user:
            return
        if "hello there" in message.content.lower():
            await client.send_message(message.channel, "General Kenobi")

class Wack(Command):

    async def on_message(self, message):
        if message.author == client.user:
            return
        if "wack" in message.content.lower():
            await client.send_file(message.channel, "wack.png")

class Quote(Command):
    
    async def on_message(self, message):
        if message.author == client.user:
            return
        if message.content.lower().startswith("!quote"):
            quote = re.sub(r'\n+', '\n', message.content.replace("```", "")).split(' ')
            msg = ""
            if len(quote)==1:
                count = 1
                async for log in client.logs_from(message.channel, limit=2):
                    if count>1:
                        lastMessage = log
                    count+=1
                lastMessageContent = re.sub(r'\n+', '\n', lastMessage.content.replace("```", ""))
                lastMessageAuthor = lastMessage.author
                quote = lastMessageAuthor.display_name+": "+lastMessageContent
                quote = quote.split(' ')
            else:
                if quote[1].lower() == "help":
                    await client.send_message(message.channel, "!quote [quote]\nIf no quote provided, the last message in the channel is used")
                    return
                quote.pop(0)
            quoteString = ' '.join(quote)
            quotecat = datetime.now(timezone('US/Eastern')).strftime('%d %b %Y, %I:%M%p')+'\n'+quoteString
            quotecat = quotecat+"\n"
            try:
                if message.channel!="bot-testing":
                    line_prepender("quotes.txt", quotecat)
                msg = "Quote added on "+datetime.now().strftime('%d %b %Y, %I:%M%p')
                msg += "\n```\n"+quoteString+"```"
            except:
                msg = "Problem with quote encoding"
            await client.send_message(message.channel, msg)
            await client.delete_message(message)

class GetQuote(Command):

    async def on_message(self, message):
        if message.author == client.user:
            return
        if message.content.lower().startswith("!getquote"):
            content = message.content.split(' ')
            if len(content)==1:
                quoteFile = open("quotes.txt", "r", -1, "utf-8")
                quoteString = quoteFile.read()
                quoteFile.close()
                quotes = quoteString.split("\n\n")
                randQuote = random.choice(quotes)
                time = randQuote.split("\n")[0]
                randQuote = randQuote.split("\n")
                randQuote.pop(0)
                randQuote = "\n".join(randQuote)
                await client.send_message(message.channel, time+"```"+randQuote+"```")
            

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

    def get_consumers(self):
        return self.consumers

consumptions = []

REPLACEMENTS = {"my": "our", "i": "we", "me": "us", "mine": "ours"}

CONSUME_EMOJI = "mao"
LATE_EMOJI = "daddyloh"
CANCEL_EMOJI = "downmao"

commands = [Consume(), CollegeChants(), RandomMao(), Cowsay(), Roll(), Kenobi(), Wack(), Quote(), GetQuote()]

def get_consumption_by_message(message):
    for con in consumptions:
        if message.id == con.message.id:
            return con
    return None

@client.event
async def on_message(message):
    for comm in commands:
        await comm.on_message(message)
    
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_reaction_add(reaction, user):
    for comm in commands:
        await comm.on_reaction_add(reaction, user)
    
@client.event
async def on_reaction_remove(reaction, user):
    for comm in commands:
        await comm.on_reaction_remove(reaction, user)

def line_prepender(filename, line):
    with open(filename, 'r+', -1, "utf-8") as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line + '\n' + content)

def parse_time(t):
    return int(t)

client.run(TOKEN)
