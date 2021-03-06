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

with open('points.txt', 'r') as f:
    points = int(f.read().strip())

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
        if message.channel.name == "consumption":
            await client.purge_from(message.channel, limit=100, check=not_self)
            
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
                t = parse_time(args[0])
                if t==None:
                    await client.send_message(message.channel, "Invalid time")
                    return
                consumptions.append(Consumption(message.author, args[0], location=(args[1] if len(args) >= 2 else ""), comment = (" ".join(args[2:]) if len(args) >= 3 else "")))
                msg = consumptions[-1].print_consumption()
                consumptions[-1].add_message(await client.send_message(message.channel, msg))
                consumption = consumptions[-1]
                emoji = discord.utils.get(client.get_all_emojis(), name=CONSUME_EMOJI)
                late_emoji = discord.utils.get(client.get_all_emojis(), name=LATE_EMOJI)
                cancel_emoji = discord.utils.get(client.get_all_emojis(), name=CANCEL_EMOJI)
                await client.add_reaction(consumptions[-1].message, emoji)
                await client.add_reaction(consumptions[-1].message, late_emoji)
                await asyncio.sleep(t)
                if get_consumption_by_message(consumption.message)==None:
                    return
                consumers = consumption.get_consumers()
                msg = ""
                for consumer in consumers:
                    msg+="<@!"+consumer.id+"> "
                msg+="\nIt's time to consume"
                if len(consumption.location) >=1:
                    msg+=" at "+consumption.location+"\n"+consumption.comment
                consumption.started = True
                await client.send_message(message.channel, msg)
                await client.add_reaction(consumption.message, cancel_emoji)

    async def on_reaction_add(self, reaction, user):
        global points
        
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
                    if len(consumption.consumers) == 2:
                        await client.send_message(consumption.author, "Someone has joined your consumption!")
                await client.edit_message(consumption.message, consumption.print_consumption())
                if user == consumption.author:
                    await client.remove_reaction(consumption.message, emoji, client.user)
            elif reaction.emoji == late_emoji:
                consumption.add_late_consumer(user)
                if len(consumption.lates) > 0:
                    await client.remove_reaction(consumption.message, late_emoji, client.user)
                await client.edit_message(consumption.message, consumption.print_consumption())
            elif reaction.emoji == cancel_emoji and user.id == consumption.author.id:
                if consumption.started:
                    new_points = sum([1 for consumer in consumption.consumers]) + sum([1 for consumer in consumption.lates])
                    points += new_points
                    await client.edit_message(consumption.message, "This consumption earned " + str(new_points) +
                                              " point" + ("" if new_points == 1 else "s") + " for the collective.")
                    consumptions.remove(consumption)
                    with open('points.txt', 'w') as f:
                        f.write(str(points))
                else:
                    await client.edit_message(consumption.message, "Consumption canceled.")
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
        if message.channel.name == "general" and random.random()< .005:
            quoteFile = open("chairman.txt", "r", -1, "utf-8")
            quoteString = quoteFile.read()
            quoteFile.close()
            quotes = quoteString.split("\n\n")
            randQuote = random.choice(quotes)
            splitQuote = randQuote.split(" ")
            users = [user for user in client.get_all_members()]
            random.shuffle(users)
            for i in range(len(splitQuote)):
                if splitQuote[i] == "@user":
                    newUser = users.pop()
                    if newUser == client.user:
                        newUser = users.pop()
                    splitQuote[i] = "<@!"+newUser.id+">"
            quote = " ".join(splitQuote)
            await client.send_typing(message.channel)
            await asyncio.sleep(5)
            await client.send_typing(message.channel)
            await asyncio.sleep(5)
            await client.send_typing(message.channel)
            await asyncio.sleep(5)
            await client.send_message(message.channel, quote)
            
class Cowsay(Command):

    async def on_message(self, message):
        global points
        
        if message.author == client.user:
            return
        if message.content.lower().startswith("!cowsay"):
            if points < 1:
                await client.send_message(message.channel, "Additional consumptions required.")
                return
            points -= 1
            update_points()
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
        global points
        
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
                amount = 1
                die_parts = die_str.split("d")
                if len(die_parts) >= 2:
                    amount = int(die_parts[0])
                    die = int(die_parts[1])
                else:
                    die = int(die_parts[0])
                if amount>1000:
                    msg = "Too many dice. They fell out of my hand."
                elif die < 1 or amount < 1:
                    msg = die + " is not a die."
                else:
                    roll = 0
                    roll_str = "("
                    for i in range(amount):
                        t_roll = random.randint(1, die)
                        roll += t_roll
                        roll_str += str(t_roll)
                        if i!=amount-1:
                            roll_str+= "+"
                    roll_str += ")"
                    msg = "It's " + str(roll) + "."
                    if amount>1:
                        msg+= " "+roll_str
                    if roll == amount:
                        msg += " Sucks to be you."
                    elif roll == amount*die:
                        msg += " Crit!"
                    if message.channel.name !="dnd":
                        if points>=1:
                            if roll == amount:
                                msg += "\nUp to "+str(die*amount)+" points used."
                                points-=die*amount
                                if points < 0:
                                    points = 0
                            elif roll == amount*die:
                                msg += "\n"+str(die*amount)+" points gained."
                                points+=die*amount
                            else:
                                msg += "\n1 point used."
                                points-=1
                            update_points()
                        else:
                            await client.send_message(message.channel, "More consumptions required.")
                            return
            except ValueError:
                msg = "Please input a number next time."
            try:
                await client.send_message(message.channel, msg)
            except:
                await client.send_message(message.channel, msg.replace(roll_str, ""))

