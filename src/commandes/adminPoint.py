import discord
from discord import app_commands
from discord.ext import commands
from utils.discordutils import target_autocomplete, admin_autocomplete
from utils.const import ADMIN_CHOICES, EVENT_CHOICES, DIFFICULTY_CHOICES

class AdminPointCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name="adminpoint", description="commande administrateur(ajoute ou retire des points a un joueur)")
    @app_commands.describe(target="Choisissez un utilisateur")
    @app_commands.autocomplete(target=target_autocomplete)
    @app_commands.describe(action="Choisissez une action")
    @app_commands.autocomplete(action=admin_autocomplete)
    async def adminpoint(self, interaction: discord.Interaction, action: str, target: str, nb_de_points: int = 0):
        # Importer ici pour éviter les importations circulaires
        from utils.utils import log_db, get_player_by_name, target_exist
        from player import players, player_lock
        from myembed.Myembed import create_embeds_ranking, getEmbedMessage
        from utils.const import AdminIds
        
        is_admin = False
        for role in interaction.user.roles:
            role_id_str = str(role.id)
            if role_id_str in AdminIds:
                is_admin = True
                break
        
        exception_users = [330002117987270663]
        sign_char = '+'

        if interaction.user.id not in exception_users and not is_admin:
            await interaction.response.send_message("🚫 Tu n'as pas la permission d'utiliser cette commande.")
            return

        if action in ["Ajouter des points a un joueur", "Retirer des points a un joueur"]:
            with player_lock:
              player = await get_player_by_name(interaction, target)
            if player:
                i = target_exist(players, player.mention)
                if i >= 0 :
                    if action == "Ajouter des points a un joueur":
                        players[i].addScore(nb_de_points)
                    else:
                        sign_char = '-'
                        negative_score = -abs(nb_de_points)
                        players[i].addScore(negative_score)
                log_db(players)
                ranking_embed = create_embeds_ranking(players)
                embed_message = getEmbedMessage()
                await embed_message.edit(embed=ranking_embed)
                await interaction.response.send_message(f"joueur {target} a bien recu {sign_char}{nb_de_points}")
            else:
                await interaction.response.send_message(f"joueur {target} n'a pas ete trouvé dans les participants")
        #elif action == "Suprimer la participation d'un joueur":
            
            
        with open("commandsArchives/Admincommand.txt", "a") as fichier:
            fichier.write(f"{interaction.user.name} as {interaction.user.top_role} asked for /Adminpoint command for {action} at {interaction.created_at}\n")


async def setup(bot):
    await bot.add_cog(AdminPointCog(bot))