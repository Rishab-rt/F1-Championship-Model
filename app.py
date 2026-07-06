import os 
import random
import joblib
import pandas as pd
import numpy as np
import requests
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import logging
from datetime import date as date_type, datetime

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
    "Silverstone Sprint": 11321,
    "British Grand Prix" : 11326,
}

circuit_info = {
    "albert_park":  {"length": "5.278 km", "laps": 58,  "lap_record": "1:20.235", "lap_record_holder": "Leclerc (2022)",      "type": "Street"},
    "americas":     {"length": "5.513 km", "laps": 56,  "lap_record": "1:36.169", "lap_record_holder": "Leclerc (2019)",      "type": "Permanent"},
    "baku":         {"length": "6.003 km", "laps": 51,  "lap_record": "1:43.009", "lap_record_holder": "Leclerc (2019)",      "type": "Street"},
    "bahrain":      {"length": "5.412 km", "laps": 57,  "lap_record": "1:31.447", "lap_record_holder": "De la Rosa (2005)",   "type": "Permanent"},
    "catalunya":    {"length": "4.675 km", "laps": 66,  "lap_record": "1:16.330", "lap_record_holder": "Verstappen (2021)",   "type": "Permanent"},
    "hungaroring":  {"length": "4.381 km", "laps": 70,  "lap_record": "1:16.627", "lap_record_holder": "Hamilton (2020)",     "type": "Permanent"},
    "interlagos":   {"length": "4.309 km", "laps": 71,  "lap_record": "1:10.540", "lap_record_holder": "Verstappen (2023)",   "type": "Permanent"},
    "jeddah":       {"length": "6.174 km", "laps": 50,  "lap_record": "1:30.734", "lap_record_holder": "Leclerc (2022)",      "type": "Street"},
    "vegas":        {"length": "6.201 km", "laps": 50,  "lap_record": "1:35.490", "lap_record_holder": "Leclerc (2023)",      "type": "Street"},
    "losail":       {"length": "5.380 km", "laps": 57,  "lap_record": "1:24.319", "lap_record_holder": "Russell (2023)",      "type": "Permanent"},
    "miami":        {"length": "5.412 km", "laps": 57,  "lap_record": "1:29.708", "lap_record_holder": "Verstappen (2023)",   "type": "Street"},
    "monaco":       {"length": "3.337 km", "laps": 78,  "lap_record": "1:12.909", "lap_record_holder": "Leclerc (2024)",      "type": "Street"},
    "monza":        {"length": "5.793 km", "laps": 53,  "lap_record": "1:21.046", "lap_record_holder": "Barrichello (2004)",  "type": "Permanent"},
    "villeneuve":   {"length": "4.361 km", "laps": 70,  "lap_record": "1:13.078", "lap_record_holder": "Bottas (2019)",       "type": "Street"},
    "red_bull_ring":{"length": "4.318 km", "laps": 71,  "lap_record": "1:05.619", "lap_record_holder": "Leclerc (2020)",      "type": "Permanent"},
    "rodriguez":    {"length": "4.304 km", "laps": 71,  "lap_record": "1:17.774", "lap_record_holder": "Bottas (2021)",       "type": "Permanent"},
    "shanghai":     {"length": "5.451 km", "laps": 56,  "lap_record": "1:32.238", "lap_record_holder": "Verstappen (2024)",   "type": "Permanent"},
    "silverstone":  {"length": "5.891 km", "laps": 52,  "lap_record": "1:27.097", "lap_record_holder": "Hamilton (2020)",     "type": "Permanent"},
    "marina_bay":   {"length": "4.940 km", "laps": 62,  "lap_record": "1:35.867", "lap_record_holder": "Leclerc (2023)",      "type": "Street"},
    "spa":          {"length": "7.004 km", "laps": 44,  "lap_record": "1:46.286", "lap_record_holder": "Bottas (2018)",       "type": "Permanent"},
    "suzuka":       {"length": "5.807 km", "laps": 53,  "lap_record": "1:30.983", "lap_record_holder": "Verstappen (2023)",   "type": "Permanent"},
    "yas_marina":   {"length": "5.281 km", "laps": 58,  "lap_record": "1:26.103", "lap_record_holder": "Leclerc (2021)",      "type": "Permanent"},
    "zandvoort":    {"length": "4.259 km", "laps": 72,  "lap_record": "1:11.097", "lap_record_holder": "Verstappen (2021)",   "type": "Permanent"},
    "madring":      {"length": "5.059 km", "laps": 59,  "lap_record": "N/A",      "lap_record_holder": "New circuit",         "type": "Street"},
    "monte_carlo":  {"length": "3.337 km", "laps": 78,  "lap_record": "1:12.909", "lap_record_holder": "Leclerc (2024)",      "type": "Street"},
}

