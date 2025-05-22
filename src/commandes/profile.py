import discord
from discord import app_commands
from discord.ext import commands
from utils.discordutils import target_autocomplete
from player import players

class profileCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="profile", description="Montre le profil du joueur designer, le votre si pas argument")
    @app_commands.autocomplete(target=target_autocomplete)
    async def Profile(self, interaction: discord.Interaction, target: str = None) -> None:
        from utils.utils import get_player_by_name, target_exist
        from myembed.Myembed import create_profile_embed

        await interaction.response.defer()

        if target is None :
          target = interaction.user.mention
        else:
          selected_player = await get_player_by_name(interaction, target, players)
          if selected_player is None:
            await interaction.followup.send("Joueur non trouvé")
            return
        i = target_exist(players, selected_player.mention)
        if i >= 0 :
          embed = await create_profile_embed(players[i], interaction)
          await interaction.followup.send(embed=embed)
        else :
          await interaction.followup.send("Joueur non trouvé")



async def setup(bot):
  await bot.add_cog(profileCog(bot))