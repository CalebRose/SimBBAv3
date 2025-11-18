import random
from typing import List, Optional
from constants import *
import util
from play_by_play_generator import *


def GetPlayerLabel(player):
    return f"{player.TeamAbbr} {player.Position} {player.FirstName} {player.LastName}"


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
    filtered_roster = [
        player for player in roster if player.Usage > 0 and player.IsInjured == False
    ]

    # make sure that there are players available to shoot
    if not filtered_roster:
        filtered_roster = [player for player in roster if player.IsInjured == False]

    weight = []
    final_roster = []
    if shot_type == 1:
        final_roster = [x for x in filtered_roster if x.ThreePointUsage > 0]
        weight = [x.ThreePointUsage for x in final_roster]
    elif shot_type == 2:
        final_roster = [x for x in filtered_roster if x.MidUsage > 0]
        weight = [x.MidUsage for x in final_roster]
    else:
        final_roster = [x for x in filtered_roster if x.InsideUsage > 0]
        weight = [x.InsideUsage for x in final_roster]
    if sum(weight) == 0:
        final_roster = [x for x in filtered_roster]
        weight = [x.Usage for x in final_roster]
        if sum(weight) == 0:
            weight = [
                1 for _ in final_roster
            ]  # assign equal weight if no usage stats are available

    pickPlayer = random.choices(
        final_roster,
        weights=weight,
        k=1,
    )
    return pickPlayer[0]


def GetRebounder(roster):
    filtered_roster = [player for player in roster if player.Usage > 0]
    if not filtered_roster:
        filtered_roster = [player for player in roster if player.IsInjured == False]
    weight = [
        player.AdjRebounding * POSITION_WEIGHTS.get(player.Position, 1.0)
        for player in filtered_roster
    ]
    if sum(weight) == 0:
        weight = [
            1 for _ in filtered_roster
        ]  # assign equal weight if no usage stats are available
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