race_coords = {
    "Australian Grand Prix":            ("-37.8497", "144.968"),
    "China Sprint":                     ("31.3389", "121.220"),
    "Chinese Grand Prix":               ("31.3389", "121.220"),
    "Japanese Grand Prix":              ("34.8431", "136.541"),
    "Miami Sprint":                     ("25.9581", "-80.2389"),
    "Miami Grand Prix":                 ("25.9581", "-80.2389"),
    "Canada Sprint":                    ("45.5000", "-73.5228"),
    "Canadian Grand Prix":              ("45.5000", "-73.5228"),
    "Monaco Grand Prix":                ("43.7347", "7.42056"),
    "Spanish Grand Prix":               ("41.5700", "2.26111"),
    "Austrian Grand Prix":              ("47.2197", "14.7647"),
    "Silverstone Sprint":               ("52.0786", "-1.01694"),
    "British Grand Prix":               ("52.0786", "-1.01694"),
    "Belgian Grand Prix - SPA":         ("50.4372", "5.97139"),
    "Hungarian Grand Prix":             ("47.5789", "19.2486"),
    "Dutch Sprint":                     ("52.3888", "4.54092"),
    "Dutch Grand Prix":                 ("52.3888", "4.54092"),
    "Italian Grand Prix":               ("45.6156", "9.28111"),
    "Madrid Grand Prix":                ("40.3831", "-3.71444"),
    "Azerbaijan Grand Prix":            ("40.3725", "49.8533"),
    "Singapore Sprint":                 ("1.2914", "103.864"),
    "Singapore Grand Prix":             ("1.2914", "103.864"),
    "Circuit of Americas Grand Prix":   ("30.1328", "-97.6411"),
    "Mexican Grand Prix":               ("19.4042", "-99.0907"),
    "São Paulo Grand Prix":             ("-23.7036", "-46.6997"),
    "Las Vegas Grand Prix":             ("36.1147", "-115.173"),
    "Qatar Grand Prix":                 ("25.4900", "51.4542"),
    "Abu Dhabi Grand Prix":             ("24.4672", "54.6031"),
}

race_dates = {
    "Australian Grand Prix":            "2026-03-15",
    "China Sprint":                     "2026-03-21",
    "Chinese Grand Prix":               "2026-03-22",
    "Japanese Grand Prix":              "2026-04-05",
    "Miami Sprint":                     "2026-05-02",
    "Miami Grand Prix":                 "2026-05-03",
    "Canada Sprint":                    "2026-06-13",
    "Canadian Grand Prix":              "2026-06-14",
    "Monaco Grand Prix":                "2026-05-24",
    "Spanish Grand Prix":               "2026-06-28",
    "Austrian Grand Prix":              "2026-07-05",
    "Silverstone Sprint":               "2026-07-18",
    "British Grand Prix":               "2026-07-19",
    "Belgian Grand Prix - SPA":         "2026-08-02",
    "Hungarian Grand Prix":             "2026-08-02",
    "Dutch Sprint":                     "2026-08-29",
    "Dutch Grand Prix":                 "2026-08-30",
    "Italian Grand Prix":               "2026-09-06",
    "Madrid Grand Prix":                "2026-09-13",
    "Azerbaijan Grand Prix":            "2026-09-20",
    "Singapore Sprint":                 "2026-10-03",
    "Singapore Grand Prix":             "2026-10-04",
    "Circuit of Americas Grand Prix":   "2026-10-18",
    "Mexican Grand Prix":               "2026-10-25",
    "São Paulo Grand Prix":             "2026-11-08",
    "Las Vegas Grand Prix":             "2026-11-21",
    "Qatar Grand Prix":                 "2026-11-28",
    "Abu Dhabi Grand Prix":             "2026-12-06",
}

