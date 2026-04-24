# File that collects the data from API-football 

import requests
import json
import os
from scipy.stats import poisson
from datetime import datetime

# General values (needed for all/most requests)
API_key = "583c030f85fea127dc37854adb80d696"
url = "https://v3.football.api-sports.io/"

# Getting each team's ID and checking if there is a file with some team's IDs in the system already
if os.path.isfile("team_ids.json"):
    with open("team_ids.json", "r") as file:
        content = file.read()
        dictionary_of_ids = json.loads(content)
else:
    dictionary_of_ids = {}

def team_id(team):
    endpoint = "teams"
    parameters = {
        "name": team
    }

    # If already cached, return team's ID immediately
    if team in dictionary_of_ids:
        team_id = dictionary_of_ids[team]

    # Otherwise fetch from API     
    else: 
        response = requests.get(url+endpoint, headers = {"x-apisports-key": API_key}, params = parameters)
        response_data = json.loads(response.text)
        team_id = None
        for number in response_data["response"]:
            if number["team"]["country"] == "England":
                team_id = number["team"]["id"]

                # Save the value to a dictionary and then to a json file 
                dictionary_of_ids[team] = team_id
                with open("team_ids.json", "w") as file:
                    json.dump(dictionary_of_ids, file)
    return team_id

# Getting the average goals scored/conceded at home/away per game in the league
def average_goals(season):
    endpoint = "standings"
    parameters = {
        "league": 39,
        "season": season - 1
    }

    response = requests.get(url+endpoint, headers = {"x-apisports-key": API_key}, params = parameters)
    response_data = json.loads(response.text)

    total_home_goals_scored = 0
    teams = response_data["response"][0]["league"]["standings"][0]
    for team in teams:
        total_home_goals_scored += team["home"]["goals"]["for"]

    home_goals_scored_average = total_home_goals_scored/380

    total_away_goals_scored = 0
    for team in teams:
        total_away_goals_scored += team["away"]["goals"]["for"]

    away_goals_scored_average = total_away_goals_scored/380

    # Goals conceded is the inverse of the goals scored
    home_goals_conceded_average = away_goals_scored_average
    away_goals_conceded_average = home_goals_scored_average

    return home_goals_scored_average, away_goals_scored_average, home_goals_conceded_average, away_goals_conceded_average

# Getting the average goals scored/conceded by the home team and calculating its attacking/defensive strength
def home_attacking_defensive_strength(team1_id, home_goals_scored_average, home_goals_conceded_average, season):
    endpoint = "teams/statistics"
    parameters = {
        "league": 39,
        "season": season - 1,
        "team": team1_id
    }

    response = requests.get(url+endpoint, headers = {"x-apisports-key": API_key}, params = parameters)
    response_data = json.loads(response.text)["response"]

    # Get the goals scored and calculate the home attacking strength
    try:
        team_goals_scored_home_average = response_data["goals"]["for"]["total"]["home"]/response_data["fixtures"]["played"]["home"]
        home_attacking_strength = team_goals_scored_home_average/home_goals_scored_average
    except ZeroDivisionError:
        home_attacking_strength = 0
    except KeyError:
        home_attacking_strength = 0
    
    # Get the goals conceded and calculate the home defensive strength
    try:
        team_goals_conceded_home_average = response_data["goals"]["against"]["total"]["home"]/response_data["fixtures"]["played"]["home"]
        home_defensive_strength = team_goals_conceded_home_average/home_goals_conceded_average
    except ZeroDivisionError:
        home_defensive_strength = 0
    except KeyError:
        home_defensive_strength = 0

    return home_attacking_strength, home_defensive_strength

