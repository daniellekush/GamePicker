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

@bot.command()
# -addgame | If the person has permission to kick members, they can add new games to the list
async def addgame(ctx, args=None, emote=None):
  if not args or not emote:
    await ctx.channel.send("You must include 2 arguments! The correct way to use this command is `-addgame [game] [emoji]`")
    return
  if ctx.message.author.guild_permissions.kick_members:
    file = open("games.txt", "r")
    for item in file.readlines():
      if args in item:
        await ctx.channel.send(args + " is already registered! See it in `-listgames`")
        return
    if args == args.lower():
      await ctx.channel.send("Don't mean to be annoying but please capitalise that first letter of the game in order to add it!")
      return
    file.close()
    file = open("games.txt", 'a')
    arg = args.replace('"', '')
    file.write(arg + "," + str(START_VALUE) + "," + emote +"\n")
    file.close()
    await ctx.channel.send("Adding '" + arg + "'")

@bot.command()
# -listgames | Allows anyone to list the games and their weights
async def listgames(ctx):
  try:
    file = open("games.txt", 'r')
  except:
    file = open("games.txt", 'w')
    file.close()
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
async def vote(ctx):
  text = "Vote for the games you like watching the most to make them appear more often!\n"
  file = open("games.txt", "r")

  global emojis
  global votes
  global games
  emojis = []
  votes = []
  games = []

  for i in file.readlines():
    games.append(i.split(',')[0])
    votes.append(i.split(',')[1])
    emojis.append(i.split(',')[2].replace('\n', ''))
    
  counter = 0
  for game in games:
    text += game + " " + emojis[counter] + '\n'
    counter += 1
  
  message = await ctx.channel.send(text)
  counter2 = 0

  while counter2 < counter:
    await message.add_reaction(emojis[counter2].replace('\n', ''))
    counter2 += 1
  file.close()

@bot.event
# Reaction event handler to count votes
async def on_reaction_add(reaction, user):
  emoji = reaction.emoji

  if emoji not in emojis:
    return
  if user.bot:
    return
  if "Vote for the games you like watching the most to make them appear more often!\n" not in reaction.message.content:
    return
  
  try:
    file = open("users.txt", 'r')
  except:
    file = open("users.txt", 'w')
    file.close()
    file = open("users.txt", 'r')
  dupCheck = user.name + emoji + '\n'

  if dupCheck in file.readlines():
    await reaction.message.channel.send("You can't vote for the same game twice, that's cheating!")
    return

  file = open("users.txt", 'a')
  file.write(dupCheck)
  file.close()

  for i,j in enumerate(emojis):
    file = open('games.txt', 'r')
    copy = file.readlines()
    
    if i >= len(copy):
      break
      
    if emoji == j:
      num = int(votes[i])
      num += INCREMENT_VALUE
      copy[i] = games[i] + ',' + str(num) + ',' + emojis[i] + '\n'
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
    try:
      file = open("games.txt", 'r')
    except:
      file = open("games.txt", 'w')
      file.close()
      file = open("games.txt", 'r')
    list = []
    choices = []
  
    for i in file.readlines():
      for j,x in enumerate(i.split(',')):
        if j % 2 == 0:
          choices.append(x)
          continue
        list.append(int(x.replace('\n', '')))
        
    choice = random.choices(choices, weights=tuple(list), k=1)
    await ctx.channel.send(choice[0])

bot.run(TOKEN)