race_to_circuit_id = {
    "Australian Grand Prix":          "albert_park",
    "Chinese Grand Prix":             "shanghai",
    "China Sprint":                   "shanghai",
    "Japanese Grand Prix":            "suzuka",
    "Miami Grand Prix":               "miami",
    "Miami Sprint":                   "miami",
    "Canadian Grand Prix":            "villeneuve",
    "Canada Sprint":                  "villeneuve",
    "Monaco Grand Prix":              "monaco",
    "Spanish Grand Prix":             "catalunya",
    "Austrian Grand Prix":            "red_bull_ring",
    "Silverstone Sprint":             "silverstone",
    "British Grand Prix":             "silverstone",
    "Belgian Grand Prix - SPA":       "spa",
    "Hungarian Grand Prix":           "hungaroring",
    "Dutch Sprint":                   "zandvoort",
    "Dutch Grand Prix":               "zandvoort",
    "Italian Grand Prix":             "monza",
    "Madrid Grand Prix":              "madring",
    "Azerbaijan Grand Prix":          "baku",
    "Singapore Sprint":               "marina_bay",
    "Singapore Grand Prix":           "marina_bay",
    "Circuit of Americas Grand Prix": "americas",
    "Mexican Grand Prix":             "rodriguez",
    "São Paulo Grand Prix":           "interlagos",
    "Las Vegas Grand Prix":           "vegas",
    "Qatar Grand Prix":               "losail",
    "Abu Dhabi Grand Prix":           "yas_marina",
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

def get_circuit_chaos(circuit_id):
    """Fetch last 3 seasons of results for a circuit and compute mean absolute grid-to-finish delta."""
    deltas = []
    for year in [2023, 2024, 2025]:
        try:
            r = requests.get(
                f"https://api.jolpi.ca/ergast/f1/{year}/circuits/{circuit_id}/results.json",
                timeout=5
            ).json()
            races = r["MRData"]["RaceTable"]["Races"]
            for race in races:
                for result in race["Results"]:
                    try:
                        grid = int(result["grid"])
                        pos = int(result["position"])
                        if grid > 0:  # ignore pit lane starts (grid=0)
                            deltas.append(abs(grid - pos))
                    except (ValueError, KeyError):
                        continue
        except Exception:
            continue
    return round(np.mean(deltas), 2) if deltas else 2.0  # fallback to 2.0

def get_race_weather(lat, lon, race_date_str):
    """Fetch weather for a race — historical if past, forecast if upcoming."""
    try:
        # Parse the date
        race_date = datetime.strptime(race_date_str, "%Y-%m-%d").date()
        
        # Determine whether to use the archive or forecast API
        if race_date < date_type.today():
            url = "https://archive-api.open-meteo.com/v1/archive"
        else:
            url = "https://api.open-meteo.com/v1/forecast"

        if lat == "0" and lon == "0":
            tz = "UTC"
        else:
            tz = "auto"
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": race_date_str, 
            "end_date": race_date_str,   
            "daily": "precipitation_sum,temperature_2m_max",  
            "timezone": tz
        }
        
        # 1. Make the request (DO NOT chain .json() here yet)
        r = requests.get(url, params=params, timeout=10)
        
        # 2. Raise an error if the API responded with a 404, 500, etc.
        r.raise_for_status()
        
        # 3. Parse the JSON safely
        data = r.json()
        rain = data["daily"]["precipitation_sum"][0] or 0.0
        temp = data["daily"]["temperature_2m_max"][0] or 20.0
        
        return rain, temp
        
    except ValueError as e:
        # Catches bad date formats passed into the function
        logging.error(f"Date formatting error for '{race_date_str}': {e}")
        return 0.0, 20.0

    except requests.exceptions.RequestException as e:
        # Catches network drops, timeouts, and bad HTTP status codes
        logging.error(f"Network/API error fetching weather for {race_date_str} at {lat}, {lon}: {e}")
        return 0.0, 20.0
        
    except (KeyError, IndexError, TypeError) as e:
        # Catches issues if Open-Meteo changes their JSON format or returns empty arrays
        logging.error(f"Data parsing error for weather on {race_date_str}. Unexpected JSON structure: {e}")
        return 0.0, 20.0
        
    except Exception as e:
        # The ultimate fallback for anything totally unexpected
        logging.error(f"An unexpected error occurred while fetching weather for {race_date_str}: {e}")
        return 0.0, 20.0

