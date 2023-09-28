import pandas as pd
from SimulationLayer import *
from teamclasses import *
from matchdata import *
import csv
import os


num = input("Which week of Games do you want to run? ")

newPath = "../simulation/BBA/"
if not os.path.exists(newPath):
    os.makedirs(newPath)

cbb_result_list = []
nba_result_list = []
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
        results = rungame(
            row[0], row[1], row[2], row[3], is_nba, newPath, row[5], num, matchType
        )

        if is_nba == 0:
            cbb_result_list.append(results)
        else:
            nba_result_list.append(results)


dto = ImportDTO(cbb_result_list, nba_result_list)
# SendStats(dto)
