import pandas as pd
from SimulationLayer import *
from teamclasses import *
from matchdata import *
import csv
import os

testing = False
cbb_result_list = []
nba_result_list = []
script_dir = os.path.dirname(
    os.path.abspath(__file__)
)  # Get the absolute dir the script is in
os.chdir(script_dir)
nba_match = True
print("Current Directory: ", os.getcwd())
year = "2023"
special_match = "All-Star"
newPath = os.path.normpath(os.path.join(script_dir, "../simulation/BBA/"))
folderPath = "special"
game_data_path = os.path.normpath(
    os.path.join(script_dir, f"./special_game_data/{year}")
)
if not os.path.exists(newPath):
    os.makedirs(newPath)

yearDirectory = os.path.normpath(os.path.join(newPath, folderPath, "Year " + year))
if not os.path.exists(yearDirectory):
    os.makedirs(yearDirectory)
fullDirectory = os.path.normpath(os.path.join(yearDirectory, special_match))
if not os.path.exists(fullDirectory):
    os.makedirs(fullDirectory)
play_by_play_path = os.path.normpath(os.path.join(fullDirectory, "play_by_plays"))
box_score_path = os.path.normpath(os.path.join(fullDirectory, "box_scores"))
if not os.path.exists(play_by_play_path):
    os.makedirs(play_by_play_path)

if not os.path.exists(box_score_path):
    os.makedirs(box_score_path)

