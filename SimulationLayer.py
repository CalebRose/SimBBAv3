import random
import math
from baseprobabilities import *
from teamclasses import *
from teamstate import *
from play_by_play_collector import *
from matchdata import *
from bbaevents import *
from gamestate import *
import util
import os
import csv


def rungame(
    gameid,
    awayteam,
    hometeam,
    is_neutral,
    is_nba,
    filePath,
    livestream_channel,
    week,
    matchType,
    match_name,
    arena,
    capacity,
    city,
    state,
):
    load_injury_data = open("injuries.json")
    injury_state = json.load(load_injury_data)
    h = hometeam
    a = awayteam
    game = GameState()
    Neutral = util.GetBooleanValue(is_neutral)
    nba_match = util.GetBooleanValue(is_nba)

    game.SetInitialValues(Neutral, nba_match)

    # Get the Match Data
    match_data = GetMatchData(h, a, game.IsNBA)
    Home = match_data["HomeTeam"]
    Away = match_data["AwayTeam"]

    # Coach Info
    HomeCoach = match_data["HomeTeam"]["Coach"]
    AwayCoach = match_data["AwayTeam"]["Coach"]

    # Gameplan and Bonuses
    t1team_df = match_data["HomeTeamGameplan"]
    t1FocusPlayer = t1team_df["FocusPlayer"]
    t2team_df = match_data["AwayTeamGameplan"]
    t2FocusPlayer = t2team_df["FocusPlayer"]
    t1State = TeamState()
    t2State = TeamState()
    t1State.SetOffensiveBonuses(
        t1team_df["OffensiveFormation"], t1team_df["OffensiveStyle"]
    )
    t1State.SetDefensiveBonus(t1team_df["DefensiveFormation"])
    t1State.SetDefensiveMaluses(
        t2team_df["DefensiveFormation"],
        t1team_df["FocusPlayer"],
        t2team_df["FocusPlayer"],
    )
    t2State.SetOffensiveBonuses(
        t2team_df["OffensiveFormation"], t2team_df["OffensiveStyle"]
    )
    t2State.SetDefensiveBonus(t2team_df["DefensiveFormation"])
    t2State.SetDefensiveMaluses(
        t1team_df["DefensiveFormation"],
        t2team_df["FocusPlayer"],
        t1team_df["FocusPlayer"],
    )

    # Rosters
    t1rosterRaw_df = match_data["HomeTeamRoster"]
    t2rosterRaw_df = match_data["AwayTeamRoster"]
    t1State.SetTeamAttributes(t1rosterRaw_df)
    t2State.SetTeamAttributes(t2rosterRaw_df)
    t1State.SetRoster(game.IsNBA, t1rosterRaw_df, matchType)
    t1State.ReloadRoster(0, 0, {})
    t2State.SetRoster(game.IsNBA, t2rosterRaw_df, matchType)
    t2State.ReloadRoster(0, 0, {})
    t1State.SetDefensiveAttributes()
    t2State.SetDefensiveAttributes()

    t1SortByMinutes = sorted(t1State.Roster, key=lambda x: x.Minutes, reverse=True)
    t1Tip1 = t1SortByMinutes[0:4]
    t1SortByHeight = sorted(t1Tip1, key=lambda x: x.Height, reverse=True)
    t2SortByMinutes = sorted(t2State.Roster, key=lambda x: x.Minutes, reverse=True)
    t2Tip1 = t2SortByMinutes[0:4]
    t2SortByHeight = sorted(t2Tip1, key=lambda x: x.Height, reverse=True)
    t1Tip2 = t1SortByHeight[0]
    t2Tip2 = t2SortByHeight[0]

    t1TipChance = ((t1Tip2.Height - t2Tip2.Height) * 0.01) + 0.5
    t2TipChance = ((t2Tip2.Height - t1Tip2.Height) * 0.01) + 0.5

    t1State.SetHeightDiff(t2State.Height)
    t2State.SetHeightDiff(t1State.Height)
    t1State.SetAdjustedVariables()
    t2State.SetAdjustedVariables()
    t1State.SetDifferences(
        t2State.AdjRebound, t2State.AdjDefense, t2State.DefRateTO, True
    )
    t2State.SetDifferences(
        t1State.AdjRebound, t1State.AdjDefense, t1State.DefRateTO, False
    )
    t1State.SetCutoffs(game.HCA, game.HCAAdj, True)
    t2State.SetCutoffs(game.HCA, game.HCAAdj, False)
    t1State.SetPace(t1team_df["Pace"], nba_match)
    t2State.SetPace(t2team_df["Pace"], nba_match)

    game.SetPossessions(t1State.Pace, t2State.Pace)
    team_one = Team(match_data["HomeTeam"])
    team_two = Team(match_data["AwayTeam"])
    collector = Play_By_Play_Collector()
    h_logo = ""
    a_logo = ""
    h_team = Home["TeamName"]
    a_team = Away["TeamName"]
    if game.IsNBA:
        h_logo = Home["TeamName"] + " " + Home["Mascot"]
        a_logo = Away["TeamName"] + " " + Away["Mascot"]
    else:
        h_logo = Home["Abbr"]
        a_logo = Away["Abbr"]
    tipoff_occurred = False
    print("Starting Game")
    print("Away Team: " + a_team)
    print("Home Team: " + h_team)

    while game.PossessionNumber <= game.Total_Possessions:
        if game.PossessionNumber == 0 and not tipoff_occurred:
            pos = GetTipoffPossession(
                t1TipChance,
                collector,
                t1Tip2,
                t2Tip2,
                h_logo,
                a_logo,
                h_team,
                a_team,
                game.Total_Possessions,
            )
            game.SetPossessingTeam(pos)
            game.SetGameHCA(capacity)
            tipoff_occurred = True
        game.IncrementPossessions()
        possrand = random.random()

        if game.PossessingTeam == h_logo:
            team_one.Stats.AddPossession()

            if possrand < t1State.StealCutoff:
                game.IncrementEventCount("Steal")
                StealEvent(
                    game,
                    t2State.Roster,
                    t1State.Roster,
                    team_one,
                    team_two,
                    a_logo,
                    a_team,
                    collector,
                )
            elif possrand < t1State.OtherTOCutoff:
                game.IncrementEventCount("Turnover")
                OtherTurnoverEvent(
                    game, t1State, t2State, team_one, a_logo, a_team, collector
                )
            elif (
                (game.PossessionNumber == game.Total_Possessions)
                or (game.PossessionNumber == game.Total_Possessions - 1)
                and (game.T2Points - game.T1Points == 3)
            ):
                game.IncrementEventCount("Three")
                ThreePointAttemptEvent(
                    game,
                    t1State,
                    t2State,
                    team_one,
                    team_two,
                    h_team,
                    a_logo,
                    a_team,
                    t2FocusPlayer,
                    True,
                    collector,
                )
            elif possrand < t1State.ThreePtAttemptCutoff:
                game.IncrementEventCount("Three")
                ThreePointAttemptEvent(
                    game,
                    t1State,
                    t2State,
                    team_one,
                    team_two,
                    h_team,
                    a_logo,
                    a_team,
                    t2FocusPlayer,
                    True,
                    collector,
                )
            elif possrand < t1State.TwoJumperCutoff:
                game.IncrementEventCount("Mid")
                JumperAttemptEvent(
                    game,
                    t1State,
                    t2State,
                    team_one,
                    team_two,
                    h_team,
                    a_logo,
                    a_team,
                    t2FocusPlayer,
                    True,
                    collector,
                )
            else:
                game.IncrementEventCount("Inside")
                InsideAttemptEvent(
                    game,
                    t1State,
                    t2State,
                    team_one,
                    team_two,
                    h_team,
                    a_logo,
                    a_team,
                    t2FocusPlayer,
                    True,
                    collector,
                )
        else:
            team_two.Stats.AddPossession()
            if possrand < t2State.StealCutoff:
                game.IncrementEventCount("Steal")
                StealEvent(
                    game,
                    t1State.Roster,
                    t2State.Roster,
                    team_two,
                    team_one,
                    h_logo,
                    h_team,
                    collector,
                )
            elif possrand < t2State.OtherTOCutoff:
                game.IncrementEventCount("Turnover")
                OtherTurnoverEvent(
                    game, t2State, t1State, team_two, h_logo, h_team, collector
                )
            elif (
                (game.PossessionNumber == game.Total_Possessions)
                or (game.PossessionNumber == game.Total_Possessions - 1)
                and (game.T1Points - game.T2Points == 3)
            ):
                game.IncrementEventCount("Three")
                ThreePointAttemptEvent(
                    game,
                    t2State,
                    t1State,
                    team_two,
                    team_one,
                    a_team,
                    h_logo,
                    h_team,
                    t1FocusPlayer,
                    False,
                    collector,
                )
            elif possrand < t2State.ThreePtAttemptCutoff:
                game.IncrementEventCount("Three")
                ThreePointAttemptEvent(
                    game,
                    t2State,
                    t1State,
                    team_two,
                    team_one,
                    a_team,
                    h_logo,
                    h_team,
                    t1FocusPlayer,
                    False,
                    collector,
                )
            elif possrand < t2State.TwoJumperCutoff:
                game.IncrementEventCount("Mid")
                JumperAttemptEvent(
                    game,
                    t2State,
                    t1State,
                    team_two,
                    team_one,
                    a_team,
                    h_logo,
                    h_team,
                    t1FocusPlayer,
                    False,
                    collector,
                )
            else:
                game.IncrementEventCount("Inside")
                InsideAttemptEvent(
                    game,
                    t2State,
                    t1State,
                    team_two,
                    team_one,
                    a_team,
                    h_logo,
                    h_team,
                    t1FocusPlayer,
                    False,
                    collector,
                )

        injury_rand = random.random()
        if injury_rand > injury_cutoff:
            print("AN INJURY HAS OCCURED!")
            HandleInjury(t1State, t2State, injury_state, collector, game)

        # if NBA GAME
        if (
            game.PossessionNumber == math.floor((game.Total_Possessions) / 4)
            and game.IsNBA
        ):
            print("\n")
            print("-----End of the 1st Quarter!-----")
            print("Halftime score")
            print(a_team + ": " + str(game.T2Points))
            print(h_team + ": " + str(game.T1Points))
            msg = ""
            collector.AppendPlay(
                "",
                msg,
                "END OF 1ST QUARTER",
                game.T1Points,
                game.T2Points,
                game.PossessionNumber,
                game.Total_Possessions,
            )
            print("\n")

        if game.PossessionNumber == math.floor((game.Total_Possessions) / 2):
            print("\n")
            print("-----HALFTIME!-----")
            print("Halftime score")
            print(a_team + ": " + str(game.T2Points))
            print(h_team + ": " + str(game.T1Points))
            msg = ""
            collector.AppendPlay(
                "",
                msg,
                "HALFTIME",
                game.T1Points,
                game.T2Points,
                game.PossessionNumber,
                game.Total_Possessions,
            )
            print("\n")

        # if NBA GAME
        if (
            game.PossessionNumber == math.floor((game.Total_Possessions) / 1.5)
            and nba_match
        ):
            print("\n")
            print("-----End of the 3rd Quarter!-----")
            print("Halftime score")
            print(a_team + ": " + str(game.T2Points))
            print(h_team + ": " + str(game.T1Points))
            msg = ""
            collector.AppendPlay(
                "",
                msg,
                "END OF 3rd QUARTER",
                game.T1Points,
                game.T2Points,
                game.PossessionNumber,
                game.Total_Possessions,
            )
            print("\n")

        if (
            game.PossessionNumber >= game.Total_Possessions
            and game.T1Points == game.T2Points
        ):
            print("-----OVERTIME!-----")
            game.SetOvertime
            game.Total_Possessions += math.floor((game.Total_Possessions) / 8)
            msg = "...and we're going to Overtime!"
            collector.AppendPlay(
                "",
                msg,
                "OVERTIME",
                game.T1Points,
                game.T2Points,
                game.PossessionNumber,
                game.Total_Possessions,
            )

    print("\n")
    print("Final Score")
    print(a_team + ": " + str(game.T2Points))
    print(h_team + ": " + str(game.T1Points))
    print("\n")

    msg = "Match Complete"
    collector.AppendPlay(
        "",
        msg,
        "FinalScore",
        game.T1Points,
        game.T2Points,
        game.PossessionNumber,
        game.Total_Possessions,
    )

    folderPath = ""
    if livestream_channel == 1 or livestream_channel == "1":
        folderPath = "cbs"
    elif livestream_channel == 2 or livestream_channel == "2":
        folderPath = "tbs"
    elif livestream_channel == 3 or livestream_channel == "3":
        folderPath = "espn"
    elif livestream_channel == 4 or livestream_channel == "4":
        folderPath = "espn2"
    elif livestream_channel == 5 or livestream_channel == "5":
        folderPath = "tnt"
    elif livestream_channel == 6 or livestream_channel == "6":
        folderPath = "nbatv"
    else:
        folderPath = "int"
    weekDirectory = os.path.normpath(os.path.join(filePath, folderPath, "Week " + week))
    if not os.path.exists(weekDirectory):
        os.makedirs(weekDirectory)
    fullDirectory = os.path.normpath(os.path.join(weekDirectory, matchType))
    if not os.path.exists(fullDirectory):
        os.makedirs(fullDirectory)
    play_by_play_path = os.path.normpath(os.path.join(fullDirectory, "play_by_plays"))
    box_score_path = os.path.normpath(os.path.join(fullDirectory, "box_scores"))
    pbp_logic_path = os.path.normpath(os.path.join(fullDirectory, "logics"))
    if not os.path.exists(play_by_play_path):
        os.makedirs(play_by_play_path)

    if not os.path.exists(box_score_path):
        os.makedirs(box_score_path)

    if not os.path.exists(pbp_logic_path):
        os.makedirs(pbp_logic_path)

    file_name = os.path.normpath(
        play_by_play_path + f"/{gameid}_{h_team}_{a_team}_play_by_play.csv"
    )
    with open(file_name, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "Team",
            "Result",
            "PlayType",
            "TeamOneScore",
            "TeamTwoScore",
            "Possession",
            "Total Possessions",
        ]
        writer = csv.writer(csvfile)
        writer.writerow(
            [
                "HomeTeam",
                "AwayTeam",
                "HomeTeamScore",
                "AwayTeamScore",
                "Total Possessions",
                "Home Coach",
                "HomeOffensiveStyle",
                "HomeOffensiveFormation",
                "HomeDefensiveFormation",
                "HomePace",
                "Away Coach",
                "AwayOffensiveStyle",
                "AwayOffensiveFormation",
                "AwayDefensiveFormation",
                "AwayPace",
                "Match Name",
                "Arena",
                "City",
                "State",
            ]
        )
        writer.writerow(
            [
                h_logo,
                a_logo,
                str(game.T1Points),
                str(game.T2Points),
                str(game.Total_Possessions),
                HomeCoach,
                t1team_df["OffensiveStyle"],
                t1team_df["OffensiveFormation"],
                t1team_df["DefensiveFormation"],
                t1team_df["Pace"],
                AwayCoach,
                t2team_df["OffensiveStyle"],
                t2team_df["OffensiveFormation"],
                t2team_df["DefensiveFormation"],
                t2team_df["Pace"],
                match_name,
                arena,
                city,
                state,
            ]
        )
        writer.writerow([""])
        writer.writerow(fieldnames)
        for x in collector.List:
            writer.writerow(
                [
                    x["Team"],
                    x["Result"],
                    x["PlayType"],
                    x["TeamOneScore"],
                    x["TeamTwoScore"],
                    x["Possession"],
                    x["Total Possessions"],
                ]
            )

    file_name = os.path.normpath(
        box_score_path + "/" + gameid + "_" + h_team + "_" + a_team + "_box_score.csv"
    )
    with open(file_name, "w", newline="", encoding="utf-8") as csvfile:
        box_score_writer = csv.writer(csvfile)
        box_score_writer.writerow(["=====BOX SCORE====="])
        if game.IsNBA == False:
            box_score_writer.writerow(["", "", "1st", "2nd", "OT", "Total"])
            box_score_writer.writerow(
                [
                    team_one.TeamName,
                    team_one.Mascot,
                    str(team_one.Stats.FirstHalfScore),
                    str(team_one.Stats.SecondHalfScore),
                    str(team_one.Stats.OvertimeScore),
                    str(game.T1Points),
                ]
            )
            box_score_writer.writerow(
                [
                    team_two.TeamName,
                    team_two.Mascot,
                    str(team_two.Stats.FirstHalfScore),
                    str(team_two.Stats.SecondHalfScore),
                    str(team_two.Stats.OvertimeScore),
                    str(game.T2Points),
                ]
            )
        else:
            box_score_writer.writerow(
                ["", "", "1st", "2nd", "3rd", "4th", "OT", "Total"]
            )
            box_score_writer.writerow(
                [
                    team_one.TeamName,
                    team_one.Mascot,
                    str(team_one.Stats.FirstHalfScore),
                    str(team_one.Stats.SecondQuarterScore),
                    str(team_one.Stats.SecondHalfScore),
                    str(team_one.Stats.FourthQuarterScore),
                    str(team_one.Stats.OvertimeScore),
                    str(game.T1Points),
                ]
            )
            box_score_writer.writerow(
                [
                    team_two.TeamName,
                    team_two.Mascot,
                    str(team_two.Stats.FirstHalfScore),
                    str(team_two.Stats.SecondQuarterScore),
                    str(team_two.Stats.SecondHalfScore),
                    str(team_two.Stats.FourthQuarterScore),
                    str(team_two.Stats.OvertimeScore),
                    str(game.T2Points),
                ]
            )
        box_score_writer.writerow([""])
        box_score_writer.writerow(["Event Results"])
        box_score_writer.writerow(
            [
                "Threes",
                "ThreesMade",
                "ThreesMissed",
                "ThreesBlocked",
                "ThreesFoulMiss",
                "ThreesFoulMade",
                "Mid",
                "MidMade",
                "MidMissed",
                "MidBlocked",
                "MidFoulMiss",
                "MidFoulMade",
                "Inside",
                "InsideMade",
                "InsideMissed",
                "InsideBlocked",
                "InsideFoulMiss",
                "InsideFoulMade",
                "Turnovers",
                "Steals",
                "OffensiveRebounds",
                "DefensiveRebounds",
            ]
        )
        box_score_writer.writerow(
            [
                str(game.ThreePointEvents),
                str(game.ThreeShotMade),
                str(game.ThreeShotMissed),
                str(game.ThreeShotBlocked),
                str(game.ThreeShotFoulMiss),
                str(game.ThreeShotFoulMade),
                str(game.MidEvents),
                str(game.MidShotMade),
                str(game.MidShotMissed),
                str(game.MidShotBlocked),
                str(game.MidShotFoulMiss),
                str(game.MidShotFoulMade),
                str(game.InsideEvents),
                str(game.InsideShotMade),
                str(game.InsideShotMissed),
                str(game.InsideShotBlocked),
                str(game.InsideShotFoulMiss),
                str(game.InsideShotFoulMade),
                str(game.TurnoverEvents),
                str(game.StealEvents),
                str(game.Offensive_Rebounds),
                str(game.Defensive_Rebounds),
            ]
        )
        box_score_writer.writerow([""])
        box_score_writer.writerow([""])
        box_score_writer.writerow(["=====" + team_one.TeamName + " Players====="])
        box_score_writer.writerow(
            [
                "Player",
                "Minutes",
                "Possessions",
                "FGM",
                "FGA",
                "FG%",
                "3PM",
                "3PA",
                "3P%",
                "FTM",
                "FTA",
                "FT%",
                "Points",
                "Rebounds",
                "Assists",
                "Steals",
                "Blocks",
                "TOs",
                "Fouls",
                "Fouled Out",
                "Injury Status",
            ]
        )
        for player in t1State.Roster:
            i_status = "Healthy"
            f_o_status = "No"
            if player.FouledOut:
                f_o_status = "Yes"

            if player.IsInjured:
                i_status = f"{player.InjuryType} {player.InjuryName} for {player.WeeksOfRecovery} games."
            box_score_writer.writerow(
                [
                    player.FirstName + " " + player.LastName,
                    str(player.Minutes),
                    str(player.Stats.Possessions),
                    str(player.Stats.FGM),
                    str(player.Stats.FGA),
                    str(player.Stats.FGPercent),
                    str(player.Stats.ThreePointsMade),
                    str(player.Stats.ThreePointAttempts),
                    str(player.Stats.ThreePointPercent),
                    str(player.Stats.FTM),
                    str(player.Stats.FTA),
                    str(player.Stats.FTPercent),
                    str(player.Stats.Points),
                    str(player.Stats.TotalRebounds),
                    str(player.Stats.Assists),
                    str(player.Stats.Steals),
                    str(player.Stats.Blocks),
                    str(player.Stats.Turnovers),
                    str(player.Stats.Fouls),
                    f_o_status,
                    i_status,
                ]
            )
        box_score_writer.writerow([""])
        box_score_writer.writerow(["=====" + team_two.TeamName + " Players====="])
        box_score_writer.writerow(
            [
                "Player",
                "Minutes",
                "Possessions",
                "FGM",
                "FGA",
                "FG%",
                "3PM",
                "3PA",
                "3P%",
                "FTM",
                "FTA",
                "FT%",
                "Points",
                "Rebounds",
                "Assists",
                "Steals",
                "Blocks",
                "TOs",
                "Fouls",
            ]
        )
        for player in t2State.Roster:
            i_status = "Healthy"
            f_o_status = "No"
            if player.FouledOut:
                f_o_status = "Yes"

            if player.IsInjured:
                i_status = f"{player.InjuryType} {player.InjuryName} for {player.WeeksOfRecovery} games."
            box_score_writer.writerow(
                [
                    player.FirstName + " " + player.LastName,
                    str(player.Minutes),
                    str(player.Stats.Possessions),
                    str(player.Stats.FGM),
                    str(player.Stats.FGA),
                    str(player.Stats.FGPercent),
                    str(player.Stats.ThreePointsMade),
                    str(player.Stats.ThreePointAttempts),
                    str(player.Stats.ThreePointPercent),
                    str(player.Stats.FTM),
                    str(player.Stats.FTA),
                    str(player.Stats.FTPercent),
                    str(player.Stats.Points),
                    str(player.Stats.TotalRebounds),
                    str(player.Stats.Assists),
                    str(player.Stats.Steals),
                    str(player.Stats.Blocks),
                    str(player.Stats.Turnovers),
                    str(player.Stats.Fouls),
                    f_o_status,
                    i_status,
                ]
            )
        box_score_writer.writerow([""])
        box_score_writer.writerow([""])
        box_score_writer.writerow(["=====TEAM STATS====="])
        box_score_writer.writerow(["Stat", team_one.TeamName, team_two.TeamName])
        box_score_writer.writerow(
            ["Points", team_one.Stats.Points, team_two.Stats.Points]
        )
        box_score_writer.writerow(
            ["Possessions", team_one.Stats.Possessions, team_two.Stats.Possessions]
        )
        box_score_writer.writerow(["FGM", team_one.Stats.FGM, team_two.Stats.FGM])
        box_score_writer.writerow(["FGA", team_one.Stats.FGA, team_two.Stats.FGA])
        box_score_writer.writerow(
            ["FGPercent", team_one.Stats.FGPercent, team_two.Stats.FGPercent]
        )
        box_score_writer.writerow(
            ["3PM", team_one.Stats.ThreePointsMade, team_two.Stats.ThreePointsMade]
        )
        box_score_writer.writerow(
            [
                "3PA",
                team_one.Stats.ThreePointAttempts,
                team_two.Stats.ThreePointAttempts,
            ]
        )
        box_score_writer.writerow(
            ["3P%", team_one.Stats.ThreePointPercent, team_two.Stats.ThreePointPercent]
        )
        box_score_writer.writerow(["FTM", team_one.Stats.FTM, team_two.Stats.FTM])
        box_score_writer.writerow(["FTA", team_one.Stats.FTA, team_two.Stats.FTA])
        box_score_writer.writerow(
            ["FT%", team_one.Stats.FTPercent, team_two.Stats.FTPercent]
        )
        box_score_writer.writerow(
            ["Rebounds", team_one.Stats.Rebounds, team_two.Stats.Rebounds]
        )
        box_score_writer.writerow(
            ["OffRebounds", team_one.Stats.OffRebounds, team_two.Stats.OffRebounds]
        )
        box_score_writer.writerow(
            ["DefRebounds", team_one.Stats.DefRebounds, team_two.Stats.DefRebounds]
        )
        box_score_writer.writerow(
            ["Assists", team_one.Stats.Assists, team_two.Stats.Assists]
        )
        box_score_writer.writerow(
            ["Steals", team_one.Stats.Steals, team_two.Stats.Steals]
        )
        box_score_writer.writerow(
            ["Blocks", team_one.Stats.Blocks, team_two.Stats.Blocks]
        )
        box_score_writer.writerow(
            [
                "Total Turnovers",
                team_one.Stats.TotalTurnovers,
                team_two.Stats.TotalTurnovers,
            ]
        )
        box_score_writer.writerow(
            ["Largest Lead", team_one.Stats.LargestLead, team_two.Stats.LargestLead]
        )

    file_name = os.path.normpath(
        pbp_logic_path + f"/{gameid}_{h_team}_{a_team}_shot_logic.csv"
    )

    with open(file_name, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "Team",
            "PlayType",
            "Outcome",
            "Shooter",
            "Defender",
            "Percentage",
            "Made Cutoff",
            "Missed Cutoff",
            "Blocked Cutoff",
            "Missed Foul Cutoff",
            "Made Foul Cutoff",
            "Possession",
            "Total Possessions",
        ]
        writer = csv.writer(csvfile)
        writer.writerow(
            [
                "HomeTeam",
                "AwayTeam",
                "HomeTeamScore",
                "AwayTeamScore",
                "Total Possessions",
                "Home Coach",
                "HomeOffensiveStyle",
                "HomeOffensiveFormation",
                "HomeDefensiveFormation",
                "HomePace",
                "Away Coach",
                "AwayOffensiveStyle",
                "AwayOffensiveFormation",
                "AwayDefensiveFormation",
                "AwayPace",
                "Match Name",
                "Arena",
                "City",
                "State",
            ]
        )
        writer.writerow(
            [
                h_logo,
                a_logo,
                str(game.T1Points),
                str(game.T2Points),
                str(game.Total_Possessions),
                HomeCoach,
                t1team_df["OffensiveStyle"],
                t1team_df["OffensiveFormation"],
                t1team_df["DefensiveFormation"],
                t1team_df["Pace"],
                AwayCoach,
                t2team_df["OffensiveStyle"],
                t2team_df["OffensiveFormation"],
                t2team_df["DefensiveFormation"],
                t2team_df["Pace"],
                match_name,
                arena,
                city,
                state,
            ]
        )
        writer.writerow([""])
        writer.writerow(fieldnames)
        for x in collector.LogicList:
            writer.writerow(
                [
                    x["Team"],
                    x["PlayType"],
                    x["Outcome"],
                    x["Shooter"],
                    x["Defender"],
                    x["Percentage"],
                    x["Made"],
                    x["Missed"],
                    x["Blocked"],
                    x["MissedFoul"],
                    x["MadeFoul"],
                    x["Possession"],
                    x["Total Possessions"],
                ]
            )

    results = MatchResults(
        team_one, team_two, t1State.Roster, t2State.Roster, gameid, is_nba
    )

    return results
