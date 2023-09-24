import util


class Roster:
    def __init__(self, r):
        self.roster = r


class Player:
    def __init__(
        self, is_nba, cp, finishingBonus, midBonus, threePtBonus, bwBonus, rebBonus
    ):
        self.ID = cp["ID"]
        self.FirstName = cp["FirstName"]
        self.LastName = cp["LastName"]
        self.TeamID = cp["TeamID"]
        self.TeamAbbr = cp["TeamAbbr"]
        if is_nba == False:
            self.IsRedshirt = cp["IsRedshirt"]
            self.IsRedshirting = cp["IsRedshirting"]
            self.Stars = cp["Stars"]
        else:
            self.IsGLeague = cp["IsGLeague"]
            self.IsTwoWay = cp["IsTwoWay"]
            self.IsInternational = cp["IsInternational"]
            self.IsNBA = cp["IsNBA"]
        self.Position = cp["Position"]
        self.Age = cp["Age"]
        self.Height = util.Get_Inches(cp["Height"])
        self.Shooting2 = cp["Shooting2"] + midBonus
        self.Shooting3 = cp["Shooting3"] + threePtBonus
        self.FreeThrow = cp["FreeThrow"]
        self.Finishing = cp["Finishing"] + finishingBonus
        self.Ballwork = cp["Ballwork"] + bwBonus
        self.Rebounding = cp["Rebounding"] + rebBonus
        self.InteriorDefense = cp["InteriorDefense"]
        self.PerimeterDefense = cp["PerimeterDefense"]
        self.Stealing = (cp["InteriorDefense"] + cp["PerimeterDefense"]) / 2
        self.Stamina = cp["Stamina"]
        self.Minutes = cp["Minutes"]
        if self.Minutes > self.Stamina:
            self.Minutes = self.Stamina
        self.InsideProportion = cp["InsideProportion"]
        self.MidRangeProportion = cp["MidRangeProportion"]
        self.ThreePointProportion = cp["ThreePointProportion"]
        self.Overall = cp["Overall"]
        self.Stats = PlayerStats(cp)
        self.Shooting = 0
        self.AdjShooting = 0
        self.AdjFinishing = 0
        self.AdjBallwork = 0
        self.AdjRebounding = 0
        self.AdjInteriorDefense = 0
        self.AdjPerimeterDefense = 0
        self.AdjStealing = 0
        self.ReboundingPer = 0
        self.InteriorDefensePer = 0
        self.PerimeterDefensePer = 0
        self.DefensePer = 0
        self.AssistPer = 0
        self.Usage = 0
        self.InsideUsage = 0
        self.MidUsage = 0
        self.ThreePointUsage = 0
        self.DefRateTO = 0

    def get_advanced_stats(
        self,
        totalrebounding,
        totalDefense,
        totalAssist,
        InsideProportion,
        MidProportion,
        ThreePtProportion,
        turnoverBonus,
    ):
        self.Shooting = (self.Shooting2 + self.Shooting3) / 2
        self.AdjShooting = self.Shooting * self.Minutes
        self.AdjFinishing = self.Finishing * self.Minutes
        self.AdjBallwork = self.Ballwork * self.Minutes
        self.AdjRebounding = self.Rebounding * self.Minutes
        self.AdjInteriorDefense = self.InteriorDefense * self.Minutes
        self.AdjPerimeterDefense = self.PerimeterDefense * self.Minutes
        self.AdjStealing = self.Stealing * self.Minutes
        self.ReboundingPer = self.AdjRebounding / totalrebounding
        # self.InteriorDefensePer = self.AdjInteriorDefense / totalDefense
        # self.PerimeterDefensePer = self.AdjPerimeterDefense / totalDefense
        self.DefensePer = (
            ((self.InteriorDefense + self.PerimeterDefense) / 2) * self.Minutes
        ) / totalDefense
        self.AssistPer = self.AdjBallwork / totalAssist
        self.Usage = self.Minutes / 20
        self.InsideUsage = self.InsideProportion / (
            240 * (InsideProportion / 100) * 2.4
        )
        self.MidUsage = self.MidRangeProportion / (240 * (MidProportion / 100) * 2.4)
        self.ThreePointUsage = self.ThreePointProportion / (
            240 * (ThreePtProportion / 100) * 2.4
        )
        self.DefRateTO = (
            (self.PerimeterDefense + self.InteriorDefense + turnoverBonus) / 2
        ) * self.Minutes


class PlayerStats:
    def __init__(self, cp):
        self.PlayerID = cp["ID"]
        self.Minutes = cp["Minutes"]
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
        self.Points = 0
        self.TotalRebounds = 0
        self.OffRebounds = 0
        self.DefRebounds = 0
        self.Assists = 0
        self.Steals = 0
        self.Blocks = 0
        self.Turnovers = 0
        self.Fouls = 0

    def AddPossession(self):
        self.Possessions += 1

    def AddFieldGoal(self, made_shot, pts=0):
        self.Possessions += 1
        self.FGA += 1
        if made_shot:
            self.FGM += 1
            self.Points += pts
        self.FGPercent = self.FGM / self.FGA
        if pts == 3:
            self.AddThreePoint(made_shot)

    def AddThreePoint(self, made_shot):
        self.ThreePointAttempts += 1
        if made_shot:
            self.ThreePointsMade += 1
        self.ThreePointPercent = self.ThreePointsMade / self.ThreePointAttempts

    def AddFTAttempt(self):
        self.FTA += 1
        self.FTPercent = self.FTM / self.FTA

    def AddFTMade(self):
        self.FTA += 1
        self.FTM += 1
        self.FTPercent = self.FTM / self.FTA
        self.Points += 1

    def AddAssist(self):
        self.Assists += 1

    def AddSteal(self):
        self.Steals += 1

    def AddBlock(self):
        self.Blocks += 1

    def AddRebound(self, is_offense):
        self.TotalRebounds += 1
        if is_offense == True:
            self.OffRebounds += 1
        else:
            self.DefRebounds += 1

    def AddTurnover(self):
        self.Turnovers += 1

    def AddFoul(self):
        self.Fouls += 1
