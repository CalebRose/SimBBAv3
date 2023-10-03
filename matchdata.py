import requests
import json

url = "https://simnba.azurewebsites.net/"
# url = "http://localhost:8081/"


def GetMatchesForSimulation():
    res = requests.get(url + "simbba/matches/simulation")
    if res.status_code == 200:
        return res.json()
    return False


def GetMatchData(home, away, is_NBA):
    if is_NBA == False:
        res = requests.get(url + "cbb/match/data/" + home + "/" + away)
        if res.status_code == 200:
            return res.json()
        return False
    else:
        res = requests.get(url + "nba/match/data/" + home + "/" + away)
        if res.status_code == 200:
            return res.json()
        return False


def SendStats(dto):
    obj = json.dumps(dto, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    r = requests.post(url + "admin/results/import/", data=obj)
