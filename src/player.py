class player :
  def __init__(self, pseudo : str, point : int, rank : int, arobase : str, discord_id : int, exoScore : int = 0, exoRank : int = 0,
                victoryRatio : int = 0, defeatRatio : int = 0, all_time_point : int = 0) :
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

  def addScore(self, point : int) -> None:
    self.point += point
    self.all_time_point += point
    if self.point < 0:
      self.point = 0

  def clearPoint(self) -> None:
    self.point = 0
  
  def clearRank(self) -> None:
    self.rank = 0

  def addVictoryRatio(self) -> None:
    self.victoryRatio += 1

  def addDefeatRatio(self) -> None:
    self.defeatRatio += 1
    
  def SetExoScore(self, point : int) -> None:
    self.exoScore = point

  def SetExoRank(self, rank : int) -> None:
    self.exoRank = rank

  def setExoPoint(self, point : int, rank : int) -> None:
    self.exoPoints = point
    self.exoRank = rank

  def Print(self) -> None:
    print(f"{self.pseudo}{self.arobase} : {self.point} points, ==> {self.rank}")

  def Db_log(self, f) -> None:
    print(f"{self.pseudo},{self.point},{self.rank},{self.arobase},{self.discord_id},{self.exoScore},{self.exoRank},{self.victoryRatio},{self.defeatRatio},{self.all_time_point}", file=f)


players :list[player] = []