def StealEvent(gamestate, t2roster, t1Roster, team1, team2, t, label, collector):
    steal_weights = [x.DefensePer for x in t2roster]
    if sum(steal_weights) == 0:
        steal_weights = [1] * len(t2roster)
    pickPlayer = random.choices(t2roster, weights=steal_weights, k=1)
    if not pickPlayer:
        pickPlayer = random.choices(t2roster, k=1)  # this might not be right
    stealPlayer = pickPlayer[0]
    stealPlayer.Stats.AddPossession()
    stealPlayer.Stats.AddSteal()
    possess_weights = [x.Usage for x in t1Roster]
    if sum(possess_weights) <= 0:
        possess_weights = [1] * len(t1Roster)
    possessing_player = random.choices(t1Roster, weights=possess_weights, k=1)
    if not possessing_player:
        possessing_player = random.choices(t1Roster, k=1)
    pos_player = possessing_player[0]
    team1.Stats.AddTurnover()
    team2.Stats.AddSteal()
    printPlayer = GetPlayerLabel(pos_player)
    printShooter = GetPlayerLabel(stealPlayer)
    msg = GenerateStealBallText(printPlayer, printShooter, gamestate.PossessingTeam, t)
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
    gamestate, tState, t2State, team, receiving_team, receiving_label, collector
):
    otherTO = random.random()
    usage_t1_weights = [x.Usage for x in tState.Roster]
    if sum(usage_t1_weights) == 0:
        usage_t1_weights = [1] * len(tState.Roster)
    pickPlayer = random.choices(tState.Roster, weights=usage_t1_weights, k=1)
    if not pickPlayer:
        pickPlayer = random.choices(tState.Roster, k=1)
    toPlayer = pickPlayer[0]
    toPlayer.Stats.AddPossession()
    toPlayer.Stats.AddTurnover()
    printShooter = GetPlayerLabel(toPlayer)
    team.Stats.AddTurnover()
    assister = SelectAssister(toPlayer, tState)
    ast_label = GetPlayerLabel(assister)
    usage_t2_weights = [x.Usage for x in t2State.Roster]
    if sum(usage_t2_weights) == 0:
        usage_t2_weights = [1] * len(t2State.Roster)
    defender = random.choices(
        t2State.Roster, weights=usage_t2_weights, k=1
    )  # might want to add messages saying that the gameplan was not set
    if not defender:
        defender = random.choices(t2State.Roster, k=1)
    defPlayer = defender[0]
    def_label = GetPlayerLabel(defPlayer)
    if otherTO < outOfBoundsCutoff:
        msg = GenerateOutOfBoundsText(
            printShooter,
            ast_label,
            def_label,
            gamestate.PossessingTeam,
            receiving_label,
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
        msg = GenerateShotClockViolationText(
            printShooter, ast_label, def_label, gamestate.PossessingTeam, receiving_team
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
        toLabel = GetPlayerLabel(toPlayer)
        msg = GenerateOffensiveFoulText(
            toLabel, ast_label, def_label, gamestate.PossessingTeam, receiving_team
        )
        proportions = toPlayer.AddFoul(
            gamestate.IsNBA, gamestate.PossessionNumber, gamestate.Total_Possessions
        )
        if toPlayer.FouledOut == True:
            tState.ReloadRoster(toPlayer.ID, toPlayer.TeamID, proportions)
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
    printRebounder = GetPlayerLabel(rebounder)
    reb_text = GenerateReboundText(printRebounder, receiving_label, is_offense)
    message = play + reb_text
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
    assist_weights = [x.AssistPer for x in assistList]
    if sum(assist_weights) == 0:
        assist_weights = [1] * len(assistList)
    pickPlayer = random.choices(assistList, weights=assist_weights, k=1)
    if not pickPlayer:
        pickPlayer = [random.choice(assistList, k=1)]
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
    player_label = GetPlayerLabel(shooter)
    while shots > 0:
        if random.random() <= ftCutoff:
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
            msg = GenerateFreeThrowText(
                player_label,
                isHome,
                True,
                home_label,
                receiving_label,
                gamestate.Capacity,
                shots,
            )
            collector.AppendPlay(
                gamestate.PossessingTeam,
                msg,
                "FreeThrow",
                gamestate.T1Points,
                gamestate.T2Points,
                gamestate.PossessionNumber,
                gamestate.Total_Possessions,
            )
            collector.AppendLogic(
                gamestate.PossessingTeam,
                "Foul",
                "Made",
                player_label,
                "",
                0,
                ftCutoff,
                0,
                0,
                0,
                0,
                gamestate.PossessionNumber,
                gamestate.Total_Possessions,
            )
            if shots == 0:
                gamestate.SetPossessingTeam(receiving_team)
        else:
            shooter.Stats.AddFTAttempt()
            team_one.Stats.AddFreeThrow(False)
            shots -= 1
            play = GenerateFreeThrowText(
                player_label,
                isHome,
                False,
                home_label,
                receiving_label,
                gamestate.Capacity,
                shots,
            )
            collector.AppendLogic(
                gamestate.PossessingTeam,
                "Foul",
                "Missed",
                player_label,
                "",
                0,
                ftCutoff,
                0,
                0,
                0,
                0,
                gamestate.PossessionNumber,
                gamestate.Total_Possessions,
            )
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
    filtered_defense = [
        p for p in roster if p.Usage > 0 and not getattr(p, "IsInjured", False)
    ]
    if formation == "Man-to-Man" and shooter is not None:
        # collect the shooter’s three eligible positions
        shooter_pos = {
            pos
            for pos in (
                shooter.PositionOne,
                shooter.PositionTwo,
                shooter.PositionThree,
            )
            if pos
        }
        # only defenders who share at least one of those spots
        m2m = [
            p
            for p in filtered_defense
            if any(
                pos in shooter_pos
                for pos in (p.PositionOne, p.PositionTwo, p.PositionThree)
            )
        ]

        # if that fails, try your “style” fallback
        if not m2m or sum(p.Usage for p in m2m) == 0:
            if offensive_style == "Jumbo" and shooter.PositionOne == "PG":
                match_pos = "SG"
            elif offensive_style == "Small Ball" and shooter.PositionOne == "C":
                match_pos = "PF"
            elif offensive_style == "Microball" and shooter.PositionOne in ("C", "PF"):
                match_pos = "SF"
            else:
                match_pos = None

            if match_pos:
                m2m = [
                    p
                    for p in roster
                    if p.Usage > 0
                    and match_pos in (p.PositionOne, p.PositionTwo, p.PositionThree)
                ]

    if not filtered_defense:
        filtered_defense = roster

    usage_weights = [x.Usage for x in filtered_defense]
    if sum(usage_weights) == 0:
        usage_weights = [1] * len(
            filtered_defense
        )  # assign equal weight if no usage stats are available
    defensivePlayer = random.choices(
        filtered_defense,
        weights=usage_weights,
        k=1,
    )
    return defensivePlayer[0]


def GetFouler(roster):
    eligible_players = [player for player in roster if player.Usage > 0]
    if not eligible_players:
        eligible_players = roster
    weights = [player.AdjDiscipline for player in eligible_players]
    if sum(weights) == 0:
        weights = [1] * len(
            eligible_players
        )  # assign equal weight if no usage stats are available
    fouling_player = random.choices(
        eligible_players,
        weights=weights,
        k=1,
    )
    return fouling_player[0]


def HandleInjury(t1State, t2State, injury_state, collector, gamestate):
    combined_list = t1State.Roster + t2State.Roster
    filtered_combined_list = [player for player in combined_list if player.Usage > 0.0]
    if not filtered_combined_list:
        filtered_combined_list = [
            player for player in combined_list if not player.IsInjured
        ]
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
    proportions = injuree.RecordInjury(
        injury_name,
        severity,
        recovery_time,
        gamestate.PossessionNumber,
        gamestate.Total_Possessions,
    )
    injuree_label = GetPlayerLabel(injuree)
    t1State.ReloadRoster(injuree.ID, injuree.TeamID, proportions)
    t2State.ReloadRoster(injuree.ID, injuree.TeamID, proportions)
    injury_text = GenerateInjuryText(injuree_label, injury_name, severity)
    collector.AppendPlay(
        injuree.TeamAbbr,
        injury_text,
        "Injury",
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
    shooter = GetShooter(t1State.Roster, 1)
    shooter.Stats.AddPossession()
    defender = GetDefender(
        t2State.DefensiveFormation, t2State.OffensiveStyle, t2State.Roster, shooter
    )
    # DO THE DEFENSIVE PLAYER'S ADJPERIMETER DEFENSE HERE
    # blockAdj = (blockAdjMagicNum1 * t2State.AdjPerimeterDef) - blockAdjMagicNum2
    blockAdj = (blockAdjMagicNum1 * defender.AdjPerimeterDefense) - blockAdjMagicNum2
    made3nf = 0
    three_base = gamestate.GetShootingBase(1)
    three_adj = gamestate.GetShootingAdj(1)
    if shooter.FirstName + " " + shooter.LastName == focus_player:
        made3nf = three_base + (
            three_adj * ((shooter.Shooting3 - 4) - defender.PerimeterDefense)
        )
    else:
        made3nf = cbb_three_base + (
            three_adj * ((shooter.Shooting3) - defender.PerimeterDefense)
        )
    if gamestate.IsNeutral != True and isHome == False:
        made3nf -= gamestate.HCA
    madeDiff = made3nf
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
    s_label = GetPlayerLabel(shooter)
    d_label = GetPlayerLabel(defender)

    if eventOutcome < made3Cutoff:
        collector.AppendLogic(
            gamestate.PossessingTeam,
            "3pt",
            "Made",
            s_label,
            d_label,
            eventOutcome,
            made3Cutoff,
            missed3Cutoff,
            blocked3Cutoff,
            missed3foulCutoff,
            made3foulCutoff,
            gamestate.PossessionNumber,
            gamestate.Total_Possessions,
        )
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
        collector.AppendLogic(
            gamestate.PossessingTeam,
            "3pt",
            "Missed",
            s_label,
            d_label,
            eventOutcome,
            made3Cutoff,
            missed3Cutoff,
            blocked3Cutoff,
            missed3foulCutoff,
            made3foulCutoff,
            gamestate.PossessionNumber,
            gamestate.Total_Possessions,
        )
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
            isHome,
        )
    elif eventOutcome < blocked3Cutoff:
        collector.AppendLogic(
            gamestate.PossessingTeam,
            "3pt",
            "Blocked",
            s_label,
            d_label,
            eventOutcome,
            made3Cutoff,
            missed3Cutoff,
            blocked3Cutoff,
            missed3foulCutoff,
            made3foulCutoff,
            gamestate.PossessionNumber,
            gamestate.Total_Possessions,
        )
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
            isHome,
        )
    elif eventOutcome < missed3foulCutoff:
        collector.AppendLogic(
            gamestate.PossessingTeam,
            "3pt",
            "Missed Foul",
            s_label,
            d_label,
            eventOutcome,
            made3Cutoff,
            missed3Cutoff,
            blocked3Cutoff,
            missed3foulCutoff,
            made3foulCutoff,
            gamestate.PossessionNumber,
            gamestate.Total_Possessions,
        )
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
        collector.AppendLogic(
            gamestate.PossessingTeam,
            "3pt",
            "FoulMade",
            s_label,
            d_label,
            eventOutcome,
            made3Cutoff,
            missed3Cutoff,
            blocked3Cutoff,
            missed3foulCutoff,
            made3foulCutoff,
            gamestate.PossessionNumber,
            gamestate.Total_Possessions,
        )
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
    else:
        collector.AppendLogic(
            gamestate.PossessingTeam,
            "3pt",
            "Missed",
            s_label,
            d_label,
            eventOutcome,
            made3Cutoff,
            missed3Cutoff,
            blocked3Cutoff,
            missed3foulCutoff,
            made3foulCutoff,
            gamestate.PossessionNumber,
            gamestate.Total_Possessions,
        )
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
            isHome,
        )


