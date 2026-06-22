import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#Database Object
db = SQLAlchemy(app)

#Database Table
class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    team = db.Column(db.String(100), nullable=False)
    points = db.Column(db.Integer, default=0)


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

current_race_index = 0

def get_medal_index(index):
    if index == 1:
        return "1 🥇"
    elif index == 2:
        return "2 🥈"
    elif index == 3:
        return "3 🥉"
    return str(index)

@app.route("/", methods=["GET", "POST"])
def index():
    global current_race_index, df_standings

    # If season is over, force user to the standings page
    if current_race_index >= len(races):
        return redirect(url_for('standings'))
    
    current_race = races[current_race_index]
    is_sprint = "Sprint" in current_race
    current_points = [8, 7, 6, 5, 4, 3, 2, 1] if is_sprint else [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
    required_count = len(current_points)

    error_message = None

    if request.method == "POST":
        # 1. Rebuild the list by grabbing each dropdown value sequentially
        entered_drivers = []
        for i in range(1, required_count + 1):
            driver_name = request.form.get(f"driver_{i}")
            if driver_name:
                entered_drivers.append(driver_name)
        
        # 2. Validation: We only need to check for duplicates now!
        if len(set(entered_drivers)) != len(entered_drivers):
            error_message = "⚠️ You selected the same driver multiple times. Every position must be unique!"
        else:
            # If no errors, award the points to the correct drivers
            for i, driver_name in enumerate(entered_drivers):
                driver = Driver.query.filter_by(name=driver_name).first()
                if driver:
                    driver.points += current_points[i]
            
            # Commit the changes permanently to the cloud
            db.session.commit()
            # Move to the next race in the list
            current_race_index += 1    
            # Refresh the home page so the next race shows up
            return redirect(url_for('index'))
        
    # 3. Pull the drivers list from your DataFrame to populate the HTML dropdowns
    drivers_in_db = Driver.query.order_by(Driver.name).all()
    all_drivers = [d.name for d in drivers_in_db]
        
    return render_template("index.html", 
                           race=current_race, 
                           required=required_count, 
                           error=error_message, 
                           driver_list=all_drivers) # <-- Passes drivers to Jinja
        


@app.route("/standings")

def standings():
    drivers_query = Driver.query.all()
    data = [{"Driver": d.name, "Team": d.team, "Points": d.points} for d in drivers_query]
    df_db_standings = pd.DataFrame(data)

    #Sort the Drivers' Championship and add medals
    wdc = df_db_standings.sort_values(by="Points", ascending=False).reset_index(drop=True)
    wdc.index += 1
    wdc.index = wdc.index.map(get_medal_index)
    
    #Sort the Constructors' Championship and add medals
    wcc = df_db_standings.groupby("Team")["Points"].sum().reset_index()
    wcc = wcc.sort_values(by="Points", ascending=False).reset_index(drop=True)
    wcc.index += 1
    wcc.index = wcc.index.map(get_medal_index)
    
    #Convert both DataFrames to HTML tables and send them to standings.html
    return render_template(
    "standings.html", 
    wdc_table=wdc[["Driver", "Team", "Points"]].to_html(classes="table table-striped table-hover mt-2", escape=False), 
    wcc_table=wcc.to_html(classes="table table-striped table-hover mt-2", escape=False)
)

@app.route("/reset-season", methods=["POST"])
def reset_season():
    global current_race_index
    
    #Reset the race calendar index back to the first race
    current_race_index = 0
    
    #Tell Supabase to set everyone's points back to 0
    db.session.query(Driver).update({Driver.points: 0})
    db.session.commit()
    
    #Bounce the user back to the home page fresh
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(port=3000, debug=True)