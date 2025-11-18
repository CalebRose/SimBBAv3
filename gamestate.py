import math
from baseprobabilities import *
from play_by_play_collector import *
from constants import *


class GameState:
    def __init__(self):
        self.IsNeutral = False
        self.IsNBA = False
        self.HCA = 0
        self.HCAAdj = 0
        self.Total_Possessions = 0
        self.Max_Possessions = 0
        self.Quarter = 1
        self.Halftime_Point = 0
        self.T1Points = 0
        self.T2Points = 0
        self.IsOT = 0
        self.PossessionNumber = 0
        self.PossessingTeam = ""
        self.Collector = Play_By_Play_Collector()
        self.ThreePointEvents = 0
        self.ThreeShotMade = 0
        self.ThreeShotMissed = 0
        self.ThreeShotBlocked = 0
        self.ThreeShotFoulMiss = 0
        self.ThreeShotFoulMade = 0
        self.MidEvents = 0
        self.MidShotMade = 0
        self.MidShotMissed = 0
        self.MidShotBlocked = 0
        self.MidShotFoulMiss = 0
        self.MidShotFoulMade = 0
        self.TurnoverEvents = 0
        self.InsideEvents = 0
        self.InsideShotMade = 0
        self.InsideShotMissed = 0
        self.InsideShotBlocked = 0
        self.InsideShotFoulMiss = 0
        self.InsideShotFoulMade = 0
        self.StealEvents = 0
        self.Offensive_Rebounds = 0
        self.Defensive_Rebounds = 0
        self.ReboundingPlayer = None
        self.OffTheRebound = False
        self.Capacity = 0

    def SetInitialValues(self, neutral, nba_match):
        if neutral == False:
            self.HCA = -0.01
            self.HCAAdj = round(-0.01 / -3, 12)
        else:
            self.IsNeutral = True
            self.HCA = 0
            self.HCAAdj = 0
        self.IsNBA = nba_match

    def SetGameHCA(self, capacity):
        self.Capacity = capacity
        if self.IsNeutral:
            self.HCA = 0
            self.HCAAdj = 0
        else:
            percentage = capacity / 12500
            if percentage > 1:
                percentage = 1
            self.HCA = 0.035 * percentage

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

    def DecrementPossessions(self):
        self.PossessionNumber -= 1

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

    def IncrementEventCount(self, event):
        if event == "Three":
            self.ThreePointEvents += 1
        elif event == "Mid":
            self.MidEvents += 1
        elif event == "Inside":
            self.InsideEvents += 1
        elif event == "Turnover":
            self.TurnoverEvents += 1
        elif event == "Steal":
            self.StealEvents += 1
        elif event == "OffReb":
            self.Offensive_Rebounds += 1
        elif event == "DefReb":
            self.Defensive_Rebounds += 1

    def IncrementShotResultCount(self, shot, res):
        if shot == "Three":
            if res == "Made":
                self.ThreeShotMade += 1
            elif res == "Missed":
                self.ThreeShotMissed += 1
            elif res == "Blocked":
                self.ThreeShotBlocked += 1
            elif res == "FoulMissed":
                self.ThreeShotFoulMiss += 1
            elif res == "FoulMade":
                self.ThreeShotFoulMade += 1
        elif shot == "Mid":
            if res == "Made":
                self.MidShotMade += 1
            elif res == "Missed":
                self.MidShotMissed += 1
            elif res == "Blocked":
                self.MidShotBlocked += 1
            elif res == "FoulMissed":
                self.MidShotFoulMiss += 1
            elif res == "FoulMade":
                self.MidShotFoulMade += 1
        elif shot == "Inside":
            if res == "Made":
                self.InsideShotMade += 1
            elif res == "Missed":
                self.InsideShotMissed += 1
            elif res == "Blocked":
                self.InsideShotBlocked += 1
            elif res == "FoulMissed":
                self.InsideShotFoulMiss += 1
            elif res == "FoulMade":
                self.InsideShotFoulMade += 1

    def GetShootingBase(self, shot_type):
        if shot_type == 1 and self.IsNBA:
            return nba_three_base
        if shot_type == 1 and self.IsNBA == False:
            return cbb_three_base
        if shot_type == 2 and self.IsNBA:
            return nba_mid_base
        if shot_type == 2 and self.IsNBA == False:
            return cbb_mid_base
        if shot_type == 3 and self.IsNBA:
            return nba_ins_base
        if shot_type == 3 and self.IsNBA == False:
            return cbb_ins_base

    def GetShootingAdj(self, shot_type):
        if shot_type == 1 and self.IsNBA:
            return nba_three_adj
        if shot_type == 1 and self.IsNBA == False:
            return cbb_three_adj
        if shot_type == 2 and self.IsNBA:
            return nba_mid_adj
        if shot_type == 2 and self.IsNBA == False:
            return cbb_mid_adj
        if shot_type == 3 and self.IsNBA:
            return nba_ins_adj
        if shot_type == 3 and self.IsNBA == False:
            return cbb_ins_adj
