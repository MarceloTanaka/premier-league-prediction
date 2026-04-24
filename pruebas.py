from datetime import datetime

from datetime import datetime

def ask_season():
    current_year = datetime.now().year

    while True:
        season = input("Which season do you want to predict the match for? (Type only the first year, for example 2023 for the 2023/24 season): ")

        if not season.isdigit():
            print("The input you entered is not a valid number, please enter a year")
            continue

        season = int(season)

        if 2023 <= season <= current_year:
            return season

        print(f"Please enter a year between 2023 and {current_year}")

print(ask_season())