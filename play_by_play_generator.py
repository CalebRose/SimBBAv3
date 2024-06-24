def GeneratePlayByPlayTextForTurnover(
    turnover, player, possessing_team, receiving_team
):
    if turnover == "Out Of Bounds":
        return GenerateOutOfBoundsText(player, possessing_team, receiving_team)
    if turnover == "Shot Clock Violation":
        return GenerateShotClockViolationText(player, possessing_team, receiving_team)
    if turnover == "Offensive Foul":
        return GenerateOffensiveFoulText(player, possessing_team, receiving_team)


def GenerateOutOfBoundsText(player, possessing_team, receiving_team):
    print("TEST")


def GenerateShotClockViolationText(player, possessing_team, receiving_team):
    print("TEST")


def GenerateOffensiveFoulText(player, possessing_team, receiving_team):
    print("TEST")


def GenerateFreeThrowText(shooter, is_made, possessing_team, receiving_team):
    print("TEST")
