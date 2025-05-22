import threading

class player :
  def __init__(self, pseudo : str, point : int, rank : int, arobase : str, discord_id : int, exoScore : int = 0, exoRank : int = 0,
                victoryRatio : int = 0, defeatRatio : int = 0, all_time_point : int = 0, PVP : bool = False) :
    self.pseudo = pseudo
    self.arobase = arobase
    self.point = point
    self.rank = rank
    self.discord_id = discord_id
    self.exoScore = exoScore
    self.exoRank = exoRank
    self.victoryRatio = victoryRatio
    self.defeatRatio = defeatRatio
    self.all_time_point = all_time_point
    self.PVP = PVP
    self.lock = threading.Lock()

  def addScore(self, point : int) -> None:
    with self.lock:
      self.point += point
      self.all_time_point += point
      if self.point < 0:
        self.point = 0

  def clearPoint(self) -> None:
    with self.lock:
      self.point = 0
  
  def clearRank(self) -> None:
    with self.lock:
      self.rank = 0

  def clearPVP(self) -> None:
    with self.lock:
      self.point = 0
      self.rank = 0
      self.PVP = False

  def addVictoryRatio(self) -> None:
    with self.lock:
      self.victoryRatio += 1

  def addDefeatRatio(self) -> None:
    with self.lock:
      self.defeatRatio += 1
    
  def SetExoScore(self, point : int) -> None:
    with self.lock:
      self.exoScore = point

  def SetExoRank(self, rank : int) -> None:
    with self.lock:
      self.exoRank = rank

  def TurnOnPVP(self) -> None:
    with self.lock:
      self.PVP = True

  def TurnOffPVP(self) -> None:
    with self.lock:
      self.PVP = False

  def setExoPoint(self, point : int, rank : int) -> None:
    with self.lock:
      self.exoPoints = point
      self.exoRank = rank

  def Print(self) -> None:
    print(f"{self.pseudo}{self.arobase} : {self.point} points, ==> {self.rank}")

  def Db_log(self, f) -> None:
    print(f"{self.pseudo},{self.point},{self.rank},{self.arobase},{self.discord_id},{self.exoScore},{self.exoRank},{self.victoryRatio},{self.defeatRatio},{self.all_time_point}", file=f)

player_lock = threading.Lock()
players :list[player] = []

def get_player_with_lock(index : int) -> player:
  with player_lock:
    if 0 <= index < len(players):
      return players[index]
    return None

def add_player_with_lock(player : player) -> int:
  with player_lock:
    players.append(player)
    return len(players) - 1 
  