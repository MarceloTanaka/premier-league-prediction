# Statistics to use: 
# xG(30%), xGA(30%), last 6 head-to-head(5%), current form (last 5 games)(15%), home/away strength(20%)

xG = 1.77
xGA = 0.99
results = "WDLDWLDLDWLWDDWWDLWWLWLLDWWDWDWWWWDWDW"
head_to_head = [True, True, True, True, True, True]

home_performance = {"Wins": 10, 
                    "Draws": 7,
                    "Loses": 2}

away_performance = {"Wins": 8,
                    "Draws": 5,
                    "Loses": 6}


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

#---------------------------------------------------------------------------------------------------------------
# Possible Improvement: Use only one function to measure home/away strength
#---------------------------------------------------------------------------------------------------------------
def normalized_score_home(home_performance):
    win_points = home_performance["Wins"] * 3
    draw_points = home_performance["Draws"] * 1
    total_possible_points = (home_performance["Wins"] + home_performance["Draws"] + home_performance["Loses"])*3
    total_obtained_points = win_points + draw_points
    return total_obtained_points/total_possible_points

def normalized_score_away(away_performance):
    win_points = away_performance["Wins"] * 3
    draw_points = away_performance["Draws"] * 1
    total_possible_points = (away_performance["Wins"] + away_performance["Draws"] + away_performance["Loses"])*3
    total_obtained_points = win_points + draw_points
    return total_obtained_points/total_possible_points

# Applying weight to each normalized metric
weighted_xG = normalized_xG(xG)*0.30 # 30%
weighted_current_form = normalized_current_form(results)*0.15 # 15%
weighted_xGA = normalized_xGA(xGA)*0.30 # 30%
weighted_head_to_head = normalized_head_to_head(head_to_head)*0.05 # 5%
# -------------------------------------------------------------------------------------
# CHECK IF IT IS POSSIBLE TO INTEGRATE THIS TWO INTO ONE METRIC USING IF STATEMENTS
#-------------------------------------------------------------------------------------
weighted_home_strength = normalized_score_home(home_performance)*0.2 #20%
weighted_away_strength = normalized_score_away(away_performance)*0.2 # 20%

print(f"xG: {weighted_xG}")
print(f"Current form: {weighted_current_form}")
print(f"xGA: {weighted_xGA}")
