@bot.tree.command(name="addp", description="Ajoute un nouveau joueur en utilisant ton pseudo pseudo discord")
@app_commands.describe(newplayer="Choisissez un utilisateur")
@app_commands.autocomplete(newplayer=target_autocomplete)
async def AddPlayer(interaction2: discord.Interaction, newplayer : str = None):

  #print(dir(ctx.author))
  #print(ctx.author.global_name)  
  return

  if interaction2.user.nick:
    pseudodisc = interaction2.user.nick.lower()
  else:
    pseudodisc = interaction2.user.global_name.lower()
    
  
  if(newplayer and newplayer.lower() == pseudodisc):
 
    if any(player.pseudo.lower() == newplayer.lower() for player in players):
      await interaction2.response.send_message(f"❌ Le joueur {newplayer} est deja dans la liste !")
      return

    print(interaction2.user.mention)
    print(interaction2.user.name)
    newPlayer = player(newplayer, 0, 0, interaction2.user.mention)
    players.append(newPlayer)
    await interaction2.response.send_message(f"✅ Le joueur {newplayer} a été ajouté.")
        
    log_db()

  
  else :
    await interaction2.response.send_message(f"❌ Je n'accepte que des nouveaux joueurs par leur pseudo Discord : {pseudodisc} != {newplayer}")
    return
  
