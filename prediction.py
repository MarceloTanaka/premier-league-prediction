# Statistics to use: 
# xG(30%), xGA(30%), last 6 head-to-head(5%), current form (last 5 games)(15%), home/away strength(20%)

# Metrics team 1 (West Ham)
xG_1 = 1.17
xGA_1 = 1.79
results_1 = "DLWDL"
head_to_head_1 = [True, False, True, False, False, False]

home_performance_1 = {"Wins": 3, 
                    "Draws": 4,
                    "Loses": 8}

away_performance_1 = {"Wins": 4,
                    "Draws": 4,
                    "Loses": 8}

team_is_home_1 = True

# Metrics team 2 (Wolves)
xG_2 = 1.10
xGA_2 = 1.63
results_2 = "DDLWW"
head_to_head_2 = [False, True, False, True, True, True]

home_performance_2 = {"Wins": 3, 
                    "Draws": 3,
                    "Loses": 10}

away_performance_2 = {"Wins": 0,
                    "Draws": 5,
                    "Loses": 10}

team_is_home_2 = False


# Functions to normalize all the relevant metrics
def normalized_current_form(results):
    last_5 = results[-5:]
    form = list(last_5)
    points = 0
    for outcome in form:
        if outcome == "W":
            points += 3
        elif outcome == "D":
            points += 1
        else:
            points += 0
    return points/15

def normalized_xG(xG):
    return xG/2

def normalized_xGA(xGA):
    return (2-xGA)/2

def normalized_head_to_head(head_to_head):
    history = 0
    for winner in head_to_head:
        if winner == True:
            history += 3
        elif winner == False:
            history += 0
        else:
            history += 1

    max_points = len(head_to_head) * 3
    return history/max_points

def normalized_score(performance):
    win_points = performance["Wins"] * 3
    draw_points = performance["Draws"] * 1
    total_possible_points = (performance["Wins"] + performance["Draws"] + performance["Loses"])*3
    total_obtained_points = win_points + draw_points
    return total_obtained_points/total_possible_points

# Applying weight to each normalized metric and calculating the team's score
def team_score(xG, xGA, results, head_to_head, home_performance, away_performance, team_is_home):
    weighted_xG = normalized_xG(xG)*0.30 # 30%
    weighted_current_form = normalized_current_form(results)*0.15 # 15%
    weighted_xGA = normalized_xGA(xGA)*0.30 # 30%
    weighted_head_to_head = normalized_head_to_head(head_to_head)*0.05 # 5%
    if team_is_home:
        weighted_strength = normalized_score(home_performance)*0.2 # 20%
    else:
        weighted_strength = normalized_score(away_performance)*0.2 # 20%

    return sum([weighted_xGA, weighted_current_form, weighted_xG, weighted_strength, weighted_head_to_head])

# Calculating each team's score
team1_score = team_score(xG_1, xGA_1, results_1, head_to_head_1, home_performance_1, away_performance_1, team_is_home_1)
team2_score = team_score(xG_2, xGA_2, results_2, head_to_head_2, home_performance_2, away_performance_2, team_is_home_2)

# Function that calculates the probability of drawing
def draw_chances(team1_score, team2_score):
    difference = abs(team1_score - team2_score)
    return 0.3 * (1/(1 + difference))

# Function that calculates winning and drawing probabilities
def winning_probability(team1_score, team2_score, draw_chances):
    probability_team1 = team1_score/(team1_score + team2_score + draw_chances) 
    probability_team2 = team2_score/(team1_score + team2_score + draw_chances)
    probability_draw = draw_chances/(team1_score + team2_score + draw_chances)
    return probability_team1, probability_draw, probability_team2

draw = draw_chances(team1_score, team2_score)
print(f"{winning_probability(team1_score, team2_score, draw)}")




