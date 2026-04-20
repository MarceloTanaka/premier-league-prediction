# File that collects the data from API-football 
# NEED goals scored, goals scored against, last 6 head-to-head, home/away strength, home/away goals scored/against

import requests
import json
import os
from scipy.stats import poisson

# General values (needed for all/most requests)
API_key = "583c030f85fea127dc37854adb80d696"
url = "https://v3.football.api-sports.io/"

# Asks the user what two teams are playing (this will go in the main function later)
# team1 = input("Enter the name of the home team: ").title().rstrip().lstrip()
# team2 = input("Enter the name of the away team: ").title().rstrip().lstrip()

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
def average_goals():
    endpoint = "standings"
    parameters = {
        "league": 39,
        "season": 2023
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

# Getting the average goals scored by the home team and calculating its attacking strength
def home_attacking_strength(team1, home_goals_scored_average):
    endpoint = "teams/statistics"
    parameters = {
        "league": 39,
        "season": 2023,
        "team": dictionary_of_ids[team1]
    }

    response = requests.get(url+endpoint, headers = {"x-apisports-key": API_key}, params = parameters)
    response_data = json.loads(response.text)["response"]

    team_goals_scored_home_average = response_data["goals"]["for"]["total"]["home"]/response_data["fixtures"]["played"]["home"]
    home_attacking_strength = team_goals_scored_home_average/home_goals_scored_average

    return home_attacking_strength

# Getting the average goals conceded by the away team and calculatiing its defensive strength
def away_defensive_strength(team2, away_goals_conceded_average):
    endpoint = "teams/statistics"
    parameters = {
        "league": 39,
        "season": 2023,
        "team": dictionary_of_ids[team2]
    }

    response = requests.get(url+endpoint, headers = {"x-apisports-key": API_key}, params = parameters)
    response_data = json.loads(response.text)["response"]

    team_goals_conceded_away_average = response_data["goals"]["against"]["total"]["away"]/response_data["fixtures"]["played"]["away"]
    away_defensive_strength = team_goals_conceded_away_average/away_goals_conceded_average

    return away_defensive_strength

# Projecting expected home team goals
def expected_home_team_goals(home_attacking_strength, away_defensive_strength, home_goals_scored_average):
    return home_attacking_strength*away_defensive_strength*home_goals_scored_average

# Getting the average goals scored by the away team and calculating its attacking strength
def away_attacking_strength(team2, away_goals_scored_average):
    endpoint = "teams/statistics"
    parameters = {
        "league": 39,
        "season": 2023,
        "team": dictionary_of_ids[team2]
    }

    response = requests.get(url+endpoint, headers = {"x-apisports-key": API_key}, params = parameters)
    response_data = json.loads(response.text)["response"]

    team_goals_scored_away_average = response_data["goals"]["for"]["total"]["away"]/response_data["fixtures"]["played"]["away"]
    away_attacking_strength = team_goals_scored_away_average/away_goals_scored_average

    return away_attacking_strength

# Getting the average goals conceded by the home team and calculatiing its defensive strength
def home_defensive_strength(team1, home_goals_conceded_average):
    endpoint = "teams/statistics"
    parameters = {
        "league": 39,
        "season": 2023,
        "team": dictionary_of_ids[team1]
    }

    response = requests.get(url+endpoint, headers = {"x-apisports-key": API_key}, params = parameters)
    response_data = json.loads(response.text)["response"]

    team_goals_conceded_home_average = response_data["goals"]["against"]["total"]["home"]/response_data["fixtures"]["played"]["home"]
    home_defensive_strength = team_goals_conceded_home_average/home_goals_conceded_average

    return home_defensive_strength

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

    return score_prob

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
                


probability_home_goals, probability_away_goals = goal_probability(2.016, 0.653)
probable_outcome(probability_home_goals, probability_away_goals)
win_lose_draw_probability(probability_home_goals, probability_away_goals)

    
    