class Kenobi(Command):

    async def on_message(self, message):
        if message.author == client.user:
            return
        if "hello there" in message.content.lower():
            await client.send_message(message.channel, "General Kenobi")

class Wack(Command):

    async def on_message(self, message):
        global points
        
        if message.author == client.user:
            return
        if "wack" in message.content.lower():
            if points >= 1:
                await client.send_file(message.channel, "wack.png")
                points -= 1
                update_points()
            else:
                await client.send_message(message.channel, "Additional consumptions required.")

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
                if message.channel.name!="bot-testing":
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

class Lootbox(Command):

    async def on_message(self, message):
        global points

        if message.author == client.user:
            return
        if message.content.lower().startswith('!lootbox'):
            if points >= 3:
                msg = "Lootbox purchased for 3 point.\nOpening box..."
                await client.send_message(message.channel, msg)
                await client.send_file(message.channel, "lootbox.gif")
                points -= 3
                roll = random.randint(1,100)
                if roll<=10:
                    msg = "The lootbox is empty."
                    await client.send_message(message.channel, msg)
                elif roll<=40:
                    msg = "The lootbox contains 1 point."
                    await client.send_message(message.channel, msg)
                    points+=1
                elif roll<=65:
                    msg = "The lootbox contains 2 points."
                    await client.send_message(message.channel, msg)
                    points+=2
                elif roll<=80:
                    msg = "The lootbox contains 3 points."
                    await client.send_message(message.channel, msg)
                    points+=3
                elif roll<=90:
                    msg = "The lootbox contains 4 points."
                    await client.send_message(message.channel, msg)
                    points+=4
                else:
                    await client.send_message(message.channel,"The lootbox contains a cosmetic item!")
                    randline = random.choice([2,3,4,5,6,7,8,9,11,12,13,14,16,17,18,20,21])
                    cos = open("cosmetics.txt","r")
                    cosmetics = cos.readlines()
                    cosmetics2 = cosmetics[randline].split(" ")
                    if cosmetics2[0]==1:
                        msg = "It was a duplicate. You get 2 points back."
                        await client.send_message(message.channel, msg)
                        points+=2
                    else:
                        msg = cosmetics2[1]," was collected."
                        await client.send_message(message.channel, msg)
                        cos = open("cosmetics.txt","w")
                        cosmetics2[0] = 1
                        cosmetics[randline] = cosmetics2
                        cos.writelines( cosmetics )
                    cos.close()
                update_points()
            else:
                await client.send_message(message.channel, "Additional consumptions required.")
class GetLoot(Command):

    async def on_message(self, message):
        global points

        if message.author == client.user:
            return
        if message.content.lower().startswith("!loot"):
            if points>=1:
                points-=1
                msg = "1 point spent to peek at my cosmetic items."
                await client.send_message(message.channel, msg)
                cos = open("cosmetics.txt","r")
                cosmetics = cos.readlines()
                await client.send_message(message.channel, cosmetics)
                cos.close()
            else:
                await client.send_message(message.channel, "Additional consumptions required.")                
            
class Points(Command):

    async def on_message(self, message):
        global points
        
        if message.author == client.user:
            return

        if message.content.lower().startswith("!points"):
            if points >= 1:
                points -= 1
                msg = "The collective currently has " + str(points) + " point" + ("" if points == 1 else "s") + "."
                await client.send_message(message.channel, msg)
                update_points()
            else:
                await client.send_message(message.channel, "Additional consumptions required.")

class Consumption:

    def __init__(self, author, time, location="", comment=""):
        self.author = author
        self.consumers = [author]
        self.time = time
        self.location = location
        self.comment = comment
        self.lates = []
        self.started = False


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

commands = [Consume(), CollegeChants(), Cowsay(), Roll(), Kenobi(), Wack(), Quote(), GetQuote(), Points(), RandomMao()]

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
    try:
        parts = t.split(":")
        h = int(parts[0])
        m = int(parts[1][:2])
        ch = datetime.now().hour%12
        cm = datetime.now().minute
        cs = datetime.now().second
        hours = (h+m/60)-(ch+cm/60+cs/60/60)
        if abs(hours)<1/60:
            return 0
        if hours<0:
            hours+=12
        seconds = hours*60*60
        return seconds
    except:
        return None

def not_self(message):
    return message.author != client.user

def update_points():
    global points
    with open('points.txt', 'w') as f:
        f.write(str(points))
        
client.run(TOKEN)
