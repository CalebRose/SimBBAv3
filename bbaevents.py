import random


def GetTipoffPossession(
    t1TipChance,
    collector,
    t1Tip,
    t2Tip,
    Home,
    Away,
    Home_Label,
    Away_Label,
    total_possessions,
):
    tipOff = random.random()
    if tipOff < t1TipChance:
        collector.AppendPlay(
            Away,
            t2Tip.FirstName + " wins the tipoff for " + Away_Label + "!",
            "Tipoff",
            0,
            0,
            0,
            total_possessions,
        )
        return Away
    collector.AppendPlay(
        Home,
        t1Tip.FirstName + " wins the tipoff for " + Home_Label + "!",
        "Tipoff",
        0,
        0,
        0,
        total_possessions,
    )
    return Home


def StealEvent(gamestate, roster, team1, team2, t, label, collector):
    pickPlayer = random.choices(roster, weights=[x.DefensePer for x in roster], k=1)
    stealPlayer = pickPlayer[0]
    stealPlayer.Stats.AddPossession()
    stealPlayer.Stats.AddSteal()
    team1.Stats.AddTurnover()
    team2.Stats.AddSteal()
    printShooter = stealPlayer.FirstName + " " + stealPlayer.LastName
    msg = printShooter + " steals the ball for " + label + "!"
    gamestate.SetPossessingTeam(t)
    collector.AppendPlay(
        t,
        msg,
        "Turnover",
        gamestate.T1Points,
        gamestate.T2Points,
        gamestate.PossessionNumber,
        gamestate.Total_Possessions,
    )


def OtherTurnoverEvent(
    gamestate, roster, team, receiving_team, receiving_label, collector
):
    otherTO = random.random()
    pickPlayer = random.choices(roster, weights=[x.Usage for x in roster], k=1)
    toPlayer = pickPlayer[0]
    toPlayer.Stats.AddPossession()
    toPlayer.Stats.AddTurnover()
    printShooter = (
        toPlayer.Position + " " + toPlayer.FirstName + " " + toPlayer.LastName
    )
    team.Stats.AddTurnover()
    if otherTO < 0.582:
        msg = (
            gamestate.PossessingTeam
            + " "
            + printShooter
            + " lost the ball out of bounds. "
            + receiving_label
            + " now has the possession."
        )
        collector.AppendPlay(
            receiving_team,
            msg,
            "Out of Bounds",
            gamestate.T1Points,
            gamestate.T2Points,
            gamestate.PossessionNumber,
            gamestate.Total_Possessions,
        )
    elif otherTO < 0.64:
        msg = (
            receiving_team
            + ": Shot clock violation on "
            + gamestate.PossessingTeam
            + " "
            + printShooter
            + "."
        )
        collector.AppendPlay(
            receiving_team,
            msg,
            "Shot Clock Violation",
            gamestate.T1Points,
            gamestate.T2Points,
            gamestate.PossessionNumber,
            gamestate.Total_Possessions,
        )
    elif otherTO < 1:
        msg = (
            receiving_team
            + ": Offensive foul on "
            + gamestate.PossessingTeam
            + " "
            + printShooter
            + "."
        )
        collector.AppendPlay(
            receiving_team,
            msg,
            "Foul",
            gamestate.T1Points,
            gamestate.T2Points,
            gamestate.PossessionNumber,
            gamestate.Total_Possessions,
        )
        toPlayer.Stats.AddFoul()
    gamestate.SetPossessingTeam(receiving_team)


def ReboundTheBall(
    gamestate,
    team_state,
    team,
    receiving_team,
    receiving_label,
    is_offense,
    play,
    collector,
):
    pickRebounder = random.choices(
        team_state.Roster,
        weights=[x.ReboundingPer for x in team_state.Roster],
        k=1,
    )
    rebounder = pickRebounder[0]
    rebounder.Stats.AddRebound(is_offense)
    team.Stats.AddRebound(is_offense)
    printRebounder = (
        rebounder.Position + " " + rebounder.FirstName + " " + rebounder.LastName
    )
    message = play + " Rebounded by " + receiving_label + " " + printRebounder + "."
    collector.AppendPlay(
        gamestate.PossessingTeam,
        message,
        "Missed",
        gamestate.T1Points,
        gamestate.T2Points,
        gamestate.PossessionNumber,
        gamestate.Total_Possessions,
    )
    gamestate.SetPossessingTeam(receiving_team)


