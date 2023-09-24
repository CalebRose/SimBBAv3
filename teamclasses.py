import random
from player import *
from baseprobabilities import *


class ImportDTO:
    def __init__(self, cbb, nba):
        self.CBBResults = cbb
        self.NBAResults = nba


class MatchResults:
    def __init__(self, t1, t2, r1, r2, game_id, is_nba):
        self.TeamOne = t1
        self.TeamTwo = t2
        self.RosterOne = r1
        self.RosterTwo = r2
        self.GameID = game_id
        self.IsNBA = is_nba


class Team:
    def __init__(self, t):
        self.TeamName = t["TeamName"]
        self.Mascot = t["Mascot"]
        self.Abbr = t["Abbr"]
        self.Conference = t["Conference"]
        self.Coach = t["Coach"]
        self.ID = t["ID"]
        self.Stats = TeamStats()


class TeamStats:
    def __init__(self):
        self.Points = 0
        self.Possessions = 0
        self.FGM = 0
        self.FGA = 0
        self.FGPercent = 0
        self.ThreePointsMade = 0
        self.ThreePointAttempts = 0
        self.ThreePointPercent = 0
        self.FTM = 0
        self.FTA = 0
        self.FTPercent = 0
        self.Rebounds = 0
        self.OffRebounds = 0
        self.DefRebounds = 0
        self.Assists = 0
        self.Steals = 0
        self.Blocks = 0
        self.TotalTurnovers = 0
        self.LargestLead = 0
        self.FirstHalfScore = 0
        self.SecondQuarterScore = 0
        self.SecondHalfScore = 0
        self.FourthQuarterScore = 0
        self.OvertimeScore = 0
        self.Fouls = 0

    def AddPoints(self, pts, poss, ht, is_ot, is_nba, q):
        self.Points += pts
        if is_nba == False:
            if poss <= ht:
                self.FirstHalfScore += pts
            elif is_ot == False:
                self.SecondHalfScore += pts
            else:
                self.OvertimeScore += pts
        else:
            if q == 1:
                self.FirstHalfScore += pts
            elif q == 2:
                self.SecondQuarterScore += pts
            elif q == 3:
                self.SecondHalfScore += pts
            elif q == 4:
                self.FourthQuarterScore += pts
            else:
                self.OvertimeScore += pts

    def CalculateLead(self, pts, diff):
        if self.LargestLead < diff:
            self.LargestLead += pts

    def AddFieldGoal(self, made_shot):
        self.FGA += 1
        if made_shot == True:
            self.FGM += 1
        self.FGPercent = self.FGM / self.FGA

    def AddThreePointShot(self, made_shot):
        self.ThreePointAttempts += 1
        if made_shot == True:
            self.ThreePointsMade += 1
        self.ThreePointPercent = self.ThreePointsMade / self.ThreePointAttempts

    def AddFreeThrow(self, made_shot):
        self.FTA += 1
        if made_shot == True:
            self.FTM += 1
        self.FTPercent = self.FTM / self.FTA

    def AddRebound(self, is_offense):
        self.Rebounds += 1
        if is_offense == True:
            self.OffRebounds += 1
        else:
            self.DefRebounds += 1

    def AddAssist(self):
        self.Assists += 1

    def AddSteal(self):
        self.Steals += 1

    def AddBlocks(self):
        self.Blocks += 1

    def AddTurnover(self):
        self.TotalTurnovers += 1

    def AddPossession(self):
        self.Possessions += 1

    def AddFoul(self):
        self.Fouls += 1
