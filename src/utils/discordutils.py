import discord
from discord import app_commands
from utils.const import ADMIN_CHOICES, EVENT_CHOICES, DIFFICULTY_CHOICES

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

@app_commands.describe(target="Choisissez un utilisateur")
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
