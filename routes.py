from flask import Blueprint, render_template, request, redirect, url_for
import random
import numpy as np
import joblib
import requests
from datetime import date as date_type
from extensions import db
from models import Driver, Result
from utils import recalculate_all_points, sync_results, get_race_weather, get_circuit_chaos, get_quali_grid
from data import *

main = Blueprint('main', __name__)
model = joblib.load("f1_model.pkl")

# Master state for the live race calendar index
current_race_index = 0

def init_race_index():
    global current_race_index
    current_race_index = Result.query.with_entities(Result.race_name).distinct().count()

@main.route("/", methods=["GET", "POST"])
def index():
    global current_race_index
    if current_race_index >= len(races):
        return redirect(url_for('main.standings'))
    
    current_race = races[current_race_index]
    current_points = [8, 7, 6, 5, 4, 3, 2, 1] if "Sprint" in current_race else [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
    required_count = len(current_points)
    error_message = None

    if request.method == "POST":
        entered_drivers = []
        for i in range(1, required_count + 1):
            driver_name = request.form.get(f"driver_{i}")
            if driver_name: entered_drivers.append(driver_name)

        if len(set(entered_drivers)) != len(entered_drivers):
            error_message = "⚠️ You selected the same driver multiple times. Every position must be unique!"
        else:
            for i, driver_name in enumerate(entered_drivers):
                driver = Driver.query.filter_by(name=driver_name).first()
                if driver:
                    driver.points += current_points[i]
                    db.session.add(Result(driver_id=driver.id, race_name=current_race, position=i + 1, source="manual"))
            db.session.commit()
            current_race_index += 1    
            return redirect(url_for('main.index'))
        
    drivers_in_db = Driver.query.order_by(Driver.name).all()
    all_drivers = [d.name for d in drivers_in_db]
        
    return render_template("index.html", race=current_race, required=required_count, error=error_message, 
                           driver_list=all_drivers, current_race_index=current_race_index, races=races,
                           driver_teams={d.name: d.team for d in drivers_in_db})

@main.route("/standings")
def standings():
    drivers = Driver.query.all()
    
    def f1_sorting_key(driver):
        finish_counts = [0] * 20 
        for r in driver.results:
            if 1 <= r.position <= 20: finish_counts[r.position - 1] += 1
        return (driver.points, *finish_counts)

    sorted_drivers = sorted(drivers, key=f1_sorting_key, reverse=True)
    constructors_dict = {}
    for d in drivers:
        constructors_dict[d.team] = constructors_dict.get(d.team, 0) + d.points
    sorted_constructors = sorted(constructors_dict.items(), key=lambda x: x[1], reverse=True)

    return render_template("standings.html", drivers=sorted_drivers, constructors=sorted_constructors,
                           current_race_index=current_race_index, races=races)

@main.route("/reset-season", methods=["POST"])
def reset_season():
    global current_race_index
    current_race_index = 0
    Result.query.delete()
    db.session.commit()
    recalculate_all_points()
    return redirect(url_for('main.index'))

@main.route("/edit/<int:race_index>", methods=["GET", "POST"])
def edit_race(race_index):
    if race_index >= current_race_index or race_index >= len(races): return redirect(url_for('main.index'))
    
    race_name = races[race_index]
    points_scale = [8, 7, 6, 5, 4, 3, 2, 1] if "Sprint" in race_name else [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
    required_count = len(points_scale)

    existing_results = Result.query.filter_by(race_name=race_name).order_by(Result.position).all()
    existing_order = [r.driver.name for r in existing_results]

    drivers_in_db = Driver.query.order_by(Driver.name).all()
    all_drivers = [d.name for d in drivers_in_db]
    driver_teams = {d.name: d.team for d in drivers_in_db}

    if request.method == "POST":
        entered_drivers = []
        for i in range(1, required_count + 1):
            driver_name = request.form.get(f"driver_{i}")
            if driver_name: entered_drivers.append(driver_name)

        if len(set(entered_drivers)) != len(entered_drivers):
            return render_template("edit_race.html", race=race_name, required=required_count, driver_list=all_drivers,
                                   driver_teams=driver_teams, existing_order=existing_order, error="Every position must be unique!", race_index=race_index)

        Result.query.filter_by(race_name=race_name).delete()
        for i, driver_name in enumerate(entered_drivers):
            driver = Driver.query.filter_by(name=driver_name).first()
            if driver:
                db.session.add(Result(driver_id=driver.id, race_name=race_name, position=i + 1, source="manual"))

        db.session.commit()
        recalculate_all_points()
        return redirect(url_for('main.standings'))

    return render_template("edit_race.html", race=race_name, required=required_count, driver_list=all_drivers,
                           driver_teams=driver_teams, existing_order=existing_order, race_index=race_index, error=None)

@main.route("/stats")
def stats():
    drivers = Driver.query.all()
    sorted_drivers = sorted(drivers, key=lambda d: d.points, reverse=True)
    top10 = sorted_drivers[:10]

    all_results = Result.query.all()
    results_lookup = {(r.driver_id, r.race_name): r for r in all_results}

    timeline = {}
    for driver in top10:
        cumulative = 0
        race_points = []
        for race_name in races[:current_race_index]:
            result = results_lookup.get((driver.id, race_name))
            points_scale = [8, 7, 6, 5, 4, 3, 2, 1] if "Sprint" in race_name else [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
            if result and 1 <= result.position <= len(points_scale):
                cumulative += points_scale[result.position - 1]
            race_points.append(cumulative)
        timeline[driver.name] = race_points

    heatmap = {}
    for driver in sorted_drivers:
        heatmap[driver.name] = [results_lookup.get((driver.id, race_name)).position if results_lookup.get((driver.id, race_name)) else 0 for race_name in races[:current_race_index]]

    teams = {}
    for driver in sorted_drivers:
        teams.setdefault(driver.team, []).append(driver)

    h2h_data = {}
    for team, team_drivers in teams.items():
        if len(team_drivers) != 2: continue
        d1, d2 = team_drivers[0], team_drivers[1]
        
        d1_ahead, d2_ahead = 0, 0
        for race_name in races[:current_race_index]:
            r1 = results_lookup.get((d1.id, race_name))
            r2 = results_lookup.get((d2.id, race_name))
            if r1 and r2:
                if r1.position < r2.position: d1_ahead += 1
                else: d2_ahead += 1

        h2h_data[team] = {
            "d1": d1.name, "d2": d2.name, "d1_points": d1.points, "d2_points": d2.points,
            "d1_wins": sum(1 for r in d1.results if r.position == 1), "d2_wins": sum(1 for r in d2.results if r.position == 1),
            "d1_podiums": sum(1 for r in d1.results if r.position <= 3), "d2_podiums": sum(1 for r in d2.results if r.position <= 3),
            "d1_ahead": d1_ahead, "d2_ahead": d2_ahead,
        }

    return render_template("stats.html", timeline=timeline, race_labels=races[:current_race_index],
                           driver_codes=driver_codes, top10=top10, current_race_index=current_race_index,
                           heatmap=heatmap, all_drivers=sorted_drivers, h2h_data=h2h_data)

@main.route("/sync", methods=["POST"])
def sync():
    global current_race_index
    sync_results()
    current_race_index = Result.query.with_entities(Result.race_name).distinct().count()
    return redirect(url_for('main.standings'))

@main.route("/predictions")
def predictions():
    drivers = Driver.query.all()
    sorted_drivers = sorted(drivers, key=lambda d: d.points, reverse=True)
    remaining_races = races[current_race_index:]
    drivers_dict = {driver.name: driver for driver in sorted_drivers}
    all_driver_names = [d.name for d in sorted_drivers]
    N_SIMS = 1000

    team_avgs = {}
    for driver in sorted_drivers:
        recent_results = Result.query.filter_by(driver_id=driver.id).order_by(Result.id.desc()).limit(5).all()
        team_avgs[driver.name] = {"team": driver.team, "avg": np.mean([r.position for r in recent_results]) if recent_results else 10.0}

    driver_features = {}
    for driver in sorted_drivers:
        recent_results = Result.query.filter_by(driver_id=driver.id).order_by(Result.id.desc()).limit(current_race_index).all()
        avg_position = np.mean([r.position for r in recent_results]) if recent_results else 10.0
        teammate_avgs = [v["avg"] for k, v in team_avgs.items() if v["team"] == driver.team and k != driver.name]
        constructor_form = np.mean(teammate_avgs) if teammate_avgs else avg_position
        driver_features[driver.name] = {"driver_form": avg_position, "constructor_form": constructor_form, "cumulative_points": driver.points, "circuit_avg": avg_position}

    circuit_avg_cache = {}
    for driver in sorted_drivers:
        for race_name in remaining_races:
            circuit_results = Result.query.filter_by(driver_id=driver.id, race_name=race_name).order_by(Result.id.desc()).limit(current_race_index).all()
            circuit_avg_cache[(driver.name, race_name)] = np.mean([r.position for r in circuit_results]) if circuit_results else driver_features[driver.name]["driver_form"]

    race_weather_cache = {race_name: get_race_weather(race_coords.get(race_name, ("0", "0"))[0], race_coords.get(race_name, ("0", "0"))[1], race_dates.get(race_name, str(date_type.today()))) for race_name in remaining_races}

    driver_form_arr = np.array([driver_features[n]["driver_form"] for n in all_driver_names])
    constructor_form_arr = np.array([driver_features[n]["constructor_form"] for n in all_driver_names])

    total_points_accum = np.zeros(len(all_driver_names))
    championship_counts = np.zeros(len(all_driver_names))

    for _ in range(N_SIMS):
        projected_points = np.array([driver_features[n]["cumulative_points"] for n in all_driver_names], dtype=float)
        for race_name in remaining_races:
            points_scale = [8, 7, 6, 5, 4, 3, 2, 1] if "Sprint" in race_name else [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
            rain_mm, temp_c = race_weather_cache[race_name]
            circuit_avg_arr = np.array([circuit_avg_cache[(name, race_name)] for name in all_driver_names])

            noise = np.random.normal(0, 3, len(all_driver_names))
            grid_order_idx = np.argsort(driver_form_arr + noise)
            grid_positions = np.empty(len(all_driver_names), dtype=int)
            grid_positions[grid_order_idx] = np.arange(1, len(all_driver_names) + 1)

            X_batch = np.column_stack([grid_positions, driver_form_arr, constructor_form_arr, projected_points, circuit_avg_arr, np.full(len(all_driver_names), rain_mm), np.full(len(all_driver_names), temp_c)])
            predicted_positions = model.predict(X_batch)

            sorted_idx = np.argsort(predicted_positions)
            for pos, driver_idx in enumerate(sorted_idx):
                if pos < len(points_scale): projected_points[driver_idx] += points_scale[pos]

        championship_counts[np.argmax(projected_points)] += 1
        total_points_accum += projected_points

    avg_points = {all_driver_names[i]: round(total_points_accum[i] / N_SIMS) for i in range(len(all_driver_names))}
    projected_standings = sorted(avg_points.items(), key=lambda x: x[1], reverse=True)

    championship_pct = {name: 0.5 if round((championship_counts[i] / N_SIMS) * 100) == 0 else min(95, round((championship_counts[i] / N_SIMS) * 100)) for i, name in enumerate(all_driver_names)}
    
    constructor_points = {}
    for name, pts in avg_points.items():
        team = drivers_dict[name].team
        constructor_points[team] = constructor_points.get(team, 0) + pts
    constructor_standings = sorted(constructor_points.items(), key=lambda x: x[1], reverse=True)

    return render_template("predictions.html", drivers=sorted_drivers, projected_standings=projected_standings,
                           remaining_races=remaining_races, current_race_index=current_race_index,
                           driver_teams={d.name: d.team for d in sorted_drivers}, championship_pct=championship_pct, constructor_standings=constructor_standings)

@main.route("/raceprediction")
def raceprediction():
    drivers = Driver.query.all()
    sorted_drivers = sorted(drivers, key=lambda d: d.points, reverse=True)
    race = races[current_race_index]
    rain_mm, temp_c = get_race_weather(race_coords.get(race, ("0", "0"))[0], race_coords.get(race, ("0", "0"))[1], race_dates.get(race, str(date_type.today())))

    team_avgs = {}
    for driver in sorted_drivers:
        recent_results = Result.query.filter_by(driver_id=driver.id).order_by(Result.id.desc()).limit(5).all()
        team_avgs[driver.name] = {"team": driver.team, "avg": np.mean([r.position for r in recent_results]) if recent_results else 10.0}

    driver_features = {}
    for driver in sorted_drivers:
        recent_results = Result.query.filter_by(driver_id=driver.id).order_by(Result.id.desc()).limit(current_race_index).all()
        avg_position = np.mean([r.position for r in recent_results]) if recent_results else 10.0
        teammate_avgs = [v["avg"] for k, v in team_avgs.items() if v["team"] == driver.team and k != driver.name]
        
        circuit_results = Result.query.filter_by(driver_id=driver.id, race_name=race).order_by(Result.id.desc()).limit(current_race_index).all()
        circuit_avg = np.mean([r.position for r in circuit_results]) if circuit_results else avg_position

        driver_features[driver.name] = {"driver_form": avg_position, "constructor_form": np.mean(teammate_avgs) if teammate_avgs else avg_position, "cumulative_points": driver.points, "circuit_avg": circuit_avg}
    
    circuit_id = race_to_circuit_id.get(race, "albert_park")
    chaos_factor = get_circuit_chaos(circuit_id)
    quali_grid = get_quali_grid(race)
    quali_used = quali_grid is not None

    N_SIMS = 1000
    all_driver_names = [d.name for d in sorted_drivers]
    position_counts = {name: {} for name in all_driver_names}
    podium_counts = {name: 0 for name in all_driver_names}

    for _ in range(N_SIMS):
        grid_order = sorted(all_driver_names, key=lambda name: quali_grid.get(name, 20) + random.gauss(0, chaos_factor * 0.5)) if quali_used else sorted(all_driver_names, key=lambda name: driver_features[name]["driver_form"] + random.gauss(0, chaos_factor))

        sim_predictions = []
        for i, driver_name in enumerate(grid_order):
            features = driver_features[driver_name]
            grid_pos = quali_grid.get(driver_name, i + 1) if quali_used else i + 1
            X_pred = np.array([[grid_pos, features["driver_form"], features["constructor_form"], features["cumulative_points"], features["circuit_avg"], rain_mm, temp_c]])
            sim_predictions.append((driver_name, model.predict(X_pred)[0] + random.gauss(0, 2.0)))

        sim_predictions.sort(key=lambda x: x[1])
        for pos, (driver_name, _) in enumerate(sim_predictions):
            actual_pos = pos + 1
            position_counts[driver_name][actual_pos] = position_counts[driver_name].get(actual_pos, 0) + 1
            if actual_pos <= 3: podium_counts[driver_name] += 1

    race_predictions = []
    for driver_name in all_driver_names:
        counts = position_counts[driver_name]
        most_common_pos = max(counts, key=counts.get) if counts else 20
        race_predictions.append((driver_name, most_common_pos, round((podium_counts[driver_name] / N_SIMS) * 100, 1)))

    race_predictions.sort(key=lambda x: x[1])
    return render_template("raceprediction.html", race_predictions=race_predictions, race=race, current_race_index=current_race_index, rain_mm=rain_mm, temp_c=temp_c, quali_used=quali_used)

@main.route("/save-simulation", methods=["POST"])
def save_simulation():
    global current_race_index
    race_name = races[current_race_index]
    num_drivers = int(request.form.get("num_drivers"))

    Result.query.filter_by(race_name=race_name).delete()
    for i in range(num_drivers):
        driver_name = request.form.get(f"driver_{i}")
        if driver_name:
            driver = Driver.query.filter_by(name=driver_name).first()
            if driver: db.session.add(Result(driver_id=driver.id, race_name=race_name, position=i + 1, source="simulation"))

    db.session.commit()
    recalculate_all_points()
    current_race_index += 1

    if current_race_index >= len(races): return redirect(url_for('main.finale'))
    return redirect(url_for('main.index'))


@main.route("/finale")
def finale():
    drivers = Driver.query.order_by(Driver.points.desc()).all()
    champion = drivers[0]

    constructor_points = {}
    for driver in drivers:
        constructor_points[driver.team] = constructor_points.get(driver.team, 0) + driver.points
    constructor_standings = sorted(constructor_points.items(), key=lambda x: x[1], reverse=True)

    return render_template("finale.html", champion=champion, drivers=drivers, constructor_standings=constructor_standings)

@main.route("/circuitguide")
def circuitguide():
    circuits = requests.get("https://api.jolpi.ca/ergast/f1/2026/circuits.json").json()["MRData"]["CircuitTable"]["Circuits"]

    races_all = []
    for year in [2025, 2026]:
        offset = 0
        while True:
            r = requests.get(f"https://api.jolpi.ca/ergast/f1/{year}/results.json?limit=30&offset={offset}").json()
            batch = r["MRData"]["RaceTable"]["Races"]
            if not batch: break
            races_all.extend(batch)
            offset += 30
            if offset >= int(r["MRData"]["total"]): break

    recent_winners = {}
    for race in races_all:
        circuit_id = race["Circuit"]["circuitId"]
        if race.get("Results") and (circuit_id not in recent_winners or race["season"] == "2026"):
            winner = next((r for r in race["Results"] if r["position"] == "1"), None)
            if winner: recent_winners[circuit_id] = {"name": f"{winner['Driver']['givenName']} {winner['Driver']['familyName']}", "year": race["season"]}

    return render_template("circuitguide.html", circuits=circuits, races=races, current_race_index=current_race_index, circuit_info=circuit_info, recent_winners=recent_winners)