import random


def GetPossessionText():
    pos_text = [
        "now has the possession",
        "takes over",
        "gains possession",
        "will inbound the ball",
        "gets the ball",
        "will take over",
        "takes possession",
        "has possession",
        "now has possession",
        "now has the ball",
        "takes control",
        "will inbound",
        "will get the ball",
    ]
    return random.choice(pos_text)


def GenerateOutOfBoundsText(
    player, attemptedPassee, defender, possessing_team, receiving_team
):
    pos_text = GetPossessionText()
    text_list = [
        f"{player} lost the ball out of bounds. {receiving_team} {pos_text}.",
        f"A miscommunication between {player} and {attemptedPassee} results in the ball sailing out of bounds. {receiving_team} {pos_text}.",
        f"{defender} puts the pressure on {player}, forcing a turnover as the ball goes out of bounds. {receiving_team} {pos_text}.",
        f"Great defense by {defender}, who forces {player} to throw the ball out of bounds. {receiving_team} {pos_text}.",
        f"{player} loses control of the ball, sending it out of bounds. {receiving_team} {pos_text}.",
        f"{player}'s pass attempt to {attemptedPassee} goes awry under heavy defense from {defender}. The ball is out of bounds, and {pos_text}.",
        f"Under pressure from {defender}, {player} steps out of bounds. Possession goes to {receiving_team}.",
        f"{player} attempts a risky pass to {attemptedPassee}, but the ball goes out of bounds. {receiving_team} {pos_text}.",
        f"{player} couldn't find an open teammate and stepped out of bounds. {receiving_team} {pos_text}.",
        f"{player}'s pass is deflected by {defender}, sending the ball out of bounds. {receiving_team} {pos_text}.",
        f"An overthrown pass from {player} to {attemptedPassee} results in a turnover. {receiving_team} {pos_text}.",
        f"{defender}'s tight coverage forces {player} to lose the ball out of bounds. {receiving_team} {pos_text}.",
        f"{player} loses the handle on the ball, and it goes out of bounds. {receiving_team} {pos_text}.",
        f"{player}'s pass to {attemptedPassee} is off-target, going out of bounds. {receiving_team} {pos_text}.",
        f"Through {defender}'s efforts, {player} accidentally steps out of bounds. {receiving_team} {pos_text}.",
        f"{player} tries to pass under pressure but sends the ball out of bounds. {receiving_team} {pos_text}.",
    ]
    return random.choice(text_list)


def GenerateShotClockViolationText(
    player, assister, defender, possessing_team, receiving_team
):
    pos_text = GetPossessionText()
    text_list = [
        f"{receiving_team}: Shot clock violation on {player}.",
        f"{assister} makes a pass to {player}. Can't seem to find an open lane to the basket, and shot clock goes off! {receiving_team} {pos_text}.",
        f"{defender} covers {player}. {player} cannot seem to get an opening and the shot clock fires! {receiving_team} {pos_text}.",
        f"{player} is caught by the shot clock! {receiving_team} {receiving_team} {pos_text}.",
        f"{player} took too much time and is caught by the shot clock! {receiving_team} {pos_text}.",
        f"{player} takes too long to make a play, resulting in a shot clock violation. {receiving_team} {pos_text}.",
        f"With tight defense from {defender}, {player} couldn't get a shot off in time. {receiving_team} {pos_text}.",
        f"{player} dribbles out the clock, leading to a shot clock violation. {receiving_team} {pos_text}.",
        f"{assister} passes to {player}, but they're unable to beat the shot clock. {receiving_team} {pos_text}.",
        f"{defender}'s defense forces {player} into a shot clock violation. {receiving_team} {pos_text}.",
        f"{player} is caught without an open shot, leading to a shot clock violation. {receiving_team} {pos_text}.",
        f"The shot clock expires on {player} as {defender} prevents any clear attempt. {receiving_team} {pos_text}.",
        f"{player} hesitates too long, resulting in a shot clock violation. {receiving_team} {pos_text}.",
        f"Great defense by {defender} keeps {player} from getting a shot off, and the shot clock buzzes. {receiving_team} {pos_text}.",
        f"{player} fails to get a shot off before the buzzer, and {receiving_team} {pos_text}.",
        f"{player} looks for an opportunity but can't find one, leading to a shot clock violation. {receiving_team} {pos_text}.",
    ]

    return random.choice(text_list)


