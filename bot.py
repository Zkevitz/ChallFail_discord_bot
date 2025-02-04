import discord
from dotenv import load_dotenv
import os
import asyncio
from discord.ext import commands
from discord import app_commands

load_dotenv()


class aclient(discord.Client):
  def __init__(self):
    super().__init__(intents=discord.Intents.default(), application_id=os.environ['DISCORD_APP_ID'])
    self.synced = False


class player :
  def __init__(self, pseudo, point, rank, arobase):
    self.pseudo = pseudo
    self.arobase = arobase
    self.point = point
    self.rank = rank

  def addScore(self, point):
    self.point += point
    if self.point < 0:
      self.point = 0
      
  def Print(self):
    print(f"{self.pseudo}{self.arobase} : {self.point} points, ==> {self.rank}")

  def Db_log(self, f):
    print(f"{self.pseudo},{self.point},{self.rank},{self.arobase}", file=f)


  

intents = discord.Intents.all()
intents.messages = True
bot = commands.Bot(command_prefix='!', intents=intents)
client = aclient()
tree = app_commands.CommandTree(client)
players = []
  


@bot.event
async def on_ready():

  if not client.synced:  # Vérifie si la synchronisation a déjà eu lieu
        await bot.tree.sync()
        client.synced = True  # Mets à jour le statut de la synchronisation
        print("Commands synced")
  print("Bot is ready")
  try:
    with open('db/player_db.txt', 'r') as file:
      for line in file:
        # Supprimer les espaces et les retours à la ligne
        line = line.strip()
        # Séparer la ligne par des virgules
        data = line.split(',')

        # Créer un objet Player avec les données extraites
        if len(data) == 4:
            pseudo, points1, points2, arobase = data
            # Convertir les points en entiers
            points1 = int(points1)
            points2 = int(points2)
            players.append(player(pseudo, points1, points2, arobase))
            print(f"Player {arobase}/{pseudo} added with {points1} points and {points2} rank")

  
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

def create_embeds_ranking(players) :

  createPlayerRanking()
  embed = discord.Embed(title="|\t\tTABLEAU DES PLUS GROSSES MERDES\t\t\t\t| :poo:", color=0x72d345)

  for player in players :
    if(player.rank == 1):
      embed.add_field(name=f"🥇 {player.pseudo} : {player.point} points", value=player.arobase, inline=False)
    elif(player.rank == 2):
      embed.add_field(name=f"🥈 {player.pseudo} : {player.point} points", value=player.arobase, inline=False)
    elif(player.rank == 3):
      embed.add_field(name=f"🥉 {player.pseudo} : {player.point} points", value=player.arobase, inline=False)
    elif(player.rank > 3):
      embed.add_field(name=f"{player.rank} : {player.point} points", value=player.arobase, inline=False)
      
  embed.set_footer(text="code by Ceremonia")
  return embed
  
def create_embeds(players, image) :

  createPlayerRanking()
  embed = discord.Embed(title="|\t\tTABLEAU DES PLUS GROSSES MERDES\t\t\t\t| :poo:", color=0x72d345, url=image)

  for player in players :
    if(player.rank == 1):
      embed.add_field(name=f"🥇 {player.pseudo} : {player.point} points", value=player.arobase, inline=False)
    elif(player.rank == 2):
      embed.add_field(name=f"🥈 {player.pseudo} : {player.point} points", value=player.arobase, inline=False)
    elif(player.rank == 3):
      embed.add_field(name=f"🥉 {player.pseudo} : {player.point} points", value=player.arobase, inline=False)
    elif(player.rank > 3):
      embed.add_field(name=f"{player.rank} {player.pseudo} : {player.point} points", value=player.arobase, inline=False)
      
  embed.set_footer(text="code by Ceremonia")
  return embed


@bot.tree.command(name="addp", description="Ajoute un nouveau joueur en utilisant ton pseudo pseudo discord")
async def AddPlayer(interaction2: discord.Interaction, newplayer : str = None):

  #print(dir(ctx.author))
  #print(ctx.author.global_name)  
  
  if interaction2.user.nick:
    pseudodisc = interaction2.user.nick.lower()
  else:
    pseudodisc = interaction2.user.global_name.lower()
    
  
  if(newplayer and newplayer.lower() == pseudodisc):
 
    if any(player.pseudo.lower() == newplayer.lower() for player in players):
      await interaction2.response.send_message(f"❌ Le joueur {newplayer} est deja dans la liste !")
      return

    print(interaction2.user.mention)
    print(interaction2.user.name)
    newPlayer = player(newplayer, 0, 0, interaction2.user.mention)
    players.append(newPlayer)
    await interaction2.response.send_message(f"✅ Le joueur {newplayer} a été ajouté.")
        
    log_db()

  
  else :
    await interaction2.response.send_message(f"❌ Je n'accepte que des nouveaux joueurs par leur pseudo Discord : {pseudodisc} != {newplayer}")
    return
  

  

@bot.tree.command(name="addscore", description="Ajoute un point a un joueur cite")
async def AddScore(interaction: discord.Interaction, target: str = None, image : discord.Attachment = None, image2 : discord.Attachment = None):

  if target is None :
    await interaction.response.send_message("❌ j'ai besoin du {Pseudo} du joueur ")
    return
  else :
    player_found = False
    
    for player in players:  
      if(player.pseudo.lower() == target.lower()):
        player.addScore(1)
        player_found = True
        break

    if not player_found:
      await interaction.response.send_message("❌ je n'ai pas trouvé de joueur avec ce pseudo")
      return

    if image :
      file_path = f'images/{target}_{int(interaction.created_at.timestamp())}.png'
      os.makedirs(os.path.dirname(file_path), exist_ok=True)
      await image.save(file_path)
      await interaction.response.send_message(f"✅ L'image pour {target} a été téléchargée et enregistrée sous {file_path}")

    embed = create_embeds(players, image.url)
    embed.set_image(url=image.url)
    #embed.add_field()
    embeds = [embed]
    embed_img = discord.Embed(url=image.url)
    embed_img.set_image(url=image.url)
    embeds.append(embed_img)
    embed_img2 = discord.Embed(url=image.url)
    embed_img2.set_image(url=image2.url)
    embeds.append(embed_img2)

    await interaction.followup.send(f"✅ Le joueur {target} a bien reçu un point")
    await interaction.followup.send(embeds=embeds)

    log_db()

@bot.tree.command(name="showscore", description="Affiche le tableau des scores des joueurs")
async def ShowScore(interaction: discord.Interaction):
  embed = create_embeds_ranking(players)
  await interaction.response.send_message(embed=embed)
  

BOT_TOKEN = os.environ['BOT_TOKEN']

bot.run(BOT_TOKEN)