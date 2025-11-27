LEC = 0
HAM = 0
PIA = 0
NOR = 0
RUS = 0
ANT = 0
VER = 0
TSU = 0
ALB = 0
SAI = 0
ALO = 0
STR = 0
OCO = 0
BEA = 0
HAD = 0
LAW = 0
HUL = 0
BOR = 0
GAS = 0
DOO = 0

lastNames = ["Leclerc","Hamilton","Piastri","Norris","Russel","Antonelli","Verstappen","Tsunoda","Albon","Sainz",
             "Alonso","Stroll","Ocon","Bearman","Hadjar","Lawson","Hulkenberg","Bortoleto","Gasly","Doohan"]
drivers = [LEC,HAM,PIA,NOR,RUS,ANT,VER,TSU,ALB,SAI,ALO,STR,OCO,BEA,HAD,LAW,HUL,BOR,GAS,DOO]
teams = ["Ferrari","McLaren","Mercedes","Red Bull","Williams","Aston Martin","Haas","Vcarb","Kick Sauber","Alpine"]
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

def calculate_constructor_points():
    constructor_points = {}
    for i in range(len(lastNames)):
        name = lastNames[i]
        team = driver_to_team[name]
        if team not in constructor_points:
            constructor_points[team] = 0
        constructor_points[team] += drivers[i]
    return constructor_points

def checkStandings():
    which = input("WDC or WCC?: ")
    if which == "WDC":
        standings = list(zip(lastNames,drivers))
        standings.sort(key=lambda x: x[1], reverse=True)
        for i in range(20):
            print(standings[i])
        print()
        again = input("Would you like to view the constructors championship?: ")
        if again == "yes":
            constructor_points = calculate_constructor_points()
            constructors = list(constructor_points.items())
            constructors.sort(key=lambda x: x[1], reverse=True)
            for i in range(10):
                print(constructors[i])
    else:
        constructor_points = calculate_constructor_points()
        constructors = list(constructor_points.items())
        constructors.sort(key=lambda x: x[1], reverse=True)
        for i in range(10):
            print(constructors[i])
        print()
        again = input("Would you like to view the drivers championship?: ")
        if again == "yes":
            standings = list(zip(lastNames,drivers))
            standings.sort(key=lambda x: x[1], reverse=True)
            for i in range(20):
                print(": ".join(standings[i]))

def startSeason():
    print("WELCOME TO THE 2024 FORMULA ONE SEASON")
    round = 0
    while round < 31:
        points = [25,18,15,12,10,8,6,4,2,1]
        print()
        while True:
            print("Hello and Welcome to the",races[round])
            if "Sprint" in races[round]:
                sprint_points = [8,7,6,5,4,3,2,1]
                for i in range(8):
                    name = input(f"Who finished sprint in position {i+1}: ")
                    index = lastNames.index(name)
                    drivers[index] += sprint_points[i]
                round += 1
                check = input("Would you like to view the standings? ")
                if check == "yes":
                    checkStandings()
                break
            else:
                for i in range(10):
                    name = input(f"Who finished race in position {i+1}: ")
                    index = lastNames.index(name)
                    drivers[index] += points[i]
                round += 1
                check = input("Would you like to view standings right now: ")
                if check == "yes":
                    checkStandings()
                break
        if round == 30:
            break
    print("Season Finished.")
    checkStandings()
    print()

startSeason()