def GenerateOffensiveFoulText(
    player, assister, defender, possessing_team, receiving_team
):
    pos_text = GetPossessionText()
    dice_roll = random.randint(1, 1000)
    if dice_roll < 1000:
        text_list = [
            f"{receiving_team}: Offensive foul on {player}.",
            f"{player} drives to the basket for the layup and shoves {defender}. Ref has called the foul, and {pos_text}.",
            f"{assister} drives to the basket and a foul is called on {player} for shoving {defender}! {pos_text}.",
            f"{player} charges into {defender}, drawing an offensive foul. {pos_text}.",
            f"{defender} stands firm as {player} barrels through, resulting in an offensive foul on {player}. {pos_text}.",
            f"An illegal screen set by {player} on {defender} results in an offensive foul. {receiving_team} {pos_text}.",
            f"{player} is called for an offensive foul after a push-off against {defender}. {receiving_team} {pos_text}.",
            f"{assister} tries to pass to {player}, but {player} is called for an offensive foul after pushing {defender}. {receiving_team} {pos_text}.",
            f"{player} extends the arm on the drive, drawing an offensive foul on {defender}. {receiving_team} {pos_text}.",
            f"{player} lowers the shoulder and charges into {defender}, resulting in an offensive foul. {receiving_team} {pos_text}.",
            f"A moving screen by {player} on {defender} results in an offensive foul. {receiving_team} {pos_text}.",
            f"{player} makes contact with {defender} while driving to the hoop, resulting in an offensive foul. {receiving_team} {pos_text}.",
            f"{defender} draws an offensive foul on {player} for excessive contact. {receiving_team} {pos_text}.",
            f"{player} tries to clear space but is called for an offensive foul on {defender}. {receiving_team} {pos_text}.",
            f"An off-ball foul by {player} on {defender} gives possession to {receiving_team}.",
        ]
        return random.choice(text_list)
    text_list = [
        f"{assister} drives to the basket and a foul is called on {player} for what appears to be nut-shot on {defender}! {pos_text}.",
        f"{player} runs right over {defender}, drawing what appears to be an egregious offensive foul. {pos_text}.",
        f"{player} is called for an offensive foul after a elbowing {defender} in the face. {pos_text}.",
        f"{player} gets frustrated and purposely throws the ball right at {defender}'s head. Foul has been called. {pos_text}.",
        f"{player} extends the arm on the drive, drawing an offensive foul on {defender}. {pos_text}.",
        f"{player} headbutts {defender} while attempting to screen, resulting in an offensive foul. {pos_text}.",
        f"{player} attempts a screen and accidentally trips {defender}, resulting in an offensive foul. {pos_text}.",
        f"{player} gets frustrated on the screen and deliberately throws {defender}, resulting in an offensive foul. {pos_text}.",
        f"{player} slips with the ball and accidentally strikes {defender} in the groin, resulting in an offensive foul. {pos_text}.",
        f"{player} slips and appears to take {defender} right with him, resulting in an offensive foul. {pos_text}.",
    ]
    return random.choice(text_list)


