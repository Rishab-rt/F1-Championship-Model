from flask import Flask, render_template, request, redirect, url_for
import pandas as pd

app = Flask(__name__)


races = ["Australian Grand Prix", "China Sprint", "Chinese Grand Prix", "Japanese Grand Prix", 
         "Miami Sprint", "Miami Grand Prix", "Canada Sprint", "Canadian Grand Prix", 
         "Monaco Grand Prix", "Spanish Grand Prix", "Austrian Grand Prix", "Silverstone Sprint",
         "British Grand Prix", "Belgian Grand Prix - SPA", "Hungarian Grand Prix", "Dutch Sprint", 
         "Dutch Grand Prix", "Italian Grand Prix", "Madrid Grand Prix", "Azerbaijan Grand Prix", 
         "Singapore Sprint", "Singapore Grand Prix", "Circuit of Americas Grand Prix", "Mexican Grand Prix", 
         "São Paulo Grand Prix", "Las Vegas Grand Prix", "Qatar Grand Prix", "Abu Dhabi Grand Prix"]

driver_to_team = {
    "Leclerc": "Ferrari", "Hamilton": "Ferrari",
    "Piastri": "McLaren", "Norris": "McLaren",
    "Russell": "Mercedes", "Antonelli": "Mercedes",
    "Verstappen": "Red Bull", "Hadjar": "Red Bull",
    "Sainz": "Williams", "Albon": "Williams",
    "Alonso": "Aston Martin", "Stroll": "Aston Martin",
    "Ocon": "Haas", "Bearman": "Haas",
    "Linblad": "Vcarb", "Lawson": "Vcarb",
    "Hulkenberg": "Audi", "Bortoleto": "Audi",
    "Gasly": "Alpine", "Colapinto": "Alpine",
    "Perez":"Cadillac","Bottas":"Cadillac"
}

df_standings = pd.DataFrame(list(driver_to_team.items()), columns=["Driver", "Team"])
df_standings["Points"] = 0

current_race_index = 0

def get_medal_index(index):
    if index == 1:
        return "1 🥇"
    elif index == 2:
        return "2 🥈"
    elif index == 3:
        return "3 🥉"
    return str(index)

@app.route("/",methods=["GET","POST"])

def index():
    global current_race_index, df_standings

    #If season is over, force user to the standings page
    if current_race_index >= len(races):
        return redirect(url_for('standings'))
    
    current_race = races[current_race_index]
    is_sprint = "Sprint" in current_race
    current_points = [8, 7, 6, 5, 4, 3, 2, 1] if is_sprint else [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
    required_count = len(current_points)

    error_message = None

    if request.method == "POST":
        # Grab the text from the HTML input box named "drivers"
        user_input = request.form.get("drivers")
        
        # Clean the input
        entered_drivers = [name.title().strip() for name in user_input.split(",")]
        
        # Check for drivers that don't exist in our dictionary
        invalid_drivers = [name for name in entered_drivers if name not in df_standings["Driver"].values]

        #Error when the number of drivers entered is less than the number of drivers with points
        if len(entered_drivers) != required_count:
            error_message = f"Need exactly {required_count} drivers. You entered {len(entered_drivers)}."
        #Error for when the drivers entered do not exist (usually spelling mistakes)
        elif invalid_drivers:
            error_message = f"These drivers don't exist: {', '.join(invalid_drivers)}."
        elif len(set(entered_drivers)) != len(entered_drivers):
            error_message = "You entered the same driver multiple times."
        else:
            # If no errors, award the points to the correct drivers
            for i, driver in enumerate(entered_drivers):
                df_standings.loc[df_standings["Driver"] == driver, "Points"] += current_points[i]    
            
            # Move to the next race in the list
            current_race_index += 1    
            # Refresh the home page so the next race shows up
            return redirect(url_for('index'))
        
    return render_template("index.html", race=current_race, required=required_count, error=error_message)    
        


@app.route("/standings")

def printWCC():
    print("\n\t CONSTRUCTORS' CHAMPIONSHIP STANDING ")
    wcc = df_standings.groupby("Team")["Points"].sum().reset_index()
    wcc = wcc.sort_values(by="Points", ascending=False).reset_index(drop=True)
    wcc.index += 1
    wcc.index = wcc.index.map(get_medal_index)
    print(wcc)
    print()

def printWDC():
    print("\n--- WORLD DRIVERS' CHAMPIONSHIP ---")
    wdc = df_standings.sort_values(by="Points", ascending=False).reset_index(drop=True)
    wdc.index += 1
    wdc.index = wdc.index.map(get_medal_index) 
    print(wdc[["Driver", "Team", "Points"]])   
    print()

def checkStandings():
    which = input("WDC or WCC?: ").upper().strip()
    if which == "WDC":
        printWDC()
        if input("Would you like to view the constructors championship? (yes/no): ").lower().strip() == "yes":
            printWCC()
    elif which == "WCC":
        printWCC()
        if input("Would you like to view the drivers championship? (yes/no): ").lower().strip() == "yes":
            printWDC()

def startSeason():
    print("WELCOME TO THE 2026 FORMULA ONE SEASON")
    
    for current_race in races:
        print(f"\nHello and Welcome to the {current_race}")
        
        if "Sprint" in current_race:
            current_points = [8, 7, 6, 5, 4, 3, 2, 1]
            session_type = "sprint"
        else:
            current_points = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
            session_type = "race"

        required_count = len(current_points)

        while True:
            user_input = input(f"Enter the top {required_count} drivers separated by commas (or type 'quit' to end):\n> ")

            if user_input.strip().lower() == "quit":
                print("\nEnding the season early...")
                break
            
            entered_drivers = [name.title().strip() for name in user_input.split(",")]
            
            if len(entered_drivers) != required_count:
                print(f"⚠️ Error: You entered {len(entered_drivers)} drivers, but I need exactly {required_count}. Try again.")
                continue

            invalid_drivers = [name for name in entered_drivers if name not in df_standings["Driver"].values]
            if invalid_drivers:
                print(f"⚠️ Error: These drivers don't exist: {', '.join(invalid_drivers)}. Try again.")
                continue

            if len(set(entered_drivers)) != len(entered_drivers):
                print("⚠️ Error: You entered the same driver multiple times. Try again.")
                continue
                
            for i, driver in enumerate(entered_drivers):
                df_standings.loc[df_standings["Driver"] == driver, "Points"] += current_points[i]
                
            break 
               
        check = input("Would you like to view standings right now? (yes/no): ").lower().strip()
        if check == "yes":
            checkStandings()
            time.sleep(10)
            

        os.system('clear') 

    print("Season Finished.")
    printWDC()
    printWCC()

startSeason()