def SelectAssister(shooter, team_state):
    assistList = [x for x in team_state.Roster if x.ID != shooter.ID]
    pickPlayer = random.choices(
        assistList, weights=[x.AssistPer for x in assistList], k=1
    )
    return pickPlayer[0]


def ConductFoulShots(
    gamestate,
    foulShots,
    shooter,
    t1State,
    t2State,
    team_one,
    team_two,
    isHome,
    home_label,
    receiving_team,
    receiving_label,
    collector,
):
    shots = foulShots
    ftCutoff = (0.02 * shooter.FreeThrow) + 0.5
    while shots > 0:
        if random.random() <= ftCutoff:
            msg = "Free throw coming up... good!"
            gamestate.AddPoints(1, isHome)
            team_one.Stats.AddPoints(
                1,
                gamestate.PossessionNumber,
                gamestate.Halftime_Point,
                gamestate.IsOT,
                gamestate.IsNBA,
                gamestate.Quarter,
            )
            team_one.Stats.CalculateLead(1, gamestate.T1Points - gamestate.T2Points)
            shooter.Stats.AddFTMade()
            team_one.Stats.AddFreeThrow(True)
            shots -= 1
            collector.AppendPlay(
                gamestate.PossessingTeam,
                msg,
                "FreeThrow",
                gamestate.T1Points,
                gamestate.T2Points,
                gamestate.PossessionNumber,
                gamestate.Total_Possessions,
            )
            if shots == 0:
                gamestate.SetPossessingTeam(receiving_team)
        else:
            play = "Free throw coming up... rattled out."
            shooter.Stats.AddFTAttempt()
            team_one.Stats.AddFreeThrow(False)
            shots -= 1
            if shots == 0:
                rebrand = random.random()
                if rebrand < t1State.OffensiveRebound:
                    ReboundTheBall(
                        gamestate,
                        t1State,
                        team_one,
                        gamestate.PossessingTeam,
                        home_label,
                        True,
                        play,
                        collector,
                    )
                else:
                    ReboundTheBall(
                        gamestate,
                        t2State,
                        team_two,
                        receiving_team,
                        receiving_label,
                        False,
                        play,
                        collector,
                    )
            else:
                collector.AppendPlay(
                    gamestate.PossessingTeam,
                    play,
                    "FreeThrow",
                    gamestate.T1Points,
                    gamestate.T2Points,
                    gamestate.PossessionNumber,
                    gamestate.Total_Possessions,
                )


def ThreePointAttemptEvent(
    gamestate,
    t1State,
    t2State,
    team1,
    team2,
    h_label,
    receiving_team,
    receiving_label,
    focus_player,
    isHome,
    collector,
):
    pickPlayer = random.choices(
        t1State.Roster,
        weights=[x.ThreePointUsage for x in t1State.Roster],
        k=1,
    )
    shooter = pickPlayer[0]
    shooter.Stats.AddPossession()
    blockAdj = (0.00001 * t2State.AdjPerimeterDef) - 0.0153
    made3nf = 0
    if shooter.FirstName + " " + shooter.LastName == focus_player:
        made3nf = (0.015 * shooter.Shooting3) - 4 + 0.185
    else:
        made3nf = (0.015 * shooter.Shooting3) + 0.185
    if gamestate.IsNeutral != True and isHome == True:
        made3nf += gamestate.HCA
    madeDiff = made3nf - 0.335
    missed3nf = 0.635 - madeDiff - blockAdj
    made3foul = 0.005
    missed3foul = 0.015
    blocked = 0.01 + blockAdj
    base3Cutoff = 0
    made3Cutoff = base3Cutoff + made3nf
    missed3Cutoff = made3Cutoff + missed3nf
    blocked3Cutoff = missed3Cutoff + blocked
    missed3foulCutoff = blocked3Cutoff + missed3foul
    made3foulCutoff = missed3foulCutoff + made3foul
    eventOutcome = random.random()

    if eventOutcome < made3Cutoff:
        Made3Outcome(
            gamestate,
            shooter,
            t1State,
            team1,
            receiving_team,
            isHome,
            collector,
        )
    elif eventOutcome < missed3Cutoff:
        Missed3Outcome(
            gamestate,
            shooter,
            t1State,
            t2State,
            team1,
            team2,
            h_label,
            receiving_team,
            receiving_label,
            collector,
        )
    elif eventOutcome < blocked3Cutoff:
        Blocked3Outcome(
            gamestate,
            shooter,
            t1State,
            t2State,
            team1,
            team2,
            h_label,
            receiving_team,
            receiving_label,
            collector,
        )
    elif eventOutcome < missed3foulCutoff:
        Missed3FoulOutcome(
            gamestate,
            shooter,
            t1State,
            t2State,
            team1,
            team2,
            h_label,
            receiving_team,
            receiving_label,
            isHome,
            collector,
        )
    elif eventOutcome < made3foulCutoff:
        Made3FoulOutcome(
            gamestate,
            shooter,
            t1State,
            t2State,
            team1,
            team2,
            h_label,
            receiving_team,
            receiving_label,
            isHome,
            collector,
        )