# Getting the average goals scored/conceded by the away team and calculatiing its attacking/defensive strength
def away_attacking_defensive_strength(team2_id, away_goals_scored_average, away_goals_conceded_average, season):
    endpoint = "teams/statistics"
    parameters = {
        "league": 39,
        "season": season - 1,
        "team": team2_id
    }

    response = requests.get(url+endpoint, headers = {"x-apisports-key": API_key}, params = parameters)
    response_data = json.loads(response.text)["response"]


    away_defensive_strength = 0
    # Get goals conceded and calculate defensive strength
    try:
        team_goals_conceded_away_average = response_data["goals"]["against"]["total"]["away"]/response_data["fixtures"]["played"]["away"]
        away_defensive_strength = team_goals_conceded_away_average/away_goals_conceded_average
    except ZeroDivisionError:
        away_defensive_strength = 0
    except KeyError:
        away_defensive_strength = 0

    # Get goals scored and calculate attacking strength
    try:
        team_goals_scored_away_average = response_data["goals"]["for"]["total"]["away"]/response_data["fixtures"]["played"]["away"]
        away_attacking_strength = team_goals_scored_away_average/away_goals_scored_average
    except ZeroDivisionError:
        away_attacking_strength = 0
    except KeyError:
        away_attacking_strength = 0
    
    return away_attacking_strength, away_defensive_strength

# Projecting expected home team goals
def expected_home_team_goals(home_attacking_strength, away_defensive_strength, home_goals_scored_average):
    return home_attacking_strength*away_defensive_strength*home_goals_scored_average

# Projecting expected away team goals
def expected_away_team_goals(away_attacking_strength, home_defensive_strength, away_goals_scored_average):
    return away_attacking_strength*home_defensive_strength*away_goals_scored_average

# Calculating the probability of each score using Poisson Distribution
def goal_probability(expected_home_team_goals, expected_away_team_goals):
    
    # Calculating the probability for the home team
    goals_home_team_probability = []
    for i in range(0, 6):
        goals_for_home = poisson.pmf(i, expected_home_team_goals)
        goals_home_team_probability.append(float(goals_for_home))

    # Calculating the probability for the away team
    goals_away_team_probability = []
    for i in range(0, 6):
        goals_for_away = poisson.pmf(i, expected_away_team_goals)
        goals_away_team_probability.append(float(goals_for_away))

    return goals_home_team_probability, goals_away_team_probability

# Calculating most probable outcome
def probable_outcome(goals_home_team_probability, goals_away_team_probability):
    
    # Home team higher probability of goals scored
    home_higher_prob = 0
    home_goals = 0
    for probability in goals_home_team_probability:
        if home_higher_prob == 0:
            home_higher_prob = probability
        elif probability > home_higher_prob:
            home_higher_prob = probability
            home_goals = goals_home_team_probability.index(probability)

    # Away team higher probability of goals scored
    away_higher_prob = 0
    away_goals = 0
    for probability in goals_away_team_probability:
        if away_higher_prob == 0:
            away_higher_prob = probability
        elif probability > away_higher_prob:
            away_higher_prob = probability
            away_goals = goals_away_team_probability.index(probability)

    # Calculate what is the probability of this score
    score_prob = home_higher_prob*away_higher_prob

    return score_prob, home_goals, away_goals

# Calculating the probabilities for W/D/L for each team
def win_lose_draw_probability(goals_home_team_probability, goals_away_team_probability):
    home_win = 0
    draw = 0
    away_win = 0
    for i, p_home in enumerate(goals_home_team_probability):
        for j, p_away in enumerate(goals_away_team_probability):
            combination = p_home * p_away
            if i > j:
                home_win += combination
            elif i == j:
                draw += combination
            else:
                away_win += combination

    return home_win, draw, away_win

def promoted_team(season):
    endpoint = "standings"
    parameters = {
        "league": 40,
        "season": season - 1
    }

    response = requests.get(url+endpoint, headers = {"x-apisports-key": API_key}, params = parameters)
    response_data = json.loads(response.text)["response"][0]["league"]["standings"][0]

    promoted_teams = []
    for team in response_data:
        if team["description"] == "Promotion":
            promoted_teams.append(team["team"]["name"])

    return promoted_teams
     
