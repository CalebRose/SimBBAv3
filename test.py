def generate_round_robin_schedule_odd(teams):
    """Generate a round-robin schedule for an odd number of teams with alternating home and away games."""
    if len(teams) % 2 == 1:
        teams.append("N/A")  # Add a bye team for even number of teams

    num_rounds = len(teams) - 1
    num_matches_per_round = len(teams) // 2

    schedule = []
    for round in range(num_rounds):
        round_matches = []
        for match in range(num_matches_per_round):
            if round % 2 == 0:  # Alternate home and away
                home = teams[match]
                away = teams[-(match + 1)]
            else:
                away = teams[match]
                home = teams[-(match + 1)]

            # Ensure the bye team is always away
            if home == "N/A":
                home, away = away, home

            round_matches.append((home, away))
        teams.insert(1, teams.pop())
        schedule.append(round_matches)

    return schedule


def generate_round_robin_schedule_even(teams):
    """Generate a round-robin schedule for an even number of teams with alternating home and away games."""
    if len(teams) % 2 != 0:
        teams.append("N/A")  # Add a bye team for odd number of teams

    num_rounds = len(teams) - 1
    num_matches_per_round = len(teams) // 2

    schedule = []
    for round in range(2 * num_rounds):  # Double the rounds for home and away
        round_matches = []
        for match in range(num_matches_per_round):
            if round % 2 == 0:  # Alternate home and away for first half
                home = teams[match]
                away = teams[-(match + 1)]
            else:  # Reverse home and away for the second half
                away = teams[match]
                home = teams[-(match + 1)]
            round_matches.append((home, away))
        if round < num_rounds - 1:  # Don't rotate in the last round of the first half
            teams.insert(1, teams.pop())
        schedule.append(round_matches)

    return schedule


# Example usage
teams = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
schedule = generate_round_robin_schedule_odd(teams)

for i, round in enumerate(schedule, 1):
    print(f"Round {i}:")
    for match in round:
        print(f"{match[0]} vs {match[1]}")
    print("")