def get_quali_grid(race_name):

    circuit_id = race_to_circuit_id.get(race_name)
    race_date = race_dates.get(race_name)

    if not circuit_id or not race_date:
        return None
    
    year = race_date[:4]
    try:
        # 1. Capitalize for OpenF1 (turns "silverstone" into "Silverstone")
        search_circuit = circuit_id.capitalize()
        
        meetings = requests.get(
            "https://api.openf1.org/v1/meetings",
            params={"year": year, "circuit_short_name": search_circuit},
            timeout=10
        ).json()
        
        # 2. PREVENT THE KEYERROR: Check if API returned an error dictionary instead of a list
        if isinstance(meetings, dict) and 'detail' in meetings:
            return None
            
        if not meetings:
            return None
            
        meeting_key = meetings[0]["meeting_key"]

        is_sprint = "Sprint" in race_name
        target_session = "Sprint Qualifying" if is_sprint else "Qualifying"

        sessions = requests.get(
            "https://api.openf1.org/v1/sessions",
            params={"meeting_key": meeting_key, "session_name": target_session},
            timeout=10
        ).json()
        
        # Safely handle potential dictionary errors here too!
        if isinstance(sessions, dict) and 'detail' in sessions:
            return None
            
        if not sessions:
            return None
            
        quali_session_key = sessions[0]["session_key"]

        positions_r = requests.get(
            "https://api.openf1.org/v1/position",
            params={"session_key": quali_session_key},
            timeout=10
        ).json()
        
        if not positions_r or not isinstance(positions_r, list):
            return None


        latest = {}
        for entry in positions_r:
            num = entry["driver_number"]
            latest[num] = entry["position"]

        grid = {}
        for driver_num, pos in latest.items():
            name = driver_number_to_name.get(driver_num)
            if name:
                grid[name] = pos

        if not grid:
            return None

        return grid

    except Exception as e:
        return None


def get_meeting_key(session_key):
    """Get the meeting key for a given race session key."""
    r = requests.get(
        f"https://api.openf1.org/v1/sessions?session_key={session_key}",
        timeout=10
    ).json()
    return r[0]["meeting_key"]

def sync_results():
    print("🔄 Fetching official final race classifications (including Sprints!)...")
    Result.query.delete()
    db.session.commit()
    
    schedule_url = "https://api.jolpi.ca/ergast/f1/2026.json"
    try:
        schedule_res = requests.get(schedule_url).json()
        races_list = schedule_res["MRData"]["RaceTable"]["Races"]
    except Exception as e:
        print(f"⚠️ Could not fetch 2026 schedule: {e}")
        return

    for driver in Driver.query.all():
        driver.points = 0
    db.session.commit()

    sprint_name_map = {
        "Chinese Grand Prix": "China Sprint",
        "Miami Grand Prix": "Miami Sprint",
        "Canadian Grand Prix": "Canada Sprint",
        "Austrian Grand Prix": "Austria Sprint",
        "United States Grand Prix": "Austin Sprint",
        "São Paulo Grand Prix": "Brazil Sprint",
        "Qatar Grand Prix": "Qatar Sprint"
    }

    for race in races_list:
        round_num = race["round"]
        main_race_name = race["raceName"]
        
        sprint_url = f"https://api.jolpi.ca/ergast/f1/2026/{round_num}/sprint.json"
        try:
            sprint_res = requests.get(sprint_url).json()
            sprint_data = sprint_res["MRData"]["RaceTable"]["Races"]
            
            if len(sprint_data) > 0:
                sprint_results = sprint_data[0]["SprintResults"]
                sprint_name = sprint_name_map.get(main_race_name, f"{main_race_name} Sprint")
                
                print(f"🏎️ Syncing Sprint for Round {round_num}: {sprint_name}...")
                
                for entry in sprint_results:
                    driver_last_name = entry["Driver"]["familyName"]
                    final_position = int(entry["position"])
                    
                    local_driver = Driver.query.filter(Driver.name.like(f"%{driver_last_name}%")).first()
                    if local_driver:
                        db.session.add(Result(
                            driver_id=local_driver.id,
                            race_name=sprint_name,
                            position=final_position,
                            source="api"
                        ))
        except Exception:
            pass 
            
        print(f"🏁 Syncing Main Race for Round {round_num}: {main_race_name}...")
        results_url = f"https://api.jolpi.ca/ergast/f1/2026/{round_num}/results.json"
        try:
            res_data = requests.get(results_url).json()
            race_data = res_data["MRData"]["RaceTable"]["Races"]
            
            if len(race_data) == 0:
                print(f"⏭️ Round {round_num} has no final classifications yet. Skipping.")
                continue
                
            race_results = race_data[0]["Results"]
        except Exception:
            print(f"⏭️ Round {round_num} API error. Skipping.")
            continue

        for entry in race_results:
            driver_last_name = entry["Driver"]["familyName"]
            final_position = int(entry["position"])
            
            local_driver = Driver.query.filter(Driver.name.like(f"%{driver_last_name}%")).first()
            if local_driver:
                db.session.add(Result(
                    driver_id=local_driver.id,
                    race_name=main_race_name,
                    position=final_position,
                    source="api"
                ))

        db.session.commit()
        
    recalculate_all_points()
    print("✅ All local standings perfectly synchronized with official classifications!")