def Made3Outcome(
    gamestate, shooter, team_state, team, receiving_team, isHome, collector
):
    printShooter = shooter.Position + " " + shooter.FirstName + " " + shooter.LastName
    play = printShooter + " 3-point attempt... Score!"
    gamestate.AddPoints(3, isHome)
    shooter.Stats.AddFieldGoal(True, 3)
    team.Stats.AddPoints(
        3,
        gamestate.PossessionNumber,
        gamestate.Halftime_Point,
        gamestate.IsOT,
        gamestate.IsNBA,
        gamestate.Quarter,
    )
    team.Stats.CalculateLead(3, gamestate.T1Points - gamestate.T2Points)
    team.Stats.AddThreePointShot(True)
    team.Stats.AddFieldGoal(True)
    assistRand = random.random()
    if assistRand > 0.173:
        assister = SelectAssister(shooter, team_state)
        if assister.ID != shooter.ID:
            assister.Stats.AddAssist()
            team.Stats.AddAssist()
            printAssister = (
                assister.Position + " " + assister.FirstName + " " + assister.LastName
            )
            play += " Assisted by: " + printAssister
    collector.AppendPlay(
        gamestate.PossessingTeam,
        play,
        "Score",
        gamestate.T1Points,
        gamestate.T2Points,
        gamestate.PossessionNumber,
        gamestate.Total_Possessions,
    )
    gamestate.SetPossessingTeam(receiving_team)


def Missed3Outcome(
    gamestate,
    shooter,
    t1State,
    t2State,
    team_one,
    team_two,
    h_label,
    receiving_team,
    receiving_label,
    collector,
):
    printShooter = shooter.Position + " " + shooter.FirstName + " " + shooter.LastName
    play = printShooter + " 3-point attempt...Missed!"
    shooter.Stats.AddFieldGoal(False, 3)
    team_one.Stats.AddThreePointShot(False)
    team_one.Stats.AddFieldGoal(False)
    rebrand = random.random()
    if rebrand < t1State.OffensiveRebound:
        ReboundTheBall(
            gamestate,
            t1State,
            team_one,
            gamestate.PossessingTeam,
            h_label,
            True,
            play,
            collector,
        )
    else:
        ReboundTheBall(
            gamestate,
            t2State,
            team_two,
            receiving_team,
            receiving_label,
            False,
            play,
            collector,
        )


def Blocked3Outcome(
    gamestate,
    shooter,
    t1State,
    t2State,
    team_one,
    team_two,
    h_label,
    receiving_team,
    receiving_label,
    collector,
):
    printShooter = shooter.Position + " " + shooter.FirstName + " " + shooter.LastName
    pickBlocker = random.choices(
        t2State.Roster,
        weights=[x.DefensePer for x in t2State.Roster],
        k=1,
    )
    blocker = pickBlocker[0]
    shooter.Stats.AddFieldGoal(False, 3)
    team_one.Stats.AddThreePointShot(False)
    blocker.Stats.AddBlock()
    team_two.Stats.AddBlocks()
    printBlocker = blocker.Position + " " + blocker.FirstName + " " + blocker.LastName
    play = (
        printShooter
        + " 3-point attempt...BLOCKED by "
        + receiving_team
        + " "
        + printBlocker
        + "."
    )
    rebrand = random.random()
    if rebrand < 0.43:
        ReboundTheBall(
            gamestate,
            t1State,
            team_one,
            gamestate.PossessingTeam,
            h_label,
            True,
            play,
            collector,
        )
    else:
        ReboundTheBall(
            gamestate,
            t2State,
            team_two,
            receiving_team,
            receiving_label,
            False,
            play,
            collector,
        )


