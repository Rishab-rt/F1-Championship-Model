import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from dotenv import load_dotenv
import requests

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

#Result table
class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable=False)
    race_name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.Integer, nullable=False) # 1 for win, 2 for second, etc.
    
    # Establish a relationship so a driver can easily pull all their results
    driver = db.relationship('Driver', backref=db.backref('results', lazy=True))

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

driver_codes = {
    "Leclerc": "LEC", "Hamilton": "HAM",
    "Piastri": "PIA", "Norris": "NOR",
    "Russell": "RUS", "Antonelli": "ANT",
    "Verstappen": "VER", "Hadjar": "HAD",
    "Sainz": "SAI", "Albon": "ALB",
    "Alonso": "ALO", "Stroll": "STR",
    "Ocon": "OCO", "Bearman": "BEA",
    "Linblad": "LIN", "Lawson": "LAW",
    "Hulkenberg": "HUL", "Bortoleto": "BOR",
    "Gasly": "GAS", "Colapinto": "COL",
    "Perez": "PER", "Bottas": "BOT"
}

driver_number_to_name = {
    1: "Norris",
    3: "Verstappen",
    5: "Bortoleto",
    6: "Hadjar",
    10: "Gasly",
    12: "Antonelli",
    16: "Leclerc",
    23: "Albon",
    27: "Hulkenberg",
    30: "Lawson",
    31: "Ocon",
    41: "Bearman",
    43: "Colapinto",
    44: "Hamilton",
    63: "Russell",
    81: "Piastri",
    87: "Linblad",
    5: "Bortoleto",
    14: "Alonso",
    18: "Stroll",
    11: "Perez",
    77: "Bottas",
    20: "Sainz",
}

race_session_keys = {
    "Australian Grand Prix": 11234,
    "China Sprint": 11240,
    "Chinese Grand Prix": 11245,
    "Japanese Grand Prix": 11253,
    "Miami Sprint": 11275,
    "Miami Grand Prix": 11280,
    "Canada Sprint": 11286,
    "Canadian Grand Prix": 11291,
    "Monaco Grand Prix": 11299,
    "Spanish Grand Prix": 11307,
    "Austrian Grand Prix": 11315,
}

def recalculate_all_points():
    # Zero out everyone first
    db.session.query(Driver).update({Driver.points: 0})
    
    # Replay every result in the DB
    all_results = Result.query.all()
    for result in all_results:
        race_name = result.race_name
        if ("Sprint" in race_name):
            points_scale = [8, 7, 6, 5, 4, 3, 2, 1]
        else:
            points_scale =[25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
        
        if 1 <= result.position <= len(points_scale):
            result.driver.points += points_scale[result.position - 1]
    
    db.session.commit()

current_race_index = 0

def get_medal_index(index):
    if index == 1:
        return "1 🥇"
    elif index == 2:
        return "2 🥈"
    elif index == 3:
        return "3 🥉"
    return str(index)

def sync_results():
    for race_name, session_key in race_session_keys.items():
        # 1. check if race already exists in DB
        existing = Result.query.filter_by(race_name=race_name).first()
        if existing:
            continue
        
        # 2. fetch positions from OpenF1
        response = requests.get(f"https://api.openf1.org/v1/position?session_key={session_key}")
        positions = response.json()
        
        # 3. loop through positions and save each result
        for entry in positions:
            driver_number = entry["driver_number"]
            position = entry["position"]
            driver_name = driver_number_to_name.get(driver_number)
            if not driver_name:
                continue  # skip unknown drivers
            driver = Driver.query.filter_by(name=driver_name).first()
            if driver:
                result = Result(driver_id=driver.id, race_name=race_name, position=position)
                db.session.add(result)
        
        db.session.commit()
    
    recalculate_all_points()


@app.route("/", methods=["GET", "POST"])
def index():
    global current_race_index

    # If season is over, force user to the standings page
    if current_race_index >= len(races):
        return redirect(url_for('standings'))
    
    current_race = races[current_race_index]
    if ("Sprint" in current_race):
            current_points = [8, 7, 6, 5, 4, 3, 2, 1]
    else:
            current_points = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
            
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

                    result = Result(driver_id=driver.id, race_name=current_race, position=i + 1)
                    db.session.add(result)
            
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
                       driver_list=all_drivers,
                       current_race_index=current_race_index,
                       races=races,
                       driver_teams={d.name: d.team for d in drivers_in_db})
        