def GenerateStealBallText(player, defender, possessing_team, receiving_team):
    pos_text = GetPossessionText()
    text_list = [
        f"{defender} steals the ball for {receiving_team}!",
        f"{player} can't get past {defender} and just like that the ball is swiped!",
        f"{player} goes one-on-one with {defender}, attempts to spin with the ball but {defender} nabs the ball!",
        f"A great defensive play by {defender}, who strips the ball from {player}! {receiving_team} {pos_text}.",
        f"{defender} with quick hands, steals the ball from {player}. in transition!",
        f"{player} loses the ball to {defender}, who anticipated the move perfectly. with the steal!",
        f"{defender} pokes the ball away from {player}, and {pos_text}!",
        f"A clean steal by {defender}, taking the ball right out of {player}'s hands! on the break.",
        f"{defender} intercepts the pass intended for {player}, giving the possession!",
        f"Quick reflexes by {defender}, who steals the ball from {player}! {receiving_team} {pos_text}.",
        f"{player} tries to cross over {defender}, but loses the ball. {defender} recovers for {receiving_team}.",
        f"{defender} picks {player}'s pocket clean! {receiving_team} with a chance to score off the turnover.",
        f"{player} mishandles the ball, and {defender} takes advantage, stealing it for {receiving_team}.",
        f"{defender} reads the play perfectly and steals the ball from {player}. {receiving_team} {pos_text}.",
        f"A brilliant steal by {defender}, taking the ball away from {player} and giving an opportunity!",
    ]

    return random.choice(text_list)


def GenerateReboundText(player, receiving_team, is_offense):
    text_list = [
        f" Rebounded by {player}.",
        f" {player} reaches up with the rebound.",
        f" {player} takes possession with the rebound.",
        f" {player} catches the ball on the rebound.",
        f" {player} rebounds the ball.",
        f" {player} wins the fight for the rebound.",
        f" {player} takes the rebound.",
        f" {player} grabs the rebound.",
        f" {player} takes possession of the rebound.",
        f" {player} reaches up for the rebound.",
    ]
    statement = random.choice(text_list)

    if is_offense:
        final_list = [
            f"{receiving_team}'s possession continues. ",
            f"{receiving_team} continues on offense, shot clock closing in. ",
            f"{receiving_team} continues on offense. ",
            f"{receiving_team} continues their possession. ",
            f"{receiving_team} will attempt to score again. ",
            f"{receiving_team} will attempt again. ",
            f"{receiving_team} with another attempt. ",
            f"{receiving_team} with another attempt for the basket. ",
        ]
        off_rebound_statement = random.choice(final_list)
        statement += f" {off_rebound_statement}"

    return statement


def GenerateFreeThrowText(
    shooter, is_home, is_made, possessing_team, receiving_team, capacity, shots
):
    init_list = []
    if is_home:
        init_list = [
            f"The crowd goes silent on the free throw. ",
            f"The crowd is hushing one another as {shooter} prepares for the free throw. ",
            f"The crowd quiets down as {shooter} takes the free throw line. ",
            f"The crowd quiets down as {shooter} heads to the free throw line. ",
            f"The crowd quiets down as {shooter} makes their way to the free throw line. ",
            f"The arena falls silent in anticipation. ",
            f"All eyes are on {shooter} as the crowd hushes. ",
            f"{shooter} steps to the line, and the crowd goes silent. ",
            f"The crowd's buzz fades to a whisper as {shooter} readies for the free throw. ",
            f"A hush falls over the crowd as {shooter} steps up for the free throw. ",
        ]
    else:
        init_list = [
            f"The home crowd is roaring to life! ",
            f"The home crowd is deafening the court! ",
            f"The home crowd is erupting on the free throw! ",
            f"The home crowd is getting loud for the free throw! ",
            f"The home crowd is attempting to distract {shooter} on the free throw! ",
            f"The home fans are making noise to throw off {shooter}. ",
            f"The crowd is booing loudly as {shooter} steps to the line. ",
            f"{shooter} faces a wall of noise from the home crowd. ",
            f"The arena is filled with boos and jeers for {shooter}. ",
            f"The home crowd is doing everything to distract {shooter}. ",
        ]
    text_list = [
        f"{shooter} comes up with the free throw... ",
        f"{shooter} attempts the free throw... ",
        f"{shooter} takes their shot... ",
        f"{shooter} lines up for the free throw... ",
        f"{shooter} shoots the free throw... ",
        f"{shooter} releases the ball... ",
        f"{shooter} makes the free throw attempt... ",
        f"{shooter} goes for the free throw... ",
        f"{shooter} aims for the basket... ",
        f"{shooter} shoots... ",
        f"{shooter} focuses and takes the shot... ",
    ]

    text_choice = random.choice(text_list)

    result_list = []
    if is_made:
        result_list = [
            " and the free throw comes up good!",
            " and the free throw is good!",
            " and it swooshes in!",
            f" and {shooter} makes the basket!",
            f" and {shooter} makes it in!",
            f" and {shooter} gets it in!",
            f" and {shooter} comes up good on the free throw!",
            f" and {shooter} scores!",
            " and he scores!",
            " and it's nothing but net!",
            " and it's a clean shot!",
        ]
    else:
        result_list = [
            f" and it rattles out of the basket. ",
            f" and it rattled out. ",
            f" and it's nothing but air. ",
            f" and it misses the rim. ",
            f" and bounces off the rim.",
            f" and bounces off the backboard onto the court.",
            f" and the shot is off. ",
            f" and the free throw doesn't go in. ",
            f" and the attempt is no good. ",
            f" and the shot misses. ",
        ]

    result_choice = random.choice(result_list)

    end_list = []
    if shots > 1:
        end_list = [f"{shooter} will attempt another shot. "]
    elif shots == 1:
        end_list = [f"{shooter} has one more attempt. "]

    end_choice = random.choice(end_list) if end_list else ""

    statement = ""
    dice_roll = random.randint(1, 24000)
    if dice_roll < capacity:
        init_choice = random.choice(init_list)
        statement += init_choice
    statement += f"{text_choice} {result_choice} {end_choice}"

    return statement