def playoff_winner(season):
    endpoint = "fixtures"
    parameters = {
        "league": 40,
        "season": season - 1,
        "round": "Promotion Play-offs - Final"
    }     

    response = requests.get(url+endpoint, headers = {"x-apisports-key": API_key}, params = parameters)
    fixtures = json.loads(response.text)["response"]

    if not fixtures:
        return None  # API returned nothing

    teams = fixtures[0]["teams"]

    if teams["home"]["winner"]:
        return teams["home"]["name"]
    else:
        return teams["away"]["name"]
    
def ask_season():
    current_year = datetime.now().year

    while True:
        season = input("Which season do you want to predict the match for? (Type only the first year, for example 2023 for the 2023/24 season): ")

        if not season.isdigit(): # Check if the input is a number
            print("The input you entered is not a valid number, please enter a year")
            continue

        season = int(season) # If it is a number, it will convert it into an integer

        if 2023 <= season <= current_year: # Check if the year entered is in the expected range of the program
            return season

        print(f"Please enter a year between 2023 and {current_year}")

def main():
    # Ask the user what two teams are playing
    team1 = input("Enter the name of the home team: ").title().rstrip().lstrip()
    team2 = input("Enter the name of the away team: ").title().rstrip().lstrip()

    # Ask the user the season he wants to predict
    season = ask_season()

    # Get each team's ID
    team1_id = team_id(team1)
    team2_id = team_id(team2)

    # Check if any of the team's ID is None and stop the program there to prevent any crashes
    if team1_id is None or team2_id is None:
        print("The team you entered is not in the system. Please check spelling.")
        return

    # Get all the promoted teams, including the one promoted through playoffs
    promoted_teams = promoted_team(season)
    promoted_teams.append(playoff_winner(season))
    
    # Get the average goals scored/conceded in the league
    home_goals_scored_average, away_goals_scored_average, home_goals_conceded_average, away_goals_conceded_average = average_goals(season)

    # Calculating the home team's attacking/defensive strength
    if team1.lower() in [t.lower() for t in promoted_teams]:
        # Promoted home team: fixed strengths
        team1_attacking_strength = 0.8/home_goals_scored_average
        team1_defensive_strength = 1.0/home_goals_conceded_average
    else:
        team1_attacking_strength, team1_defensive_strength = home_attacking_defensive_strength(team1_id, home_goals_scored_average, home_goals_conceded_average, season)

    # Calculating the away team's attacking/defensive strength
    if team2.lower() in [t.lower() for t in promoted_teams]:
        # Promoted away team: fixed strengths
        team2_attacking_strength = 0.8/away_goals_scored_average
        team2_defensive_strength = 1.0/away_goals_conceded_average
    else:
        team2_attacking_strength, team2_defensive_strength = away_attacking_defensive_strength(team2_id, away_goals_scored_average, away_goals_conceded_average, season)

    # Calculating the expected home/away team goals
    team1_expected_goals = expected_home_team_goals(team1_attacking_strength, team2_defensive_strength, home_goals_scored_average)
    team2_expected_goals = expected_away_team_goals(team2_attacking_strength, team1_defensive_strength, away_goals_scored_average)

    # Calculating goal probability and putting these probabilities in a list
    goals_team1_probabilities, goals_team2_probabilities = goal_probability(team1_expected_goals, team2_expected_goals)

    # Calculating the most probable outcome based on the highest goal probability for each team
    score_prob, home_goals, away_goals = probable_outcome(goals_team1_probabilities, goals_team2_probabilities)

    # Calculating the probabilities for a W/D/L
    home_win, draw, away_win = win_lose_draw_probability(goals_team1_probabilities, goals_team2_probabilities)

    # Displaying the results in the terminal
    print(f"The most probable score is {team1} {home_goals} : {team2} {away_goals} with a{score_prob*100: .2f}%")
    print(f"{team1}:{home_win*100: .2f}% \nDraw:{draw*100: .2f}% \n{team2}:{away_win*100: .2f}%")

if __name__ == "__main__":
    main()
    