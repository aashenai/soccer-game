import random
import gspread
import math
import time
from oauth2client.service_account import ServiceAccountCredentials


# Reads data from a Google sheet, read the manual (1) to know more
scope = ["https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(
    "C:\\Users\\Anirudh\\PycharmProjects\\soccer\\client_secret.json", scope)
client = gspread.authorize(creds)
sheet = client.open("HPL Season 4").worksheet("Rosters")
sheet2 = client.open("HPL Season 4").worksheet("Database")
sheet3 = client.open("HPL Season 4").worksheet("Injuries and Suspensions")

all_scorers = []
all_assisters = []
all_ratings = []
all_cards = []
all_injuries = []
card_indices = [0]
injury_indices = [0]
teams_map = {"ars": 1, "avl": 2, "bou": 3, "bha": 4, "car": 5, "che": 6, "cry": 7, "eve": 8, "lee": 9, "lei": 10,
                "liv": 11, "mci": 12, "mun": 13, "new": 14, "sou": 15, "tot": 16, "wat": 17, "wba": 18, "whu": 19,
                "wol": 20, "el": 21, "g": 22, "cl": 23, "c": 24, "bc": 25, "juv": 26, "rma": 27, "vil": 28, "bvb": 29,
                "acm": 30}
formations_map = {"4-4-2": [4, 2, 2, 2], "4-3-3": [4, 3, 2, 1], "4-4-2 (D)": [4, 3, 1, 2], "3-4-3": [5, 2, 2, 1],
                  "3-4-1-2": [5, 2, 1, 2], "3-5-2": [5, 3, 0, 2], "5-2-3": [5, 2, 2, 1], "5-3-2": [5, 3, 0, 2],
                  "3-5-1-1": {5, 3, 1, 1}, "5-4-1 (D)": {5, 3, 1, 1}, "5-4-1": {5, 2, 2, 1}}


# Reads player names, FIFA ratings, set piece takers, and tactics from the sheet
def read_players(team):

    fatigue = 0
    b_team = 0
    while team[-1] == '0':
        team = team[:-1]
        fatigue = fatigue + 1
    if team[-1] == '1':
        b_team = 2
        team = team[:-1]

    if teams_map[team] < 21:
        col = (teams_map[team] * 4) - 2
    else:
        col = 82 + (2 * (teams_map[team] - 21))
    count = 0
    formation = [4, 2, 2, 2]
    pk_taker = 10
    fk_taker = 7
    c_taker = 7
    tactics = 0
    ratings = []
    player_names = []
    v1 = sheet.col_values(col + b_team)
    v2 = sheet.col_values(col + b_team + 1)
    team_name = sheet.cell(2, col).value
    r1 = random.randint(1, 6)
    r2 = random.randint(1, 4)
    r3 = random.randint(1, 3)

    while count < 24:
        # The first row is the team name
        if count == 0:
            count = 1
            continue
        # The next 14 rows are player names and ratings
        elif count < 19:
            player_names.append(v1[1 + count])
            ratings.append(int(v2[1 + count]) - fatigue)
        # Followed by number of defenders
        elif count == 19:
            if v1[20] in formations_map:
                formation = formations_map[v1[20]]
            else:
                formation = v1[20].split('-')
            if len(formation) != 4:
                formation.append(formation[2])
                formation[2] = 0
        # Row number of penalty taker
        elif count == 20:
            pk_taker = int(v1[21]) - 3
        # Row number of free kick taker
        elif count == 21:
            fk_taker = int(v1[22]) - 3
        elif count == 22:
            c_taker = int(v2[22]) - 3
        # Tactics
        else:
            tactics = int(v1[23])
        count += 1
    # See manual (2) for order of entering formations

    # Chooses the subs
    player_names.pop(11)
    ratings.pop(11)
    player_names.pop(10 + r1)
    ratings.pop(10 + r1)
    player_names.pop(10 + r2)
    ratings.pop(10 + r2)
    player_names.pop(10 + r3)
    ratings.pop(10 + r3)

    return team_name, formation, pk_taker, fk_taker, c_taker, tactics, ratings, player_names, fatigue