def Made3Outcome(
    gamestate, shooter, defender, team_state, team, receiving_team, isHome, collector
):
    s = shooter
    printDefender = GetPlayerLabel(defender)
    printAssister = ""
    gamestate.AddPoints(3, isHome)
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
        assister = SelectAssister(s, team_state)
        if assister.ID != s.ID:
            assister.Stats.AddAssist()
            team.Stats.AddAssist()
            printAssister = GetPlayerLabel(assister)
    s.Stats.AddFieldGoal(True, 3)
    printShooter = GetPlayerLabel(s)
    play = GenerateThreePointText(
        printShooter,
        printDefender,
        printAssister,
        "",
        False,
        isHome,
        gamestate.Capacity,
        1,
        gamestate.PossessingTeam,
    )
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
    isHome,
):
    printShooter = GetPlayerLabel(shooter)
    printDefender = GetPlayerLabel(defender)
    shooter.Stats.AddFieldGoal(False, 3)
    team_one.Stats.AddThreePointShot(False)
    team_one.Stats.AddFieldGoal(False)
    play = GenerateThreePointText(
        printShooter,
        printDefender,
        "",
        "",
        False,
        isHome,
        gamestate.Capacity,
        2,
        gamestate.PossessingTeam,
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
    isHome,
):
    printShooter = GetPlayerLabel(shooter)
    printDefender = GetPlayerLabel(defender)
    shooter.Stats.AddFieldGoal(False, 3)
    team_one.Stats.AddThreePointShot(False)
    defender.Stats.AddBlock()
    team_two.Stats.AddBlocks()
    play = GenerateThreePointText(
        printShooter,
        printDefender,
        "",
        "",
        False,
        isHome,
        gamestate.Capacity,
        3,
        gamestate.PossessingTeam,
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
    printShooter = GetPlayerLabel(shooter)
    printDefender = GetPlayerLabel(defender)
    fouling_player = GetFouler(t2State.Roster)
    proportions = fouling_player.AddFoul(
        gamestate.IsNBA, gamestate.PossessionNumber, gamestate.Total_Possessions
    )
    print_fouler = GetPlayerLabel(fouling_player)
    if fouling_player.FouledOut:
        t2State.ReloadRoster(fouling_player.ID, fouling_player.TeamID, proportions)
    play = GenerateThreePointText(
        printShooter,
        printDefender,
        "",
        print_fouler,
        fouling_player.FouledOut,
        isHome,
        gamestate.Capacity,
        4,
        gamestate.PossessingTeam,
    )
    collector.AppendPlay(
        gamestate.PossessingTeam,
        play,
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
    printDefender = GetPlayerLabel(defender)
    printAssister = ""
    fouling_player = GetFouler(t2State.Roster)
    proportions = fouling_player.AddFoul(
        gamestate.IsNBA, gamestate.PossessionNumber, gamestate.Total_Possessions
    )
    fouling_label = GetPlayerLabel(fouling_player)
    if fouling_player.FouledOut:
        t2State.ReloadRoster(fouling_player.ID, fouling_player.TeamID, proportions)

    gamestate.AddPoints(3, isHome)
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
            printAssister = GetPlayerLabel(assister)
    printShooter = GetPlayerLabel(shooter)
    play = GenerateThreePointText(
        printShooter,
        printDefender,
        printAssister,
        fouling_label,
        fouling_player.FouledOut,
        isHome,
        gamestate.Capacity,
        5,
        gamestate.PossessingTeam,
    )
    shooter.Stats.AddFieldGoal(True, 3)
    # Add play generation text
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
    mid_base = gamestate.GetShootingBase(2)
    mid_adj = gamestate.GetShootingAdj(2)
    if shooter.FirstName + " " + shooter.LastName == focus_player:
        made2jnf = mid_base + (
            mid_adj * ((shooter.Shooting2 - 4) - defender.PerimeterDefense)
        )
    else:
        made2jnf = mid_base + (
            mid_adj * ((shooter.Shooting2) - defender.PerimeterDefense)
        )
    if gamestate.IsNeutral != True and isHome == False:
        made2jnf -= gamestate.HCA
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
    s_label = GetPlayerLabel(shooter)
    d_label = GetPlayerLabel(defender)

    if eventOutcome < made2jCutoff:
        collector.AppendLogic(
            gamestate.PossessingTeam,
            "Mid",
            "Made",
            s_label,
            d_label,
            eventOutcome,
            made2jCutoff,
            missed2jCutoff,
            blocked2jCutoff,
            missed2jfoulCutoff,
            made2jfoulCutoff,
            gamestate.PossessionNumber,
            gamestate.Total_Possessions,
        )
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
        collector.AppendLogic(
            gamestate.PossessingTeam,
            "Mid",
            "Missed",
            s_label,
            d_label,
            eventOutcome,
            made2jCutoff,
            missed2jCutoff,
            blocked2jCutoff,
            missed2jfoulCutoff,
            made2jfoulCutoff,
            gamestate.PossessionNumber,
            gamestate.Total_Possessions,
        )
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
            isHome,
        )
    elif eventOutcome < blocked2jCutoff:
        collector.AppendLogic(
            gamestate.PossessingTeam,
            "Mid",
            "Blocked",
            s_label,
            d_label,
            eventOutcome,
            made2jCutoff,
            missed2jCutoff,
            blocked2jCutoff,
            missed2jfoulCutoff,
            made2jfoulCutoff,
            gamestate.PossessionNumber,
            gamestate.Total_Possessions,
        )
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
            isHome,
        )
    elif eventOutcome < missed2jfoulCutoff:
        collector.AppendLogic(
            gamestate.PossessingTeam,
            "Mid",
            "Missed Foul",
            s_label,
            d_label,
            eventOutcome,
            made2jCutoff,
            missed2jCutoff,
            blocked2jCutoff,
            missed2jfoulCutoff,
            made2jfoulCutoff,
            gamestate.PossessionNumber,
            gamestate.Total_Possessions,
        )
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
        collector.AppendLogic(
            gamestate.PossessingTeam,
            "Mid",
            "MadeFoul",
            s_label,
            d_label,
            eventOutcome,
            made2jCutoff,
            missed2jCutoff,
            blocked2jCutoff,
            missed2jfoulCutoff,
            made2jfoulCutoff,
            gamestate.PossessionNumber,
            gamestate.Total_Possessions,
        )
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
    else:
        collector.AppendLogic(
            gamestate.PossessingTeam,
            "Mid",
            "Missed",
            s_label,
            d_label,
            eventOutcome,
            made2jCutoff,
            missed2jCutoff,
            blocked2jCutoff,
            missed2jfoulCutoff,
            made2jfoulCutoff,
            gamestate.PossessionNumber,
            gamestate.Total_Possessions,
        )
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
            isHome,
        )