def GenerateHomeCourtText(is_home, capacity, shooter):
    home_court_choice = ""
    hc_dice_roll = random.randint(1, 24000)
    if is_home == False and hc_dice_roll < capacity:
        home_court_list = [
            f"The home crowd roars to life to throw off the opposing team! ",
            f"The home crowd roars to life to throw off {shooter}! ",
            f"The home crowd is getting loud, trying to distract {shooter}. ",
            f"The home fans are making noise to unsettle {shooter}. ",
        ]
        home_court_choice = random.choice(home_court_list)
    return home_court_choice


def GenerateFouledOutText(player, fouled_out):
    if fouled_out == False:
        return ""
    full_list = [
        f" It looks like {player} has accumulated the maximum limit on fouls and cannot play for the remainder of the game.",
        f" And just like that, {player} has reached the maximum count of fouls possible and is leaving courtside.",
        f" The refs are asking {player} to step off the court, as he has now fouled out.",
        f" It appears that {player} has fouled out of the game and is leaving the court.",
    ]

    return random.choice(full_list)


def GenerateInjuryText(player, injury_name, severity):
    full_list = [
        f"Refs have stopped the clock... there appears to be an injury on the play! {player} is heading to the bench for the remainder of the game.",
        f"It looks like a player is down! {player} is walking off the court with what appears to be a {severity} {injury_name}.",
        f"And {player} is down! Refs have stopped the clock and medical staff are escorting {player} off the court. Looks like it's a {injury_name}.",
        f"And {player} is down! The assistant head coach and medical staff are escorting {player} off the court. Looks like it's a {injury_name}.",
        f"The court goes silent as a player cries in pain. {player} is being escorted off the court by medical staff for what appears to be a {severity} {injury_name}",
    ]
    return random.choice(full_list)