@app.route("/", methods=["GET", "POST"])
def index():
    global current_race_index
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
        entered_drivers = []
        for i in range(1, required_count + 1):
            driver_name = request.form.get(f"driver_{i}")
            if driver_name:
                entered_drivers.append(driver_name)

        if len(set(entered_drivers)) != len(entered_drivers):
            error_message = "⚠️ You selected the same driver multiple times. Every position must be unique!"
        else:
            for i, driver_name in enumerate(entered_drivers):
                driver = Driver.query.filter_by(name=driver_name).first()
                if driver:
                    driver.points += current_points[i]

                    result = Result(driver_id=driver.id, race_name=current_race, position=i + 1, source = "manual")
                    db.session.add(result)
            
            db.session.commit()
            current_race_index += 1    
            return redirect(url_for('index'))
        
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
    
    def f1_sorting_key(driver):
        finish_counts = [0] * 20 
        for r in driver.results:
            if 1 <= r.position <= 20:
                finish_counts[r.position - 1] += 1
        return (driver.points, *finish_counts)

    sorted_drivers = sorted(drivers, key=f1_sorting_key, reverse=True)

    constructors_dict = {}
    for d in drivers:
        constructors_dict[d.team] = constructors_dict.get(d.team, 0) + d.points
    sorted_constructors = sorted(constructors_dict.items(), key=lambda x: x[1], reverse=True)

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

#statistics page
@app.route("/stats")
def stats():
    drivers = Driver.query.all()
    sorted_drivers = sorted(drivers, key=lambda d: d.points, reverse=True)
    top10 = sorted_drivers[:10]

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
    count = Result.query.with_entities(Result.race_name).distinct().count()
    print(f"After sync: {count} distinct races in DB")
    current_race_index = count
    return redirect(url_for('standings'))

