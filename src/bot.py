import discord
from dotenv import load_dotenv
from utils.utils import generate_backup_filename, createPlayerRanking, calculate_point, log_db
from utils.json_utils import load_players_from_json, convert_txt_to_json, backup_player_db
from utils.discordutils import target_autocomplete, event_autocomplete, difficulty_autocomplete
import os
import json
from discord.ext import commands
from typing import Optional, Literal
from time import sleep
from datetime import datetime, timedelta
from myembed.Myembed import setEmbedMessage, getEmbedMessage, create_embeds_ranking, create_embeds, create_embeds_exo_ranking, create_profile_embed
from player import player, players
from redis_cache import cache  # Importer le module Redis cache
from utils.const import LadderChannelId, errorChannelId, CommandChannelId, AdminIds

load_dotenv()

class aclient(discord.Client):
  def __init__(self):
    super().__init__(intents=discord.Intents.default(), application_id=os.environ['DISCORD_APP_ID'])
    self.synced = False

LadderMessageId = None # test
intents = discord.Intents.all()
intents.members = True
intents.messages = True
bot = commands.Bot(command_prefix='!', intents=intents)
#client = aclient()
#tree = app_commands.CommandTree(client)
commandes = {"addScore", "adminPoint", "tryexo", "profile"}

async def load_commands(bot : commands.Bot) -> None:
  for commande in commandes :
    await bot.load_extension(f'commandes.{commande}')

@bot.event
async def on_ready():

  global players
  global LadderChannelId
  global LadderMessageId
  channel = bot.get_channel(LadderChannelId)

  await load_commands(bot)
  await bot.tree.sync()
  print("Commands synced")
  try:
    # Essayer d'abord de charger depuis le fichier JSON
    json_players = load_players_from_json('db/player_db.json')
    
    if json_players:
      players.extend(json_players)
      print(f"Chargement réussi de {len(json_players)} joueurs depuis le fichier JSON")
    else:
      # Si le fichier JSON est vide ou n'existe pas, essayer avec l'ancien format
      # Convertir l'ancien format vers JSON pour les prochaines utilisations
      players = convert_txt_to_json('db/player_db.txt', 'db/player_db.json')

    discord_ids = json.load(open("DiscordID.json"))
    for role in discord_ids["roles"]:
      AdminIds.append(role["id"])
    embed = create_embeds_ranking(players)
    embed_message = await channel.send(embed=embed)
    setEmbedMessage(embed_message)
    LadderMessageId = embed_message.id
    print("Bot is ready")
  
  except FileNotFoundError:
    print("Le fichier spécifié n'a pas été trouvé.")
  except IOError:
    print("Erreur lors de l'ouverture du fichier.")
  except Exception as e :
    print(f"erreur inconnu as {e}")


@bot.tree.command(name="showscore", description="Affiche le tableau des scores des joueurs")
async def ShowScore(interaction: discord.Interaction) -> None:
  embed = create_embeds_ranking(players)
  await interaction.response.send_message(embed=embed)

@bot.tree.command(name="exoscore", description="Affiche le tableau des joueurs les plus nul en forgemagie")
async def ExoScore(interaction: discord.Interaction) -> None:
  embed = create_embeds_exo_ranking(players)
  await interaction.response.send_message(embed=embed)

@bot.command()
async def setmessage(ctx) -> None:
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
async def clearchannel(ctx) -> None:
  # if amount > 100:
  #   await ctx.send("🚫 Vous ne pouvez supprimer plus de 100 messages a la fois.")
  #   return
  deleted = await ctx.channel.purge(limit=90)
  if len(deleted) >= 90 :
    await ctx.send("✅ 90 messages supprimés. j'arrete la purge", delete_after= 10)
    return
  await ctx.send(f"✅ {len(deleted)} messages supprimés.", delete_after=10)

 

@bot.command()
async def clearLadder(ctx: commands.Context) -> None:
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

  # Créer une sauvegarde du fichier JSON
  backup_file = backup_player_db('db/player_db.json')
  
  if backup_file:
    await ctx.send(f"✅ Sauvegarde effectuée -->  {backup_file}")
  else:
    await ctx.send("❌ Erreur lors de la sauvegarde")

  try:
    with open("commandsArchives/Admincommand.txt", "a") as fichier:
      fichier.write(f"{ctx.author.name} as {ctx.author.top_role} ask for !clearLadder command at {ctx.message.created_at}\n")  
  except Exception as e:
    await ctx.send(f"❗ Erreur lors de la copie du ladder as {e}")
  
  for player in players :
    player.clearPVP()
  log_db(players)
  ranking_embed = create_embeds_ranking(players)
  embed_message = getEmbedMessage()
  await embed_message.edit(embed=ranking_embed)


@bot.command()
@commands.guild_only()
async def sync(ctx: commands.Context, guilds: commands.Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
  await ctx.send("syncing commands")
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