def Missed3FoulOutcome(
    gamestate,
    shooter,
    t1State,
    t2State,
    team_one,
    team_two,
    h_label,
    receiving_team,
    receiving_label,
    isHome,
    collector,
):
    printShooter = shooter.Position + " " + shooter.FirstName + " " + shooter.LastName
    collector.AppendPlay(
        gamestate.PossessingTeam,
        printShooter + " 3-point attempt... Missed. There is a foul on the play.",
        "Foul",
        gamestate.T1Points,
        gamestate.T2Points,
        gamestate.PossessionNumber,
        gamestate.Total_Possessions,
    )
    shooter.Stats.AddFieldGoal(False, 3)
    team_one.Stats.AddThreePointShot(False)
    team_one.Stats.AddFieldGoal(False)
    team_two.Stats.AddFoul()
    ConductFoulShots(
        gamestate,
        3,
        shooter,
        t1State,
        t2State,
        team_one,
        team_two,
        isHome,
        h_label,
        receiving_team,
        receiving_label,
        collector,
    )


def Made3FoulOutcome(
    gamestate,
    shooter,
    t1State,
    t2State,
    team_one,
    team_two,
    h_label,
    receiving_team,
    receiving_label,
    isHome,
    collector,
):
    printShooter = shooter.Position + " " + shooter.FirstName + " " + shooter.LastName
    play = printShooter + " 3-point attempt...Score! Fouled on the play... and one!"
    gamestate.AddPoints(3, isHome)
    shooter.Stats.AddFieldGoal(True, 3)
    team_one.Stats.AddThreePointShot(True)
    team_one.Stats.AddPoints(
        3,
        gamestate.PossessionNumber,
        gamestate.Halftime_Point,
        gamestate.IsOT,
        gamestate.IsNBA,
        gamestate.Quarter,
    )
    team_one.Stats.CalculateLead(3, gamestate.T1Points - gamestate.T2Points)
    team_one.Stats.AddFieldGoal(True)
    assistRand = random.random()
    if assistRand > 0.173:
        assister = SelectAssister(shooter, t1State)
        if assister.ID != shooter.ID:
            assister.Stats.AddAssist()
            team_one.Stats.AddAssist()
            printAssister = (
                assister.Position + " " + assister.FirstName + " " + assister.LastName
            )
            play += " Assisted by: " + printAssister
    collector.AppendPlay(
        gamestate.PossessingTeam,
        play,
        "Score",
        gamestate.T1Points,
        gamestate.T2Points,
        gamestate.PossessionNumber,
        gamestate.Total_Possessions,
    )
    ConductFoulShots(
        gamestate,
        1,
        shooter,
        t1State,
        t2State,
        team_one,
        team_two,
        isHome,
        h_label,
        receiving_team,
        receiving_label,
        collector,
    )