def GenerateInsideShotText(
    shooter,
    defender,
    assister,
    fouling_player,
    fouled_out,
    is_home,
    capacity,
    shot_outcome,
    possessing_team,
    receiving_team,
):
    init_list = []
    pass_list = []
    init_choice = ""
    pass_choice = ""
    if len(assister) == 0:
        init_list = [
            f"{shooter} drives the ball up the court. ",
            f"{shooter} brings the ball up for {possessing_team}. ",
            f"{shooter} advances the ball for {possessing_team}. ",
            f"{shooter} takes it up the court for {possessing_team}. ",
            f"{shooter} takes it up the court and goes one on one against {defender}. ",
            f"{shooter} advances, finding pressure from {defender}. ",
            f"{shooter} takes point, finding immediate pressure from {defender}. ",
            f"{shooter} brings the ball up, goes one on one against {defender}. ",
        ]
    elif len(assister) > 0:
        init_list = [
            f"{assister} drives the ball up the court,",
            f"{assister} moves up the court,",
            f"{assister} advances the ball,",
            f"{assister} pushes the pace,",
            f"{assister} takes point,",
        ]
        pass_list = [
            f" tries to drive and is blocked by {defender}. Passes to {shooter} on an opening. ",
            f" finds {shooter} on the low post. ",
            f" dishes it to {shooter}. ",
            f" feeds {shooter} in the paint. ",
            f" feeds {shooter} below the free throw lane. ",
            f" passes to {shooter} amidst pressure by {defender}. ",
            f" finds an open man and passes to {shooter}. ",
            f" can't seem to get passed {defender}, he passes to {shooter} on an opening. ",
            f" quickly passes to {shooter} on an opening. ",
            f" quickly finds {shooter} on the low post. ",
            f" dishes it to {shooter}. ",
            f" quickly passes to {shooter} amidst pressure by {defender}. ",
        ]
        pass_choice = random.choice(pass_list)
    init_choice = random.choice(init_list)
    home_court_choice = GenerateHomeCourtText(is_home, capacity, shooter)

    critical_shot = random.randint(1, 20)
    if critical_shot < 19:
        attempt_list = [
            f"He makes the layup attempt...",
            f"He pump-fakes {defender} and attempts for 2...",
            "Goes in for the layup...",
            f"{shooter} fires it on the inside...",
        ]
    else:
        attempt_list = [
            f"{shooter} drives towards the basket... ",
            f"He drives past the defenders successfully and... ",
            f"{shooter} makes it to the basket... ",
        ]

    attempt_choice = random.choice(attempt_list)
    result_list = []
    dunk_reaction_choice = ""
    dunk_reaction_list = []
    foul_out_text = ""
    critical_shot = random.randint(1, 20)
    # Made shot
    if shot_outcome == 1:
        if critical_shot == 20:
            result_list = [
                " AND BRINGS IT HOME WITH THE DUNK!",
                " AND SLAMS THE RIM ON THE DUNK!",
                " OH!!!!! HE DUNKS IT IN!",
                " OH MY WORD HE DUNKS IT RIGHT IN!",
                f" OH MY WORD HE STUNS WITH A DUNK!",
                f" OH!!! {shooter.upper()} WITH NO REGARD FOR {receiving_team.upper()} ON THE DUNK!",
                f" OH MY GOODNESS WHAT A SLAM DUNK!",
                f" {shooter.upper()} RIGHT IN THE FACE OF {defender.upper()} WITH THE DUNK!",
            ]
            if is_home and random.randint(1, 5) == 5:
                dunk_reaction_list = [
                    " THE CROWD GOES WILD!",
                    " THE ARENA CAN'T GET ENOUGH OF WHAT JUST HAPPENED! ",
                    " THE HOME CROWD CAN'T GET ENOUGH OF WHAT JUST HAPPENED! ",
                    " WHAT A PLAY! ",
                    " OH MAN! ",
                    " DID YOU JUST SEE THAT? ",
                ]
            elif is_home == False and random.randint(1, 5) == 5:
                dunk_reaction_list = [
                    " THE CROWD GOES SILENT!",
                    " THE ARENA CAN'T BELIEVE WHAT JUST HAPPENED! ",
                    " THE HOME CROWD CAN'T BELIEVE WHAT JUST HAPPENED! ",
                    " WHAT A PLAY! ",
                    " OH MAN! ",
                    " OH WOW! ",
                    " I THOUGHT I'VE SEEN IT ALL! ",
                    " DID YOU JUST SEE THAT? ",
                ]
            dunk_reaction_choice = (
                random.choice(dunk_reaction_list) if len(dunk_reaction_list) > 1 else ""
            )
        else:
            result_list = [
                f" and he scores!",
                " and it swishes right in for 2!",
                " and it's good for jumper!",
                " and he nails it!",
                " and it's in for two points!",
                " and he makes it!",
                " and it's bouncing on the rim... it makes it in!",
            ]
    elif shot_outcome == 2:
        if critical_shot == 20:
            result_list = [
                f" and he misses the basket on the dunk!",
                " and it bounces off the rim on the dunk attempt! Embarrassing!",
                " but it bounces right out on the dunk attempt!",
                " and he falls short on the dunk attempt!",
            ]
        else:
            result_list = [
                f" and he misses the basket!",
                " and it bounces off the rim!",
                " but it doesn't go in!",
                " and it falls short!",
                " and it clanks off the iron!",
                " and it bounces hard off the backboard, what a miss!",
            ]
    elif shot_outcome == 3:
        result_list = [
            f" and he is blocked by {defender}!",
            f" but {defender} gets a hand on it!",
            f" and {defender} rejects the shot!",
            f" but {defender} blocks it!",
            f" and it's swatted away by {defender}!",
        ]
    elif shot_outcome == 4:
        result_list = [
            f" and he misses the shot. Whistle is blown! Looks like {fouling_player} has been called for a foul!",
            f" and he's pushed out of the way by {fouling_player}! Foul has been called. ",
            f" but he gets fouled by {fouling_player}! Free throws coming up.",
            f" and the shot doesn't go in, but there's a foul on {fouling_player}!",
            f" and he's fouled by {fouling_player} while shooting! Shot is a miss, {shooter} will now go to the free throw line.",
            f" and {fouling_player} bumps right into him as the shot is made! Foul has been called, and there will be free throws.",
        ]
        foul_out_text = GenerateFouledOutText(fouling_player, fouled_out)
    elif shot_outcome == 5:
        result_list = [
            f" and he makes the shot! But there's a call on the play - looks like {fouling_player} has been called for a foul!",
            f" and it's good! Plus, a foul on {fouling_player}!",
            f" and he scores! And there's a foul on the play by {fouling_player}!",
            f" and he nails the jumper! And a foul is called on {fouling_player}!",
            f" and it's in! And a foul on {fouling_player} as well!",
        ]
        foul_out_text = GenerateFouledOutText(fouling_player, fouled_out)
    result_choice = random.choice(result_list)

    statement = f"{init_choice}{pass_choice}{home_court_choice}{attempt_choice}{result_choice}{dunk_reaction_choice}{foul_out_text}"
    return statement