def MadeJumperOutcome(
    gamestate, shooter, defender, team_state, team, receiving_team, isHome, collector
):
    printDefender = GetPlayerLabel(defender)
    printAssister = ""
    gamestate.AddPoints(2, isHome)
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
            printAssister = GetPlayerLabel(assister)
            assister.Stats.AddAssist()
            team.Stats.AddAssist()
    printShooter = GetPlayerLabel(shooter)
    shooter.Stats.AddFieldGoal(True, 2)
    play = GenerateMidShotText(
        printShooter,
        printDefender,
        printAssister,
        "",
        False,
        isHome,
        gamestate.Capacity,
        1,
        gamestate.PossessingTeam,
    )
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
    isHome,
):
    printShooter = GetPlayerLabel(shooter)
    printDefender = GetPlayerLabel(defender)
    shooter.Stats.AddFieldGoal(False, 2)
    team_one.Stats.AddFieldGoal(False)
    rebrand = random.random()
    off_rebounder = GetRebounder(t1State.Roster)
    def_rebounder = GetRebounder(t2State.Roster)
    reb_probability = GetReboundProbability(off_rebounder, def_rebounder)
    play = GenerateMidShotText(
        printShooter,
        printDefender,
        "",
        "",
        False,
        isHome,
        gamestate.Capacity,
        2,
        gamestate.PossessingTeam,
    )
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
    isHome,
):
    printShooter = GetPlayerLabel(shooter)
    shooter.Stats.AddFieldGoal(False, 2)
    team_one.Stats.AddFieldGoal(False)
    defender.Stats.AddBlock()
    team_two.Stats.AddBlocks()
    printBlocker = GetPlayerLabel(defender)
    play = GenerateMidShotText(
        printShooter,
        printBlocker,
        "",
        "",
        False,
        isHome,
        gamestate.Capacity,
        3,
        gamestate.PossessingTeam,
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
    printShooter = GetPlayerLabel(shooter)
    printDefender = GetPlayerLabel(defender)
    fouling_player = GetFouler(t2State.Roster)
    proportions = fouling_player.AddFoul(
        gamestate.IsNBA, gamestate.PossessionNumber, gamestate.Total_Possessions
    )
    print_fouler = GetPlayerLabel(fouling_player)
    if fouling_player.FouledOut:
        t2State.ReloadRoster(fouling_player.ID, fouling_player.TeamID, proportions)
    play = GenerateMidShotText(
        printShooter,
        printDefender,
        "",
        print_fouler,
        fouling_player.FouledOut,
        isHome,
        gamestate.Capacity,
        4,
        gamestate.PossessingTeam,
    )
    collector.AppendPlay(
        gamestate.PossessingTeam,
        play,
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
    printDefender = GetPlayerLabel(defender)
    printAssister = ""
    fouling_player = GetFouler(t2State.Roster)
    proportions = fouling_player.AddFoul(
        gamestate.IsNBA, gamestate.PossessionNumber, gamestate.Total_Possessions
    )
    print_fouler = GetPlayerLabel(fouling_player)
    if fouling_player.FouledOut:
        t2State.ReloadRoster(fouling_player.ID, fouling_player.TeamID, proportions)
    gamestate.AddPoints(2, isHome)

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
            printAssister = GetPlayerLabel(assister)
            assister.Stats.AddAssist()
            team_one.Stats.AddAssist()
            printAssister = GetPlayerLabel(assister)
    printShooter = GetPlayerLabel(shooter)
    shooter.Stats.AddFieldGoal(True, 2)
    play = GenerateMidShotText(
        printShooter,
        printDefender,
        printAssister,
        print_fouler,
        fouling_player.FouledOut,
        isHome,
        gamestate.Capacity,
        5,
        gamestate.PossessingTeam,
    )
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
    ins_base = gamestate.GetShootingBase(3)
    ins_adj = gamestate.GetShootingAdj(3)
    if shooter.FirstName + " " + shooter.LastName == focus_player:
        made2inf = ins_base + (
            ins_adj * ((shooter.Finishing - 4) - defender.InteriorDefense)
        )
    else:
        made2inf = ins_base + (
            ins_adj * ((shooter.Finishing) - defender.InteriorDefense)
        )
    if gamestate.IsNeutral != True and isHome == False:
        made2inf -= gamestate.HCA
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
    s_label = GetPlayerLabel(shooter)
    d_label = GetPlayerLabel(defender)

    if eventOutcome < made2inCutoff:
        collector.AppendLogic(
            gamestate.PossessingTeam,
            "Ins",
            "Made",
            s_label,
            d_label,
            eventOutcome,
            made2inCutoff,
            missed2inCutoff,
            blocked2inCutoff,
            missed2infoulCutoff,
            made2infoulCutoff,
            gamestate.PossessionNumber,
            gamestate.Total_Possessions,
        )
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
        collector.AppendLogic(
            gamestate.PossessingTeam,
            "Ins",
            "Missed",
            s_label,
            d_label,
            eventOutcome,
            made2inCutoff,
            missed2inCutoff,
            blocked2inCutoff,
            missed2infoulCutoff,
            made2infoulCutoff,
            gamestate.PossessionNumber,
            gamestate.Total_Possessions,
        )
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
            isHome,
        )
    elif eventOutcome < blocked2inCutoff:
        collector.AppendLogic(
            gamestate.PossessingTeam,
            "Ins",
            "Blocked",
            s_label,
            d_label,
            eventOutcome,
            made2inCutoff,
            missed2inCutoff,
            blocked2inCutoff,
            missed2infoulCutoff,
            made2infoulCutoff,
            gamestate.PossessionNumber,
            gamestate.Total_Possessions,
        )
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
            isHome,
        )
    elif eventOutcome < missed2infoulCutoff:
        collector.AppendLogic(
            gamestate.PossessingTeam,
            "Ins",
            "Missed Foul",
            s_label,
            d_label,
            eventOutcome,
            made2inCutoff,
            missed2inCutoff,
            blocked2inCutoff,
            missed2infoulCutoff,
            made2infoulCutoff,
            gamestate.PossessionNumber,
            gamestate.Total_Possessions,
        )
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
        collector.AppendLogic(
            gamestate.PossessingTeam,
            "Ins",
            "Made Foul",
            s_label,
            d_label,
            eventOutcome,
            made2inCutoff,
            missed2inCutoff,
            blocked2inCutoff,
            missed2infoulCutoff,
            made2infoulCutoff,
            gamestate.PossessionNumber,
            gamestate.Total_Possessions,
        )
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
    else:
        collector.AppendLogic(
            gamestate.PossessingTeam,
            "Ins",
            "Missed",
            s_label,
            d_label,
            eventOutcome,
            made2inCutoff,
            missed2inCutoff,
            blocked2inCutoff,
            missed2infoulCutoff,
            made2infoulCutoff,
            gamestate.PossessionNumber,
            gamestate.Total_Possessions,
        )
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
            isHome,
        )


