import discord
from dotenv import load_dotenv
from utils import generate_backup_filename, createPlayerRanking, calculate_point
import os
import random
import json
import asyncio
import handlesignal
from discord.ext import commands
from discord import app_commands
from typing import Optional, Literal
from time import sleep
from datetime import datetime, timedelta
from ograT5 import *
from Myembed import *
from player import player




load_dotenv()


class CancelButton(discord.ui.Button):
  def __init__(self, participants, gain, author, view, formatted_time):
    super().__init__(label="Cancel", style=discord.ButtonStyle.danger)
    self.participants = participants
    self.gain = gain
    self.author = author
    self.formatted_time = formatted_time
    self.custom_view = view

  async def callback(self, interaction: discord.Interaction):
    await interaction.response.defer()

    # Vérifier si c'est l'auteur ou un admin avec niveau ≥ 1
    is_admin = False
    for role in interaction.user.roles:
        role_id_str = str(role.id)
        if role_id_str in AdminIds:
            is_admin = True
            break
    
    if self.author != interaction.user and not is_admin:
        await interaction.followup.send("❌ Tu n'as pas la permission d'annuler cette action !", ephemeral=False)
        return

    #print(dir(interaction))
    await self.author.send(f"Ton post datant du {self.formatted_time} a ete annule par {interaction.user}")
    for participant in self.participants :
      participant.point -= self.gain
      if participant.point < 0 :
        participant.point = 0
    log_db(players)
    ranking_embed = create_embeds_ranking(players)
    await embed_message.edit(embed=ranking_embed)

    if self.view.message:
      await self.view.message.edit(content="❌ Action annulée.", view=None)
    await interaction.followup.send("✅ Action annulée.", ephemeral=False)
    self.disabled = True
    await interaction.message.edit(view=self.view)
    self.view.stop()

class CancelView(discord.ui.View):
  def __init__(self, participants, gain, author : discord.Member, formatted_time):
    super().__init__(timeout=None)
    self.participants = participants
    self.gain = gain
    self.author = author
    self.message = None
    self.formatted_time = formatted_time
    self.add_item(CancelButton(self.participants, self.gain, self.author, self, self.formatted_time))
  
  async def on_timeout(self):
    if self.message is None:
      print("Erreur message is None!!")

    try: 
      new_view = CancelView(self.participants, self.gain, self.author, self.formatted_time)
      new_view.message = self.message
      await self.message.edit(content="bouton renouvele", view=new_view)
    except discord.NotFound:
        print("⚠️ Erreur : Le message n'existe plus.")
    except discord.Forbidden:
        print("❌ Erreur : Permissions insuffisantes pour modifier le message.")
    except discord.HTTPException as e:
        print(f"⚠️ Erreur HTTP : {e}")  
  
  def set_message(self, message: discord.Message):
    self.message = message

class aclient(discord.Client):
  def __init__(self):
    super().__init__(intents=discord.Intents.default(), application_id=os.environ['DISCORD_APP_ID'])
    self.synced = False

EVENT_CHOICES = ["Attaques de percepteur(alliance cibler sans defenseur)",
                 "Defenses de percepteur", "Attaques de Percepteur", "Attaques de Percepteur contre DOSE"]
ADMIN_CHOICES = ["Ajouter des points a un joueur",
                 "Retirer des points a un joueur", "Supprimer la participation d'un joueur"]
DIFFICULTY_CHOICES = [0, 1, 2, 3, 4, 5]
embed_message = None
LadderMessageId = None # test
AdminIds = []
LadderChannelId = 1353274218074341447
errorChannelId = 1355944321601376286
CommandChannelId = 1353274373691150407
intents = discord.Intents.all()
intents.members = True
intents.messages = True
bot = commands.Bot(command_prefix='!', intents=intents)
#client = aclient()
#tree = app_commands.CommandTree(client)
players = []