def GenerateMidShotText(
    shooter,
    defender,
    assister,
    fouling_player,
    fouled_out,
    is_home,
    capacity,
    shot_outcome,
    possessing_team,
):
    init_list = []
    pass_list = []
    init_choice = ""
    pass_choice = ""
    if len(assister) == 0:
        init_list = [
            f"{shooter} drives the ball up the court. ",
            f"{shooter} brings the ball up for {possessing_team}. ",
            f"{shooter} advances the ball for {possessing_team}. ",
            f"{shooter} takes it up the court for {possessing_team}. ",
            f"{shooter} takes it up the court and goes one on one against {defender}. ",
            f"{shooter} advances, finding pressure from {defender}. ",
            f"{shooter} takes point, finding immediate pressure from {defender}. ",
            f"{shooter} brings the ball up, goes one on one against {defender}. ",
        ]
    elif len(assister) > 0:
        init_list = [
            f"{assister} drives the ball up the court, ",
            f"{assister} moves up the court, ",
            f"{assister} advances the ball, ",
            f"{assister} pushes the pace, ",
            f"{assister} takes point, ",
        ]
        pass_list = [
            f" passes to {shooter}. ",
            f" finds {shooter} on the wing. ",
            f" dishes it to {shooter}. ",
            f" feeds {shooter} on the short corner. ",
            f" feeds {shooter} on the elbow. ",
            f" feeds {shooter} on the high post. ",
            f" feeds {shooter} at the top of the key. ",
            f" passes to {shooter} amidst pressure by {defender}. ",
            f" finds an open man and passes to {shooter}. ",
            f" can't seem to get passed {defender}, he passes to {shooter} on an opening. ",
            f" quickly passes to {shooter} on an opening outside the paint. ",
            f" quickly finds {shooter} on the short corner. ",
            f" dishes it to {shooter} outside the paint. ",
            f" quickly passes to {shooter} outside the paint amidst pressure by {defender}. ",
        ]
        pass_choice = random.choice(pass_list)
        # 1 == made shot
        # 2 == Missed shot
        # 3 == blocked shot
        # 4 == Missed shot + foul
        # 5 == Made shot + foul
    init_choice = random.choice(init_list)
    home_court_choice = GenerateHomeCourtText(is_home, capacity, shooter)

    attempt_list = [
        f"He makes the jump attempt...",
        f"He pump-fakes {defender} and attempts for 2...",
        f"He fools {defender} on the fake and attempts for 2...",
        "He shoots for 2...",
        "He attempts a shot at mid range...",
        f"{shooter} pulls up for a jump...",
        f"{shooter} fires it...",
        f"{shooter} launches a jumper...",
        f"{shooter} takes a mid-range shot...",
    ]

    foul_out_text = ""
    attempt_choice = random.choice(attempt_list)
    result_list = []
    # Made shot
    if shot_outcome == 1:
        result_list = [
            f" and he scores!",
            " and it swishes right in for 2!",
            " and it's good for jumper!",
            " and he nails it!",
            " and it's in for two points!",
            " and he makes it!",
            " and it's bouncing on the rim... it makes it in!",
        ]
    elif shot_outcome == 2:
        result_list = [
            f" and he misses the basket!",
            " and it bounces off the rim!",
            " but it doesn't go in!",
            " and it falls short!",
            " and it clanks off the iron!",
            " and it bounces hard off the backboard, what a miss!",
        ]
    elif shot_outcome == 3:
        result_list = [
            f" and he is blocked by {defender}!",
            f" but {defender} gets a hand on it!",
            f" and {defender} rejects the shot!",
            f" but {defender} blocks it!",
            f" and it's swatted away by {defender}!",
        ]
    elif shot_outcome == 4:
        result_list = [
            f" and he misses the shot. Whistle is blown! Looks like {fouling_player} has been called for a foul!",
            f" and he's pushed out of the way by {fouling_player}! Foul has been called. ",
            f" but he gets fouled by {fouling_player}! Free throws coming up.",
            f" and the shot doesn't go in, but there's a foul on {fouling_player}!",
            f" and he's fouled by {fouling_player} while shooting! Shot is a miss, {shooter} will now go to the free throw line.",
            f" and {fouling_player} bumps right into him as the shot is made! Foul has been called, and there will be free throws.",
        ]
        foul_out_text = GenerateFouledOutText(fouling_player, fouled_out)
    elif shot_outcome == 5:
        result_list = [
            f" and he makes the shot! But there's a call on the play - looks like {fouling_player} has been called for a foul!",
            f" and it's good! Plus, a foul on {fouling_player}!",
            f" and he scores! And there's a foul on the play by {fouling_player}!",
            f" and he nails the jumper! And a foul is called on {fouling_player}!",
            f" and it's in! And a foul on {fouling_player} as well!",
        ]
        foul_out_text = GenerateFouledOutText(fouling_player, fouled_out)
    result_choice = random.choice(result_list)

    statement = f"{init_choice}{pass_choice}{home_court_choice}{attempt_choice}{result_choice}{foul_out_text}"
    return statement


