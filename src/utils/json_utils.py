import json
import os
from player import player
from typing import List
import shutil
from datetime import datetime

def generate_backup_filename(base_name="LadderArchives"):
    """Génère un nom de fichier de sauvegarde avec un timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  # Format YYYY-MM-DD_HH-MM-SS
    return f"{base_name}/LadderArchives{timestamp}.json"

def player_to_dict(player_obj):
    """Convertit un objet player en dictionnaire pour la sérialisation JSON"""
    return {
        "pseudo": player_obj.pseudo,
        "point": player_obj.point,
        "rank": player_obj.rank,
        "arobase": player_obj.arobase,
        "discord_id": player_obj.discord_id,
        "exoScore": player_obj.exoScore,
        "exoRank": player_obj.exoRank,
        "victoryRatio": player_obj.victoryRatio,
        "defeatRatio": player_obj.defeatRatio,
        "all_time_point": player_obj.all_time_point
    }

def dict_to_player(player_dict):
    """Convertit un dictionnaire en objet player"""
    return player(
        pseudo=player_dict["pseudo"],
        point=player_dict["point"],
        rank=player_dict["rank"],
        arobase=player_dict["arobase"],
        discord_id=player_dict["discord_id"],
        exoScore=player_dict["exoScore"],
        exoRank=player_dict["exoRank"],
        victoryRatio=player_dict.get("victoryRatio", 0),
        defeatRatio=player_dict.get("defeatRatio", 0),
        all_time_point=player_dict.get("all_time_point", 0)
    )

def save_players_to_json(players: List[player], filepath='db/player_db.json'):
    """Sauvegarde la liste des joueurs dans un fichier JSON"""
    # Créer le répertoire si nécessaire
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # Convertir chaque joueur en dictionnaire
    players_data = [player_to_dict(p) for p in players]
    
    # Écrire dans le fichier JSON
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(players_data, f, ensure_ascii=False, indent=2)

def load_players_from_json(filepath='db/player_db.json'):
    """Charge la liste des joueurs depuis un fichier JSON"""
    if not os.path.exists(filepath):
        return []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            players_data = json.load(f)
        
        # Convertir chaque dictionnaire en objet player
        return [dict_to_player(p) for p in players_data]
    except Exception as e:
        print(f"Erreur lors du chargement du fichier JSON: {e}")
        return []

def backup_player_db(source_file='db/player_db.json'):
    """Crée une sauvegarde du fichier de base de données des joueurs"""
    if not os.path.exists(source_file):
        print(f"Le fichier {source_file} n'existe pas, aucune sauvegarde créée.")
        return None
    
    backup_file = generate_backup_filename()
    os.makedirs(os.path.dirname(backup_file), exist_ok=True)
    
    try:
        shutil.copy2(source_file, backup_file)
        print(f"Sauvegarde créée: {backup_file}")
        return backup_file
    except Exception as e:
        print(f"Erreur lors de la création de la sauvegarde: {e}")
        return None

def convert_txt_to_json(txt_file='db/player_db.txt', json_file='db/player_db.json') -> list[player]:
    """Convertit le fichier texte existant en format JSON"""
    players = []
    
    try:
        with open(txt_file, 'r', encoding='utf-8') as file:
            for line in file:
                # Supprimer les espaces et les retours à la ligne
                line = line.strip()
                # Séparer la ligne par des virgules
                data = line.split(',')
                
                # Créer un objet Player avec les données extraites
                if len(data) >= 5:
                    if len(data) == 5:
                        pseudo, points1, points2, arobase, discord_id = data
                        exoPoints = 0
                        exoRank = 0
                        victoryRatio = 0
                        defeatRatio = 0
                        all_time_point = 0
                    else:
                        pseudo, points1, points2, arobase, discord_id, exoPoints, exoRank, victoryRatio, defeatRatio, all_time_point = data
                    
                    # Convertir les points en entiers
                    points1 = int(points1)
                    points2 = int(points2)
                    discord_id = int(discord_id)
                    exoPoints = int(exoPoints)
                    exoRank = int(exoRank)
                    victoryRatio = int(victoryRatio)
                    defeatRatio = int(defeatRatio)
                    all_time_point = int(all_time_point)
                    
                    # Ajouter le joueur à la liste
                    players.append(player(
                        pseudo=pseudo,
                        point=points1,
                        rank=points2,
                        arobase=arobase,
                        discord_id=discord_id,
                        exoScore=exoPoints,
                        exoRank=exoRank,
                        victoryRatio=victoryRatio,
                        defeatRatio=defeatRatio,
                        all_time_point=all_time_point
                    ))
        
        # Sauvegarder les joueurs au format JSON
        save_players_to_json(players, json_file)
        print(f"Conversion réussie: {len(players)} joueurs convertis de {txt_file} vers {json_file}")
        return players
    except Exception as e:
        print(f"Erreur lors de la conversion: {e}")
        return []