@app.route("/predictions")
def predictions():
    drivers = Driver.query.all()
    sorted_drivers = sorted(drivers, key=lambda d: d.points, reverse=True)
    remaining_races = races[current_race_index:]
    drivers_dict = {driver.name: driver for driver in sorted_drivers}
    all_driver_names = [d.name for d in sorted_drivers]
    N_SIMS = 1000

    # Build teammate lookup
    team_avgs = {}
    for driver in sorted_drivers:
        recent_results = Result.query.filter_by(driver_id=driver.id).order_by(Result.id.desc()).limit(5).all()
        team_avgs[driver.name] = {
            "team": driver.team,
            "avg": np.mean([r.position for r in recent_results]) if recent_results else 10.0
        }

    driver_features = {}
    for driver in sorted_drivers:
        recent_results = Result.query.filter_by(driver_id=driver.id).order_by(Result.id.desc()).limit(current_race_index).all()
        avg_position = np.mean([r.position for r in recent_results]) if recent_results else 10.0
        teammate_avgs = [
            v["avg"] for k, v in team_avgs.items()
            if v["team"] == driver.team and k != driver.name
        ]
        constructor_form = np.mean(teammate_avgs) if teammate_avgs else avg_position
        driver_features[driver.name] = {
            "driver_form": avg_position,
            "constructor_form": constructor_form,
            "cumulative_points": driver.points,
            "circuit_avg": avg_position
        }

    circuit_avg_cache = {}
    for driver in sorted_drivers:
        for race_name in remaining_races:
            circuit_results = Result.query.filter_by(
                driver_id=driver.id, race_name=race_name
            ).order_by(Result.id.desc()).limit(current_race_index).all()
            circuit_avg_cache[(driver.name, race_name)] = (
                np.mean([r.position for r in circuit_results])
                if circuit_results else driver_features[driver.name]["driver_form"]
            )

    race_weather_cache = {}
    for race_name in remaining_races:
        lat, lon = race_coords.get(race_name, ("0", "0"))
        race_date = race_dates.get(race_name, str(date_type.today()))
        race_weather_cache[race_name] = get_race_weather(lat, lon, race_date)

    driver_form_arr = np.array([driver_features[n]["driver_form"] for n in all_driver_names])
    constructor_form_arr = np.array([driver_features[n]["constructor_form"] for n in all_driver_names])
    cumulative_pts_arr = np.array([driver_features[n]["cumulative_points"] for n in all_driver_names])
    name_to_idx = {name: i for i, name in enumerate(all_driver_names)}

    total_points = np.array([driver_features[n]["cumulative_points"] for n in all_driver_names], dtype=float)
    total_points_accum = np.zeros(len(all_driver_names))
    championship_counts = np.zeros(len(all_driver_names))

    for _ in range(N_SIMS):
        projected_points = np.array([driver_features[n]["cumulative_points"] for n in all_driver_names], dtype=float)

        for race_name in remaining_races:
            is_sprint = "Sprint" in race_name
            points_scale = [8, 7, 6, 5, 4, 3, 2, 1] if is_sprint else [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
            rain_mm, temp_c = race_weather_cache[race_name]

            circuit_avg_arr = np.array([
                circuit_avg_cache[(name, race_name)] for name in all_driver_names
            ])

            noise = np.random.normal(0, 3, len(all_driver_names))
            grid_order_idx = np.argsort(driver_form_arr + noise)
            grid_positions = np.empty(len(all_driver_names), dtype=int)
            grid_positions[grid_order_idx] = np.arange(1, len(all_driver_names) + 1)

            X_batch = np.column_stack([
                grid_positions,
                driver_form_arr,
                constructor_form_arr,
                projected_points,
                circuit_avg_arr,
                np.full(len(all_driver_names), rain_mm),
                np.full(len(all_driver_names), temp_c)
            ])
            predicted_positions = model.predict(X_batch)

            sorted_idx = np.argsort(predicted_positions)
            for pos, driver_idx in enumerate(sorted_idx):
                if pos < len(points_scale):
                    projected_points[driver_idx] += points_scale[pos]

        champion_idx = np.argmax(projected_points)
        championship_counts[champion_idx] += 1
        total_points_accum += projected_points

    avg_points = {all_driver_names[i]: round(total_points_accum[i] / N_SIMS) for i in range(len(all_driver_names))}
    projected_standings = sorted(avg_points.items(), key=lambda x: x[1], reverse=True)

    championship_pct = {}
    for i, name in enumerate(all_driver_names):
        raw = round((championship_counts[i] / N_SIMS) * 100)
        championship_pct[name] = 0.5 if raw == 0 else min(95, raw)

    constructor_points = {}
    for name, pts in avg_points.items():
        team = drivers_dict[name].team
        constructor_points[team] = constructor_points.get(team, 0) + pts
    constructor_standings = sorted(constructor_points.items(), key=lambda x: x[1], reverse=True)

    return render_template(
        "predictions.html",
        drivers=sorted_drivers,
        projected_standings=projected_standings,
        remaining_races=remaining_races,
        current_race_index=current_race_index,
        driver_teams={d.name: d.team for d in sorted_drivers},
        championship_pct=championship_pct,
        constructor_standings=constructor_standings,
    )

@app.route("/raceprediction")
def raceprediction():
    drivers = Driver.query.all()
    sorted_drivers = sorted(drivers, key=lambda d: d.points, reverse=True)

    race = races[current_race_index]

    lat, lon = race_coords.get(race, ("0", "0"))
    race_date = race_dates.get(race, str(date_type.today()))
    rain_mm, temp_c = get_race_weather(lat, lon, race_date)

    # Build teammate lookup first
    team_avgs = {}
    for driver in sorted_drivers:
        recent_results = Result.query.filter_by(driver_id=driver.id).order_by(Result.id.desc()).limit(5).all()
        team_avgs[driver.name] = {
            "team": driver.team,
            "avg": np.mean([r.position for r in recent_results]) if recent_results else 10.0
        }

    driver_features = {}
    for driver in sorted_drivers:
        recent_results = Result.query.filter_by(driver_id=driver.id).order_by(Result.id.desc()).limit(current_race_index).all()
        avg_position = np.mean([r.position for r in recent_results]) if recent_results else 10.0

        teammate_avgs = [
            v["avg"] for k, v in team_avgs.items()
            if v["team"] == driver.team and k != driver.name
        ]
        constructor_form = np.mean(teammate_avgs) if teammate_avgs else avg_position

        driver_features[driver.name] = {
            "driver_form": avg_position,
            "constructor_form": constructor_form,
            "cumulative_points": driver.points
        }

    next_race_name = races[current_race_index]
    for driver in sorted_drivers:
        circuit_results = Result.query.filter_by(driver_id=driver.id, race_name=next_race_name).order_by(Result.id.desc()).limit(current_race_index).all()
        if circuit_results:
            circuit_avg = np.mean([r.position for r in circuit_results])
        else:
            circuit_avg = driver_features[driver.name]["driver_form"]
        driver_features[driver.name]["circuit_avg"] = circuit_avg
    
    circuit_id = race_to_circuit_id.get(race, "albert_park")
    chaos_factor = get_circuit_chaos(circuit_id)
    print(f"Chaos factor for {race} ({circuit_id}): {chaos_factor}")
    quali_grid = get_quali_grid(race)
    quali_used = quali_grid is not None

    # --- Monte Carlo: 1000 simulations ---
    N_SIMS = 1000
    all_driver_names = [d.name for d in sorted_drivers]
    
    position_counts = {name: {} for name in all_driver_names}
    podium_counts = {name: 0 for name in all_driver_names}

    for _ in range(N_SIMS):
        if quali_used:
            grid_order = sorted(all_driver_names, key=lambda name: quali_grid.get(name, 20) + random.gauss(0, chaos_factor * 0.5))
        else:
            grid_order = sorted(all_driver_names, key=lambda name: driver_features[name]["driver_form"] + random.gauss(0, chaos_factor))

        sim_predictions = []
        for i, driver_name in enumerate(grid_order):
            features = driver_features[driver_name]
            grid_pos = quali_grid.get(driver_name, i + 1) if quali_used else i + 1
            X_pred = np.array([[
                grid_pos,
                features["driver_form"],
                features["constructor_form"],
                features["cumulative_points"],
                features["circuit_avg"],
                rain_mm,
                temp_c
            ]])
            base_prediction = model.predict(X_pred)[0]
            predicted_position = base_prediction + random.gauss(0, 2.0)
            sim_predictions.append((driver_name, predicted_position))

        sim_predictions.sort(key=lambda x: x[1])

        for pos, (driver_name, _) in enumerate(sim_predictions):
            actual_pos = pos + 1
            position_counts[driver_name][actual_pos] = position_counts[driver_name].get(actual_pos, 0) + 1
            if actual_pos <= 3:
                podium_counts[driver_name] += 1

    race_predictions = []
    for driver_name in all_driver_names:
        counts = position_counts[driver_name]
        if counts:
            most_common_pos = max(counts, key=counts.get)
        else:
            most_common_pos = 20
        podium_pct = round((podium_counts[driver_name] / N_SIMS) * 100,1)
        race_predictions.append((driver_name, most_common_pos, podium_pct))

    race_predictions.sort(key=lambda x: x[1])

    return render_template(
        "raceprediction.html",
        race_predictions=race_predictions,
        race=race,
        current_race_index=current_race_index,
        rain_mm=rain_mm,
        temp_c=temp_c,
        quali_used=quali_used
    )

@app.route("/save-simulation", methods=["POST"])
def save_simulation():
    global current_race_index

    race_name = races[current_race_index]
    num_drivers = int(request.form.get("num_drivers"))

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

    # Redirect to finale if last race just saved
    if current_race_index >= len(races):
        return redirect(url_for('finale'))

    return redirect(url_for('index'))


@app.route("/finale")
def finale():
    drivers = Driver.query.order_by(Driver.points.desc()).all()

    # Driver champion
    champion = drivers[0]

    # Constructor standings — sum points per team
    constructor_points = {}
    for driver in drivers:
        constructor_points[driver.team] = constructor_points.get(driver.team, 0) + driver.points
    constructor_standings = sorted(constructor_points.items(), key=lambda x: x[1], reverse=True)

    return render_template(
        "finale.html",
        champion=champion,
        drivers=drivers,
        constructor_standings=constructor_standings,
    )

@app.route("/circuitguide")
def circuitguide():
    # Fetch circuits list
    response = requests.get("https://api.jolpi.ca/ergast/f1/2026/circuits.json")
    data = response.json()
    circuits = data["MRData"]["CircuitTable"]["Circuits"]

    # Fetch ALL 2025 results with pagination
    races_2025 = []
    offset = 0
    while True:
        r = requests.get(f"https://api.jolpi.ca/ergast/f1/2025/results.json?limit=30&offset={offset}").json()
        batch = r["MRData"]["RaceTable"]["Races"]
        if not batch:
            break
        races_2025.extend(batch)
        total = int(r["MRData"]["total"])
        offset += 30
        if offset >= total:
            break

    # Fetch ALL 2026 results with pagination
    races_2026 = []
    offset = 0
    while True:
        r = requests.get(f"https://api.jolpi.ca/ergast/f1/2026/results.json?limit=30&offset={offset}").json()
        batch = r["MRData"]["RaceTable"]["Races"]
        if not batch:
            break
        races_2026.extend(batch)
        total = int(r["MRData"]["total"])
        offset += 30
        if offset >= total:
            break

    # Build winner lookup — deduplicate by circuitId
    recent_winners = {}

    for race in races_2025:
        circuit_id = race["Circuit"]["circuitId"]
        if circuit_id in recent_winners:
            continue
        if race.get("Results"):
            winner = next((r for r in race["Results"] if r["position"] == "1"), None)
            if winner:
                recent_winners[circuit_id] = {
                    "name": f"{winner['Driver']['givenName']} {winner['Driver']['familyName']}",
                    "year": "2025"
                }

    for race in races_2026:
        circuit_id = race["Circuit"]["circuitId"]
        if race.get("Results"):
            winner = next((r for r in race["Results"] if r["position"] == "1"), None)
            if winner:
                recent_winners[circuit_id] = {
                    "name": f"{winner['Driver']['givenName']} {winner['Driver']['familyName']}",
                    "year": "2026"
                }

    return render_template(
        "circuitguide.html",
        circuits=circuits,
        races=races,
        current_race_index=current_race_index,
        circuit_info=circuit_info,
        recent_winners=recent_winners
    )



if __name__ == "__main__":
    with app.app_context():
        if Driver.query.count() == 0:
            print("🏎️ Populating empty database with drivers...")
            for name, team in driver_to_team.items():
                db.session.add(Driver(name=name, team=team, points=0))
            db.session.commit()
            print("✅ Drivers loaded.")
        try:
            current_race_index = Result.query.with_entities(Result.race_name).distinct().count()
            sync_results()
            print(f"✅ Synced successfully. {current_race_index} races loaded.")
        except Exception as e:
            print(f"⚠️ Sync failed: {e}")
    app.run(port=3000, debug=True)