import discord
from discord import app_commands
from discord.ext import commands
from utils.discordutils import target_autocomplete, admin_autocomplete
from utils.const import ADMIN_CHOICES, EVENT_CHOICES, DIFFICULTY_CHOICES


class tryExoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="tryexo", description="Essayer de faire un exo")
    async def try_exo(self, interaction: discord.Interaction) -> None:
        from utils.utils import log_db, target_exist, createExoRanking
        from myembed.Myembed import create_embeds_ranking, create_embeds_exo_ranking
        from player import players
        import random

        await interaction.response.defer()
        await interaction.followup.send("Nous allons essayer de faire un exo")

        # Utiliser directement la mention de l'utilisateur
        user_mention = interaction.user.mention
  
        # Vérifier si l'utilisateur existe dans votre système
        user_index = target_exist(players, user_mention)
  
        i = 1 
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
              if interaction.user:  # Vérifie si le membre existe dans le serveur
                new_player = player(interaction.user.name, 0, 0, interaction.user.mention, interaction.user.id, i , 0)
                new_player.Print()
                players.append(new_player)
                createExoRanking(players)
                await interaction.followup.send(f"{interaction.user.mention} a battu son record 🎉\n Nouveaux Score -> {i} Tentas et obtiens le rang {new_player.exoRank}")
        log_db(players)

async def setup(bot):
    await bot.add_cog(tryExoCog(bot))