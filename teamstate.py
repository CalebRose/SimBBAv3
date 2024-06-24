import random
from player import *
from baseprobabilities import *


class TeamState:
    def __init__(self):
        self.OffensiveFormation = ""
        self.DefensiveFormation = ""
        self.OffensiveStyle = ""
        self.InsShootingBonus = 0
        self.MidShootingBonus = 0
        self.t3ptShootingBonus = 0
        self.BallworkBonus = 0
        self.ReboundingBonus = 0
        self.TurnoverBonus = 0
        self.Rebounding = 0
        self.StealBlock = 0
        self.Ballwork = 0
        self.InsPro = 0
        self.MidPro = 0
        self.T3ptPro = 0
        self.InteriorDefense = 0
        self.PerimeterDefense = 0
        self.AdjHeightDiff = 0
        self.AdjShooting = 0
        self.AdjFinishing = 0
        self.AdjBallwork = 0
        self.AdjRebound = 0
        self.AdjDefense = 0
        self.DefRateTO = 0
        self.AdjPerimeterDef = 0
        self.AdjInteriorDef = 0
        self.ReboundDiff = 0
        self.BallDef = 0
        self.TO = 0
        self.OffensiveRebound = 0
        self.StealsAdj = 0
        self.OtherTO = 0
        self.StealsAdjNeg = 0
        self.OtherTOAdjNeg = 0
        self.ThreePtAttGPAdj = 0
        self.TwoPtJumpGPAdj = 0
        self.TwoPtInsideGPAdj = 0
        self.BaseCuttoff = 0
        self.StealCutoff = 0
        self.OtherTOCutoff = 0
        self.ThreePtAttemptCutoff = 0
        self.TwoJumperCutoff = 0
        self.TwoInsideCutoff = 0
        self.Height = 0
        self.HeightDiff = 0
        self.Pace = 0
        self.BaseCutoff = 0
        self.Roster = []
        self.FocusPlayer = 0

    def SetOffensiveBonuses(self, formation, style):
        self.OffensiveFormation = formation
        self.OffensiveStyle = style
        if formation == "Motion":
            self.InsShootingBonus += 1.5
            self.t3ptShootingBonus += 0.5
            self.BallworkBonus -= 1.5
            self.ReboundingBonus -= 0.5
        elif formation == "Pick-and-Roll":
            self.InsShootingBonus += 1.5
            self.BallworkBonus += 1.5
            self.MidShootingBonus -= 0.5
            self.ReboundingBonus -= 0.5
        elif formation == "Post-Up":
            self.InsShootingBonus += 1.5
            self.ReboundingBonus += 1.5
            self.MidShootingBonus -= 0.5
            self.t3ptShootingBonus -= 0.5
        elif formation == "Space-and-Post":
            self.MidShootingBonus += 1.75
            self.t3ptShootingBonus += 0.5
            self.BallworkBonus -= 1.5
            self.ReboundingBonus -= 0.5

    def SetDefensiveBonus(self, formation):
        self.DefensiveFormation = formation
        if formation == "1-3-1 Zone":
            self.TurnoverBonus += 0.5
        elif formation == "2-3 Zone":
            self.ReboundingBonus += 1.5

    def SetDefensiveMaluses(self, formation, t1FocusPlayer, t2FocusPlayer):
        if formation == "Man-to-Man":
            if t2FocusPlayer in t1FocusPlayer:
                self.InsShootingBonus += 1.5
                self.MidShootingBonus += 1.5
                self.t3ptShootingBonus += 1.5
        elif formation == "1-3-1 Zone":
            self.MidShootingBonus -= 1.5
            self.t3ptShootingBonus += 0.5
            self.InsShootingBonus += 0.5
        elif formation == "3-2 Zone":
            self.t3ptShootingBonus -= 1.5
            self.InsShootingBonus += 0.5
            self.ReboundingBonus += 0.5
        elif formation == "2-3 Zone":
            self.InsShootingBonus -= 1.5
            self.t3ptShootingBonus += 0.5
        elif formation == "Box-and-One Zone":
            self.InsShootingBonus += 1.5
            self.MidShootingBonus += 1.5
            self.t3ptShootingBonus += 1.5

    def SetTeamAttributes(self, rosterRaw_df):
        self.Rebounding = round(sum(cp["Rebounding"] for cp in rosterRaw_df))
        self.StealBlock = round(
            sum(cp["InteriorDefense"] + cp["PerimeterDefense"] for cp in rosterRaw_df)
        )
        self.Ballwork = round(sum(cp["Ballwork"] for cp in rosterRaw_df))
        self.InsPro = sum(cp["InsideProportion"] for cp in rosterRaw_df)
        self.MidPro = sum(cp["MidRangeProportion"] for cp in rosterRaw_df)
        self.T3ptPro = sum(cp["ThreePointProportion"] for cp in rosterRaw_df)

    def SetRoster(self, is_nba, rosterRaw_df, matchType):
        for x in rosterRaw_df:
            cp = Player(
                is_nba,
                x,
                self.InsShootingBonus,
                self.MidShootingBonus,
                self.t3ptShootingBonus,
                self.BallworkBonus,
                self.ReboundingBonus,
                matchType,
            )
            self.Roster.append(cp)

    def ReloadRoster(self):
        for x in self.Roster:
            x.get_advanced_stats(
                self.Rebounding,
                self.StealBlock,
                self.Ballwork,
                self.InsPro,
                self.MidPro,
                self.T3ptPro,
                self.TurnoverBonus,
            )

    def SetDefensiveAttributes(self):
        self.Height = round(sum(cp.Height for cp in self.Roster))
        self.InteriorDefense = round(sum(cp.InteriorDefense for cp in self.Roster))
        self.PerimeterDefense = round(sum(cp.PerimeterDefense for cp in self.Roster))

    def SetHeightDiff(self, opposingTeamHeight):
        self.HeightDiff = self.Height - opposingTeamHeight

    def SetAdjustedVariables(self):
        self.AdjHeightDiff = self.HeightDiff * 10
        self.AdjShooting = round(sum(cp.AdjShooting for cp in self.Roster))
        self.AdjFinishing = round(sum(cp.AdjFinishing for cp in self.Roster))
        self.AdjBallwork = round(sum(cp.AdjBallwork for cp in self.Roster))
        self.AdjRebound = round(sum(cp.AdjRebounding for cp in self.Roster))
        self.AdjDefense = round(sum(cp.AdjStealing for cp in self.Roster))
        self.DefRateTO = round(sum(cp.DefRateTO for cp in self.Roster))
        self.AdjPerimeterDef = round(sum(cp.AdjPerimeterDefense for cp in self.Roster))
        self.AdjInteriorDef = round(sum(cp.AdjInteriorDefense for cp in self.Roster))

    def SetDifferences(self, oppAdjReb, oppAdjDef, oppDefRateTO, isHome):
        self.ReboundDiff = round(self.AdjRebound - oppAdjReb + self.AdjHeightDiff)
        self.BallDef = round(self.AdjBallwork - oppAdjDef + self.AdjHeightDiff)
        self.TO = round(self.AdjBallwork - oppDefRateTO + self.AdjHeightDiff)
        self.OffensiveRebound = round((0.00003 * self.ReboundDiff) + 0.28, 6)
        self.StealsAdj = round(-0.000008 * self.TO, 6)
        self.OtherTO = round(-0.000005 * self.TO, 6)
        if isHome == True:
            self.StealsAdjNeg = self.StealsAdj / (-3)
            self.OtherTOAdjNeg = self.OtherTO / (-3)
        else:
            self.StealsAdjNeg = round(self.StealsAdj / -3, 12)
            self.OtherTOAdjNeg = round(self.OtherTO / -3, 12)
        self.ThreePtAttGPAdj = round(
            (0.81 * (self.T3ptPro / 100)) - threeptAttemptProbability, 5
        )
        self.TwoPtJumpGPAdj = round(
            (0.81 * (self.MidPro / 100)) - twoptJumperProbability, 6
        )
        self.TwoPtInsideGPAdj = round(
            (0.81 * (self.InsPro / 100)) - twoptInsideProbability, 6
        )

    def SetCutoffs(self, HCA, HCAAdj, isHome):
        self.StealCutoff = stealProbability + self.StealsAdj + self.BaseCutoff
        self.OtherTOCutoff = otherTurnoverProbability + self.OtherTO + self.StealCutoff
        self.ThreePtAttemptCutoff = round(
            threeptAttemptProbability
            + self.StealsAdjNeg
            + self.OtherTOAdjNeg
            + self.ThreePtAttGPAdj
            + self.OtherTOCutoff,
            5,
        )
        self.TwoJumperCutoff = round(
            twoptJumperProbability
            + self.StealsAdjNeg
            + self.OtherTOAdjNeg
            + self.TwoPtJumpGPAdj
            + self.ThreePtAttemptCutoff,
            5,
        )
        self.TwoInsideCutoff = round(
            twoptInsideProbability
            + self.StealsAdjNeg
            + self.OtherTOAdjNeg
            + self.TwoPtInsideGPAdj
            + self.TwoJumperCutoff
        )
        if isHome == True:
            self.OtherTOCutoff = self.OtherTOCutoff + HCA
            self.ThreePtAttemptCutoff = self.ThreePtAttemptCutoff + HCAAdj
            self.TwoJumperCutoff = self.TwoJumperCutoff + HCAAdj
            self.TwoInsideCutoff = self.TwoInsideCutoff + HCAAdj

    def SetPace(self, pace, isNBA):
        if pace == "Very Fast":
            if isNBA == True:
                self.Pace = random.randint(105, 110)
            else:
                self.Pace = random.randint(75, 80)
        elif pace == "Fast":
            if isNBA:
                self.Pace = random.randint(100, 105)
            else:
                self.Pace = random.randint(70, 75)
        elif pace == "Balanced":
            if isNBA:
                self.Pace = random.randint(95, 100)
            else:
                self.Pace = random.randint(65, 70)
        elif pace == "Slow":
            if isNBA:
                self.Pace = random.randint(90, 95)
            else:
                self.Pace = random.randint(60, 65)
        elif pace == "Very Slow":
            if isNBA:
                self.Pace = random.randint(85, 90)
            else:
                self.Pace = random.randint(55, 60)
