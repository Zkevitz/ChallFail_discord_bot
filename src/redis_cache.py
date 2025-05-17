import redis
import json
import os
from dotenv import load_dotenv
from typing import Any, Optional, Union, List, Dict

# Charger les variables d'environnement
load_dotenv()

class RedisCache:
    """
    Classe pour gérer le cache Redis dans le bot Discord.
    """
    def __init__(self, host='localhost', port=6379, db=0, password=None, expire_time=3600):

        # Récupérer les paramètres depuis les variables d'environnement si disponibles
        redis_host = os.getenv('REDIS_HOST', host)
        redis_port = int(os.getenv('REDIS_PORT', port))
        redis_db = int(os.getenv('REDIS_DB', db))
        redis_password = os.getenv('REDIS_PASSWORD', password)
        
        self.expire_time = int(os.getenv('REDIS_EXPIRE_TIME', expire_time))
        
        # Connexion à Redis
        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            password=redis_password,
            decode_responses=True  # Pour décoder automatiquement les réponses en UTF-8
        )
        
        try:
            # Vérifier la connexion
            self.redis_client.ping()
            print("✅ Connexion à Redis établie avec succès")
        except redis.ConnectionError:
            print("❌ Erreur de connexion à Redis")
            self.redis_client = None
    
    def is_connected(self) -> bool:
        """Vérifie si la connexion à Redis est active"""
        if not self.redis_client:
            return False
        try:
            self.redis_client.ping()
            return True
        except:
            return False
    
    def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """
        Stocke une valeur dans le cache.
        
        Args:
            key (str): Clé de cache
            value (Any): Valeur à stocker (sera sérialisée en JSON)
            expire (int, optional): Temps d'expiration en secondes"""
            
        if not self.is_connected():
            return False
        
        try:
            # Sérialiser les objets complexes en JSON
            if not isinstance(value, (str, int, float, bool)):
                value = json.dumps(value)
            
            # Définir la valeur dans Redis
            self.redis_client.set(key, value)
            
            # Définir le temps d'expiration
            if expire is None:
                expire = self.expire_time
            
            if expire > 0:
                self.redis_client.expire(key, expire)
            
            return True
        except Exception as e:
            print(f"❌ Erreur lors de la mise en cache: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Récupère une valeur du cache.
        
        Args:
            key (str): Clé de cache
            default (Any): Valeur par défaut si la clé n'existe pas
            
        Returns:
            Any: Valeur stockée ou valeur par défaut
        """
        if not self.is_connected():
            return default
        
        try:
            # Récupérer la valeur de Redis
            value = self.redis_client.get(key)
            
            if value is None:
                return default
            
            # Essayer de désérialiser la valeur JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                # Si ce n'est pas du JSON valide, retourner la valeur telle quelle
                return value
        except Exception as e:
            print(f"❌ Erreur lors de la récupération du cache: {e}")
            return default
    
    def delete(self, key: str) -> bool:
        """
        Supprime une clé du cache.
        
        Args:
            key (str): Clé à supprimer
            
        Returns:
            bool: True si l'opération a réussi, False sinon
        """
        if not self.is_connected():
            return False
        
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            print(f"❌ Erreur lors de la suppression du cache: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """
        Vérifie si une clé existe dans le cache.
        
        Args:
            key (str): Clé à vérifier
            
        Returns:
            bool: True si la clé existe, False sinon
        """
        if not self.is_connected():
            return False
        
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            print(f"❌ Erreur lors de la vérification du cache: {e}")
            return False
    
    def flush(self) -> bool:
        """
        Vide tout le cache.
        
        Returns:
            bool: True si l'opération a réussi, False sinon
        """
        if not self.is_connected():
            return False
        
        try:
            self.redis_client.flushdb()
            return True
        except Exception as e:
            print(f"❌ Erreur lors du vidage du cache: {e}")
            return False
    
    def set_player_data(self, player_id: Union[int, str], data: Dict) -> bool:
        """
        Stocke les données d'un joueur dans le cache.
        
        Args:
            player_id (Union[int, str]): ID Discord du joueur
            data (Dict): Données du joueur
            
        Returns:
            bool: True si l'opération a réussi, False sinon
        """
        key = f"player:{player_id}"
        return self.set(key, data)
    
    def get_player_data(self, player_id: Union[int, str]) -> Optional[Dict]:
        """
        Récupère les données d'un joueur du cache.
        
        Args:
            player_id (Union[int, str]): ID Discord du joueur
            
        Returns:
            Optional[Dict]: Données du joueur ou None si non trouvé
        """
        key = f"player:{player_id}"
        return self.get(key)
    
    def set_ranking(self, ranking_data: List[Dict]) -> bool:
        """
        Stocke les données de classement dans le cache.
        
        Args:
            ranking_data (List[Dict]): Données de classement
            
        Returns:
            bool: True si l'opération a réussi, False sinon
        """
        return self.set("ranking", ranking_data)
    
    def get_ranking(self) -> Optional[List[Dict]]:
        """
        Récupère les données de classement du cache.
        
        Returns:
            Optional[List[Dict]]: Données de classement ou None si non trouvé
        """
        return self.get("ranking")

# Créer une instance unique pour l'utiliser dans tout le projet
cache = RedisCache()
