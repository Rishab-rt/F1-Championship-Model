import os 
import random
import joblib
import pandas as pd
import numpy as np
import requests
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

model = joblib.load("f1_model.pkl")
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
    source = db.Column(db.String(20), default="manual")
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable=False)
    race_name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    
    
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
    55: "Sainz",
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
        print(f"Checking {race_name}...")
        
        # Only skip if already synced from API — allow overwriting manual entries
        existing = Result.query.filter_by(race_name=race_name, source="api").first()
        if existing:
            print(f"Already synced from API, skipping")
            continue
        
        # Delete any manual entries for this race before inserting API data
        Result.query.filter_by(race_name=race_name).delete()
        db.session.commit()

        print(f" --> Fetching from OpenF1")
        response = requests.get(f"https://api.openf1.org/v1/position?session_key={session_key}")
        positions = response.json()

        if not isinstance(positions, list) or len(positions) == 0:
            print(f"  → No data returned, skipping")
            continue

        final_positions = {}
        for entry in positions:
            driver_number = entry["driver_number"]
            final_positions[driver_number] = entry["position"]

        sorted_positions = sorted(final_positions.items(), key=lambda x: x[1])

        for driver_number, position in sorted_positions:
            driver_name = driver_number_to_name.get(driver_number)
            if not driver_name:
                continue
            driver = Driver.query.filter_by(name=driver_name).first()
            if driver:
                result = Result(driver_id=driver.id, race_name=race_name, position=position, source="api")
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

                    result = Result(driver_id=driver.id, race_name=current_race, position=i + 1, source = "manual")
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
                result = Result(driver_id=driver.id, race_name=race_name, position=i + 1, source = "manual")
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

    # Fetch all results once for efficiency
    all_results = Result.query.all()
    results_lookup = {}
    for r in all_results:
        key = (r.driver_id, r.race_name)
        results_lookup[key] = r

    timeline = {}
    for driver in top10:
        cumulative = 0
        race_points = []
        for race_name in races[:current_race_index]:
            result = results_lookup.get((driver.id, race_name))
            if "Sprint" in race_name:
                points_scale = [8, 7, 6, 5, 4, 3, 2, 1]
            else:
                points_scale = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
            if result and 1 <= result.position <= len(points_scale):
                cumulative += points_scale[result.position - 1]
            race_points.append(cumulative)
        timeline[driver.name] = race_points

    # Heatmap data
    heatmap = {}
    for driver in sorted_drivers:
        positions = []
        for race_name in races[:current_race_index]:
            result = results_lookup.get((driver.id, race_name))
            positions.append(result.position if result else 0)
        heatmap[driver.name] = positions

    # Group drivers by team
    teams = {}
    for driver in sorted_drivers:
        team = driver.team
        if team not in teams:
            teams[team] = []
        teams[team].append(driver)

    # Head to head stats per team
    h2h_data = {}
    for team, team_drivers in teams.items():
        if len(team_drivers) != 2:
            continue

        d1, d2 = team_drivers[0], team_drivers[1]

        d1_points = d1.points
        d2_points = d2.points

        d1_wins = sum(1 for r in d1.results if r.position == 1)
        d2_wins = sum(1 for r in d2.results if r.position == 1)

        d1_podiums = sum(1 for r in d1.results if r.position <= 3)
        d2_podiums = sum(1 for r in d2.results if r.position <= 3)

        d1_ahead = 0
        d2_ahead = 0
        for race_name in races[:current_race_index]:
            r1 = results_lookup.get((d1.id, race_name))
            r2 = results_lookup.get((d2.id, race_name))
            if r1 and r2:
                if r1.position < r2.position:
                    d1_ahead += 1
                else:
                    d2_ahead += 1

        h2h_data[team] = {
            "d1": d1.name,
            "d2": d2.name,
            "d1_points": d1_points,
            "d2_points": d2_points,
            "d1_wins": d1_wins,
            "d2_wins": d2_wins,
            "d1_podiums": d1_podiums,
            "d2_podiums": d2_podiums,
            "d1_ahead": d1_ahead,
            "d2_ahead": d2_ahead,
        }

    return render_template(
        "stats.html",
        timeline=timeline,
        race_labels=races[:current_race_index],
        driver_codes=driver_codes,
        top10=top10,
        current_race_index=current_race_index,
        heatmap=heatmap,
        all_drivers=sorted_drivers,
        h2h_data=h2h_data
    )

@app.route("/sync", methods=["POST"])
def sync():
    global current_race_index
    sync_results()
    current_race_index = Result.query.with_entities(Result.race_name).distinct().count()
    return redirect(url_for('standings'))

