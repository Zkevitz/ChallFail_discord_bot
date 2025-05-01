from datetime import datetime
from player import player

def generate_backup_filename(base_name="LadderArchives"):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  # Format YYYY-MM-DD_HH-MM-SS
    return f"{base_name}/LadderArchives{timestamp}.txt"

def createPlayerRanking(players):
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

def createExoRanking(players):
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

        players[i].exoRank = rank  # Attribuer le rang au joueur
    
    return players

def log_db(players):
  with open('db/player_db.txt', 'w') as file:
    for player in players:
      player.Db_log(file)


def calculate_point(nb_of_opponent, event, victory) :
  point = 0
  # print(nb_of_opponent)
  # print(event)
  # print(victory)

  if (event ==  "Attaques de Percepteur contre DOSE") : 
    return 22
  if(event == "Attaques de percepteur(alliance cibler sans defenseur)") :
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
    if not victory and nb_of_opponent == 5:
      return 2
    if nb_of_opponent == 1 and victory:
      return 1
    elif nb_of_opponent == 2 and victory:
      return 2
    elif nb_of_opponent == 3 and victory:
      return 3
    elif nb_of_opponent == 4 and victory:
      return 12
    elif nb_of_opponent == 5 and victory:
      return 22

  return point