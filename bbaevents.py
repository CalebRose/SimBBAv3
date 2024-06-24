import random
from constants import *
import util


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


def GetShooter(roster, shot_type):
    filtered_roster = [player for player in roster if player.Usage > 0]
    weight = []
    if shot_type == 1:
        weight = [x.ThreePointUsage for x in filtered_roster]
    elif shot_type == 2:
        weight = [x.MidUsage for x in filtered_roster]
    else:
        weight = [x.InsideUsage for x in filtered_roster]
    pickPlayer = random.choices(
        filtered_roster,
        weights=weight,
        k=1,
    )
    return pickPlayer[0]


def GetRebounder(roster):
    filtered_roster = [player for player in roster if player.Usage > 0]
    weight = [
        player.AdjRebounding * POSITION_WEIGHTS.get(player.Position, 1.0)
        for player in filtered_roster
    ]
    pickPlayer = random.choices(
        filtered_roster,
        weights=weight,
        k=1,
    )
    return pickPlayer[0]


def GetReboundProbability(offReb, defReb):
    height_diff = offReb.Height - defReb.Height
    adj_height_diff = height_diff * adj_height_magic_num
    off_rebound_adj = offReb.AdjRebounding + adj_height_diff
    probability = (
        off_rebound_adj / (off_rebound_adj + defReb.AdjRebounding)
    ) * adj_rebound_magic_num
    return probability


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
    gamestate, tState, team, receiving_team, receiving_label, collector
):
    otherTO = random.random()
    pickPlayer = random.choices(
        tState.Roster, weights=[x.Usage for x in tState.Roster], k=1
    )
    toPlayer = pickPlayer[0]
    toPlayer.Stats.AddPossession()
    toPlayer.Stats.AddTurnover()
    printShooter = (
        toPlayer.Position + " " + toPlayer.FirstName + " " + toPlayer.LastName
    )
    team.Stats.AddTurnover()
    if otherTO < outOfBoundsCutoff:
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
    elif otherTO < shotClockViolationCutoff:
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
    elif otherTO < offensiveFoulCutoff:
        msg = f"{receiving_team}: Offensive foul on {gamestate.PossessingTeam} {printShooter}."
        toPlayer.AddFoul(gamestate.IsNBA)
        if toPlayer.FouledOut == True:
            tState.ReloadRoster()
            msg += f"It looks like {toPlayer.LastName} has accumulated the maximum limit on fouls and cannot play for the remainder of the game."
        collector.AppendPlay(
            receiving_team,
            msg,
            "Foul",
            gamestate.T1Points,
            gamestate.T2Points,
            gamestate.PossessionNumber,
            gamestate.Total_Possessions,
        )
    gamestate.SetPossessingTeam(receiving_team)


