class player :
  def __init__(self, pseudo, point, rank, arobase, exoScore = 0, exoRank = 0) :
    self.pseudo = pseudo
    self.arobase = arobase
    self.point = point
    self.rank = rank
    self.exoScore = exoScore
    self.exoRank = exoRank

  def addScore(self, point):
    self.point += point
    if self.point < 0:
      self.point = 0

  def SetExoScore(self, point):
    self.exoScore = point

  def setExoPoint(self, point, rank):
    self.exoPoints = point
    self.exoRank = rank

  def Print(self):
    print(f"{self.pseudo}{self.arobase} : {self.point} points, ==> {self.rank}")

  def Db_log(self, f):
    print(f"{self.pseudo},{self.point},{self.rank},{self.arobase},{self.exoScore},{self.exoRank}", file=f)