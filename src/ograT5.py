import discord 
from discord import app_commands
from discord.ext import commands
from utils import *
from bot import *

class OrgaModal(discord.ui.Modal, title="organisons ensemble un evenement"):
    date_input = discord.ui.TextInput(
        label="date de l'evenement",
        placeholder="Exemple : 17/04/25",
        required=True,
        max_length=100
    )
    
    time_input = discord.ui.TextInput(
        label="Heure de l'evenement",
        placeholder="Exemple : 19:00",
        required=True,
        max_length=5
    )

    async def on_submit(self, interaction: discord.Interaction):
        date_str = self.date_input.value
        time_str = self.time_input.value

        try:
            # Combine les deux en datetime
            full_datetime = datetime.datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M")
            await interaction.response.send_message(
                f"✅ Date et heure reçues : {full_datetime.strftime('%d/%m/%Y à %H:%M')}",
                ephemeral=True
            )
        except ValueError:
            await interaction.response.send_message(
                "❌ Format invalide. Utilise JJ/MM/AAAA pour la date et HH:MM pour l'heure.",
                    ephemeral=True
            )

