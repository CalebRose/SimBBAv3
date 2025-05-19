class Play_By_Play_Collector:
    def __init__(self) -> None:
        self.List = []
        self.LogicList = []

    def AppendPlay(self, team, msg, type, t1Score, t2Score, possessionNum, total):
        play = {
            "Team": team,
            "Result": msg,
            "PlayType": type,
            "TeamOneScore": t1Score,
            "TeamTwoScore": t2Score,
            "Possession": possessionNum,
            "Total Possessions": total,
        }
        self.List.append(play)

    def AppendLogic(
        self,
        team,
        type,
        outcome,
        shooter,
        defender,
        percentage,
        made,
        missed,
        blocked,
        missedFoul,
        madeFoul,
        possessionNum,
        total,
    ):
        play = {
            "Team": team,
            "PlayType": type,
            "Outcome": outcome,
            "Shooter": shooter,
            "Defender": defender,
            "Percentage": percentage,
            "Made": made,
            "Missed": missed,
            "Blocked": blocked,
            "MissedFoul": missedFoul,
            "MadeFoul": madeFoul,
            "Possession": possessionNum,
            "Total Possessions": total,
        }
        self.LogicList.append(play)
