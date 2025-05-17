import discord
from discord import app_commands
from discord.ext import commands
from utils.discordutils import target_autocomplete, admin_autocomplete
from utils.const import ADMIN_CHOICES, EVENT_CHOICES, DIFFICULTY_CHOICES

# Ne pas importer bot directement pour éviter l'importation circulaire

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
        from utils.utils import log_db
        from player import players
        from myembed.Myembed import create_embeds_ranking, embed_message
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
            player = next((p for p in players if p.pseudo == target), None)
            if player:
                if action == "Ajouter des points a un joueur":
                    player.addScore(nb_de_points)
                else:
                    sign_char = '-'
                    negative_score = -abs(nb_de_points)
                    player.addScore(negative_score)
                log_db(players)
                ranking_embed = create_embeds_ranking(players)
                await embed_message.edit(embed=ranking_embed)
                await interaction.response.send_message(f"joueur {target} a bien recu {sign_char}{nb_de_points}")
            else:
                await interaction.response.send_message(f"joueur {target} n'a pas ete trouvé dans les participants")
        
        with open("commandsArchives/Admincommand.txt", "a") as fichier:
            fichier.write(f"{interaction.user.name} as {interaction.user.top_role} asked for /Adminpoint command for {action} at {interaction.created_at}\n")

    # Fonctions d'autocomplétion locales
    async def target_autocomplete(self, interaction: discord.Interaction, current: str) -> list:
        # Récupérer les membres du serveur
        members = interaction.guild.members
        # Filtrer les membres en fonction de la chaîne entrée par l'utilisateur
        options = [member.display_name for member in members if member.display_name and current.lower() in member.display_name.lower()] 
        data = []
        # Limiter le nombre de suggestions
        for member_name in options[:10]:
            data.append(app_commands.Choice(name=member_name, value=member_name))
        return data
    
    async def admin_autocomplete(self, interaction: discord.Interaction, current: str):
        # Importer ici pour éviter les importations circulaires
        from utils.utils import ADMIN_CHOICES
        # Filtrer les options en fonction de ce que l'utilisateur tape
        filtered_choices = [
            app_commands.Choice(name=action, value=action)
            for action in ADMIN_CHOICES if current.lower() in action.lower()
        ]
        return filtered_choices[:5]

async def setup(bot):
    await bot.add_cog(AdminPointCog(bot))