def MadeInsideOutcome(
    gamestate, shooter, defender, team_state, team, receiving_team, isHome, collector
):
    printDefender = GetPlayerLabel(defender)
    printAssister = ""
    gamestate.AddPoints(2, isHome)
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
            printAssister = GetPlayerLabel(assister)
            assister.Stats.AddAssist()
            team.Stats.AddAssist()
    printShooter = GetPlayerLabel(shooter)
    shooter.Stats.AddFieldGoal(True, 2)
    play = GenerateInsideShotText(
        printShooter,
        printDefender,
        printAssister,
        "",
        False,
        isHome,
        gamestate.Capacity,
        1,
        gamestate.PossessingTeam,
        receiving_team,
    )
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
    isHome,
):
    printShooter = GetPlayerLabel(shooter)
    printDefender = GetPlayerLabel(defender)
    shooter.Stats.AddFieldGoal(False, 2)
    team_one.Stats.AddFieldGoal(False)
    rebrand = random.random()
    off_rebounder = GetRebounder(t1State.Roster)
    def_rebounder = GetRebounder(t2State.Roster)
    reb_probability = GetReboundProbability(off_rebounder, def_rebounder)
    play = GenerateInsideShotText(
        printShooter,
        printDefender,
        "",
        "",
        False,
        isHome,
        gamestate.Capacity,
        2,
        gamestate.PossessingTeam,
        receiving_team,
    )
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
    isHome,
):
    printShooter = GetPlayerLabel(shooter)
    printDefender = GetPlayerLabel(defender)
    shooter.Stats.AddFieldGoal(False, 2)
    team_one.Stats.AddFieldGoal(False)
    defender.Stats.AddBlock()
    team_two.Stats.AddBlocks()
    play = GenerateInsideShotText(
        printShooter,
        printDefender,
        "",
        "",
        False,
        isHome,
        gamestate.Capacity,
        3,
        gamestate.PossessingTeam,
        receiving_team,
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
    printShooter = GetPlayerLabel(shooter)
    printDefender = GetPlayerLabel(defender)
    fouling_player = GetFouler(t2State.Roster)
    proportions = fouling_player.AddFoul(
        gamestate.IsNBA, gamestate.PossessionNumber, gamestate.Total_Possessions
    )
    print_fouler = GetPlayerLabel(fouling_player)
    if fouling_player.FouledOut:
        t2State.ReloadRoster(fouling_player.ID, fouling_player.TeamID, proportions)
    play = GenerateInsideShotText(
        printShooter,
        printDefender,
        "",
        print_fouler,
        fouling_player.FouledOut,
        isHome,
        gamestate.Capacity,
        4,
        gamestate.PossessingTeam,
        receiving_team,
    )
    collector.AppendPlay(
        gamestate.PossessingTeam,
        play,
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
    printDefender = GetPlayerLabel(defender)
    printAssister = ""
    fouling_player = GetFouler(t2State.Roster)
    proportions = fouling_player.AddFoul(
        gamestate.IsNBA, gamestate.PossessionNumber, gamestate.Total_Possessions
    )
    print_fouler = GetPlayerLabel(fouling_player)
    if fouling_player.FouledOut:
        t2State.ReloadRoster(fouling_player.ID, fouling_player.TeamID, proportions)
    gamestate.AddPoints(2, isHome)
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
            printAssister = GetPlayerLabel(assister)
    printShooter = GetPlayerLabel(shooter)
    shooter.Stats.AddFieldGoal(True, 2)
    play = GenerateInsideShotText(
        printShooter,
        printDefender,
        printAssister,
        print_fouler,
        fouling_player.FouledOut,
        isHome,
        gamestate.Capacity,
        5,
        gamestate.PossessingTeam,
        receiving_team,
    )
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