# Gets the scoreline when given the FIFA ratings and tactics
def get_scoreline(home_fifa_ratings, away_fifa_ratings, home_tactics, away_tactics):

    home_total_fifa_rating = int(0)
    away_total_fifa_rating = int(0)

    # Finds the total team rating as the sum of all starter ratings + half the sum of all sub ratings
    for i in range(0, 11):
        home_total_fifa_rating += int(home_fifa_ratings[i])
        away_total_fifa_rating += int(away_fifa_ratings[i])
    for i in range(11, 14):
        home_total_fifa_rating += (int(home_fifa_ratings[i]) // 2)
        away_total_fifa_rating += (int(away_fifa_ratings[i]) // 2)

    # Sets the home advantage
    home_total_fifa_rating += 20
    rnd_t = random.randint(0, 99)
    home_xg = 0
    away_xg = 0
    # Sets tactical advantages, see manual (3) for how tactics work
    if 0 < home_tactics < 4 and 0 < away_tactics < 4:
        home_tactics %= 3
        away_tactics %= 3
        if rnd_t < 20:
            xg = 1
        elif rnd_t < 24:
            xg = 2
        elif rnd_t == 24:
            xg = 3
        else:
            xg = 0
        if home_tactics == 0:
            home_tactics += 3
        if away_tactics == 0:
            away_tactics += 3
        if (home_tactics - away_tactics) % 3 == 1:
            home_total_fifa_rating += 20
            home_xg = xg
        if (home_tactics - away_tactics) % 3 == 2:
            away_total_fifa_rating += 20
            away_xg = xg
    if rnd_t < 33:
        xg = 1
    elif rnd_t < 50:
        xg = 2
    else:
        xg = 0
    if home_tactics == 0:
        home_total_fifa_rating -= 33
        away_xg = xg
    if away_tactics == 0:
        away_total_fifa_rating -= 33
        home_xg = xg

    # Finds the scoreline using the team ratings and probability of each scoreline
    goal_probs = []
    fifa_rating_difference = abs(home_total_fifa_rating - away_total_fifa_rating)
    if fifa_rating_difference < 20:
        goal_probs.append([50, 150, 215, 220, 222, 223])
        goal_probs.append([323, 483, 583, 603, 608, 609])
        goal_probs.append([674, 774, 879, 904, 909, 911])
        goal_probs.append([916, 936, 961, 967, 971, 973])
        goal_probs.append([975, 980, 985, 989, 991, 992])
        goal_probs.append([993, 994, 996, 998, 999, 1000])
    elif fifa_rating_difference < 40:
        goal_probs.append([20, 130, 230, 275, 278, 280])
        goal_probs.append([355, 505, 655, 705, 708, 710])
        goal_probs.append([715, 800, 880, 900, 905, 908])
        goal_probs.append([913, 933, 943, 991, 995, 997])
        goal_probs.append([997, 997, 997, 997, 999, 1000])
        goal_probs.append([1000, 1000, 1000, 1000, 1000, 1000])
    elif fifa_rating_difference < 60:
        goal_probs.append([73, 193, 313, 413, 423, 428])
        goal_probs.append([476, 574, 674, 814, 822, 826])
        goal_probs.append([831, 871, 919, 944, 954, 956])
        goal_probs.append([958, 963, 988, 994, 998, 1000])
        goal_probs.append([1000, 1000, 1000, 1000, 1000, 1000])
        goal_probs.append([1000, 1000, 1000, 1000, 1000, 1000])
    else:
        goal_probs.append([50, 170, 320, 395, 445, 455])
        goal_probs.append([480, 563, 663, 813, 888, 898])
        goal_probs.append([900, 920, 934, 959, 978, 988])
        goal_probs.append([988, 989, 991, 994, 998, 1000])
        goal_probs.append([1000, 1000, 1000, 1000, 1000, 1000])
        goal_probs.append([1000, 1000, 1000, 1000, 1000, 1000])

    # Uses the goal probability matrix to determine home and away goals
    higher_rated_team_goals = 0
    lower_rated_team_goals = 0
    rnd = random.randint(0, 999)
    i = 0
    while i < 6:
        j = 0
        while j < 6:
            if rnd < goal_probs[i][j]:
                higher_rated_team_goals = j
                lower_rated_team_goals = i
                i = 6
                j = 6
            j += 1
        i += 1
    if home_total_fifa_rating >= away_total_fifa_rating:
        home_goals = higher_rated_team_goals
        away_goals = lower_rated_team_goals
    else:
        home_goals = lower_rated_team_goals
        away_goals = higher_rated_team_goals

    # Adds the possibility of thrashings if there is a large difference in quality
    if (home_total_fifa_rating - away_total_fifa_rating) / 12.5 > 12.0:
        rdm = random.randint(0, 1)
        if rdm == 1:
            home_goals += 3
    if (away_total_fifa_rating - home_total_fifa_rating) / 12.5 > 12.0:
        rdm = random.randint(0, 1)
        if rdm == 1:
            away_goals += 3

    # Changes number of goals for bus parking
    random_limit = home_total_fifa_rating + away_total_fifa_rating - 17
    if home_tactics == 4 or away_tactics == 4:
        rdm = random.randint(0, random_limit)
        if rdm < home_total_fifa_rating:
            home_goals -= 2
            if home_goals < 0:
                home_goals = 0
        rdm = random.randint(0, random_limit)
        if rdm < away_total_fifa_rating:
            away_goals -= 2
            if away_goals < 0:
                away_goals = 0

    # Changes number of goals for all out attack
    if home_tactics == 5 or away_tactics == 5:
        rdm = random.randint(0, random_limit)
        if rdm < home_total_fifa_rating:
            home_goals += 2
        rdm = random.randint(0, random_limit)
        if rdm < away_total_fifa_rating:
            away_goals += 2

    return home_goals + home_xg, away_goals + away_xg


# Gets player ratings for a game based on FPL-like formulas
def get_ratings(goal_data, chance_data, num_conceded, formation):

    ratings = []
    fpl_points = []
    num_scored = len(goal_data[0])
    # Highest index of a non-attacking player
    max_mid = 1 + int(formation[0]) + int(formation[1])

    for i in range(0, 14):
        fpl_points.append(0)

    for i in range(0, 14):
        # Deducts FPL points to non-attacking starters for every 2 goals conceded by team
        if i < max_mid:
            fpl_points[i] -= int(num_conceded // 2)
        # Adds FPL points to attacking starters for every 2 goals scored by team
        elif i < 11:
            fpl_points[i] += int(num_scored // 2)

    # Formula for chances
    for i in range(0, len(chance_data[1])):
        if chance_data[1][i] < 3 and chance_data[0][i] < 14:
            fpl_points[chance_data[0][i]] += 1
        elif chance_data[0][i] < 14:
            fpl_points[chance_data[0][i]] -= 1

    # FPL formula for goals, with subs being considered as defenders (def: +6, mid: +5, fwd: +4)
    for i in goal_data[0]:
        if i < max_mid:
            fpl_points[i] += 6
        elif i < max_mid + int(formation[2]) or 10 < i < 14:
            fpl_points[i] += 5
        elif i < 14:
            fpl_points[i] += 4

    # FPL formula for assists (+3)
    for i in goal_data[1]:
        fpl_points[i] += 3

    # FPL formula for clean sheets (+4), but for defenders as well as wing backs and defensive midfielders
    if num_conceded == 0:
        for i in range(0, max_mid):
            fpl_points[i] += 4

    # Deducts FPL points for attacking players if team does not score
    if num_scored == 0:
        for i in range(max_mid, 11):
            fpl_points[i] -= 3

    # Goalkeeper performance points, independent of result
    rnd = random.randint(0, 12)
    fpl_points[0] += (rnd - 5)

    # Outfield player performance points, dependent on result
    for i in range(1, 14):
        rnd = random.randint(0, 7)
        if fpl_points[i] < 8:
            fpl_points[i] += (rnd - 3)
        else:
            fpl_points[i] += (rnd // 2)

    for i in range(0, 14):

        # Converts the FPL points into player ratings by scaling to an appropriate number
        # A different scale is used for negative points, to enable ratings closer to zero and one.
        if fpl_points[i] >= 0:
            fpl_points[i] = int(10 + (2.0 * fpl_points[i] / 3.0))
        else:
            fpl_points[i] = int(10 + (4.0 * fpl_points[i] / 3.0))

        # Final player ratings are a multiple of 0.5
        player_rating = fpl_points[i] / 2.0

        # Adds 1 to winning team ratings and 0.5 to both teams if it's a draw
        if num_scored > num_conceded:
            player_rating += 1
        elif num_scored == num_conceded:
            player_rating += 0.5

        # Restricts ratings from 0 to 10
        if player_rating < 0:
            player_rating = 0.0
        if player_rating > 10:
            player_rating = 10.0

        ratings.append(player_rating)

    return ratings


# Determines scorers, assisters, and minutes. See manual (4)
def determine_goal_data(fifa_ratings, formation, num_scored, c_taker):

    max_def = 1 + int(formation[0])
    max_mid = max_def + int(formation[1])
    max_wing = max_mid + int(formation[2])
    cam = int(formation[2]) % 2

    adj_ratings = [0]
    for i in fifa_ratings[1:max_def]:
        adj_ratings.append(int(i))
    for i in fifa_ratings[max_def:max_mid]:
        adj_ratings.append(int(i))
    if cam == 1:
        adj_ratings.append(6 * fifa_ratings[max_mid])
    for i in fifa_ratings[max_mid + cam:max_wing]:
        adj_ratings.append(8 * int(i))
    for i in fifa_ratings[max_wing:11]:
        adj_ratings.append(10 * int(i))
    for i in fifa_ratings[11:14]:
        adj_ratings.append(int(i))

    prob_bins = [0]
    for i in adj_ratings[1:]:
        prob_bins.append(int(prob_bins[-1]) + int(i))

    goal_data = []
    scorers = []

    for i in range(0, num_scored):
        rnd = random.randint(0, prob_bins[13] - 1)
        j = 0
        while j < 14:
            if rnd < prob_bins[j]:
                rnd_diff = random.randint(0, 20)
                if rnd_diff < 2:
                    scorers.append(14)
                elif rnd_diff == 2:
                    rnd_og = random.randint(0, max_def)
                    scorers.append(16 + int(rnd_og))
                elif rnd_diff == 3:
                    scorers.append(15)
                else:
                    scorers.append(int(j))
                j = 14
            j += 1

    while len(scorers) < num_scored:
        scorers.append(10)
    while len(scorers) > num_scored:
        scorers.pop()

    goal_data.append(scorers)

    adj_ratings = [50]
    for i in fifa_ratings[1:3]:
        if int(formation[0]) % 2 == 1:
            adj_ratings.append(8 * int(i))
        else:
            adj_ratings.append(5 * int(i))
    for i in fifa_ratings[3:max_def]:
        adj_ratings.append(int(i))
    for i in fifa_ratings[max_def:max_mid]:
        adj_ratings.append(3 * int(i))
    if cam == 1:
        adj_ratings.append(10 * int(fifa_ratings[max_mid]))
    for i in fifa_ratings[max_mid + cam:max_wing]:
        adj_ratings.append(8 * int(i))
    for i in fifa_ratings[max_wing:11]:
        adj_ratings.append(6 * int(i))
    for i in fifa_ratings[11:14]:
        adj_ratings.append(int(i))

    prob_bins = [50]
    for i in adj_ratings[1:]:
        prob_bins.append(int(prob_bins[-1]) + int(i))

    assisters = []
    for i in range(0, len(goal_data[0])):
        rnd = random.randint(0, prob_bins[13] - 1)
        j = 0
        rnd_c = random.randint(0, 6)
        if rnd_c == 2:
            assisters.append(int(c_taker))
            headers = [1, 2]
            for k in range(3, int(formation[0]) + 1):
                headers.append(k)
                headers.append(k)
            for k in range(11 - int(formation[3]), 11):
                headers.append(k)
                headers.append(k)
            rnd_h = random.randint(0, len(headers) - 1)
            if rnd_h != c_taker:
                goal_data[0][i] = headers[rnd_h]
            else:
                if c_taker != 10:
                    goal_data[0][i] = 10
                else:
                    goal_data[0][i] = 9
            j = 14
        while j < 14:
            if rnd < prob_bins[j]:
                assisters.append(int(j))
                j = 14
            j += 1

    goal_data.append(assisters)

    minutes = []
    for i in range(0, len(goal_data[0])):
        rnd = random.randint(0, 97) + 1
        if 10 < goal_data[0][i] < 14 or goal_data[1][i] > 10:
            rnd = random.randint(0, 37) + 60
        minutes.append(rnd)

    goal_data.append(minutes)

    if num_scored > 1:
        for i in range(0, len(goal_data[0]) - 1):
            for j in range(0, len(goal_data[0]) - i - 1):
                if goal_data[2][j] > goal_data[2][j + 1]:
                    for k in range(0, 3):
                        goal_data[k][j], goal_data[k][j + 1] = goal_data[k][j + 1], goal_data[k][j]

    return goal_data


# Erases duplicate minutes
def erase_dups(a1, a2):
    all_mins = a1[2] + a2[2]
    mid = len(a1[2])
    s = set(all_mins)
    if len(s) != len(all_mins):
        for i in range(1, len(all_mins) + 1):
            while all_mins.count(all_mins[-i]) > 1:
                all_mins[-i] += 1
    a1[2] = all_mins[0:mid]
    a2[2] = all_mins[mid:]


# Gets best and worst players of a match, based on player ratings
def get_motm_and_dotm(names_1, names_2, ratings_1, ratings_2):

    ratings_data = []
    for i in range(0, 14):
        ratings_data.append((ratings_1[i], names_1[i]))
        ratings_data.append((ratings_2[i], names_2[i]))
    random.shuffle(ratings_data)

    motm = max(ratings_data)
    dotm = min(ratings_data)
    if motm == dotm:
        dotm = min(ratings_data[:-1])

    return motm[1], dotm[1]


# Shows the final result
def show_result(goal_data, player_names, opp_player_names, pk_taker, fk_taker, big):
    goal_string = ""
    for i in range(0, len(goal_data[0])):
        goal_type = ""
        # Penalty
        if goal_data[0][i] == 14:
            goal_data[0][i] = pk_taker
            all_scorers.append(player_names[pk_taker])
            all_assisters.append(".")
            goal_string += (player_names[pk_taker] + " (p, ")
            if random.randint(0, 2) == 1 and big == 0:
                goal_type = " [VAR]"
        # Free kick
        elif goal_data[0][i] == 15:
            goal_data[0][i] = fk_taker
            all_scorers.append(player_names[fk_taker])
            all_assisters.append(".")
            goal_string += (player_names[fk_taker] + " (fk, ")
        # Own goal
        elif goal_data[0][i] > 15:
            goal_string += opp_player_names[goal_data[0][i] - 16]
            all_scorers.append(".")
            all_assisters.append(player_names[goal_data[1][i]])
            goal_string += (" (og), off " + player_names[goal_data[1][i]] + " (")
        else:
            goal_string += player_names[goal_data[0][i]]
            if goal_data[0][i] == goal_data[1][i]:
                goal_string += " ("
                all_scorers.append(player_names[goal_data[0][i]])
                all_assisters.append(".")
            else:
                goal_string += (", a " + player_names[goal_data[1][i]] + " (")
                all_scorers.append(player_names[goal_data[0][i]])
                all_assisters.append(player_names[goal_data[1][i]])
            if random.randint(0, 10) == 2 and big == 0:
                goal_type = " [WONDER GOAL]"
        minute = goal_data[2][i]
        # Sets minute with respect to stoppage time
        if minute <= 45:
            goal_string += (str(minute) + "')" + goal_type + "\n")
        elif minute <= 48:
            goal_string += ("45+" + str(minute - 45) + "')" + goal_type + "\n")
        elif minute <= 93:
            goal_string += (str(minute - 3) + "')" + goal_type + "\n")
        else:
            goal_string += ("90+" + str(minute - 93) + "')" + goal_type + "\n")

    return goal_string


# Determines the different chances created in the game
def determine_chances(fifa_ratings, formation, num_scored):

    max_def = 1 + int(formation[0])
    max_mid = max_def + int(formation[1])

    adj_ratings = [2000]
    for i in fifa_ratings[1:max_def]:
        adj_ratings.append(2 * int(i))
    for i in fifa_ratings[max_def:max_mid]:
        adj_ratings.append(int(i))
    for i in fifa_ratings[max_mid:10]:
        adj_ratings.append(8 * int(i))
    adj_ratings.append(10 * int(fifa_ratings[10]))
    for i in fifa_ratings[11:14]:
        adj_ratings.append(int(i))

    prob_bins = [0]
    for i in adj_ratings[1:]:
        prob_bins.append(int(prob_bins[-1]) + int(i))

    scorers = []

    for i in range(0, num_scored):
        rnd = random.randint(0, prob_bins[13])
        j = 0
        while j < 14:
            if rnd < prob_bins[j]:
                rnd_diff = random.randint(0, 40)
                if rnd_diff < 2:
                    scorers.append(14)
                elif rnd_diff < 4:
                    scorers.append(15)
                else:
                    scorers.append(int(j))
                    j = 14
            j += 1

    return scorers


# Returns commentary about different chances
def commentary(goal_data_1, goal_data_2, ratings_1, ratings_2, formation_1, formation_2):

    rnd_1 = random.randint(0, 169)
    c_1 = int(math.sqrt(rnd_1))
    rnd_2 = random.randint(0, 169)
    c_2 = int(math.sqrt(rnd_2))

    if c_1 < 2:
        c_1 = 0
    else:
        c_1 -= 2
    if 5 <= c_1 <= 7:
        c_1 += 3
    elif 8 <= c_1 <= 10:
        c_1 -= 3

    if c_2 < 2:
        c_2 = 0
    else:
        c_2 -= 2
    if 5 <= c_2 <= 7:
        c_2 += 3
    elif 8 <= c_2 <= 10:
        c_2 -= 3

    goal_data = [goal_data_1, goal_data_2]
    ratings = [ratings_1, ratings_2]
    formations = [formation_1, formation_2]
    chances = [c_1, c_2]
    return_data = [[[], [], []], [[], [], []]]

    for i in range(0, 2):
        for j in goal_data[i][2]:
            rnd_m = random.randint(0, 6)
            if rnd_m == 3:
                rnd_p = random.randint(0, int(formations[(i + 1) % 2][1]))
                return_data[(i + 1) % 2][0].append(rnd_p)
                return_data[(i + 1) % 2][1].append(4)
                return_data[(i + 1) % 2][2].append(j)

    for i in range(0, 2):
        players = determine_chances(ratings[i], formations[i], chances[i])
        minutes = []
        types = []
        chances[i] = len(players)

        for j in range(0, chances[i]):
            minute = random.randint(0, 97) + 1
            g_type = random.randint(0, 5)
            if players[j] == 0:
                g_type = 2
            if g_type == 2:
                players[j] = 0
            if 10 < players[j] < 14 or players[j] > 10:
                minute = random.randint(0, 34) + 64
            minutes.append(minute)
            types.append(g_type)

            if 13 < players[j] < 16:
                rnd_o = random.randint(0, 2)
                if rnd_o == 1:
                    other = (i + 1) % 2
                    return_data[other][0].append(0)
                    return_data[other][1].append(2)
                    return_data[other][2].append(minute)

        return_data[i][0].extend(players)
        return_data[i][1].extend(types)
        return_data[i][2].extend(minutes)

    return return_data


# Converts number coded commentary to strings
def comm_to_string(comm_data, goal_data_1, goal_data_2, player_names_1, player_names_2, pk1, pk2, fk1, fk2, t1, t2):
    comm_mins = []
    player_names = [player_names_1, player_names_2]
    gd = [goal_data_1, goal_data_2]
    takers = [player_names_1[pk1], player_names_2[pk2], player_names_1[fk1], player_names_2[fk2]]
    teams = [t1, t2]
    superlatives = ["Great", "Wonderful", "Brilliant", "Superb", "Unbelievable", "Bad", "Terrible", "Huge", "Stupid",
                    "Shocking"]
    defaults = [" effort by ", " run by ", " save by ", " miss by ", " waste of possession by ", " miss by "]

    for i in range(0, 2):
        for j in range(0, len(comm_data[i][2])):
            comm_string = teams[i] + ", "
            minute = comm_data[i][2][j]
            if minute <= 45:
                comm_string += (str(minute) + "': ")
            elif minute <= 48:
                comm_string += ("45+" + str(minute - 45) + "': ")
            elif minute <= 93:
                comm_string += (str(minute - 3) + "': ")
            else:
                comm_string += ("90+" + str(minute - 93) + "': ")

            rnd_s = random.randint(0, 4)
            priority = 0
            if comm_data[i][1][j] > 5:
                comm_data[i][1][j] = 4
            if comm_data[i][0][j] < 14:
                comm_string += superlatives[((comm_data[i][1][j] // 3) * 5) + rnd_s] + defaults[comm_data[i][1][j]]
                comm_string += player_names[i][comm_data[i][0][j]]
            elif comm_data[i][0][j] == 14:
                r = random.randint(0, 3)
                if r == 1:
                    comm_string += "Penalty missed by " + takers[i]
                else:
                    comm_string += "Free kick missed by " + takers[2 + i]
                priority = 0.5
            else:
                comm_string += "Free kick missed by " + takers[2 + i]
                priority = 0.5
            comm_string += "!"
            comm_mins.append([comm_string, priority + comm_data[i][2][j]])

        for j in range(0, len(gd[i][0])):
            comm_string = teams[i] + ", "
            minute = gd[i][2][j]
            if minute <= 45:
                comm_string += (str(minute) + "': ")
            elif minute <= 48:
                comm_string += ("45+" + str(minute - 45) + "': ")
            elif minute <= 93:
                comm_string += (str(minute - 3) + "': ")
            else:
                comm_string += ("90+" + str(minute - 93) + "': ")

            if gd[i][0][j] < 14:
                goal_compliments = ["BANGER! ", "SCREAMER! ", "STUNNER! ", "YOU BEAUTY! ", "GOLAZO! "]
                rnd_s = random.randint(0, 50)
                if rnd_s < 5:
                    comm_string += goal_compliments[rnd_s]
                comm_string += ("GOAL by " + player_names[i][gd[i][0][j]])
                if gd[i][0][j] != gd[i][1][j]:
                    comm_string += (", assisted by " + player_names[i][gd[i][1][j]])

            elif gd[i][0][j] == 14:
                comm_string += ("GOAL! Penalty scored by " + takers[i])
                rnd_v = random.randint(0, 2)
                if rnd_v == 1:
                    comm_string += ", rewarded by VAR"
            elif gd[i][0][j] == 15:
                comm_string += ("GOAL! Free kick scored by " + takers[2 + i])
            else:
                comm_string += ("OWN GOAL by " + player_names[(i + 1) % 2][gd[i][0][j] - 16] + ", off " +
                                player_names[i][gd[i][1][j]])
            comm_string += "!"
            comm_mins.append([comm_string, gd[i][2][j]])
    if len(comm_mins) > 1:
        for i in range(0, len(comm_mins) - 1):
            for j in range(0, len(comm_mins) - i - 1):
                if comm_mins[j][1] > comm_mins[j + 1][1]:
                    for k in range(0, 2):
                        comm_mins[j][k], comm_mins[j + 1][k] = comm_mins[j + 1][k], comm_mins[j][k]

    for i in comm_mins:
        print(i[0])
    print("\n")


# Simulates a random penalty shootout
def penalties():

    home_score = 0
    away_score = 0
    home_left = 5
    away_left = 5

    # 4/5 chance of scoring in regular penalties
    while away_left > 0:
        rnd = random.randint(0, 5)
        if rnd != 4:
            home_score += 1
        home_left -= 1

        # If it is not possible for away to come back
        if home_score > away_score + away_left:
            return home_score, away_score
        # If it is not possible for home to come back
        if away_score > home_score + home_left:
            return home_score, away_score

        rnd = random.randint(0, 5)
        if rnd != 4:
            away_score += 1
        away_left -= 1

        # If it is not possible for away to come back
        if home_score > away_score + away_left:
            return home_score, away_score
        # If it is not possible for home to come back
        if away_score > home_score + home_left:
            return home_score, away_score

    # Sudden death: 2/3 chance of scoring
    while 0 == 0:
        rnd_1 = random.randint(0, 3)
        rnd_2 = random.randint(0, 3)
        if rnd_1 != 2:
            home_score += 1
        if rnd_2 != 2:
            away_score += 1
        # Stops once one team scores and the other team misses
        if home_score != away_score:
            return home_score, away_score


# Generates yellow and red cards
def cards(players, formation):
    yellows = []
    reds = []
    yellow_chances = [0.02]
    red_chances = [0.002]
    for i in range(1, int(formation[0]) + 1):
        yellow_chances.append(0.05)
        red_chances.append(0.005)
    for i in range(int(formation[0]) + 1, int(formation[0]) + int(formation[1]) + 1):
        yellow_chances.append(0.06)
        red_chances.append(0.01)
    for i in range(int(formation[0]) + int(formation[1]) + 1, 11):
        yellow_chances.append(0.02)
        red_chances.append(0.004)
    for i in range(11, 14):
        yellow_chances.append(0.01)
        red_chances.append(0.001)
    for i in range(0, 14):
        rnd_c = random.randint(0, 999) / 1000
        if rnd_c < red_chances[i]:
            reds.append(players[i])
        elif rnd_c < yellow_chances[i]:
            yellows.append(players[i])
    if len(reds) > 4:
        yellows.extend(reds[4:])
        reds = reds[:4]
    susp = []
    for red in reds:
        rnd_s = random.randint(0, 2)
        if rnd_s > 0:
            susp.append(1)
        else:
            susp.append(3)
    return yellows, reds, susp


# Generates injuries
def injuries(players, fatigue):
    injured = []
    for player in players[:11]:
        rnd_i = random.randint(0, 999) / 1000
        if rnd_i < (fatigue + 1) * 0.002:
            rnd_l = random.randint(10, 17)
        elif rnd_i < (fatigue + 1) * 0.006:
            rnd_l = random.randint(5, 9)
        elif rnd_i < (fatigue + 1) * 0.013:
            rnd_l = random.randint(1, 4)
        else:
            rnd_l = 0
        if rnd_l != 0:
            injured.append((player, rnd_l))
    return injured


# Checks if a team has injured or suspended players
def check_for_injuries(team_name, players):
    out_list = sheet3.col_values(1)
    yellow_list = sheet3.col_values(10)
    if str(5) in yellow_list or 5 in yellow_list:
        print("Suspensions")
        exit(0)
    out = []
    rows = []
    for ele in out_list:
        if ele != '':
            out_info = ele.split(';')
            out.append(out_info)
            if out_info[0] in players:
                print("Ineligible")
                print(out_info[0])
                exit(0)
    for i in range(1, len(out) + 1):
        if out[i - 1][2] == str(-1):
            print("There are eligible players")
            exit(0)
        elif out[i - 1][1] == team_name.upper():
            out[i - 1][2] = str(int(out[i - 1][2]) - 1)
            rows.append(i)
    for i in range(0, len(rows)):
        return_st = str(out[rows[i] - 1][0]) + ";" + str(out[rows[i] - 1][1]) + ";" + str(out[rows[i] - 1][2]) + ";" + str(out[rows[i] - 1][3])
        sheet3.update_cell(rows[i], 1, return_st)


# Updates yellow cards in the spreadsheet
def update_ycs(yellows, team):
    yellow_list = sheet3.col_values(7)
    w = len(yellow_list) + 1
    s = []
    t = []
    u = []
    m = []
    for i in range(0, len(yellow_list)):
        k = yellow_list[i].split(';')
        s.append(k[0])
        t.append(k[1])
        u.append(int(k[2]) + 1)
        m.append(i + 1)
    for y in yellows:
        if y in s:
            index = s.index(y)
            row = m[index]
            return_st = str(y) + ";" + str(t[index]) + ";" + str(u[index])
            sheet3.update_cell(row, 7, return_st)
        else:
            return_st = str(y) + ";" + str(team) + ";" + str(1)
            sheet3.update_cell(w, 7, return_st)
            w += 1


# Generates cards and injuries for a game
def add_injuries(players_1, players_2, formation_1, formation_2, fatigue_1, fatigue_2):
    all_cards_1 = cards(players_1, formation_1)
    all_injuries_1 = injuries(players_1, fatigue_1)
    all_cards_2 = cards(players_2, formation_2)
    all_injuries_2 = injuries(players_2, fatigue_2)
    return all_cards_1, all_cards_2, all_injuries_1, all_injuries_2


# Writes injuries and red cards on spreadsheet
def write_injuries(team, the_cards, the_injuries):
    v4 = sheet3.col_values(1)
    k = len(v4) + 1
    for i in range(0, len(the_cards[1])):
        return_st = str(the_cards[1][i]) + ";" + str(team) + ";" + str(the_cards[2][i]) + ";Red card"
        sheet3.update_cell(k, 1, return_st)
        k += 1
    for i in range(0, len(the_injuries)):
        return_st = str(the_injuries[i][0]) + ";" + str(team) + ";" + str(the_injuries[i][1]) + ";Injury"
        sheet3.update_cell(k, 1, return_st)
        k += 1


# Plays a game
# team_1 and team_2 should be the same as in the map in line 19
# cup = 1 for one legged knockout games or finals, cup = 0 otherwise
def play(team_1, team_2, cup, big, read, leg_2=0, home=0, away=0):

    # Sets the team details
    if read == 0:
        home_name, home_formation, home_pk_taker, home_fk_taker, home_c_taker, home_tactics, home_fifa_ratings, \
            home_player_names, home_fatigue = read_players(team_1)
        away_name, away_formation, away_pk_taker, away_fk_taker, away_c_taker, away_tactics, away_fifa_ratings, \
            away_player_names, away_fatigue = read_players(team_2)
    else:
        home_name, home_formation, home_pk_taker, home_fk_taker, home_c_taker, home_tactics, home_fifa_ratings, \
            home_player_names, home_fatigue = (team_1[i] for i in range(0, 8))
        away_name, away_formation, away_pk_taker, away_fk_taker, away_c_taker, away_tactics, away_fifa_ratings, \
            away_player_names, away_fatigue = (team_2[i] for i in range(0, 8))

    check_for_injuries(strip(team_1).upper(), home_player_names)
    check_for_injuries(strip(team_2).upper(), away_player_names)

    # Gets the score
    home_goals, away_goals = get_scoreline(home_fifa_ratings, away_fifa_ratings, home_tactics, away_tactics)

    # Gets the scorers, assisters, and minutes
    home_goal_data = determine_goal_data(home_fifa_ratings, home_formation, home_goals, home_c_taker)
    away_goal_data = determine_goal_data(away_fifa_ratings, away_formation, away_goals, away_c_taker)
    erase_dups(home_goal_data, away_goal_data)

    # Gets the commentary
    comm_data = commentary(home_goal_data, away_goal_data, home_fifa_ratings, away_fifa_ratings, home_formation,
                           away_formation)
    if big == 1:
        comm_to_string(comm_data, home_goal_data, away_goal_data, home_player_names, away_player_names, home_pk_taker,
                    away_pk_taker, home_fk_taker, away_fk_taker, home_name, away_name)

    # Simulates a penalty shootout if it is a cup game
    pen_score = ""
    if cup == 1 and home_goals == away_goals:
        home_pens, away_pens = penalties()
        pen_score = "(" + str(home_pens) + "-" + str(away_pens) + " p) "

    # Does required calculations for second leg
    final_line = ""
    if leg_2 == 1:
        home_tot = int(home) + home_goals
        away_tot = int(away) + away_goals
        final_line += home_name + " " + str(home_tot) + "-" + str(away_tot) + " " + away_name + " on aggregate\n"
        if home_tot == away_tot:
            if int(home) != away_goals:
                if int(home) > away_goals:
                    final_line += home_name
                else:
                    final_line += away_name
                final_line += " go through on away goals\n"
            else:
                home_pens, away_pens = penalties()
                fp = max(home_pens, away_pens)
                sp = min(home_pens, away_pens)
                if home_pens > away_pens:
                    final_line += home_name
                else:
                    final_line += away_name
                final_line += " win " + str(fp) + "-" + str(sp) + " on penalties\n" + "\n"

    # Shows the result
    result = home_name + " " + str(home_goals) + "-" + str(away_goals) + " " + pen_score + away_name + "\n" + "\n"
    result += (show_result(home_goal_data, home_player_names, away_player_names, home_pk_taker, home_fk_taker, big))
    if home_goals != 0:
        result += "\n"
    result += (show_result(away_goal_data, away_player_names, home_player_names, away_pk_taker, away_fk_taker, big))
    if away_goals != 0:
        result += "\n"
    result += final_line

    # Gets the player ratings
    home_player_ratings = get_ratings(home_goal_data, comm_data[0], away_goals, home_formation)
    away_player_ratings = get_ratings(away_goal_data, comm_data[1], home_goals, away_formation)

    if read == 0:
        while team_1[-1] == '0' or team_1[-1] == '1':
            team_1 = team_1[:-1]
        while team_2[-1] == '0' or team_2[-1] == '1':
            team_2 = team_2[:-1]
        s = ""
        for i in range(0, 14):
            if teams_map[team_1] <= 20:
                s += (str(home_player_names[i]) + ";" + str(home_player_ratings[i]) + ";")
            if teams_map[team_2] <= 20:
                s += (str(away_player_names[i]) + ";" + str(away_player_ratings[i]) + ";")
            if i % 2 != 0:
                all_ratings.append(s[:-1])
                s = ""

    # Shows the player ratings
    if big == 1:
        for i in range(0, 14):
            result += (str.ljust(home_player_names[i] + ": " + str(round(home_player_ratings[i], 1)), 25) +
                       str.ljust(away_player_names[i] + ": " + str(round(away_player_ratings[i], 1)), 25) + "\n")

    team_1 = strip(team_1)
    team_2 = strip(team_2)

    cards_1, cards_2, injuries_1, injuries_2 = add_injuries(home_player_names, away_player_names, home_formation, away_formation, home_fatigue,  away_fatigue)
    if len(cards_1[0]) > 0 or len(cards_2[0]) > 0:
        result += "Yellows: "
        for i in cards_1[0]:
            result += i + " (" + team_1.upper() + "), "
        for i in cards_2[0]:
            result += i + " (" + team_2.upper() + "), "
        result = result[:-2]
        result += "\n"
    if len(cards_1[1]) > 0 or len(cards_2[1]) > 0:
        result += "Reds: "
        for i in cards_1[1]:
            result += i + " (" + team_1.upper() + "), "
        for i in cards_2[1]:
            result += i + " (" + team_2.upper() + "), "
        result = result[:-2]
        result += "\n"
    if len(injuries_1) > 0 or len(injuries_2) > 0:
        result += "Injuries: "
        for i in injuries_1:
            result += i[0] + " (" + team_1.upper() + "), "
        for i in injuries_2:
            result += i[0] + " (" + team_2.upper() + "), "
        result = result[:-2]
        result += "\n"
    result += "\n"

    # Gets the best and worst players
    motm, dotm = get_motm_and_dotm(home_player_names, away_player_names, home_player_ratings, away_player_ratings)

    # Shows the best and worst players
    if big == 1:
        result += ("Man of the match: " + motm + "\nDonkey of the match: " + dotm + "\n\n")

    return result, home_goal_data, away_goal_data, home_player_names, away_player_names, home_player_ratings, \
        away_player_ratings, motm, dotm, [cards_1, cards_2], [injuries_1, injuries_2]


# Returns a set of fixtures for a double round-robin league (i.e. PL, CL group)
# See manual (5) for how to edit
# Taken from like the fifth reply somewhere on Stack Overflow
def fixtures(teams):
    n = len(teams)
    matches = []
    all_fixtures = []
    return_matches = []
    for fixture in range(1, n):
        for i in range(n // 2):
            matches.append((teams[i], teams[n - 1 - i]))
            return_matches.append((teams[n - 1 - i], teams[i]))
        teams.insert(1, teams.pop())
        all_fixtures.insert(len(all_fixtures) // 2, matches)
        all_fixtures.append(return_matches)
        matches = []
        return_matches = []
    return all_fixtures


def strip(a_string):
    a_copy = a_string
    while a_copy[-1] == '0' or a_copy[-1] == '1':
        a_copy = a_copy[:-1]
    return a_copy


# Plays a league, uses the fixtures generated by the above function
def play_league(team_list):

    # Does not work for an odd number of teams
    if len(team_list) % 2 != 0:
        exit(2)

    # Sets fixtures
    matches = fixtures(team_list)
    table = {}
    team_data = {}
    team_info = {}

    # Reads team names for the table and player names for leaderboard
    # Will not work if multiple teams or players have the same name
    for team in team_list:
        team_info[team] = read_players(team)
        table[team] = [team_info[team][0], 0, 0, 0, 0, 0, 0, 0, 0]
        player_data = []
        for name in team_info[team][-1]:
            player_data.append([name, 0, 0, 0.0])
        team_data[team] = player_data

    count = 1
    for gameweek in matches:
        print("Gameweek " + str(int(count)))
        count += 1
        for game in gameweek:
            print(game[0] + " vs " + game[1])
            result, hgd, agd, _, _, hpr, apr, _, _, _, _ = play(team_info[game[0]], team_info[game[1]], 0, 0, 1)
            print(result)
            hg = len(hgd[0])
            ag = len(agd[0])

            # Sets wins, draws, and losses columns of table
            if hg > ag:
                table[game[0]][2] += 1
                table[game[1]][4] += 1
            elif ag > hg:
                table[game[1]][2] += 1
                table[game[0]][4] += 1
            else:
                table[game[0]][3] += 1
                table[game[1]][3] += 1

            # Sets goals for and goals against columns of table
            table[game[0]][6] += hg
            table[game[1]][7] += hg
            table[game[0]][7] += ag
            table[game[1]][6] += ag

            # Sets games played, points, and GD columns of table
            for team in game:
                table[team][1] += 1
                table[team][5] = (3 * table[team][2]) + table[team][3]
                table[team][8] = table[team][6] - table[team][7]

            # Updates scorers in the leaderboard
            for i in range(0, len(hgd[0])):
                if hgd[0][i] < 14:
                    scorer = hgd[0][i]
                    team_data[game[0]][scorer][1] += 1
            for i in range(0, len(agd[0])):
                if agd[0][i] < 14:
                    scorer = agd[0][i]
                    team_data[game[1]][scorer][1] += 1

            # Updates assisters in the leaderboard
            for i in range(0, len(hgd[0])):
                assister = hgd[1][i]
                team_data[game[0]][assister][2] += 1
            for i in range(0, len(agd[0])):
                if agd[0][i] < 14:
                    assister = agd[1][i]
                    team_data[game[1]][assister][2] += 1

            # Updates player ratings in the leaderboard
            for i in range(0, 14):
                team_data[game[0]][i][3] += hpr[i]
                team_data[game[1]][i][3] += apr[i]

    # Initializes final table
    final_table = []
    for key in table:
        final_table.append(table[key])

    # Sorts final table
    for i in range(0, len(final_table) - 1):
        for j in range(0, len(final_table) - i - 1):
            if final_table[j][5] < final_table[j + 1][5]:
                final_table[j], final_table[j + 1] = final_table[j + 1], final_table[j]
            # Accounts for when points are same, see manual (6) to customize
            elif final_table[j][5] == final_table[j + 1][5]:
                if final_table[j][8] < final_table[j + 1][8]:
                    final_table[j], final_table[j + 1] = final_table[j + 1], final_table[j]
                elif final_table[j][8] == final_table[j + 1][8]:
                    if final_table[j][6] < final_table[j + 1][6]:
                        final_table[j], final_table[j + 1] = final_table[j + 1], final_table[j]

    # Shows final table headers
    print("{:<25}".format("TEAM") + "{:>4}".format("P") + "{:>4}".format("W") + "{:>4}".format("D") +
          "{:>4}".format("L") + "{:>4}".format("Pts") + "{:>4}".format("GF") + "{:>4}".format("GA") +
          "{:>4}".format("GD"))

    # Shows final table
    for i in final_table:
        print("{:<25}".format(i[0]) + "{:>4}".format(i[1]) + "{:>4}".format(i[2]) + "{:>4}".format(i[3]) +
              "{:>4}".format(i[4]) + "{:>4}".format(i[5]) + "{:>4}".format(i[6]) + "{:>4}".format(i[7]) +
              "{:>4}".format(i[8]))

    # Sets scorers, assisters, and ratings, see manual (7) to customize
    high_scores = []
    high_assists = []
    ratings = []
    for key in team_data:
        for player in team_data[key]:
            if player[1] > 0:
                high_scores.append((player[1], player[0]))
            if player[2] > 0:
                high_assists.append((player[2], player[0]))
            ratings.append((round(player[3] / (2 * (len(team_list) - 1)), 1), player[0]))

    high_scores.sort(reverse=True)
    high_assists.sort(reverse=True)
    ratings.sort(reverse=True)

    print("\nHIGH SCORERS")
    for score in high_scores[:5]:
        print(str(score[1]) + ": " + str(score[0]))
    print("\nHIGH ASSISTS")
    for assist in high_assists[:5]:
        print(str(assist[1]) + ": " + str(assist[0]))
    print("\nHIGHEST RATED PLAYERS")
    for rating in ratings[:15]:
        print(str(rating[1]) + ": " + str(rating[0]))


# Plays games in general, you have to use the "cup" argument (0 or 1). I use it twice in the upcoming code
# You don't have to use this
def play_games(teams, cup, big):
    if len(teams) % 2 != 0:
        exit(2)
    print("Home advantage, Lineups correct? Is league/cup correct?")
    n = input()
    for i in range(0, len(teams) // 2):
        result, _, _, _, _, _, _, _, _, the_cards, the_injuries = play(teams[2 * i], teams[2 * i + 1], cup, big, 0)
        print(result)
        t1 = strip(teams[2 * i]).upper()
        t2 = strip(teams[2 * i + 1]).upper()
        if teams_map[strip(teams[2 * i])] <= 20:
            update_ycs(the_cards[0][0], t1)
            write_injuries(t1, the_cards[0], the_injuries[0])
        if teams_map[strip(teams[2 * i + 1])] <= 20:
            update_ycs(the_cards[1][0], t2)
            write_injuries(t2, the_cards[1], the_injuries[1])


# Plays a standard gameweek in the league
def play_week(teams, big):
    play_games(teams, 0, big)
    v3 = sheet2.col_values(1)
    i = len(v3) + 1
    writes = 0
    for j in range(0, len(all_scorers)):
        sheet2.update_cell(i, 1, all_scorers[j] + ";" + all_assisters[j])
        i += 1
        writes += 1
    v4 = sheet2.col_values(4)
    k = len(v4) + 1
    for l in range(0, len(all_ratings)):
        sheet2.update_cell(k, 4, all_ratings[l])
        writes += 1
        if writes == 98:
            time.sleep(100)
            writes = 0
        k += 1


# Plays one leg of a cup competition which has a second leg
def play_leg(teams, big):
    play_games(teams, 0, big)
    v4 = sheet2.col_values(4)
    writes = 0
    k = len(v4) + 1
    for l in range(0, len(all_ratings)):
        sheet2.update_cell(k, 4, all_ratings[l])
        writes += 1
        if writes == 98:
            time.sleep(100)
            writes = 0
        k += 1


# Plays a cup round
def play_cup_round(teams, big):
    play_games(teams, 1, big)
    writes = 0
    v4 = sheet2.col_values(4)
    k = len(v4) + 1
    for l in range(0, len(all_ratings)):
        sheet2.update_cell(k, 4, all_ratings[l])
        writes += 1
        if writes == 98:
            time.sleep(100)
            writes = 0
        k += 1


# Plays a game from file
def play_from_file(file1_s, file2_s, big):
    file1 = "C:\\Users\\Anirudh\\Documents\\Football\\" + file1_s + ".txt"
    file2 = "C:\\Users\\Anirudh\\Documents\\Football\\" + file2_s + ".txt"
    f1 = open(file1, "r")
    lines = f1.readlines()
    f2 = open(file2, "r")
    lines.extend(f2.readlines())
    if len(lines) != 40:
        print("Invalid input")
        return
    else:
        t1 = [lines[0][:-1]]
        t2 = [lines[20][:-1]]
        team_1 = []
        ratings_1 = []
        team_2 = []
        ratings_2 = []
        d_1 = lines[1].split()
        for line in d_1:
            t1.append(int(line))
        for line in lines[2:20]:
            pr = line.split()
            if len(pr) == 2:
                s = pr[0]
            else:
                s = ""
                for i in pr[:-2]:
                    s += i
                    s += " "
                s += pr[-2]
            team_1.append(s)
            ratings_1.append(int(pr[-1]))
        d_2 = lines[21].split()
        for line in d_2:
            t2.append(int(line))
        for line in lines[22:]:
            pr = line.split()
            if len(pr) == 2:
                s = pr[0]
            else:
                s = ""
                for i in pr[:-2]:
                    s += i
                    s += " "
                s += pr[-2]
            team_2.append(s)
            ratings_2.append(int(pr[-1]))
        t1.append(ratings_1)
        t1.append(team_1)
        t2.append(ratings_2)
        t2.append(team_2)
        result, hgd, agd, _, _, hpr, apr, _, _, _, _ = play(t1, t2, 0, 1, 1)
        print(result)


string = "tot eve ars mci bou sou"
playing_teams = string.split()

# See manual (8) to adjust kinds of games you can play
play_week(playing_teams, 0)
