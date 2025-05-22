import discord
from discord import app_commands
from discord.ext import commands
from datetime import timedelta
from utils.discordutils import target_autocomplete, event_autocomplete, difficulty_autocomplete
from utils.const import ADMIN_CHOICES, EVENT_CHOICES, DIFFICULTY_CHOICES
import os

# Ne pas importer bot directement pour éviter l'importation circulaire

@app_commands.describe(
  joueur1="Choisissez un utilisateur",
  joueur2="Choisissez un utilisateur2",
  joueur3="Choisissez un utilisateur3",
  joueur4="Choisissez un utilisateur4",
  joueur5="Choisissez un utilisateur5",
  event="Choisissez un evenement",
  nb_of_opponent="Choisissez un nombre d'adversaire")
class AddScoreCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name="addscore", description="enregistrer une attaque ou defense de percepteur")
    @app_commands.autocomplete(joueur1=target_autocomplete)
    @app_commands.autocomplete(joueur2=target_autocomplete)
    @app_commands.autocomplete(joueur3=target_autocomplete)
    @app_commands.autocomplete(joueur4=target_autocomplete)
    @app_commands.autocomplete(joueur5=target_autocomplete)
    @app_commands.autocomplete(event=event_autocomplete)
    @app_commands.autocomplete(nb_of_opponent=difficulty_autocomplete)
    async def addscore(self, interaction: discord.Interaction,
                      event: str,
                      victory: bool,
                      nb_of_opponent: int,
                      image: discord.Attachment,
                      image2: discord.Attachment,
                      joueur1: str,
                      joueur2: str = None,
                      joueur3: str = None,
                      joueur4: str = None,
                      joueur5: str = None):
        # Accéder aux fonctions et variables via le bot
        from utils.utils import calculate_point, target_exist, log_db
        from myembed.Myembed import create_embeds, create_embeds_ranking, getEmbedMessage
        from player import player as Player, players, get_player_with_lock, add_player_with_lock
        from button.CancelView import CancelView
        from utils.const import CommandChannelId

        
        await interaction.response.defer()

        if interaction.channel.id != CommandChannelId:
            await interaction.followup.send("Seul le salon commandes-ladder autorise l'utilisation de cette commande. Cet incident sera signalé.")
            return
        
        if not image.content_type.startswith("image/") or not image2.content_type.startswith("image/"):
            await interaction.followup.send("Le fichier fourni n'est pas une image !", ephemeral=True)
            return

        targets = [joueur1, joueur2, joueur3, joueur4, joueur5]

        for target_name in targets : 
            if targets.count(target_name) > 1:
                await interaction.followup.send("Un joueur est mentionné plusieurs fois !", ephemeral=True)
                return
        valid_targets_count = sum(1 for joueur in targets if joueur is not None)
        amount_of_point = calculate_point(nb_of_opponent, event, victory, valid_targets_count)

        participants = []
        for target_name in targets:
            if target_name is None:
                continue  

            member = interaction.guild.get_member_named(target_name)
            i = target_exist(players, member.mention)
            if (i >= 0):
                # Si le joueur existe déjà, le recupere
                player_obj = get_player_with_lock(i)
                if player_obj:
                  if player_obj.PVP == False:
                    player_obj.TurnOnPVP()
            else:
                # Si le joueur n'existe pas, crée un nouveau joueur et ajoute-le à la liste
                if member:  # Vérifie si le membre existe dans le serveur
                    player_obj = Player(target_name, 0, 0, member.mention, member.id, 0, 0, 0, 0, 0, True)
                    add_player_with_lock(player_obj)
            player_obj.addScore(amount_of_point)
            if victory:
                player_obj.addVictoryRatio()
            else:
                player_obj.addDefeatRatio()
            player_obj.Print()
            participants.append(player_obj)

        try:
            if image:
                file_path = f'images/{interaction.user}_{int(interaction.created_at.timestamp())}.png'
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                await image.save(file_path)
        except Exception as e:
            print(f"je ne comprend pas l'erreur as e {e}")

        #time = interaction.created_at
        #time += timedelta(hours=1)
        #formatted_time = time.strftime("%Y-%m-%d %H:%M:%S")
        embed = create_embeds(players, image.url, event, amount_of_point, victory, nb_of_opponent, participants)
        embed.set_image(url=image.url)
        embeds = [embed]
        embed_img = discord.Embed(url=image.url)
        embed_img.set_image(url=image2.url)
        embeds.append(embed_img)

        view = CancelView(participants, amount_of_point, interaction.user, victory)
        message = await interaction.channel.send(embeds=embeds, view=view)
        view.set_message(message)
        ranking_embed = create_embeds_ranking(players)
        embed_message = getEmbedMessage()
        await embed_message.edit(embed=ranking_embed)
        await interaction.followup.send("Commande traitée avec succès.", ephemeral=True)

        log_db(players)

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
    
    async def event_autocomplete(self, interaction: discord.Interaction, current: str):
        # Importer ici pour éviter les importations circulaires
        from utils.utils import EVENT_CHOICES
        # Afficher toute la liste d'événements ou filtrer selon ce que l'utilisateur tape
        return [
            app_commands.Choice(name=event, value=event) for event in EVENT_CHOICES
        ]
    
    async def difficulty_autocomplete(self, interaction: discord.Interaction, current: str):
        # Importer ici pour éviter les importations circulaires
        from utils.utils import DIFFICULTY_CHOICES
        return [
            app_commands.Choice(name=f"Difficulté {difficulty}", value=str(difficulty))
            for difficulty in DIFFICULTY_CHOICES
            if current in str(difficulty)  # Filtrage dynamique
        ]

async def setup(bot):
    await bot.add_cog(AddScoreCog(bot))