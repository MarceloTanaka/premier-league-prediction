# File that collects the data from API-football 
# NEED goals scored, goals scored against, last 6 head-to-head, home/away strength, home/away goals scored/against

import requests
import json
import os

# General values (needed for all/most requests)
API_key = "583c030f85fea127dc37854adb80d696"
url = "https://v3.football.api-sports.io/"

# Asks the user what two teams are playing
team1 = input("Enter the name of the home team: ").title().rstrip().lstrip()
team2 = input("Enter the name of the away team: ").title().rstrip().lstrip()

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



