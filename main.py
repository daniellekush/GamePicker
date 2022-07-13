import os
import discord
from discord.ext import commands
import random

TOKEN = os.environ['TOKEN']
intents = discord.Intents().default()
bot = commands.Bot(command_prefix='-', intents=intents)
# The starting weight value for a new game
START_VALUE = 1
# The value in which weights increase when voted for
INCREMENT_VALUE = 1
# Add more emojis to support more than 8 games
emojis = ["\N{THUMBS UP SIGN}", "\N{SLIGHTLY SMILING FACE}", "\N{SKULL}", "\N{WINKING FACE}", "\N{GHOST}", "\N{ALIEN MONSTER}", "\N{FACE WITH TEARS OF JOY}", "\N{CAT}"]

@bot.command()
# -addgame | If the person has permission to kick members, they can add new games to the list
async def addgame(ctx, args):
  if not args:
    await ctx.channel.send("You must include an argument!")
    return
    
  if ctx.message.author.guild_permissions.kick_members:
    file = open("games.txt", 'a')
    arg = args.replace('"', '')
    file.write(arg + "," + str(START_VALUE) + "\n")
    file.close()
    await ctx.channel.send("Adding '" + arg + "'")

@bot.command()
# -listgames | Allows anyone to list the games and their weights
async def listgames(ctx):
  file = open("games.txt", 'r')
  content = file.readlines()
  list = []

  if len(content) == 0:
    await ctx.channel.send("No games in the file, please add games :)")
    return
  
  for i in content:
    list.append(i.replace('\n', '').replace(',', ' '))
  file.close()
  text = ""

  for i in list:
    text += i + "\n"
  await ctx.channel.send(text)

@bot.command()
# -vote | Allows anyone to vote for a game to increase its weighting
#TODO: People can vote for the same game several times if they keep running -vote which is a clear exploit
async def vote(ctx):
  text = "Vote for the games you like watching the most to make them appear more often!\n"
  file = open("games.txt", "r").readlines()
  games = []

  for i in file:
    games.append(i.split(',')[0])

  counter = 0
  for game in games:
    text += emojis[counter] + " " + game + '\n'
    counter += 1
    
  message = await ctx.channel.send(text)
  counter2 = 0

  while counter2 < counter:
    await message.add_reaction(emojis[counter2])
    counter2 += 1

@bot.event
# Reaction event handler to count votes
async def on_reaction_add(reaction, user):
  emoji = reaction.emoji

  if user.bot:
    return
  if "Vote for the games you like watching the most to make them appear more often!\n" not in reaction.message.content:
    return

  for i,j in enumerate(emojis):
    file = open('games.txt', 'r')
    copy = file.readlines()
    
    if i >= len(copy):
      break
      
    if emoji == j:
      num = int(copy[i].split(',')[1].replace('\n', ''))
      num += INCREMENT_VALUE
      text = copy[i].split(',')
      text[1] = str(num) + '\n'
      copy[i] = text[0] + ',' + text[1]
      file.close()
      file = open('games.txt', 'w')
      
      for x in copy:
        file.write(x)
      file.close()
      break
  
  await reaction.message.channel.send(user.name + " has added " + emoji)
  

@bot.command()
# -pick | If the person has permission to kick members, they can randomly pick a game and this decision is made using weights with bigger weight meaning more likely
async def pick(ctx):
  if ctx.message.author.guild_permissions.kick_members:
    file = open('games.txt', 'r').readlines()
    list = []
    choices = []
  
    for i in file:
      for j,x in enumerate(i.split(',')):
        if j % 2 == 0:
          choices.append(x)
          continue
        list.append(int(x.replace('\n', '')))
        
    choice = random.choices(choices, weights=tuple(list), k=1)
    await ctx.channel.send(choice[0])

bot.run(TOKEN)
