import discord
from player import player, players
from myembed.Myembed import create_embeds_ranking, embed_message
from utils.utils import log_db
from utils.const import AdminIds
from datetime import datetime

class CancelButton(discord.ui.Button):
  def __init__(self, participants : list[player], gain : int, author : discord.Member, view : discord.ui.View, isVictory : bool):
    super().__init__(label="Cancel", style=discord.ButtonStyle.danger)
    self.participants = participants
    self.gain = gain
    self.isVictory = isVictory
    self.author = author
    self.custom_view = view

  async def callback(self, interaction: discord.Interaction):
    await interaction.response.defer()

    # Vérifier si c'est l'auteur ou un admin avec niveau ≥ 1
    is_admin = False
    for role in interaction.user.roles:
        role_id_str = str(role.id)
        if role_id_str in AdminIds:
            is_admin = True
            break
    
    if self.author != interaction.user and not is_admin:
        await interaction.followup.send("❌ Tu n'as pas la permission d'annuler cette action !", ephemeral=False)
        return

    #print(dir(interaction))
    await self.author.send(f"Ton post datant du {datetime.now().strftime('%Y-%m-%d_%H-%M-%S')} a ete annule par {interaction.user}")


    for participant in self.participants :
      with participant.lock:
        participant.all_time_point -= self.gain
        participant.point -= self.gain
        if participant.point < 0 :
          participant.point = 0
        if participant.all_time_point < 0 :
          participant.all_time_point = 0
        if not self.isVictory :
          participant.defeatRatio -= 1
        elif self.isVictory :
          participant.victoryRatio -= 1


    log_db(players)
    ranking_embed = create_embeds_ranking(players)
    await embed_message.edit(embed=ranking_embed)

    if self.view.message:
      await self.view.message.edit(content="❌ Action annulée.", view=None)
    await interaction.followup.send("✅ Action annulée.", ephemeral=False)
    self.disabled = True
    await interaction.message.edit(view=self.view)
    self.view.stop()

class CancelView(discord.ui.View):
  def __init__(self, participants : list[player], gain : int, author : discord.Member, isVictory : bool):
    super().__init__(timeout=None)
    self.participants = participants
    self.gain = gain
    self.isVictory = isVictory
    self.author = author
    self.message = None
    self.add_item(CancelButton(self.participants, self.gain, self.author, self, self.isVictory))
  
  async def on_timeout(self):
    if self.message is None:
      print("Erreur message is None!!")

    try: 
      new_view = CancelView(self.participants, self.gain, self.author, self.formatted_time)
      new_view.message = self.message
      await self.message.edit(content="bouton renouvele", view=new_view)
    except discord.NotFound:
        print("⚠️ Erreur : Le message n'existe plus.")
    except discord.Forbidden:
        print("❌ Erreur : Permissions insuffisantes pour modifier le message.")
    except discord.HTTPException as e:
        print(f"⚠️ Erreur HTTP : {e}")  
  
  def set_message(self, message: discord.Message):
    self.message = message