def JumperAttemptEvent(
    gamestate,
    t1State,
    t2State,
    team1,
    team2,
    h_label,
    receiving_team,
    receiving_label,
    focus_player,
    isHome,
    collector,
):
    pickPlayer = random.choices(
        t1State.Roster,
        weights=[x.MidUsage for x in t1State.Roster],
        k=1,
    )
    shooter = pickPlayer[0]
    shooter.Stats.AddPossession()
    blockAdj = (0.00001 * t2State.AdjInteriorDef) - 0.0153
    made2jnf = 0
    if shooter.FirstName + " " + shooter.LastName == focus_player:
        made2jnf = (0.006 * shooter.Shooting2) - 4 + 0.185 + gamestate.HCA
    else:
        made2jnf = (0.006 * shooter.Shooting2) + 0.185 + gamestate.HCA
    if gamestate.IsNeutral != True and isHome == True:
        made2jnf += gamestate.HCA
    madeDiff = made2jnf - 0.335
    missed2jnf = 0.53 - madeDiff - blockAdj
    made2jfoul = 0.01
    missed2jfoul = 0.02
    blocked = 0.07 + blockAdj
    base2jCutoff = 0
    made2jCutoff = base2jCutoff + made2jnf
    missed2jCutoff = made2jCutoff + missed2jnf
    blocked2jCutoff = missed2jCutoff + blocked
    missed2jfoulCutoff = blocked2jCutoff + missed2jfoul
    made2jfoulCutoff = missed2jfoulCutoff + made2jfoul
    eventOutcome = random.random()

    if eventOutcome < made2jCutoff:
        MadeJumperOutcome(
            gamestate, shooter, t1State, team1, receiving_team, isHome, collector
        )
    elif eventOutcome < missed2jCutoff:
        MissedJumperOutcome(
            gamestate,
            shooter,
            t1State,
            t2State,
            team1,
            team2,
            h_label,
            receiving_team,
            receiving_label,
            collector,
        )
    elif eventOutcome < blocked2jCutoff:
        BlockedJumperOutcome(
            gamestate,
            shooter,
            t1State,
            t2State,
            team1,
            team2,
            h_label,
            receiving_team,
            receiving_label,
            collector,
        )
    elif eventOutcome < missed2jfoulCutoff:
        MissedJumperFoulOutcome(
            gamestate,
            shooter,
            t1State,
            t2State,
            team1,
            team2,
            h_label,
            receiving_team,
            receiving_label,
            isHome,
            collector,
        )
    elif eventOutcome < made2jfoulCutoff:
        MadeJumperFoulOutcome(
            gamestate,
            shooter,
            t1State,
            t2State,
            team1,
            team2,
            h_label,
            receiving_team,
            receiving_label,
            isHome,
            collector,
        )


def MadeJumperOutcome(
    gamestate, shooter, team_state, team, receiving_team, isHome, collector
):
    printShooter = shooter.Position + " " + shooter.FirstName + " " + shooter.LastName
    play = printShooter + " 2-point jumper... Score!"
    gamestate.AddPoints(2, isHome)
    shooter.Stats.AddFieldGoal(True, 2)
    team.Stats.AddPoints(
        2,
        gamestate.PossessionNumber,
        gamestate.Halftime_Point,
        gamestate.IsOT,
        gamestate.IsNBA,
        gamestate.Quarter,
    )
    team.Stats.CalculateLead(2, gamestate.T1Points - gamestate.T2Points)
    team.Stats.AddFieldGoal(True)
    assistRand = random.random()
    if assistRand > 0.678:
        assister = SelectAssister(shooter, team_state)
        if assister.ID != shooter.ID:
            assister.Stats.AddAssist()
            team.Stats.AddAssist()
            printAssister = (
                assister.Position + " " + assister.FirstName + " " + assister.LastName
            )
            play += " Assisted by: " + printAssister
    collector.AppendPlay(
        gamestate.PossessingTeam,
        play,
        "Score",
        gamestate.T1Points,
        gamestate.T2Points,
        gamestate.PossessionNumber,
        gamestate.Total_Possessions,
    )
    gamestate.SetPossessingTeam(receiving_team)


def MissedJumperOutcome(
    gamestate,
    shooter,
    t1State,
    t2State,
    team_one,
    team_two,
    h_label,
    receiving_team,
    receiving_label,
    collector,
):
    printShooter = shooter.Position + " " + shooter.FirstName + " " + shooter.LastName
    play = printShooter + " 2-point jumper...Missed!"
    shooter.Stats.AddFieldGoal(False, 2)
    team_one.Stats.AddFieldGoal(False)
    rebrand = random.random()
    if rebrand < t1State.OffensiveRebound:
        ReboundTheBall(
            gamestate,
            t1State,
            team_one,
            gamestate.PossessingTeam,
            h_label,
            True,
            play,
            collector,
        )
    else:
        ReboundTheBall(
            gamestate,
            t2State,
            team_two,
            receiving_team,
            receiving_label,
            False,
            play,
            collector,
        )