@app.route("/predictions")
def predictions():
    drivers = Driver.query.all()
    sorted_drivers = sorted(drivers, key=lambda d: d.points, reverse=True)
    remaining_races = races[current_race_index:]

    driver_features = {}
    for driver in sorted_drivers:
        recent_results = Result.query.filter_by(driver_id=driver.id).order_by(Result.id.desc()).limit(current_race_index).all()
        avg_position = np.mean([r.position for r in recent_results]) if recent_results else 10.0
        driver_features[driver.name] = {
            "driver_form": avg_position,
            "constructor_form": avg_position,
            "cumulative_points": driver.points,
            "circuit_avg": avg_position  # default, gets overwritten per race
        }

    projected_points = {driver.name: driver.points for driver in sorted_drivers}

    for race_name in remaining_races:
        is_sprint = "Sprint" in race_name
        points_scale = [8, 7, 6, 5, 4, 3, 2, 1] if is_sprint else [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]

        # Update circuit_avg for this specific race
        for driver in sorted_drivers:
            circuit_results = Result.query.filter_by(
                driver_id=driver.id,
                race_name=race_name
            ).order_by(Result.id.desc()).limit(3).all()

            if circuit_results:
                driver_features[driver.name]["circuit_avg"] = np.mean([r.position for r in circuit_results])
            else:
                driver_features[driver.name]["circuit_avg"] = driver_features[driver.name]["driver_form"]

        # Estimate grid with noise
        grid_order = sorted(
            driver_features.keys(),
            key=lambda name: driver_features[name]["driver_form"] + random.gauss(0, 3)
        )

        # Build features and predict for each driver
        race_predictions = []
        for i, driver_name in enumerate(grid_order):
            features = driver_features[driver_name]
            X_pred = np.array([[
                i + 1,
                features["driver_form"],
                features["constructor_form"],
                features["cumulative_points"],
                features["circuit_avg"]
            ]])
            predicted_position = model.predict(X_pred)[0]
            race_predictions.append((driver_name, predicted_position))

        # Sort by predicted position and award points
        race_predictions.sort(key=lambda x: x[1])
        for pos, (driver_name, _) in enumerate(race_predictions):
            if pos < len(points_scale):
                projected_points[driver_name] += points_scale[pos]

    # Sort final projected standings
    projected_standings = sorted(
        projected_points.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return render_template(
        "predictions.html",
        drivers=sorted_drivers,
        projected_standings=projected_standings,
        remaining_races=remaining_races,
        current_race_index=current_race_index,
        driver_teams={d.name: d.team for d in sorted_drivers}
    )

@app.route("/raceprediction")
def raceprediction():
    drivers = Driver.query.all()
    sorted_drivers = sorted(drivers, key = lambda d: d.points, reverse=True)

    race = races[current_race_index]
    is_sprint = "Sprint" in race
    driver_features = {}

    for driver in sorted_drivers:
        recent_results = Result.query.filter_by(driver_id=driver.id).order_by(Result.id.desc()).limit(current_race_index).all()
        avg_position = np.mean([r.position for r in recent_results]) if recent_results else 10.0
        driver_features[driver.name] = {
            "driver_form": avg_position,
            "constructor_form": avg_position,
            "cumulative_points": driver.points
        }
    
    # Add circuit-specific bias
    next_race_name = races[current_race_index]
    for driver in sorted_drivers:
    # Find historical results at this specific circuit
        circuit_results = Result.query.filter_by(driver_id=driver.id,race_name=next_race_name).order_by(Result.id.desc()).limit(3).all()
        if circuit_results:
            circuit_avg = np.mean([r.position for r in circuit_results])
        else:
        # Fall back to overall driver form if no history at this circuit
            circuit_avg = driver_features[driver.name]["driver_form"]
    
        driver_features[driver.name]["circuit_avg"] = circuit_avg
    
    # Estimate grid with noise
    grid_order = sorted(
        driver_features.keys(),
        key=lambda name: driver_features[name]["driver_form"] + random.gauss(0, 2)
    )

    # Predict finishing order
    race_predictions = []
    for i, driver_name in enumerate(grid_order):
        features = driver_features[driver_name]
        X_pred = np.array([[
            i+1,
            features["driver_form"],
            features["constructor_form"],
            features["cumulative_points"],
            features["circuit_avg"]
        ]])
        predicted_position = model.predict(X_pred)[0]
        race_predictions.append((driver_name, predicted_position))

    race_predictions.sort(key=lambda x: x[1])

    return render_template(
        "raceprediction.html",
        race_predictions=race_predictions,
        race=race,
        current_race_index=current_race_index
    )

@app.route("/save-simulation", methods=["POST"])
def save_simulation():
    global current_race_index
    
    # Get the predicted order from the form
    race_name = races[current_race_index]
    num_drivers = int(request.form.get("num_drivers"))
    
    # Delete any existing results for this race
    Result.query.filter_by(race_name=race_name).delete()
    
    for i in range(num_drivers):
        driver_name = request.form.get(f"driver_{i}")
        if driver_name:
            driver = Driver.query.filter_by(name=driver_name).first()
            if driver:
                result = Result(
                    driver_id=driver.id,
                    race_name=race_name,
                    position=i + 1,
                    source="simulation"
                )
                db.session.add(result)
    
    db.session.commit()
    recalculate_all_points()
    current_race_index += 1
    return redirect(url_for('index'))

@app.route("/circuitguide")
def circuitguide():
    response = requests.get("https://api.jolpi.ca/ergast/f1/2026/circuits.json")
    data = response.json()
    circuits = data["MRData"]["CircuitTable"]["Circuits"]
    
    return render_template(
        "circuitguide.html",
        circuits=circuits,
        races=races,
        current_race_index=current_race_index
    )




if __name__ == "__main__":
    with app.app_context():
        try:
            current_race_index = Result.query.with_entities(Result.race_name).distinct().count()
            print(f"✅ Synced successfully. {current_race_index} races loaded.")
        except Exception as e:
            print(f"⚠️ Sync failed: {e}")
    app.run(port=3000, debug=True)