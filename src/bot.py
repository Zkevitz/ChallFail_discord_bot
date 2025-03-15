import discord
from dotenv import load_dotenv
from utils import generate_backup_filename
import os
import asyncio
from discord.ext import commands
from discord import app_commands
from typing import Optional, Literal
from time import sleep
from datetime import datetime



load_dotenv()


class CancelButton(discord.ui.Button):
  def __init__(self, participants, gain, author, view):
    super().__init__(label="Cancel", style=discord.ButtonStyle.danger)
    self.participants = participants
    self.gain = gain
    self.author = author
    self.custom_view = view

  async def callback(self, interaction: discord.Interaction):

    allowed_roles = [1322575444020822057, 1322581479015845908]
    if self.author != interaction.user and not any(role.id in allowed_roles for role in interaction.user.roles):
        await interaction.response.send_message("❌ Tu n'as pas la permission d'annuler cette action !", ephemeral=False)
        return

    print(dir(interaction))

    for participant in self.participants :
      participant.point -= self.gain
      if participant.point < 0 :
        participant.point = 0
    log_db()
    ranking_embed = create_embeds_ranking(players)
    await embed_message.edit(embed=ranking_embed)

    if self.view.message:
      await self.view.message.edit(content="❌ Action annulée.", view=None)
    await interaction.response.send_message("✅ Action annulée.", epwwwhemeral=False)
    self.disabled = True
    await interaction.message.edit(view=self.view)
    self.view.stop()

class CancelView(discord.ui.View):
  def __init__(self, participants, gain, author : discord.Member):
    super().__init__()
    self.participants = participants
    self.gain = gain
    self.author = author
    self.message = None
    self.add_item(CancelButton(self.participants, self.gain, self.author, self))
  
  def set_message(self, message: discord.Message):
    self.message = message

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


EVENT_CHOICES = ["Attaques de percepteur(alliance cibler sans defenseur)",
                 "Defenses de percepteur", "Attaques de Percepteur"]
ADMIN_CHOICES = ["Ajouter des points a un joueur",
                 "Retirer des points a un joueur", "Supprimer la participation d'un joueur"]
DIFFICULTY_CHOICES = [0, 1, 2, 3, 4, 5]
embed_message = None
intents = discord.Intents.all()
intents.members = True
intents.messages = True
bot = commands.Bot(command_prefix='!', intents=intents)
client = aclient()
tree = app_commands.CommandTree(client)
for command in bot.tree.get_commands():
  print(f"Nom de la commande: {command.name}, Description: {command.description}")
print(tree)
players = []



@bot.event
async def on_ready():

  global embed_message
  channel_id = 1348694795152920610 #1336010039886086236 #channel classement a changer par la channel qui accueil le message statique
  channel = bot.get_channel(channel_id)

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

    embed = create_embeds_ranking(players)
    embed_message = await channel.send(embed=embed)
  
  except FileNotFoundError:
    print("Le fichier spécifié n'a pas été trouvé.")
  except IOError:
    print("Erreur lors de l'ouverture du fichier.")
  except Exception as e :
    print(f"erreur inconnu as {e}")


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

@app_commands.describe(action="Choisissez une action administrateur")
async def admin_autocomplete(interaction: discord.Interaction, current: str):
    # Filtrer les options en fonction de ce que l'utilisateur tape
    filtered_choices = [
        app_commands.Choice(name=action, value=action)
        for action in ADMIN_CHOICES if current.lower() in action.lower()
    ]
    return filtered_choices[:5]

@app_commands.describe(event="Choisissez un événement")
async def event_autocomplete(interaction: discord.Interaction, current: str):
    # Afficher toute la liste d'événements ou filtrer selon ce que l'utilisateur tape
    return [
        app_commands.Choice(name=event, value=event) for event in EVENT_CHOICES
    ]

@app_commands.describe(difficulty="Choisissez une difficulté")
async def difficulty_autocomplete(interaction: discord.Interaction, current: str):
    return [
        app_commands.Choice(name=f"Difficulté {difficulty}", value=str(difficulty))
        for difficulty in DIFFICULTY_CHOICES
        if current in str(difficulty)  # Filtrage dynamique
    ]


