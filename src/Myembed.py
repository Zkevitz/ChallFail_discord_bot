from utils import createPlayerRanking, generate_backup_filename, createExoRanking
from bot import *
import discord

def create_embeds(players, image, event, gain, victory, difficulty, formatted_time) :

  players = createPlayerRanking(players)

  if victory == True :
    emojiResult = "✅"
    embedColor = 0x72d345
  else :
    emojiResult = "❌"
    embedColor = 0xee5a3c
  embed = discord.Embed(title=f"{emojiResult}{event} enregistrée", color=embedColor, url=image)
  embed.add_field(name=f"*Difficulté: {difficulty}({difficulty} adversaires)*", value="", inline=True)
  embed.add_field(name=f"Résultat: {emojiResult}", value="", inline=False)
  embed.add_field(name="📊 **Points gagnés**", value="", inline=False)
  embed.add_field(name=f"**Total par participants: {gain} points**", value="", inline=False)


  for player in players :
    if(player.rank == 1):
      embed.add_field(name="", value=f"🥇 {player.arobase} --> {player.point} points (+ {gain}pts)", inline=False)
    elif(player.rank == 2):
      embed.add_field(name="", value=f"🥈 {player.arobase} --> {player.point} points (+ {gain}pts)", inline=False)
    elif(player.rank == 3):
      embed.add_field(name="", value=f"🥉 {player.arobase} --> {player.point} points (+ {gain}pts)", inline=False)
    elif(player.rank > 3):
      embed.add_field(name="", value=f"{player.rank}: {player.arobase} --> {player.point} points (+ {gain}pts)", inline=False)
      
  embed.set_footer(text=f"code by Ceremonia | at {formatted_time}")
  return embed


def create_embeds_ranking(players):
    players = createPlayerRanking(players)
    embed = discord.Embed(title="🏆 CLASSEMENT PVP AGEIN", color=0x72d345)
    embed.add_field(name="*Top 100 des combattants*", value="", inline=False)

    group_text = ""  # Stocke les infos de 5 joueurs à la fois
    for i, player in enumerate(players[:100]):  # Limite directement à 100 joueurs
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
    embed = discord.Embed(title="🏆 CLASSEMENT EXO", color=0x72d345)
    embed.add_field(name="*Top 10 des pires forgemages*", value="", inline=False)

    group_text = ""  # Stocke les infos de 5 joueurs à la fois
    for i, player in enumerate(players[:10]):  # Limite directement à 10 joueurs
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
