import math
from baseprobabilities import *
from play_by_play_collector import *


class GameState:
    def __init__(self):
        self.IsNeutral = False
        self.IsNBA = False
        self.HCA = 0
        self.HCAAdj = 0
        self.Total_Possessions = 0
        self.Quarter = 1
        self.Halftime_Point = 0
        self.T1Points = 0
        self.T2Points = 0
        self.IsOT = 0
        self.PossessionNumber = 0
        self.PossessingTeam = ""
        self.Collector = Play_By_Play_Collector()

    def SetInitialValues(self, neutral, nba_match):
        if neutral == False:
            self.HCA = -0.01
            self.HCAAdj = round(-0.01 / -3, 12)
        else:
            self.IsNeutral = True
            self.HCA = 0
            self.HCAAdj = 0
        self.IsNBA = nba_match

    def SetGameHCA(self):
        if self.IsNeutral:
            self.HCA = 0
            self.HCAAdj = 0
        else:
            self.HCA = 0.025

    def SetPossessions(self, t1Pace, t2Pace):
        self.Total_Possessions = t1Pace + t2Pace
        self.Halftime_Point = self.Total_Possessions / 2

    def IncrementPossessions(self):
        self.PossessionNumber += 1
        if (
            self.Quarter == 1
            and self.IsNBA == True
            and self.PossessionNumber == math.floor(self.Total_Possessions / 4)
        ):
            self.Quarter = 2
        elif (
            self.Quarter == 2
            and self.IsNBA == True
            and self.PossessionNumber == math.floor(self.Total_Possessions / 2)
        ):
            self.Quarter = 3
        elif (
            self.Quarter == 3
            and self.IsNBA == True
            and self.PossessionNumber == math.floor(self.Total_Possessions / 1.5)
        ):
            self.Quarter = 4

    def SetOvertime(self):
        self.IsOT = True
        self.Total_Possessions += math.floor((self.Total_Possessions) / 8)

    def SetPossessingTeam(self, team):
        self.PossessingTeam = team

    def AddPoints(self, points, isHome):
        if isHome == True:
            self.T1Points += points
        else:
            self.T2Points += points
