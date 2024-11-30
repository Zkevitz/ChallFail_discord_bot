import discord
import os
import asyncio
from discord.ext import commands

intents = discord.Intents.all()
intents.messages = True

class player :
  def __init__(self, pseudo, point, rank):
    self.pseudo = pseudo
    self.point = point
    self.rank = rank

  def addScore(self, point):
    self.point += point
    if self.point < 0:
      self.point = 0
      
  def Print(self):
    print(f"{self.pseudo} : {self.point} points, ==> {self.rank}")

  def Db_log(self, f):
    print(f"{self.pseudo},{self.point},{self.rank}", file=f)


  

  
bot = commands.Bot(command_prefix='!', intents=intents)
players = []


@bot.event
async def on_ready():
  try:
    with open('db/player_db.txt', 'r') as file:
      for line in file:
        # Supprimer les espaces et les retours à la ligne
        line = line.strip()
        # Séparer la ligne par des virgules
        data = line.split(',')

        # Créer un objet Player avec les données extraites
        if len(data) == 3:
            pseudo, points1, points2 = data
            # Convertir les points en entiers
            points1 = int(points1)
            points2 = int(points2)
            players.append(player(pseudo, points1, points2))
            print(f"Player {pseudo} added with {points1} points and {points2} points")

  
  except FileNotFoundError:
    print("Le fichier spécifié n'a pas été trouvé.")
  except IOError:
    print("Erreur lors de l'ouverture du fichier.")


def log_db():
  with open('db/player_db.txt', 'w') as file:
    for player in players:
      player.Db_log(file)
  
def createPlayerRanking():
  players.sort(key=lambda x: x.point, reverse=True)

  # Attribution des rangs
  for i in range(len(players)):
      if i == 0:
          players[i].rank = 1
      else:
          if players[i].point < players[i-1].point:
              players[i].rank = players[i-1].rank + 1
          else:
              players[i].rank = players[i-1].rank

  
def create_embeds(players) :

  createPlayerRanking()
  embed = discord.Embed(title="|\t\tTABLEAU DES PLUS GROSSES MERDES\t\t\t\t| :poo:", color=0x72d345)

  
  for player in players :
    if(player.rank == 1):
      embed.add_field(name=f"🥇 {player.pseudo} : {player.point} points", value="", inline=False)
    elif(player.rank == 2):
      embed.add_field(name=f"🥈 {player.pseudo} : {player.point} points", value="", inline=False)
    elif(player.rank == 3):
      embed.add_field(name=f"🥉 {player.pseudo} : {player.point} points", value="", inline=False)
    elif(player.rank > 3):
      embed.add_field(name=f"{player.rank} {player.pseudo} : {player.point} points", value="", inline=False)
      
  embed.set_footer(text="code by minishell and kta")
  return embed


@bot.command()
async def AddPlayer(ctx, newPlayerstr: str = None):

  #print(dir(ctx.author))
  #print(ctx.author.global_name)
  
  if newPlayerstr is None:
    await ctx.send("Quel est le pseudo du joueur 👀 ?")
  
    try:
      message = await bot.wait_for("message", check=lambda m: m.author == ctx.author, timeout=20.0)
      
    except asyncio.TimeoutError :
      await ctx.send("❌ Désolé, vous avez mis trop de temps pour répondre !")
      return
      
    newPlayerstr = message.content

  
  if ctx.author.nick:
    pseudodisc = ctx.author.nick.lower()
  else :
    pseudodisc = ctx.author.global_name.lower()
  
  if(newPlayerstr.lower() == pseudodisc):

    if any(player.pseudo == newPlayerstr for player in players):
      await ctx.send(f"❌ Le joueur {newPlayerstr} est déjà dans la liste !")
      return

    
    newPlayer = player(newPlayerstr, 0, 0)
    players.append(newPlayer)
    await ctx.send(f"✅Le joueur {newPlayerstr} a bien été ajouté")
    
    log_db()

  
  else :
    await ctx.send(f"❌ je n'accepte que des nouveau joueurs par leurs pseudo discord : {pseudodisc} != {newPlayerstr}")
    return
  

  

@bot.command()
async def AddScore(ctx, target: str = None):

  if target is None :
    await ctx.send("❌ j'ai besoin du {Pseudo} du joueur ")
    return
  else :
    player_found = False
    
    for player in players:
      if(player.pseudo.lower() == target.lower()):
        player.addScore(1)
        player_found = True
        break

    if not player_found:
      await ctx.send("❌ je n'ai pas trouvé de joueur avec ce pseudo")
      return
      
    embed = create_embeds(players)
    await ctx.send(f"✅ Le joueur {target} a bien reçu un point")
    await ctx.send(embed = embed)

    log_db()

@bot.command()
async def ShowScore(ctx):
  embed = create_embeds(players)
  await ctx.send(embed = embed)
  

BOT_TOKEN = os.environ['BOT_TOKEN']

bot.run(BOT_TOKEN)