async def target_autocomplete(interaction: discord.Interaction, current: str) -> list:
    # Récupérer les membres du serveur
    members = interaction.guild.members
    # i = 0
    # for member in members :
    #   if i == 0:
    #     print(dir(member))
    #     i += 1
    #   print(f"1-display_name = {member.display_name}")
    #   print(f"1-nickname = {member.nick}")
    #   print(f"2-nom = {member.name}")
    
    # Filtrer les membres en fonction de la chaîne entrée par l'utilisateur (par exemple, nom d'utilisateur)
    options = [member.display_name for member in members if member.display_name and current.lower() in member.display_name.lower()] 
    data = []
    # Limiter le nombre de suggestions (par exemple 5 suggestions max)
    for member_name in options[:10]:
      data.append(app_commands.Choice(name=member_name, value=member_name))
    return data

def create_embeds_ranking(players) :

  createPlayerRanking()
  i = 0
  embed = discord.Embed(title="🏆CLASSEMENT PVP AGEIN", color=0x72d345)
  embed.add_field(name="*Top 100 des combattants*", value="", inline=False)

  for player in players :
    if i % 5 == 0:
      embed.add_field(name="", value=f"**Places {i + 1} a {i + 5}**", inline=False)
    if(player.rank == 1):
      embed.add_field(name="", value=f"🥇{player.rank}. {player.arobase} : {player.point} points", inline=False)
    elif(player.rank == 2):
      embed.add_field(name="", value=f"🥈{player.rank}. {player.arobase} : {player.point} points", inline=False)
    elif(player.rank == 3):
      embed.add_field(name="", value=f"🥉{player.rank}. {player.arobase} : {player.point} points", inline=False)
    elif(player.rank > 3):
      embed.add_field(name="", value=f"🏅{player.rank}. {player.arobase} : {player.point} points", inline=False)
    i += 1
    if i == 100:
      break
      
  embed.set_footer(text="code by Ceremonia")
  return embed
  
def create_embeds(players, image, event, gain, victory, difficulty) :

  createPlayerRanking()

  if victory == True :
    emojiResult = "✅"
    embedColor = 0x72d345
  else :
    emojiResult = "❌"
    embedColor = 0xee5a3c
  embed = discord.Embed(title=f"{emojiResult}{event} de percepteur enregistrée", color=embedColor, url=image)
  embed.add_field(name=f"*Difficulté: {difficulty}({difficulty} adversaires)*", value="", inline=True)
  embed.add_field(name=f"Résultat: {emojiResult}", value="", inline=False)
  embed.add_field(name="📊 **Points gagnés**", value="", inline=False)
  embed.add_field(name=f"**Total par participants: {gain} points**", value="", inline=False)


  for player in players :
    if(player.rank == 1):
      embed.add_field(name="", value=f"🥇 {player.pseudo} : {player.point} points (+ {gain}pts) -> {player.arobase}", inline=False)
    elif(player.rank == 2):
      embed.add_field(name="", value=f"🥈 {player.pseudo} : {player.point} points (+ {gain}pts) -> {player.arobase}", inline=False)
    elif(player.rank == 3):
      embed.add_field(name="", value=f"🥉 {player.pseudo} : {player.point} points (+ {gain}pts) -> {player.arobase}", inline=False)
    elif(player.rank > 3):
      embed.add_field(name="", value=f"{player.rank} {player.pseudo} : {player.point} points (+ {gain}pts) -> {player.arobase}", inline=False)
      
  embed.set_footer(text="code by Ceremonia")
  return embed

def target_exist(target_name) :
  i = 0
  for player in players :
    if target_name.lower() == player.pseudo.lower():
      return i
    else:
     i+=1
  return -1

def calculate_point(nb_of_opponent, event, victory) :
  point = 0
  # print(nb_of_opponent)
  # print(event)
  # print(victory)
  if(event == "Attaques de percepteur(alliance cibler sans defenseur)") :
    return 1
  
  if event == "Attaques de Percepteur":
    if not victory:  # Si l'attaque échoue
        return 1
    else:
        if nb_of_opponent <= 3:
          return 0
        elif nb_of_opponent == 4:
          return 4
        elif nb_of_opponent == 5:
          return 7

    # Cas : Défense contre une attaque
  elif event == "Defenses de percepteur":
    if not victory and nb_of_opponent == 5:
      return 1
    if nb_of_opponent == 1 and victory:
      return 1
    elif nb_of_opponent == 2 and victory:
      return 2
    elif nb_of_opponent == 3 and victory:
      return 3
    elif nb_of_opponent == 4 and victory:
      return 12
    elif nb_of_opponent == 5 and victory:
      return 22

  return point
  

