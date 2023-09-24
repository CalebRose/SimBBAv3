class Play_By_Play_Collector:
    def __init__(self) -> None:
        self.List = []

    def AppendPlay(self, team, msg, type, t1Score, t2Score, possessionNum, total):
        play = {"Team": team, "Result": msg, "PlayType" : type, "TeamOneScore": t1Score, "TeamTwoScore": t2Score, "Possession": possessionNum, "Total Possessions": total}
        self.List.append(play)