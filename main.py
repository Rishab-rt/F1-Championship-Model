import time
import os
import numpy as np
import pandas as pd

points = [25,18,15,12,10,8,6,4,2,1]
races = ["Australian Grand Prix","China Sprint","Chinese Grand Prix","Japanase Grand Prix","Bahrain Grand Prix","Saudi Grand Prix",
         "Miami Sprint","Miami Grand Prix","Emilia Rogmana Grand Prix","Monaco Grand Prix","Spanish Grand Prix",
         "Canadian Grand Prix","Austrian Grand Prix","British Grand Prix","Belgian Sprint","Belgian Grand Prix",
         "Hungarian Grand Prix","Dutch Grand Prix","Italian Grand Prix","Azerbaijanian Grand Prix","Singaporean Grand Prix",
         "COTA Sprint","American Grand Prix","Mexican Grand Prix","Brazil Sprint","Sao Paolo Grand Prix","Vegas Grand Prix",
         "Qatar Sprint","Qatar Grand Prix","Abu Dhabi Grand Prix"]

driver_to_team = {
    "Leclerc": "Ferrari", "Hamilton": "Ferrari",
    "Piastri": "McLaren", "Norris": "McLaren",
    "Russel": "Mercedes", "Antonelli": "Mercedes",
    "Verstappen": "Red Bull", "Tsunoda": "Red Bull",
    "Sainz": "Williams", "Albon": "Williams",
    "Alonso": "Aston Martin", "Stroll": "Aston Martin",
    "Ocon": "Haas", "Bearman": "Haas",
    "Hadjar": "Vcarb", "Lawson": "Vcarb",
    "Hulkenberg": "Kick Sauber", "Bortoleto": "Kick Sauber",
    "Gasly": "Alpine", "Doohan": "Alpine"
}

df_standings = pd.DataFrame(list(driver_to_team.items)),columns = ["Drivers","Teams"]
df_standings["Points"] = 0


def calculate_constructor_points():
    driver_points = np.array(drivers)
    constructor_points = {}

    for i, name in enumerate(lastNames):
        team = driver_to_team[name]
        constructor_points[team] = constructor_points.get(team, 0) + int(driver_points[i])

    return constructor_points

def printWDC():
    standings = list(zip(lastNames,drivers))
    standings.sort(key=lambda x: x[1], reverse=True)
    for i in range(20):
        print(standings[i])
    print()

def printWCC():
    constructor_points = calculate_constructor_points()
    constructors = list(constructor_points.items())
    constructors.sort(key=lambda x: x[1], reverse=True)
    for i in range(10):
        print(constructors[i])

def checkStandings():
    which = input("WDC or WCC?: ")
    if which == "WDC":
        printWDC()
        again = input("Would you like to view the constructors championship?: ")
        if again == "yes":
            printWCC()
    elif which == "WCC":
        printWCC()
        again = input("Would you like to view the drivers championship?: ")
        if again == "yes":
            printWDC()

def startSeason():
    print("WELCOME TO THE 2025 FORMULA ONE SEASON")
    round = 0
    while round < len(races):
        points = [25,18,15,12,10,8,6,4,2,1]
        sprint_points = [8,7,6,5,4,3,2,1]
        print()
        print("Hello and Welcome to the",races[round])

        if "Sprint" in races[round]:
            for i in range(len(sprint_points)):
                while True:
                    name = input(f"Who finished sprint in position {i+1}: ")
                    if name not in lastNames:
                        print("Seems like you entered a driver who doesnt exist, please try again!!!")
                        continue
                    index = lastNames.index(name)
                    drivers[index] += sprint_points[i]
                    break

            round += 1
            check = input("Would you like to view the standings? ")
            if check.lower() == "yes":
                checkStandings()
            time.sleep(5)
            os.system('clear')
            continue

        for i in range(len(points)):
            while True:
                name = input(f"Who finished race in position {i+1}: ")
                if name not in lastNames:
                    print("Seems like you entered a driver who doesnt exist, please try again!!!")
                    continue
                index = lastNames.index(name)
                drivers[index] += points[i]
                break
               
        round += 1
        check = input("Would you like to view standings right now: ")
        if check == "yes":
            checkStandings()
        time.sleep(5)
        os.system('clear')
        

    print("Season Finished.")
    checkStandings()
    print()

startSeason()