def GenerateThreePointText(
    shooter,
    defender,
    assister,
    fouling_player,
    fouled_out,
    is_home,
    capacity,
    shot_outcome,
    possessing_team,
):
    init_list = []
    pass_list = []
    init_choice = ""
    pass_choice = ""
    if len(assister) == 0:
        init_list = [
            f"{shooter} drives the ball up the court. ",
            f"{shooter} brings the ball up for {possessing_team}. ",
            f"{shooter} advances the ball for {possessing_team}. ",
            f"{shooter} takes it up the court for {possessing_team}. ",
            f"{shooter} takes it up the court and goes one on one against {defender}. ",
            f"{shooter} advances, finding pressure from {defender}. ",
            f"{shooter} takes point, finding immediate pressure from {defender}. ",
            f"{shooter} brings the ball up, goes one on one against {defender}. ",
        ]
    elif len(assister) > 0:
        init_list = [
            f"{assister} drives the ball up the court, ",
            f"{assister} moves up the court, ",
            f"{assister} advances the ball, ",
            f"{assister} pushes the pace, ",
            f"{assister} takes point, ",
        ]
        pass_list = [
            f" passes to {shooter}. ",
            f" finds {shooter} on the wing. ",
            f" dishes it to {shooter}. ",
            f" feeds {shooter} on the perimeter. ",
            f" feeds {shooter} on the corner. ",
            f" passes to {shooter} amidst pressure by {defender}. ",
            f" finds an open man and passes to {shooter}. ",
            f" can't seem to get passed {defender}, he passes to {shooter} on an opening. ",
            f" quickly passes to {shooter} on an opening on the corner. ",
            f" quickly finds {shooter} on the perimeter. ",
            f" dishes it to {shooter} on the wing. ",
            f" quickly passes to {shooter} on the perimeter amidst pressure by {defender}. ",
        ]
        pass_choice = random.choice(pass_list)
        # 1 == made shot
        # 2 == Missed shot
        # 3 == blocked shot
        # 4 == Missed shot + foul
        # 5 == Made shot + foul
    init_choice = random.choice(init_list)
    home_court_choice = GenerateHomeCourtText(is_home, capacity, shooter)

    attempt_list = [
        f"He makes the 3-point attempt...",
        f"He pump-fakes {defender} and attempts the 3 pointer...",
        "He shoots for the 3...",
        "He attempts a shot at the 3 point line...",
        f"{shooter} pulls up for a three...",
        f"{shooter} fires from beyond the arc...",
        f"{shooter} launches a 3-pointer...",
        f"{shooter} takes a long-range shot...",
    ]

    foul_out_text = ""
    attempt_choice = random.choice(attempt_list)
    result_list = []
    # Made shot
    if shot_outcome == 1:
        result_list = [
            f" and he scores!",
            " and it swishes right in for 3!",
            " and it's good for three!",
            " and he nails it!",
            " and it's in for three points!",
            " and he makes it!",
            " and it's bouncing on the rim... it makes it in!",
        ]
    elif shot_outcome == 2:
        result_list = [
            f" and he misses the basket!",
            " and it bounces off the rim!",
            " but it doesn't go in!",
            " and it falls short!",
            " and it clanks off the iron!",
            " and it bounces hard off the backboard, what a miss!",
        ]
    elif shot_outcome == 3:
        result_list = [
            f" and he is blocked by {defender}!",
            f" but {defender} gets a hand on it!",
            f" and {defender} rejects the shot!",
            f" but {defender} blocks it!",
            f" and it's swatted away by {defender}!",
        ]
    elif shot_outcome == 4:
        result_list = [
            f" and he misses the shot. Whistle is blown! Looks like {fouling_player} has been called for a foul!",
            f" and he's pushed out of the way by {fouling_player}! Foul has been called. ",
            f" but he gets fouled by {fouling_player}! Free throws coming up.",
            f" and the shot doesn't go in, but there's a foul on {fouling_player}!",
            f" and he's fouled by {fouling_player} while shooting! Shot is a miss, {shooter} will now go to the free throw line.",
            f" and {fouling_player} bumps right into him as the shot is made! Foul has been called, and there will be free throws.",
        ]
        foul_out_text = GenerateFouledOutText(fouling_player, fouled_out)
    elif shot_outcome == 5:
        result_list = [
            f" and he makes the shot! But there's a call on the play - looks like {fouling_player} has been called for a foul!",
            f" and it's good! Plus, a foul on {fouling_player}!",
            f" and he scores! And there's a foul on the play by {fouling_player}!",
            f" and he nails the three! And a foul is called on {fouling_player}!",
            f" and it's in! And a foul on {fouling_player} as well!",
        ]
        foul_out_text = GenerateFouledOutText(fouling_player, fouled_out)
    result_choice = random.choice(result_list)

    statement = f"{init_choice}{pass_choice}{home_court_choice}{attempt_choice}{result_choice}{foul_out_text}"
    return statement