def BlockedJumperOutcome(
    gamestate,
    shooter,
    t1State,
    t2State,
    team_one,
    team_two,
    h_label,
    receiving_team,
    receiving_label,
    collector,
):
    printShooter = shooter.Position + " " + shooter.FirstName + " " + shooter.LastName
    pickBlocker = random.choices(
        t2State.Roster,
        weights=[x.DefensePer for x in t2State.Roster],
        k=1,
    )
    blocker = pickBlocker[0]
    shooter.Stats.AddFieldGoal(False, 2)
    team_one.Stats.AddFieldGoal(False)
    blocker.Stats.AddBlock()
    team_two.Stats.AddBlocks()
    printBlocker = blocker.Position + " " + blocker.FirstName + " " + blocker.LastName
    play = (
        printShooter
        + " 2-point jumper...BLOCKED by "
        + receiving_team
        + " "
        + printBlocker
        + "."
    )
    rebrand = random.random()
    if rebrand < 0.43:
        ReboundTheBall(
            gamestate,
            t1State,
            team_one,
            gamestate.PossessingTeam,
            h_label,
            True,
            play,
            collector,
        )
    else:
        ReboundTheBall(
            gamestate,
            t2State,
            team_two,
            receiving_team,
            receiving_label,
            False,
            play,
            collector,
        )


def MissedJumperFoulOutcome(
    gamestate,
    shooter,
    t1State,
    t2State,
    team_one,
    team_two,
    h_label,
    receiving_team,
    receiving_label,
    isHome,
    collector,
):
    printShooter = shooter.Position + " " + shooter.FirstName + " " + shooter.LastName
    collector.AppendPlay(
        gamestate.PossessingTeam,
        printShooter + " 2-point jumper... Missed with a foul on the play.",
        "Foul",
        gamestate.T1Points,
        gamestate.T2Points,
        gamestate.PossessionNumber,
        gamestate.Total_Possessions,
    )
    shooter.Stats.AddFieldGoal(False, 2)
    team_one.Stats.AddFieldGoal(False)
    team_two.Stats.AddFoul()
    ConductFoulShots(
        gamestate,
        2,
        shooter,
        t1State,
        t2State,
        team_one,
        team_two,
        isHome,
        h_label,
        receiving_team,
        receiving_label,
        collector,
    )


def MadeJumperFoulOutcome(
    gamestate,
    shooter,
    t1State,
    t2State,
    team_one,
    team_two,
    h_label,
    receiving_team,
    receiving_label,
    isHome,
    collector,
):
    printShooter = shooter.Position + " " + shooter.FirstName + " " + shooter.LastName
    play = printShooter + " 2-point jumper...Score! Foul on the play and one!"
    gamestate.AddPoints(2, isHome)
    shooter.Stats.AddFieldGoal(True, 2)
    team_one.Stats.AddFieldGoal(True)
    team_one.Stats.AddPoints(
        2,
        gamestate.PossessionNumber,
        gamestate.Halftime_Point,
        gamestate.IsOT,
        gamestate.IsNBA,
        gamestate.Quarter,
    )
    team_one.Stats.CalculateLead(2, gamestate.T1Points - gamestate.T2Points)
    assistRand = random.random()
    if assistRand > 0.678:
        assister = SelectAssister(shooter, t1State)
        if assister.ID != shooter.ID:
            assister.Stats.AddAssist()
            team_one.Stats.AddAssist()
            printAssister = (
                assister.Position + " " + assister.FirstName + " " + assister.LastName
            )
            play += " Assisted by: " + printAssister
    collector.AppendPlay(
        gamestate.PossessingTeam,
        play,
        "Score",
        gamestate.T1Points,
        gamestate.T2Points,
        gamestate.PossessionNumber,
        gamestate.Total_Possessions,
    )
    ConductFoulShots(
        gamestate,
        1,
        shooter,
        t1State,
        t2State,
        team_one,
        team_two,
        isHome,
        h_label,
        receiving_team,
        receiving_label,
        collector,
    )