@bot.event
async def on_ready():

  global embed_message
  global LadderChannelId
  global LadderMessageId
  channel = bot.get_channel(LadderChannelId)

  #if not client.synced:  # Vérifie si la synchronisation a déjà eu lieu
  await bot.tree.sync()
  #client.synced = True  # Mets à jour le statut de la synchronisation
  print("Commands synced")
  try:
    with open('db/player_db.txt', 'r') as file:
      for line in file:
        # Supprimer les espaces et les retours à la ligne
        line = line.strip()
        # Séparer la ligne par des virgules
        data = line.split(',')

        # Créer un objet Player avec les données extraites
        if len(data) >= 4:
            if len(data) == 4:
              pseudo, points1, points2, arobase = data
              exoPoints = 0
              exoRank = 0 
            else:
              pseudo, points1, points2, arobase, exoPoints, exoRank = data
            # Convertir les points en entiers
            points1 = int(points1)
            points2 = int(points2)
            exoPoints = int(exoPoints)
            exoRank = int(exoRank)
            if not any(p.pseudo == pseudo and p.arobase == arobase for p in players):
              players.append(player(pseudo, points1, points2, arobase, exoPoints, exoRank))
            #print(f"Player {arobase}/{pseudo} added with {points1} points and {points2} rank")

    discord_ids = json.load(open("DiscordID.json"))
    for role in discord_ids["roles"]:
      AdminIds.append(role["id"])
    embed = create_embeds_ranking(players)
    embed_message = await channel.send(embed=embed)
    LadderMessageId = embed_message.id
    print("Bot is ready")
  
  except FileNotFoundError:
    print("Le fichier spécifié n'a pas été trouvé.")
  except IOError:
    print("Erreur lors de l'ouverture du fichier.")
  except Exception as e :
    print(f"erreur inconnu as {e}")


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

def target_exist(target_name) :
  i = 0
  for player in players :
    if target_name.lower() == player.arobase.lower():
      return i
    else:
     i+=1
  return -1

@bot.tree.command(name="addscore", description="enregistrer une attaque ou defense de percepteur")
@app_commands.describe(
  joueur1="Choisissez un utilisateur",
  joueur2="Choisissez un utilisateur2",
  joueur3="Choisissez un utilisateur3",
  joueur4="Choisissez un utilisateur4",
  joueur5="Choisissez un utilisateur5",
  event="Choisissez un evenement",
  nb_of_opponent="Choisissez un nombre d'adversaire")
@app_commands.autocomplete(joueur1=target_autocomplete)
@app_commands.autocomplete(joueur2=target_autocomplete)
@app_commands.autocomplete(joueur3=target_autocomplete)
@app_commands.autocomplete(joueur4=target_autocomplete)
@app_commands.autocomplete(joueur5=target_autocomplete)
@app_commands.autocomplete(event=event_autocomplete)
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
  global CommandChannelId
  await interaction.response.defer()

  if interaction.channel.id != CommandChannelId :
    await interaction.followup.send("Seul le salon commandes-ladder autorise l'utilisation de cette commande. Cet incident sera signalé.")
    return
  
  if not image.content_type.startswith("image/") or not image2.content_type.startswith("image/"):
    await interaction.followup.send("Le fichier fourni n'est pas une image !", ephemeral=True)
    return


  amount_of_point = calculate_point(nb_of_opponent, event, victory)

  targets = [joueur1, joueur2, joueur3, joueur4, joueur5]

  player_found = False
  participants = []  
  for target_name in targets:
    if target_name is None:
        continue  

    member = interaction.guild.get_member_named(target_name)
    i = target_exist(member.mention)
    if (i >= 0):
        # Si le joueur existe déjà, ajoute un score
        players[i].addScore(amount_of_point)
        player_found = True
        participants.append(players[i])
    else:
        # Si le joueur n'existe pas, crée un nouveau joueur et ajoute-le à la liste
        if member:  # Vérifie si le membre existe dans le serveur
            new_player = player(target_name, 0, 0, member.mention, 0 , 0)
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
      #await interaction.followup.send(f"✅ L'image pour {interaction.user} a été téléchargée et enregistrée sous {file_path}")
  except Exception as e :
    print(f"je ne comprend pas l'erreur as e {e}")

  time = interaction.created_at
  time += timedelta(hours=1)
  formatted_time = time.strftime("%Y-%m-%d %H:%M:%S")
  embed = create_embeds(participants, image.url, event, amount_of_point, victory, nb_of_opponent, formatted_time)
  embed.set_image(url=image.url)
  #embed.add_field()
  embeds = [embed]
  embed_img = discord.Embed(url=image.url)
  embed_img.set_image(url=image2.url)
  embeds.append(embed_img)

  view = CancelView(participants, amount_of_point, interaction.user, formatted_time)
  message = await interaction.channel.send(embeds=embeds, view=view)
  view.set_message(message)
  ranking_embed = create_embeds_ranking(players)
  await embed_message.edit(embed=ranking_embed)
  #await editStaticLadder(staticChannelId, staticMessageId, ranking_embed)
  await interaction.followup.send("Commande traitée avec succès.", ephemeral=True)

  log_db(players)

