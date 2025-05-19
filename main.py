import pandas as pd
from SimulationLayer import *
from teamclasses import *
from matchdata import *
import csv
import os

testing = True
cbb_result_list = []
nba_result_list = []
script_dir = os.path.dirname(
    os.path.abspath(__file__)
)  # Get the absolute dir the script is in
os.chdir(script_dir)
print("Current Directory: ", os.getcwd())
newPath = os.path.normpath(os.path.join(script_dir, "../simulation/BBA/2024"))
if not os.path.exists(newPath):
    os.makedirs(newPath)

if testing == False:
    response = GetMatchesForSimulation()
    matches = response["Matches"]
    week = str(response["Week"])
    match_type = response["MatchType"]
    if matches == False:
        print("COULD NOT GET MATCHES")
    else:
        for match in matches:
            is_nba_match = match["IsNBAMatch"]
            channel = str(match["Channel"])
            match_name = match["MatchName"]
            home_team = match["HomeTeam"]
            away_team = match["AwayTeam"]
            if is_nba_match:
                home_team = str(match["HomeTeamID"])
                away_team = str(match["AwayTeamID"])
            is_neutral = match["IsNeutralSite"]
            match_id = str(match["ID"])
            arena = match["Arena"]
            capacity = match["Capacity"]
            city = match["City"]
            state = match["State"]

            results = rungame(
                match_id,
                away_team,
                home_team,
                is_neutral,
                is_nba_match,
                newPath,
                channel,
                week,
                match_type,
                match_name,
                arena,
                capacity,
                city,
                state,
            )

            if is_nba_match == 0:
                cbb_result_list.append(results)
            else:
                nba_result_list.append(results)

else:
    num = input("Which week of Games do you want to run? ")
    matchType = ""
    with open("NCAA Schedule - Week " + num + ".csv", newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=",", quotechar="|")
        for row in reader:
            if (row[0]) == "Monday":
                matchType = "A"
            elif (row[0]) == "Wednesday":
                matchType = "B"
            elif (row[0]) == "Friday":
                matchType = "C"
            elif (row[0]) == "Saturday":
                matchType = "D"

            if (
                row[0] == "Monday"
                or row[0] == "GameID"
                or row[0] == "Tuesday"
                or row[0] == "Wednesday"
                or row[0] == "Thursday"
                or row[0] == "Friday"
                or row[0] == "Saturday"
                or row[0] == ""
            ):
                continue
            is_nba = row[4]
            capacity = int(row[7])
            results = rungame(
                row[0],
                row[1],
                row[2],
                row[3],
                is_nba,
                newPath,
                row[5],
                num,
                matchType,
                "",
                "",
                capacity,
                "",
                "",
            )

            if is_nba == 0:
                cbb_result_list.append(results)
            else:
                nba_result_list.append(results)


if testing == False and len(matches) > 0:
    dto = ImportDTO(cbb_result_list, nba_result_list)
    SendStats(dto)