def InsideAttemptEvent(
    gamestate,
    t1State,
    t2State,
    team1,
    team2,
    h_label,
    receiving_team,
    receiving_label,
    focus_player,
    isHome,
    collector,
):
    pickPlayer = random.choices(
        t1State.Roster,
        weights=[x.InsideUsage for x in t1State.Roster],
        k=1,
    )
    shooter = pickPlayer[0]
    shooter.Stats.AddPossession()
    blockAdj = (0.00001 * t2State.AdjInteriorDef) - 0.0153
    made2inf = 0
    if shooter.FirstName + " " + shooter.LastName == focus_player:
        made2inf = (0.005 * shooter.Finishing) - 4 + 0.185 + gamestate.HCA
    else:
        made2inf = (0.005 * shooter.Finishing) + 0.185 + gamestate.HCA
    if gamestate.IsNeutral != True and isHome == True:
        made2inf += gamestate.HCA
    madeDiff = made2inf - 0.563
    missed2inf = 0.147 - madeDiff - blockAdj
    made2infoul = 0.05
    missed2infoul = 0.14
    blocked = 0.1 + blockAdj
    base2inCutoff = 0
    made2inCutoff = base2inCutoff + made2inf
    missed2inCutoff = made2inCutoff + missed2inf
    blocked2inCutoff = missed2inCutoff + blocked
    missed2infoulCutoff = blocked2inCutoff + missed2infoul
    made2infoulCutoff = missed2infoulCutoff + made2infoul
    eventOutcome = random.random()

    if eventOutcome < made2inCutoff:
        MadeInsideOutcome(
            gamestate, shooter, t1State, team1, receiving_team, isHome, collector
        )
    elif eventOutcome < missed2inCutoff:
        MissedInsideOutcome(
            gamestate,
            shooter,
            t1State,
            t2State,
            team1,
            team2,
            h_label,
            receiving_team,
            receiving_label,
            collector,
        )
    elif eventOutcome < blocked2inCutoff:
        BlockedInsideOutcome(
            gamestate,
            shooter,
            t1State,
            t2State,
            team1,
            team2,
            h_label,
            receiving_team,
            receiving_label,
            collector,
        )
    elif eventOutcome < missed2infoulCutoff:
        MissedInsideFoulOutcome(
            gamestate,
            shooter,
            t1State,
            t2State,
            team1,
            team2,
            h_label,
            receiving_team,
            receiving_label,
            isHome,
            collector,
        )
    elif eventOutcome < made2infoulCutoff:
        MadeInsideFoulOutcome(
            gamestate,
            shooter,
            t1State,
            t2State,
            team1,
            team2,
            h_label,
            receiving_team,
            receiving_label,
            isHome,
            collector,
        )


def MadeInsideOutcome(
    gamestate, shooter, team_state, team, receiving_team, isHome, collector
):
    printShooter = shooter.Position + " " + shooter.FirstName + " " + shooter.LastName
    play = printShooter + " Inside shot... Score!"
    gamestate.AddPoints(2, isHome)
    shooter.Stats.AddFieldGoal(True, 2)
    team.Stats.AddPoints(
        2,
        gamestate.PossessionNumber,
        gamestate.Halftime_Point,
        gamestate.IsOT,
        gamestate.IsNBA,
        gamestate.Quarter,
    )
    team.Stats.CalculateLead(2, gamestate.T1Points - gamestate.T2Points)
    team.Stats.AddFieldGoal(True)
    assistRand = random.random()
    if assistRand > 0.57:
        assister = SelectAssister(shooter, team_state)
        if assister.ID != shooter.ID:
            assister.Stats.AddAssist()
            team.Stats.AddAssist()
            printAssister = (
                assister.Position + " " + assister.FirstName + " " + assister.LastName
            )
            play += " Assisted by: " + printAssister
    collector.AppendPlay(
        gamestate.PossessingTeam,
        play,
        "Score",
        gamestate.T1Points,
        gamestate.T2Points,
        gamestate.PossessionNumber,
        gamestate.Total_Possessions,
    )
    gamestate.SetPossessingTeam(receiving_team)


def MissedInsideOutcome(
    gamestate,
    shooter,
    t1State,
    t2State,
    team_one,
    team_two,
    h_label,
    receiving_team,
    receiving_label,
    collector,
):
    printShooter = shooter.Position + " " + shooter.FirstName + " " + shooter.LastName
    play = printShooter + " 2-point jumper...Missed!"
    shooter.Stats.AddFieldGoal(False, 2)
    team_one.Stats.AddFieldGoal(False)
    rebrand = random.random()
    if rebrand < t1State.OffensiveRebound:
        ReboundTheBall(
            gamestate,
            t1State,
            team_one,
            gamestate.PossessingTeam,
            h_label,
            True,
            play,
            collector,
        )
    else:
        ReboundTheBall(
            gamestate,
            t2State,
            team_two,
            receiving_team,
            receiving_label,
            False,
            play,
            collector,
        )