def ReboundTheBall(
    gamestate,
    rebounder,
    team,
    receiving_team,
    receiving_label,
    is_offense,
    play,
    collector,
):
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
    if is_offense:
        gamestate.DecrementPossessions()
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
    ftCutoff = (ftMagicNum1 * shooter.FreeThrow) + ftMagicNum2
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
                off_rebounder = GetRebounder(t1State.Roster)
                def_rebounder = GetRebounder(t2State.Roster)
                reb_probability = GetReboundProbability(off_rebounder, def_rebounder)
                if rebrand < reb_probability:
                    gamestate.IncrementEventCount("OffReb")
                    ReboundTheBall(
                        gamestate,
                        off_rebounder,
                        team_one,
                        gamestate.PossessingTeam,
                        home_label,
                        True,
                        play,
                        collector,
                    )
                else:
                    gamestate.IncrementEventCount("DefReb")
                    ReboundTheBall(
                        gamestate,
                        def_rebounder,
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


def GetDefender(formation, offensive_style, roster, shooter):
    defensivePlayer = None
    filtered_defense = []

    def total_usage(players):
        return sum(p.Usage for p in players)

    if formation == "Man-to-Man":
        filtered_defense = [
            p
            for p in roster
            if (
                (p.PositionOne != "" and p.PositionOne == shooter.PositionOne)
                or (p.PositionTwo != "" and p.PositionTwo == shooter.PositionTwo)
                or (p.PositionThree != "" and p.PositionThree == shooter.PositionThree)
            )
            and p.Usage > 0.0
        ]
        # Fallback for offensive style differences
        if not filtered_defense or total_usage(filtered_defense) == 0:
            if offensive_style == "Jumbo" and (shooter.PositionOne == "PG"):
                filtered_defense = [
                    p
                    for p in roster
                    if (
                        p.PositionOne == "SG"
                        or p.PositionTwo == "SG"
                        or p.PositionThree == "SG"
                    )
                    and p.Usage > 0.0
                ]
            elif offensive_style == "Small Ball" and (shooter.PositionOne == "C"):
                filtered_defense = [
                    p
                    for p in roster
                    if (
                        p.PositionOne == "PF"
                        or p.PositionTwo == "PF"
                        or p.PositionThree == "PF"
                    )
                    and p.Usage > 0.0
                ]
            elif offensive_style == "Microball" and (
                shooter.PositionOne == "C" or shooter.PositionTwo == "PF"
            ):
                filtered_defense = [
                    p
                    for p in roster
                    if (
                        p.PositionOne == "SF"
                        or p.PositionTwo == "SF"
                        or p.PositionThree == "SF"
                    )
                    and p.Usage > 0.0
                ]
    else:
        filtered_defense = roster

    if not filtered_defense:
        filtered_defense = roster

    defensivePlayer = random.choices(
        filtered_defense,
        weights=[x.Usage for x in filtered_defense],
        k=1,
    )
    return defensivePlayer[0]


def GetFouler(roster):
    eligible_players = [player for player in roster if player.Usage > 0]
    weights = [player.AdjDiscipline for player in eligible_players]
    fouling_player = random.choices(
        eligible_players,
        weights=weights,
        k=1,
    )
    return fouling_player[0]


def HandleInjury(t1State, t2State, injury_state):
    combined_list = t1State.Roster + t2State.Roster
    filtered_combined_list = [player for player in combined_list if player.Usage > 0.0]
    injured_player = random.choices(
        filtered_combined_list,
        weights=[x.AdjInjury for x in filtered_combined_list],
        k=1,
    )
    injuree = injured_player[0]
    # Generate injury
    injury_weights = injury_state["injury_weights"]
    designated_injury = random.choices(
        injury_weights,
        weights=[x["weight"] for x in injury_weights],
        k=1,
    )
    chosen_injury = designated_injury[0]
    injury_name = chosen_injury["name"]
    severity = util.GetInjurySeverity(injury_name)
    injury_map = injury_state["injury_map"]
    recovery_list = injury_map[injury_name][severity]
    # Because the range is within weeks, we multiply by 4 because of the number of games in a week
    minimum = recovery_list[0]
    maximum = recovery_list[1] * 4
    # If the severity isn't mild, multiply minimum by 4.
    # Mild is the only option where a player can be injured for less than 1 week
    if severity != "Mild" or severity in ("Achilles", "Arm", "Leg"):
        minimum = minimum * 4
    recovery_time = random.randrange(minimum, maximum)
    injuree.RecordInjury(injury_name, severity, recovery_time)
    t1State.ReloadRoster()
    t2State.ReloadRoster()


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
    shooter = GetShooter(t1State.Roster, 1)
    shooter.Stats.AddPossession()
    defender = GetDefender(
        t2State.DefensiveFormation, t2State.OffensiveStyle, t2State.Roster, shooter
    )
    # DO THE DEFENSIVE PLAYER'S ADJPERIMETER DEFENSE HERE
    # blockAdj = (blockAdjMagicNum1 * t2State.AdjPerimeterDef) - blockAdjMagicNum2
    blockAdj = (blockAdjMagicNum1 * defender.AdjPerimeterDefense) - blockAdjMagicNum2
    made3nf = 0
    if shooter.FirstName + " " + shooter.LastName == focus_player:
        made3nf = (made3nfMagicNum1 * (shooter.Shooting3 - 4)) + made3nfMagicNum2
    else:
        made3nf = (made3nfMagicNum1 * shooter.Shooting3) + made3nfMagicNum2
    if gamestate.IsNeutral != True and isHome == True:
        made3nf += gamestate.HCA
    madeDiff = made3nf - madeDiffMagicNum1
    missed3nf = missed3nfMagicNum1 - madeDiff - blockAdj
    made3foul = made3fMagicNum1
    missed3foul = missed3foulMagicNum
    blocked = blockedMagicNum + blockAdj
    base3Cutoff = 0
    made3Cutoff = base3Cutoff + made3nf
    missed3Cutoff = made3Cutoff + missed3nf
    blocked3Cutoff = missed3Cutoff + blocked
    missed3foulCutoff = blocked3Cutoff + missed3foul
    made3foulCutoff = missed3foulCutoff + made3foul
    eventOutcome = random.random()

    if eventOutcome < made3Cutoff:
        gamestate.IncrementShotResultCount("Three", "Made")
        Made3Outcome(
            gamestate,
            shooter,
            defender,
            t1State,
            team1,
            receiving_team,
            isHome,
            collector,
        )
    elif eventOutcome < missed3Cutoff:
        gamestate.IncrementShotResultCount("Three", "Missed")
        Missed3Outcome(
            gamestate,
            shooter,
            defender,
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
        gamestate.IncrementShotResultCount("Three", "Blocked")
        Blocked3Outcome(
            gamestate,
            shooter,
            defender,
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
        gamestate.IncrementShotResultCount("Three", "FoulMissed")
        Missed3FoulOutcome(
            gamestate,
            shooter,
            defender,
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
        gamestate.IncrementShotResultCount("Three", "FoulMade")
        Made3FoulOutcome(
            gamestate,
            shooter,
            defender,
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
    gamestate, shooter, defender, team_state, team, receiving_team, isHome, collector
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
    if assistRand > assistCutoff:
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
    defender,
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
    off_rebounder = GetRebounder(t1State.Roster)
    def_rebounder = GetRebounder(t2State.Roster)
    reb_probability = GetReboundProbability(off_rebounder, def_rebounder)
    if rebrand < reb_probability:
        gamestate.IncrementEventCount("OffReb")
        ReboundTheBall(
            gamestate,
            off_rebounder,
            team_one,
            gamestate.PossessingTeam,
            h_label,
            True,
            play,
            collector,
        )
    else:
        gamestate.IncrementEventCount("DefReb")
        ReboundTheBall(
            gamestate,
            def_rebounder,
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
    defender,
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
    shooter.Stats.AddFieldGoal(False, 3)
    team_one.Stats.AddThreePointShot(False)
    defender.Stats.AddBlock()
    team_two.Stats.AddBlocks()
    printBlocker = (
        defender.Position + " " + defender.FirstName + " " + defender.LastName
    )
    play = (
        printShooter
        + " 3-point attempt...BLOCKED by "
        + receiving_team
        + " "
        + printBlocker
        + "."
    )
    rebrand = random.random()
    off_rebounder = GetRebounder(t1State.Roster)
    def_rebounder = GetRebounder(t2State.Roster)
    reb_probability = GetReboundProbability(off_rebounder, def_rebounder)
    if rebrand < reb_probability:
        gamestate.IncrementEventCount("OffReb")
        ReboundTheBall(
            gamestate,
            off_rebounder,
            team_one,
            gamestate.PossessingTeam,
            h_label,
            True,
            play,
            collector,
        )
    else:
        gamestate.IncrementEventCount("DefReb")
        ReboundTheBall(
            gamestate,
            def_rebounder,
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
    defender,
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
    fouling_player = GetFouler(t2State.Roster)
    fouling_player.AddFoul(gamestate.IsNBA)
    print_fouler = f"{fouling_player.TeamAbbr} {fouling_player.Position} {fouling_player.FirstName} {fouling_player.LastName}. "
    if fouling_player.FouledOut:
        t2State.ReloadRoster()
        print_fouler += f"It looks like {fouling_player.LastName} has accumulated the maximum limit on fouls and cannot play for the remainder of the game."
    collector.AppendPlay(
        gamestate.PossessingTeam,
        f"{printShooter} 3-point attempt... Missed. There is a foul on the play by {print_fouler}",
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
    defender,
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
    fouling_player = GetFouler(t2State.Roster)
    fouling_player.AddFoul(gamestate.IsNBA)
    print_fouler = f"Foul called on {fouling_player.TeamAbbr} {fouling_player.Position} {fouling_player.FirstName} {fouling_player.LastName}. "
    if fouling_player.FouledOut:
        t2State.ReloadRoster()
        print_fouler += f"It looks like {fouling_player.LastName} has accumulated the maximum limit on fouls and cannot play for the remainder of the game."
    play = f"{printShooter} 3-point attempt...Score! Fouled on the play... and one! {print_fouler}"

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
    if assistRand > assistCutoff:
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
    shooter = GetShooter(t1State.Roster, 2)
    shooter.Stats.AddPossession()
    defender = GetDefender(
        t2State.DefensiveFormation, t2State.OffensiveStyle, t2State.Roster, shooter
    )
    blockAdj = (blockAdjMagicNum1 * defender.AdjInteriorDefense) - blockAdjMagicNum2
    made2jnf = 0
    if shooter.FirstName + " " + shooter.LastName == focus_player:
        made2jnf = (
            (made2jnfMagicNum1 * (shooter.Shooting2 - 4))
            + made2jnfMagicNum2
            + gamestate.HCA
        )
    else:
        made2jnf = (
            (made2jnfMagicNum1 * shooter.Shooting2) + made2jnfMagicNum2 + gamestate.HCA
        )
    if gamestate.IsNeutral != True and isHome == True:
        made2jnf += gamestate.HCA
    madeDiff = made2jnf - made2jnfDiffMagicNum1
    missed2jnf = missed2jnfMagicNum1 - madeDiff - blockAdj
    made2jfoul = made2jfoulMagicNum
    missed2jfoul = missed2jfoulMagicNum
    blocked = blockedJumperMagicNum + blockAdj
    base2jCutoff = 0
    made2jCutoff = base2jCutoff + made2jnf
    missed2jCutoff = made2jCutoff + missed2jnf
    blocked2jCutoff = missed2jCutoff + blocked
    missed2jfoulCutoff = blocked2jCutoff + missed2jfoul
    made2jfoulCutoff = missed2jfoulCutoff + made2jfoul
    eventOutcome = random.random()

    if eventOutcome < made2jCutoff:
        gamestate.IncrementShotResultCount("Mid", "Made")
        MadeJumperOutcome(
            gamestate,
            shooter,
            defender,
            t1State,
            team1,
            receiving_team,
            isHome,
            collector,
        )
    elif eventOutcome < missed2jCutoff:
        gamestate.IncrementShotResultCount("Mid", "Missed")
        MissedJumperOutcome(
            gamestate,
            shooter,
            defender,
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
        gamestate.IncrementShotResultCount("Mid", "Blocked")
        BlockedJumperOutcome(
            gamestate,
            shooter,
            defender,
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
        gamestate.IncrementShotResultCount("Mid", "FoulMissed")
        MissedJumperFoulOutcome(
            gamestate,
            shooter,
            defender,
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
        gamestate.IncrementShotResultCount("Mid", "FoulMade")
        MadeJumperFoulOutcome(
            gamestate,
            shooter,
            defender,
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
    gamestate, shooter, defender, team_state, team, receiving_team, isHome, collector
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
    if assistRand > assistJumperCutoff:
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
    defender,
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
    off_rebounder = GetRebounder(t1State.Roster)
    def_rebounder = GetRebounder(t2State.Roster)
    reb_probability = GetReboundProbability(off_rebounder, def_rebounder)
    if rebrand < reb_probability:
        gamestate.IncrementEventCount("OffReb")
        ReboundTheBall(
            gamestate,
            off_rebounder,
            team_one,
            gamestate.PossessingTeam,
            h_label,
            True,
            play,
            collector,
        )
    else:
        gamestate.IncrementEventCount("DefReb")
        ReboundTheBall(
            gamestate,
            def_rebounder,
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
    defender,
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
    shooter.Stats.AddFieldGoal(False, 2)
    team_one.Stats.AddFieldGoal(False)
    defender.Stats.AddBlock()
    team_two.Stats.AddBlocks()
    printBlocker = (
        defender.Position + " " + defender.FirstName + " " + defender.LastName
    )
    play = (
        printShooter
        + " 2-point jumper...BLOCKED by "
        + receiving_team
        + " "
        + printBlocker
        + "."
    )
    rebrand = random.random()
    off_rebounder = GetRebounder(t1State.Roster)
    def_rebounder = GetRebounder(t2State.Roster)
    reb_probability = GetReboundProbability(off_rebounder, def_rebounder)
    if rebrand < reb_probability:
        gamestate.IncrementEventCount("OffReb")
        ReboundTheBall(
            gamestate,
            off_rebounder,
            team_one,
            gamestate.PossessingTeam,
            h_label,
            True,
            play,
            collector,
        )
    else:
        gamestate.IncrementEventCount("DefReb")
        ReboundTheBall(
            gamestate,
            def_rebounder,
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
    defender,
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
    fouling_player = GetFouler(t2State.Roster)
    fouling_player.AddFoul(gamestate.IsNBA)
    print_fouler = f"{fouling_player.TeamAbbr} {fouling_player.Position} {fouling_player.FirstName} {fouling_player.LastName}. "
    if fouling_player.FouledOut:
        t2State.ReloadRoster()
        print_fouler += f"It looks like {fouling_player.LastName} has accumulated the maximum limit on fouls and cannot play for the remainder of the game."
    collector.AppendPlay(
        gamestate.PossessingTeam,
        printShooter
        + f" 2-point jumper... Missed with a foul on the play by {print_fouler}",
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
    defender,
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
    fouling_player = GetFouler(t2State.Roster)
    fouling_player.AddFoul(gamestate.IsNBA)
    print_fouler = f"{fouling_player.TeamAbbr} {fouling_player.Position} {fouling_player.FirstName} {fouling_player.LastName}. "
    if fouling_player.FouledOut:
        t2State.ReloadRoster()
        print_fouler += f"It looks like {fouling_player.LastName} has accumulated the maximum limit on fouls and cannot play for the remainder of the game."
    play = f"{printShooter} 2-point jumper...Score! Foul on the play and one! Foul was called on {print_fouler}"
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
    team_two.Stats.AddFoul()
    assistRand = random.random()
    if assistRand > assistJumperCutoff:
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
    shooter = GetShooter(t1State.Roster, 3)
    shooter.Stats.AddPossession()
    defender = GetDefender(
        t2State.DefensiveFormation, t2State.OffensiveStyle, t2State.Roster, shooter
    )
    blockAdj = (blockAdjMagicNum1 * defender.AdjInteriorDefense) - blockAdjMagicNum2
    made2inf = 0
    if shooter.FirstName + " " + shooter.LastName == focus_player:
        made2inf = (
            (made2infMagicNum1 * (shooter.Finishing - 4))
            + made2infMagicNum2
            + gamestate.HCA
        )
    else:
        made2inf = (
            (made2infMagicNum1 * shooter.Finishing) + made2infMagicNum2 + gamestate.HCA
        )
    if gamestate.IsNeutral != True and isHome == True:
        made2inf += gamestate.HCA
    madeDiff = made2inf - madeDiffInsideMagicNum
    missed2inf = missed2infMagicNum - madeDiff - blockAdj
    made2infoul = made2infoulMagicNum
    missed2infoul = missed2infoulMagicNum
    blocked = blockedInfMagicNum + blockAdj
    base2inCutoff = 0
    made2inCutoff = base2inCutoff + made2inf
    missed2inCutoff = made2inCutoff + missed2inf
    blocked2inCutoff = missed2inCutoff + blocked
    missed2infoulCutoff = blocked2inCutoff + missed2infoul
    made2infoulCutoff = missed2infoulCutoff + made2infoul
    eventOutcome = random.random()

    if eventOutcome < made2inCutoff:
        gamestate.IncrementShotResultCount("Inside", "Made")
        MadeInsideOutcome(
            gamestate,
            shooter,
            defender,
            t1State,
            team1,
            receiving_team,
            isHome,
            collector,
        )
    elif eventOutcome < missed2inCutoff:
        gamestate.IncrementShotResultCount("Inside", "Missed")
        MissedInsideOutcome(
            gamestate,
            shooter,
            defender,
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
        gamestate.IncrementShotResultCount("Inside", "Blocked")
        BlockedInsideOutcome(
            gamestate,
            shooter,
            defender,
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
        gamestate.IncrementShotResultCount("Inside", "FoulMissed")
        MissedInsideFoulOutcome(
            gamestate,
            shooter,
            defender,
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
        gamestate.IncrementShotResultCount("Inside", "FoulMade")
        MadeInsideFoulOutcome(
            gamestate,
            shooter,
            defender,
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
    gamestate, shooter, defender, team_state, team, receiving_team, isHome, collector
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
    if assistRand > assistInsideCutoff:
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
    defender,
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
    off_rebounder = GetRebounder(t1State.Roster)
    def_rebounder = GetRebounder(t2State.Roster)
    reb_probability = GetReboundProbability(off_rebounder, def_rebounder)
    if rebrand < reb_probability:
        gamestate.IncrementEventCount("OffReb")
        ReboundTheBall(
            gamestate,
            off_rebounder,
            team_one,
            gamestate.PossessingTeam,
            h_label,
            True,
            play,
            collector,
        )
    else:
        gamestate.IncrementEventCount("DefReb")
        ReboundTheBall(
            gamestate,
            def_rebounder,
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
    defender,
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
    shooter.Stats.AddFieldGoal(False, 2)
    team_one.Stats.AddFieldGoal(False)
    defender.Stats.AddBlock()
    team_two.Stats.AddBlocks()
    printBlocker = (
        defender.Position + " " + defender.FirstName + " " + defender.LastName
    )
    play = (
        printShooter
        + " Inside shot... BLOCKED by "
        + receiving_team
        + " "
        + printBlocker
        + "."
    )
    rebrand = random.random()
    off_rebounder = GetRebounder(t1State.Roster)
    def_rebounder = GetRebounder(t2State.Roster)
    reb_probability = GetReboundProbability(off_rebounder, def_rebounder)
    if rebrand < reb_probability:
        gamestate.IncrementEventCount("OffReb")
        ReboundTheBall(
            gamestate,
            off_rebounder,
            team_one,
            gamestate.PossessingTeam,
            h_label,
            True,
            play,
            collector,
        )
    else:
        gamestate.IncrementEventCount("DefReb")
        ReboundTheBall(
            gamestate,
            def_rebounder,
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
    defender,
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
    fouling_player = GetFouler(t2State.Roster)
    fouling_player.AddFoul(gamestate.IsNBA)
    print_fouler = f"{fouling_player.TeamAbbr} {fouling_player.Position} {fouling_player.FirstName} {fouling_player.LastName}. "
    if fouling_player.FouledOut:
        t2State.ReloadRoster()
        print_fouler += f"It looks like {fouling_player.LastName} has accumulated the maximum limit on fouls and cannot play for the remainder of the game."
    collector.AppendPlay(
        gamestate.PossessingTeam,
        f"{printShooter} Inside shot... Missed with a foul on the play by {print_fouler}",
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
    defender,
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
    fouling_player = GetFouler(t2State.Roster)
    fouling_player.AddFoul(gamestate.IsNBA)
    print_fouler = f"{fouling_player.TeamAbbr} {fouling_player.Position} {fouling_player.FirstName} {fouling_player.LastName} was called on the foul. "
    if fouling_player.FouledOut:
        t2State.ReloadRoster()
        print_fouler += f"It looks like {fouling_player.LastName} has accumulated the maximum limit on fouls and cannot play for the remainder of the game."
    play = (
        f"{printShooter} Inside shot...Score! Foul on the play and one! {print_fouler}"
    )
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
    team_two.Stats.AddFoul()
    team_one.Stats.CalculateLead(2, gamestate.T1Points - gamestate.T2Points)
    assistRand = random.random()
    if assistRand > assistInsideCutoff:
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
