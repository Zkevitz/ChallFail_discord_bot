from utils.utils import createPlayerRanking, generate_backup_filename, createExoRanking
import discord
from player import player
from datetime import datetime

embed_message : discord.Message = None

def setEmbedMessage(message : discord.Message) :
  global embed_message
  embed_message = message

def getEmbedMessage() -> discord.Message:
  global embed_message
  return embed_message

def create_embeds(players, image, event, gain, victory, difficulty, participants) :

  players = createPlayerRanking(players)

  if victory == True :
    emojiResult = "✅"
    embedColor = 0x72d345
  else :
    emojiResult = "❌"
    embedColor = 0xee5a3c
  embed = discord.Embed(title=f"{emojiResult}{event} enregistrée", color=embedColor, url=image, timestamp=datetime.now())
  embed.add_field(name=f"*Difficulté: {difficulty}({difficulty} adversaires)*", value="", inline=True)
  embed.add_field(name=f"Résultat: {emojiResult}", value="", inline=False)
  embed.add_field(name="📊 **Points gagnés**", value="", inline=False)
  embed.add_field(name=f"**Total par participants: {gain} points**", value="", inline=False)

  for player in participants :
    with player.lock:
      if(player.rank == 1):
        embed.add_field(name="", value=f"🥇 {player.arobase} --> {player.point} points (+ {gain}pts)", inline=False)
      elif(player.rank == 2):
        embed.add_field(name="", value=f"🥈 {player.arobase} --> {player.point} points (+ {gain}pts)", inline=False)
      elif(player.rank == 3):
        embed.add_field(name="", value=f"🥉 {player.arobase} --> {player.point} points (+ {gain}pts)", inline=False)
      elif(player.rank > 3):
        embed.add_field(name="", value=f"{player.rank}: {player.arobase} --> {player.point} points (+ {gain}pts)", inline=False)
      
  embed.set_footer(text=f"code by Ceremonia")
  return embed


def create_embeds_ranking(players):
    players = createPlayerRanking(players)

    embed = discord.Embed(title="🏆 CLASSEMENT PVP AGEIN", color=0x72d345, timestamp=datetime.now())
    embed.add_field(name="*Top 100 des combattants*", value="", inline=False)

    group_text = ""  # Stocke les infos de 5 joueurs à la fois
    PVP_Players = [player for player in players if player.PVP == True]
    for i, player in enumerate(PVP_Players[:100]):  # Limite directement à 100 joueurs
      with player.lock:
        if i % 5 == 0 and i != 0:
            # Ajoute le texte accumulé et réinitialise
            embed.add_field(name=f"**Places {i - 4} à {i}**", value=group_text, inline=False)
            group_text = ""

        # Ajoute le joueur actuel à la chaîne
        medal = "🥇" if player.rank == 1 else "🥈" if player.rank == 2 else "🥉" if player.rank == 3 else "🏅"
        group_text += f"{medal} {player.rank}. {player.arobase} : {player.point} points\n"

    # Ajoute le dernier groupe s'il en reste
    if group_text:
        embed.add_field(name=f"**Places {i - (i % 5) + 1} à {i + 1}**", value=group_text, inline=False)

    embed.set_footer(text="code by Ceremonia")
    return embed

def create_embeds_exo_ranking(players):
    players = createExoRanking(players)

    embed = discord.Embed(title="🏆 CLASSEMENT EXO", color=0x72d345, timestamp=datetime.now())
    embed.add_field(name="*Top 10 des pires forgemages*", value="", inline=False)

    group_text = ""  # Stocke les infos de 5 joueurs à la fois
    for i, player in enumerate(players[:10]):  # Limite directement à 10 joueurs
      with player.lock:
        if i % 5 == 0 and i != 0:
            # Ajoute le texte accumulé et réinitialise
            embed.add_field(name=f"**Places {i - 4} à {i}**", value=group_text, inline=False)
            group_text = ""

        # Ajoute le joueur actuel à la chaîne
        medal = "🥇" if player.exoRank == 1 else "🥈" if player.exoRank == 2 else "🥉" if player.exoRank == 3 else "🏅"
        group_text += f"{medal} {player.exoRank}. {player.arobase} : {player.exoScore} Tentas\n"

    # Ajoute le dernier groupe s'il en reste
    if group_text:
        embed.add_field(name=f"**Places {i - (i % 5) + 1} à {i + 1}**", value=group_text, inline=False)

    embed.set_footer(text="code by Ceremonia")
    return embed

async def create_profile_embed(player : player, interaction : discord.Interaction):

    with player.lock:
      color_ranks = {1: discord.Color.gold(), 2: discord.Color.light_grey(), 3: discord.Color(0xCD7F32)}
      color = color_ranks.get(player.rank, discord.Color.blue())
      embed = discord.Embed(title=f"Profil de {player.pseudo}", color=color, timestamp=datetime.now())
    
      discord_user = await interaction.guild.fetch_member(player.discord_id)
      if(hasattr(discord_user, "avatar") and discord_user.avatar) :
        embed.set_thumbnail(url=discord_user.avatar.url)

      embed.add_field(name="🏆 __Stats de Saison__", value="** **", inline=False)
      embed.add_field(name="🔹 Points", value=f"**{player.point}**", inline=True)
      embed.add_field(name="🏅 Classement", value=f"**{player.rank}**", inline=True)
      embed.add_field(name="** **", value="** **", inline=True)  # Champ vide pour l'alignement
      embed.add_field(name="🌟 __Stats Globales__", value="** **", inline=False)
      embed.add_field(name="✅ Victoires", value=f"**{player.victoryRatio}**", inline=True)
      embed.add_field(name="❌ Défaites", value=f"**{player.defeatRatio}**", inline=True)
      embed.add_field(name="💯 Points totaux", value=f"**{player.all_time_point}**", inline=True)
      embed.add_field(name="💎 __Stats Exo__", value="** **", inline=False)
      embed.add_field(name="🔸 Score Exo", value=f"**{player.exoScore}**", inline=True)
      embed.add_field(name="🏆 Rang Exo", value=f"**{player.exoRank}**", inline=True)
      embed.add_field(name="** **", value="** **", inline=True)  # Champ vide pour l'alignement
      embed.set_footer(text=f"code by Ceremonia")
      return embed