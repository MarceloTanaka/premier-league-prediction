# File that collects the data from API-football and FootyStats (scraping)
# NEED xG (FootyStats), xGA (FootyStats), last 6 head-to-head, current form, home/away strength

import requests
import json
import os

# General values (needed for all/most requests)
API_key = "583c030f85fea127dc37854adb80d696"
url = "https://v3.football.api-sports.io/"

# Asks the user what two teams are playing
team1 = input("Enter the name of team 1: ").title().rstrip().lstrip()
team2 = input("Enter the name of team 2: ").title().rstrip().lstrip()

# Getting each team's ID and checking if there is a file with some team's IDs in the system already
endpoint = "teams"
if os.path.isfile("team_ids.json"):
    with open("team_ids.json", "r") as file:
        content = file.read()
        dictionary_of_ids = json.loads(content)
else:
    dictionary_of_ids = {}

def team_id(team):
    parameters = {
        "search": team
    }

    if team in dictionary_of_ids:
        team_id = dictionary_of_ids[team]
    else: 
        response = requests.get(url+endpoint, headers = {"x-apisports-key": API_key}, params = parameters)
        response.text
        response_data = json.loads(response.text)
        for number in response_data["response"]:
            if number["team"]["country"] == "England":
                team_id = number["team"]["id"]
                dictionary_of_ids[team] = team_id
                with open("team_ids.json", "w") as file:
                    json.dump(dictionary_of_ids, file)
    return team_id