@bot.tree.command(name="addscore", description="enregistrer une attaque ou defense de percepteur")
@app_commands.describe(joueur1="Choisissez un utilisateur")
@app_commands.autocomplete(joueur1=target_autocomplete)
@app_commands.describe(joueur2="Choisissez un utilisateur2")
@app_commands.autocomplete(joueur2=target_autocomplete)
@app_commands.describe(joueur3="Choisissez un utilisateur3")
@app_commands.autocomplete(joueur3=target_autocomplete)
@app_commands.describe(joueur4="Choisissez un utilisateur4")
@app_commands.autocomplete(joueur4=target_autocomplete)
@app_commands.describe(joueur5="Choisissez un utilisateur5")
@app_commands.autocomplete(joueur5=target_autocomplete)
@app_commands.describe(event="Choisissez un evenement")
@app_commands.autocomplete(event=event_autocomplete)
@app_commands.describe(nb_of_opponent="Choisissez un nombre d'adversaire")
@app_commands.autocomplete(nb_of_opponent=difficulty_autocomplete)
async def AddScore(interaction: discord.Interaction,
                  event : str,
                  victory : bool,
                  nb_of_opponent: int,
                  image : discord.Attachment,
                  image2 : discord.Attachment,
                  joueur1: str,
                  joueur2: str = None,
                  joueur3: str = None,
                  joueur4: str = None,
                  joueur5: str = None):

  global embed_message
  print(joueur2)
  print(joueur3)
  await interaction.response.defer()
  amount_of_point = calculate_point(nb_of_opponent, event, victory)

  targets = [joueur1, joueur2, joueur3, joueur4, joueur5]
  mention = []
  # if all(t is None for t in targets):  # Vérifie si toutes les cibles sont None
  #       await interaction.response.send_message("❌ Vous devez spécifier au moins un joueur.")
  #       return

  player_found = False
  participants = []  
  for target_name in targets:
    if target_name is None:
        continue

    i = target_exist(target_name)
    if (i >= 0):
        # Si le joueur existe déjà, ajoute un score
        players[i].addScore(amount_of_point)
        player_found = True
        participants.append(players[i])
    else:
        # Si le joueur n'existe pas, crée un nouveau joueur et ajoute-le à la liste
        member = interaction.guild.get_member_named(target_name)
        if member:  # Vérifie si le membre existe dans le serveur
            new_player = player(target_name, 0, 0, member.mention)
            new_player.addScore(amount_of_point)
            new_player.Print()
            players.append(new_player)
            player_found = True
            participants.append(new_player)


  try:
    if image :
      file_path = f'images/{interaction.user}_{int(interaction.created_at.timestamp())}.png'
      os.makedirs(os.path.dirname(file_path), exist_ok=True)
      await image.save(file_path)
      await interaction.followup.send(f"✅ L'image pour {interaction.user} a été téléchargée et enregistrée sous {file_path}")
  except Exception as e :
    print(f"je ne comprend pas l'erreur as e {e}")

  embed = create_embeds(participants, image.url, event, amount_of_point, victory, nb_of_opponent)
  embed.set_image(url=image.url)
  #embed.add_field()
  embeds = [embed]
  embed_img = discord.Embed(url=image.url)
  embed_img.set_image(url=image.url)
  embeds.append(embed_img)
  # embed_img2 = discord.Embed(url=image.url)
  # embed_img2.set_image(url=image2.url)
  # embeds.append(embed_img2)

  view = CancelView(participants, amount_of_point, interaction.user)
  #await interaction.followup.send(f"✅ Le joueur {target} a bien reçu un point")
  message = await interaction.followup.send(embeds=embeds, view=view)
  view.set_message(message)
  ranking_embed = create_embeds_ranking(players)
  await embed_message.edit(embed=ranking_embed)

  log_db()