@bot.tree.command(name="adminpoint", description="commande administrateur(ajoute ou retire des points a un joueur)")
@app_commands.describe(target="Choisissez un utilisateur")
@app_commands.autocomplete(target=target_autocomplete)
@app_commands.describe(action="Choisissez une action")
@app_commands.autocomplete(action=admin_autocomplete)
async def AdminPoint(interaction: discord.Interaction, action : str, target: str, nb_de_points: int = 0):
  
  is_admin = False
  for role in interaction.user.roles:
      role_id_str = str(role.id)
      if role_id_str in AdminIds:
          is_admin = True
          break
  
  exception_users = [330002117987270663]
  sign_char = '+'

  #print(target)
  if interaction.user.id not in exception_users and not is_admin:
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
      log_db(players)
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

@bot.tree.command(name="exoscore", description="Affiche le tableau des joueurs les plus nul en forgemagie")
async def ExoScore(interaction: discord.Interaction):
  embed = create_embeds_exo_ranking(players)
  await interaction.response.send_message(embed=embed)
  

@bot.tree.command(name="tryexo", description="Essayer de faire un exo")
async def try_exo(interaction: discord.Interaction) :
  await interaction.response.send_message("Nous allons essayer de faire un exo")

  # Utiliser directement la mention de l'utilisateur
  user_mention = interaction.user.mention
  
  # Vérifier si l'utilisateur existe dans votre système
  user_index = target_exist(user_mention)
  
  i = 0 
  taux = 100
  message = await interaction.followup.send("nombres de tenta = 0")
  while True :
    randomNumber = random.randint(0, taux - 1)
    if randomNumber == 0 :
      await message.edit(content=f"+ 1PA ! reussi apres {i} tentatives")
      break
    i += 1
    if i % 5 == 0:
      await message.edit(content=f"nombres de tenta = {i}")
  
  if user_index >= 0 :
    if i > players[user_index].exoScore :
      players[user_index].SetExoScore(i)
      createExoRanking(players)
      await interaction.followup.send(f"{interaction.user.mention} a battu son record 🎉\n Nouveaux Score -> {i} Tentas et obtiens le rang {players[user_index].exoRank}")
  else:
    if member:  # Vérifie si le membre existe dans le serveur
      new_player = player(target_name, 0, 0, member.mention, i , 0)
      new_player.Print()
      players.append(new_player)
      createExoRanking(players)
  log_db(players)

@bot.command()
async def setmessage(ctx):
  #rajouter une verification de droit admin sur la commande
  is_admin = False
  for role in ctx.author.roles:
      role_id_str = str(role.id)
      if role_id_str in AdminIds:
          is_admin = True
          break
  
  if not is_admin:
    await ctx.send("🚫 Tu n'as pas la permission d'utiliser cette commande.")
    return
  global embed_message
  embed_message = await ctx.channel.send(embed=create_embeds_ranking(players))
  await ctx.send(f"✅ Message mis a jour.", delete_after=5)


@bot.command()
@commands.has_permissions(manage_messages=True)
async def clearchannel(ctx):
  # if amount > 100:
  #   await ctx.send("🚫 Vous ne pouvez supprimer plus de 100 messages a la fois.")
  #   return
  deleted = await ctx.channel.purge(limit=None)
  await ctx.send(f"✅ {len(deleted)} messages supprimés.", delete_after=10)

  

@bot.command()
async def clearLadder(ctx: commands.Context):
  # police ladder + grand chef agein
  exception_users = [330002117987270663] 

  is_admin = False
  for role in ctx.author.roles:
      role_id_str = str(role.id)
      if role_id_str in AdminIds:
          is_admin = True
          break

  if ctx.author.id not in exception_users and not is_admin:
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
  log_db(players)
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