def BlockedInsideOutcome(
    gamestate,
    shooter,
    t1State,
    t2State,
    team_one,
    team_two,
    h_label,
    receiving_team,
    receiving_label,
    collector,
):
    printShooter = shooter.Position + " " + shooter.FirstName + " " + shooter.LastName
    pickBlocker = random.choices(
        t2State.Roster,
        weights=[x.DefensePer for x in t2State.Roster],
        k=1,
    )
    blocker = pickBlocker[0]
    shooter.Stats.AddFieldGoal(False, 2)
    team_one.Stats.AddFieldGoal(False)
    blocker.Stats.AddBlock()
    team_two.Stats.AddBlocks()
    printBlocker = blocker.Position + " " + blocker.FirstName + " " + blocker.LastName
    play = (
        printShooter
        + " Inside shot... BLOCKED by "
        + receiving_team
        + " "
        + printBlocker
        + "."
    )
    rebrand = random.random()
    if rebrand < 0.43:
        ReboundTheBall(
            gamestate,
            t1State,
            team_one,
            gamestate.PossessingTeam,
            h_label,
            True,
            play,
            collector,
        )
    else:
        ReboundTheBall(
            gamestate,
            t2State,
            team_two,
            receiving_team,
            receiving_label,
            False,
            play,
            collector,
        )


def MissedInsideFoulOutcome(
    gamestate,
    shooter,
    t1State,
    t2State,
    team_one,
    team_two,
    h_label,
    receiving_team,
    receiving_label,
    isHome,
    collector,
):
    printShooter = shooter.Position + " " + shooter.FirstName + " " + shooter.LastName
    collector.AppendPlay(
        gamestate.PossessingTeam,
        printShooter + " Inside shot... Missed with a foul on the play.",
        "Foul",
        gamestate.T1Points,
        gamestate.T2Points,
        gamestate.PossessionNumber,
        gamestate.Total_Possessions,
    )
    shooter.Stats.AddFieldGoal(False, 2)
    team_one.Stats.AddFieldGoal(False)
    team_two.Stats.AddFoul()
    ConductFoulShots(
        gamestate,
        2,
        shooter,
        t1State,
        t2State,
        team_one,
        team_two,
        isHome,
        h_label,
        receiving_team,
        receiving_label,
        collector,
    )


def MadeInsideFoulOutcome(
    gamestate,
    shooter,
    t1State,
    t2State,
    team_one,
    team_two,
    h_label,
    receiving_team,
    receiving_label,
    isHome,
    collector,
):
    printShooter = shooter.Position + " " + shooter.FirstName + " " + shooter.LastName
    play = printShooter + " Inside shot...Score! Foul on the play and one!"
    gamestate.AddPoints(2, isHome)
    shooter.Stats.AddFieldGoal(True, 2)
    team_one.Stats.AddFieldGoal(True)
    team_one.Stats.AddPoints(
        2,
        gamestate.PossessionNumber,
        gamestate.Halftime_Point,
        gamestate.IsOT,
        gamestate.IsNBA,
        gamestate.Quarter,
    )
    team_one.Stats.CalculateLead(2, gamestate.T1Points - gamestate.T2Points)
    assistRand = random.random()
    if assistRand > 0.57:
        assister = SelectAssister(shooter, t1State)
        if assister.ID != shooter.ID:
            assister.Stats.AddAssist()
            team_one.Stats.AddAssist()
            printAssister = (
                assister.Position + " " + assister.FirstName + " " + assister.LastName
            )
            play += " Assisted by: " + printAssister
    collector.AppendPlay(
        gamestate.PossessingTeam,
        play,
        "Score",
        gamestate.T1Points,
        gamestate.T2Points,
        gamestate.PossessionNumber,
        gamestate.Total_Possessions,
    )
    ConductFoulShots(
        gamestate,
        1,
        shooter,
        t1State,
        t2State,
        team_one,
        team_two,
        isHome,
        h_label,
        receiving_team,
        receiving_label,
        collector,
    )