## GET GAME DATA
if os.path.exists(game_data_path):
    list_of_games = os.listdir(game_data_path)
    for filename in list_of_games:
        Home = {}
        Away = {}
        HomeCoach = ""
        AwayCoach = ""
        # Gameplan and Bonuses
        t1team_df = {}
        t1FocusPlayer = ""
        t2team_df = {}
        t2FocusPlayer = ""
        t1State = TeamState()
        t2State = TeamState()
        t1rosterRaw_df = []
        t2rosterRaw_df = []

        # Iterate File for Data
        if filename.endswith(".csv"):
            game_file_path = os.path.normpath(os.path.join(game_data_path, filename))
            with open(game_file_path, newline="") as csvfile:
                reader = csv.reader(csvfile, delimiter=",", quotechar="|")
                total_rows = list(reader)
                i = 0
                for row in total_rows:
                    if (
                        row[0] == ""
                        or row[0] == "Home Team"
                        or row[0] == "Away Team"
                        or row[0] == "Team Data"
                        or row[0] == "Roster"
                        or row[0] == "Position"
                    ):
                        i += 1
                        continue
                    if i == 2:
                        Home["ID"] = 2
                        Home["TeamName"] = row[0]
                        Home["Mascot"] = ""
                        Home["Abbr"] = "Western"
                        Home["Conference"] = "Western"
                        HomeCoach = row[1]
                        Home["Coach"] = HomeCoach
                        t1team_df["OffensiveFormation"] = row[2]
                        t1team_df["OffensiveStyle"] = row[3]
                        t1team_df["DefensiveFormation"] = row[4]
                        t1team_df["Pace"] = row[5]
                        t1team_df["Opposing Team"] = row[6]
                        t1FocusPlayer = row[7]
                        i += 1
                    elif i == 19:
                        Away["ID"] = 19
                        Away["TeamName"] = row[0]
                        Away["Mascot"] = ""
                        Away["Abbr"] = "Eastern"
                        Away["Conference"] = "Eastern"
                        AwayCoach = row[1]
                        Away["Coach"] = AwayCoach
                        t2team_df["OffensiveFormation"] = row[2]
                        t2team_df["OffensiveStyle"] = row[3]
                        t2team_df["DefensiveFormation"] = row[4]
                        t2team_df["Pace"] = row[5]
                        t2team_df["Opposing Team"] = row[6]
                        t2FocusPlayer = row[7]
                        i += 1
                    else:
                        i += 1
                        p = {}
                        p["ID"] = i
                        p["Position"] = row[0]
                        full_name = row[1]
                        name_parts = full_name.split()
                        first_name = name_parts[0]
                        last_name = name_parts[-1] if len(name_parts) > 1 else ""
                        p["FirstName"] = first_name
                        p["LastName"] = last_name
                        p["Age"] = row[2]
                        p["Year"] = row[5]
                        p["Height"] = row[3]
                        p["Shooting2"] = int(row[9])
                        p["Shooting3"] = int(row[8])
                        p["Finishing"] = int(row[10])
                        p["FreeThrow"] = int(row[11])
                        p["Ballwork"] = int(row[12])
                        p["Rebounding"] = int(row[13])
                        p["InteriorDefense"] = int(row[14])
                        p["PerimeterDefense"] = int(row[15])
                        p["Stamina"] = int(row[17])
                        p["Minutes"] = int(row[21])
                        p["InsideProportion"] = int(row[18])
                        p["MidRangeProportion"] = int(row[19])
                        p["ThreePointProportion"] = int(row[20])
                        p["Overall"] = int(row[6])
                        p["IsGLeague"] = False
                        p["IsTwoWay"] = False
                        p["IsInternational"] = False
                        p["IsNBA"] = True
                        p["IsGLeague"] = False
                        if i < 18:
                            p["TeamID"] = 2
                            p["TeamAbbr"] = "Western"
                            t1rosterRaw_df.append(p)
                        else:
                            p["TeamID"] = 19
                            p["TeamAbbr"] = "Eastern"
                            t2rosterRaw_df.append(p)

        game = GameState()
        game.SetInitialValues(True, nba_match)
        t1State.SetOffensiveBonuses(t1team_df["OffensiveFormation"])
        t1State.SetDefensiveBonus(t1team_df["DefensiveFormation"])
        t1State.SetDefensiveMaluses(
            t2team_df["DefensiveFormation"],
            t1FocusPlayer,
            t2FocusPlayer,
        )
        t2State.SetOffensiveBonuses(t2team_df["OffensiveFormation"])
        t2State.SetDefensiveBonus(t2team_df["DefensiveFormation"])
        t2State.SetDefensiveMaluses(
            t1team_df["DefensiveFormation"],
            t2FocusPlayer,
            t1FocusPlayer,
        )

        # Rosters
        t1State.SetTeamAttributes(t1rosterRaw_df)
        t2State.SetTeamAttributes(t2rosterRaw_df)
        t1State.SetRoster(game.IsNBA, t1rosterRaw_df, "B")
        t2State.SetRoster(game.IsNBA, t2rosterRaw_df, "B")
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
        t1State.SetPace(t1team_df["Pace"], True)
        t2State.SetPace(t2team_df["Pace"], True)

        game.SetPossessions(t1State.Pace, t2State.Pace)
        team_one = Team(Home)
        team_two = Team(Away)
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

        while game.PossessionNumber <= game.Total_Possessions:
            if game.PossessionNumber == 0 and tipoff_occurred == False:
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
                game.SetGameHCA()
                tipoff_occurred = True
            game.IncrementPossessions()
            possrand = random.random()

            if game.PossessingTeam == h_logo:
                team_one.Stats.AddPossession()

                if possrand < t1State.StealCutoff:
                    StealEvent(
                        game,
                        t2State.Roster,
                        team_one,
                        team_two,
                        a_logo,
                        a_team,
                        collector,
                    )
                elif possrand < t1State.OtherTOCutoff:
                    OtherTurnoverEvent(
                        game, t1State.Roster, team_one, a_logo, a_team, collector
                    )
                elif possrand < t1State.ThreePtAttemptCutoff:
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
                elif possrand < t1State.TwoInsideCutoff:
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
                    StealEvent(
                        game,
                        t1State.Roster,
                        team_two,
                        team_one,
                        h_logo,
                        h_team,
                        collector,
                    )
                elif possrand < t2State.OtherTOCutoff:
                    OtherTurnoverEvent(
                        game, t2State.Roster, team_two, h_logo, h_team, collector
                    )
                elif possrand < t2State.ThreePtAttemptCutoff:
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
                elif possrand < t2State.TwoInsideCutoff:
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
        if not os.path.exists(play_by_play_path):
            os.makedirs(play_by_play_path)

        if not os.path.exists(box_score_path):
            os.makedirs(box_score_path)

        file_name = os.path.normpath(
            play_by_play_path + f"/{h_team}_{a_team}_play_by_play.csv"
        )
        with open(file_name, "w", newline="") as csvfile:
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
                    "SPECIAL",
                    "MADISON SQUARE GARDENS",
                    "NEW YORK",
                    "NY",
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
            box_score_path + "/" + h_team + "_" + a_team + "_box_score.csv"
        )
        with open(file_name, "w", newline="") as csvfile:
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
                ]
            )
            for player in t1State.Roster:
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
                [
                    "Possessions",
                    team_one.Stats.Possessions,
                    team_two.Stats.Possessions,
                ]
            )
            box_score_writer.writerow(["FGM", team_one.Stats.FGM, team_two.Stats.FGM])
            box_score_writer.writerow(["FGA", team_one.Stats.FGA, team_two.Stats.FGA])
            box_score_writer.writerow(
                ["FGPercent", team_one.Stats.FGPercent, team_two.Stats.FGPercent]
            )
            box_score_writer.writerow(
                [
                    "3PM",
                    team_one.Stats.ThreePointsMade,
                    team_two.Stats.ThreePointsMade,
                ]
            )
            box_score_writer.writerow(
                [
                    "3PA",
                    team_one.Stats.ThreePointAttempts,
                    team_two.Stats.ThreePointAttempts,
                ]
            )
            box_score_writer.writerow(
                [
                    "3P%",
                    team_one.Stats.ThreePointPercent,
                    team_two.Stats.ThreePointPercent,
                ]
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
                [
                    "OffRebounds",
                    team_one.Stats.OffRebounds,
                    team_two.Stats.OffRebounds,
                ]
            )
            box_score_writer.writerow(
                [
                    "DefRebounds",
                    team_one.Stats.DefRebounds,
                    team_two.Stats.DefRebounds,
                ]
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
                [
                    "Largest Lead",
                    team_one.Stats.LargestLead,
                    team_two.Stats.LargestLead,
                ]
            )