@app.route("/standings")
def standings():
    drivers = Driver.query.all()
    
    # Python only handles the sorting logic
    def f1_sorting_key(driver):
        finish_counts = [0] * 20 
        for r in driver.results:
            if 1 <= r.position <= 20:
                finish_counts[r.position - 1] += 1
        return (driver.points, *finish_counts)

    sorted_drivers = sorted(drivers, key=f1_sorting_key, reverse=True)

    # Process constructors simply
    constructors_dict = {}
    for d in drivers:
        constructors_dict[d.team] = constructors_dict.get(d.team, 0) + d.points
    sorted_constructors = sorted(constructors_dict.items(), key=lambda x: x[1], reverse=True)

    # Just send the RAW lists to the HTML. No HTML strings here!
    return render_template(
        "standings.html", 
        drivers=sorted_drivers, 
        constructors=sorted_constructors,
        current_race_index=current_race_index,
        races=races
        )

#Route to reset the season
@app.route("/reset-season", methods=["POST"])
def reset_season():
    global current_race_index
    current_race_index = 0
    Result.query.delete()
    db.session.commit()
    recalculate_all_points()
    return redirect(url_for('index'))

##Route to edit the previous results
@app.route("/edit/<int:race_index>", methods=["GET", "POST"])
def edit_race(race_index):
    # Guard: can't edit a race that hasn't happened yet
    if race_index >= current_race_index or race_index >= len(races):
        return redirect(url_for('index'))
    
    race_name = races[race_index]
    is_sprint = "Sprint" in race_name
    points_scale = [8, 7, 6, 5, 4, 3, 2, 1] if is_sprint else [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
    required_count = len(points_scale)

    # Get the existing results for this race so we can pre-fill the form
    existing_results = Result.query.filter_by(race_name=race_name).order_by(Result.position).all()
    existing_order = [r.driver.name for r in existing_results]

    if request.method == "POST":
        entered_drivers = []
        for i in range(1, required_count + 1):
            driver_name = request.form.get(f"driver_{i}")
            if driver_name:
                entered_drivers.append(driver_name)

        if len(set(entered_drivers)) != len(entered_drivers):
            error = "Every position must be unique!"
            drivers_in_db = Driver.query.order_by(Driver.name).all()
            all_drivers = [d.name for d in drivers_in_db]
            driver_teams = {d.name: d.team for d in drivers_in_db}
            return render_template("edit_race.html",
                                   race=race_name,
                                   required=required_count,
                                   driver_list=all_drivers,
                                   driver_teams=driver_teams,
                                   existing_order=existing_order,
                                   error=error,
                                   race_index=race_index)

        # Delete old results for this race and write new ones
        Result.query.filter_by(race_name=race_name).delete()
        for i, driver_name in enumerate(entered_drivers):
            driver = Driver.query.filter_by(name=driver_name).first()
            if driver:
                result = Result(driver_id=driver.id, race_name=race_name, position=i + 1)
                db.session.add(result)

        db.session.commit()

        # Rebuild all points from scratch
        recalculate_all_points()

        return redirect(url_for('standings'))

    drivers_in_db = Driver.query.order_by(Driver.name).all()
    all_drivers = [d.name for d in drivers_in_db]
    driver_teams = {d.name: d.team for d in drivers_in_db}

    return render_template("edit_race.html",
                           race=race_name,
                           required=required_count,
                           driver_list=all_drivers,
                           driver_teams=driver_teams,
                           existing_order=existing_order,
                           race_index=race_index,
                           error=None)

@app.route("/stats")
def stats():
    drivers = Driver.query.all()
    sorted_drivers = sorted(drivers, key=lambda d: d.points, reverse=True)
    top10 = sorted_drivers[:10]

    timeline = {}
    for driver in top10:
        cumulative = 0
        race_points = []  
        for race_name in races[:current_race_index]:
            # 1. query Result for this driver + race_name
            result = Result.query.filter_by(driver_id=driver.id, race_name=race_name).first()
            # 2. points scale
            if ("Sprint" in race_name):
                points_scale = [8, 7, 6, 5, 4, 3, 2, 1]
            else:
                points_scale =[25, 18, 15, 12, 10, 8, 6, 4, 2, 1]

            # 3. add points if result exists
            if result and 1 <= result.position <= len(points_scale):
                cumulative += points_scale[result.position-1]

            # 4. append
            race_points.append(cumulative)
            pass
        
        timeline[driver.name] = race_points
    
    return render_template(
        "stats.html",
        timeline=timeline,
        race_labels = races[:current_race_index],
        driver_codes=driver_codes,
        top10=top10,
        current_race_index=current_race_index
        )

@app.route("/sync", methods=["POST"])
def sync():
    global current_race_index
    with app.app_context():
        sync_results()
        current_race_index = Result.query.with_entities(Result.race_name).distinct().count()
    return redirect(url_for('standings'))


with app.app_context():
    sync_results()
    current_race_index = Result.query.with_entities(Result.race_name).distinct().count()

if __name__ == "__main__":
    app.run(port=3000, debug=True)