@bot.tree.command(name="adminpoint", description="commande administrateur(ajoute ou retire des points a un joueur)")
@app_commands.describe(target="Choisissez un utilisateur")
@app_commands.autocomplete(target=target_autocomplete)
@app_commands.describe(action="Choisissez une action")
@app_commands.autocomplete(action=admin_autocomplete)
async def AdminPoint(interaction: discord.Interaction, action : str, target: str, nb_de_points: int = 0):
  allowed_roles = [1322575444020822057, 1322581479015845908] # police ladder + grand chef agein
  exception_users = [330002117987270663]
  sign_char = '+'

  print(target)
  if interaction.user.id not in exception_users and not any(role.id in allowed_roles for role in interaction.user.roles):
    await interaction.response.send_message("🚫 Tu n'as pas la permission d'utiliser cette commande.")
    return

  if action in ["Ajouter des points a un joueur", "Retirer des points a un joueur"]:
    player = next((p for p in players if p.pseudo == target), None)
    if player:
      if action == "Ajouter des points a un joueur":
        player.addScore(nb_de_points)
      else :
        sign_char = '-'
        negative_score = -abs(nb_de_points)
        player.addScore(negative_score)
      log_db()
      ranking_embed = create_embeds_ranking(players)
      await embed_message.edit(embed=ranking_embed)
      await interaction.response.send_message(f"joueur {target} a bien recu {sign_char}{nb_de_points}")
    else:
      await interaction.response.send_message(f"joueur {target} n'a pas ete trouvé dans les participants")
   with open("commandsArchives/Admincommand.txt", "a") as fichier :
      fichier.write(f"{interaction.user.name} as {interaction.user.top_role} asked for /Adminpoint command for {action} at {interaction.created_at}\n")
  

  


@bot.tree.command(name="showscore", description="Affiche le tableau des scores des joueurs")
async def ShowScore(interaction: discord.Interaction):
  embed = create_embeds_ranking(players)
  await interaction.response.send_message(embed=embed)

@bot.command()
async def clearLadder(ctx: commands.Context):
  allowed_roles = [1322575444020822057, 1322581479015845908] # police ladder + grand chef agein
  exception_users = [330002117987270663] 

  if ctx.author.id not in exception_users and not any(role.id in allowed_roles for role in ctx.author.roles):
    await ctx.send("🚫 Tu n'as pas la permission d'utiliser cette commande.")
    return

  source_file = "db/player_db.txt"
  backup_file = generate_backup_filename() 

  try:
    with open(source_file, "r") as src, open(backup_file, "w") as dest:
      dest.write(src.read())
    await ctx.send(f"✅ Sauvegarde effectuée -->  {backup_file}")

    with open("commandsArchives/Admincommand.txt", "a") as fichier :
      fichier.write(f"{ctx.author.name} as {ctx.author.top_role} ask for !clearLadder command at {ctx.message.created_at}\n")  
  except Exception as e:
    await ctx.send(f"❗ Erreur lors de la copie du ladder as e {e}")
  
  players.clear()
  log_db()
  ranking_embed = create_embeds_ranking(players)
  await embed_message.edit(embed=ranking_embed)


@bot.command()
@commands.guild_only()
async def sync(ctx: commands.Context, guilds: commands.Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
    if not guilds:
      if spec == "~":
        synced = await ctx.bot.tree.sync(guild=ctx.guild)
      elif spec == "*":
        ctx.bot.tree.copy_global_to(guild=ctx.guild)
        synced = await ctx.bot.tree.sync(guild=ctx.guild)
      elif spec == "^":
        ctx.bot.tree.clear_commands(guild=ctx.guild)
        await ctx.bot.tree.sync(guild=ctx.guild)
        synced = []
      else:
        synced = await ctx.bot.tree.sync()

      await ctx.send(f"synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}")
      for command in bot.tree.get_commands():
        print(f"Nom de la commande: {command.name}, Description: {command.description}")
      return
    ret = 0
    for guild in guilds: 
      try:
        await ctx.bot.tree.sync(guild=guild)
      except discord.HTTPException:
        pass
      else:
        ret += 1
    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")
  

BOT_TOKEN = os.environ['BOT_TOKEN']

bot.run(BOT_TOKEN)