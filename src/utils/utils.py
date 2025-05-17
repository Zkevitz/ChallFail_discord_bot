from datetime import datetime
from player import player
from typing import List
import os
from .json_utils import save_players_to_json

def generate_backup_filename(base_name="LadderArchives") -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  # Format YYYY-MM-DD_HH-MM-SS
    return f"{base_name}/LadderArchives{timestamp}.txt"

def createPlayerRanking(players : list[player]) -> list[player]:
    players.sort(key=lambda x: x.point, reverse=True)  # Tri des joueurs par points (descendant)

    rank = 1  # Premier rang attribué au premier joueur
    equal_count = 0  # Compte le nombre d'égalités

    for i in range(len(players)):
        if i > 0:
            if players[i].point < players[i-1].point:
                # Nouveau rang = rang précédent + nombre d'égalités + 1
                rank += equal_count + 1
                equal_count = 0  # Reset du compteur d'égalités
            else:
                equal_count += 1  # Incrémente le compteur d'égalités

        players[i].rank = rank  # Attribuer le rang au joueur
    
    return players

def createExoRanking(players : list[player]) -> list[player]:
    # Tri par exoScore décroissant (le plus grand score en rang 1)
    players.sort(key=lambda x: x.exoScore, reverse=True)
    
    rank = 1  # Premier rang attribué au premier joueur
    equal_count = 0  # Compte le nombre d'égalités

    for i in range(len(players)):
        if i > 0:
            # Comparer avec le joueur précédent (déjà trié)
            if players[i].exoScore < players[i-1].exoScore:
                # Nouveau rang = rang précédent + nombre d'égalités + 1
                rank += equal_count + 1
                equal_count = 0  # Reset du compteur d'égalités
            else:
                equal_count += 1  # Incrémente le compteur d'égalités

        players[i].SetExoRank(rank)  # Attribuer le rang au joueur
    
    return players

def log_db(players : list[player]) -> None:
  
  if os.getenv("STOCKAGE_MODE") == "json":
    save_players_to_json(players, 'db/player_db.json')
  
  else:# Ancien system garder de coter on sait jamais
    with open('db/player_db.txt', 'w') as file:
      for player in players:
        player.Db_log(file)


def calculate_point(nb_of_opponent : int, event : str, victory : bool, nb_of_participants : int) -> int:
  point = 0
  # print(nb_of_opponent)
  # print(event)
  # print(victory)
  print(nb_of_participants)
  if (event ==  "Attaques de Percepteur contre DOSE") :
    if (nb_of_opponent == 5):
      return 22
    else:
      return 1
  if(event == "Attaques de percepteur(alliance cibler sans defenseur)") :
    if (nb_of_opponent == 5):
      return 22
    else:
      return 1
  
  if event == "Attaques de Percepteur":
    if not victory:  # Si l'attaque échoue
        return 0
    else:
        if nb_of_opponent <= 3:
          return 0
        elif nb_of_opponent == 4:
          return 4
        elif nb_of_opponent == 5:
          return 7

    # Cas : Défense contre une attaque
  elif event == "Defenses de percepteur":
    if not victory and nb_of_opponent == 5 and nb_of_participants == 5:
      return 10
    if nb_of_opponent == 1 and victory:
      return 1
    elif nb_of_opponent == 2 and victory:
      return 2
    elif nb_of_opponent == 3 and victory:
      return 5
    elif nb_of_opponent == 4 and victory:
      return 18
    elif nb_of_opponent == 5 and victory:
      return 35

  return point

def get_player_by_name(name : str, players : list[player]) -> player | None:
  for player in players :
    if player.pseudo.lower() == name.lower():
      return player
  return None

def target_exist(players : list[player], target_name : str) -> int:
  i = 0
  for player in players :
    if target_name.lower() == player.arobase.lower():
      return i
    else:
     i+=1
  return -1