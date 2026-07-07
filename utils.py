import requests
import numpy as np
import time
import logging
from datetime import date as date_type, datetime
from extensions import db
from models import Driver, Result
from data import *

def recalculate_all_points():
    db.session.query(Driver).update({Driver.points: 0})
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

def get_medal_index(index):
    if index == 1: return "1 🥇"
    elif index == 2: return "2 🥈"
    elif index == 3: return "3 🥉"
    return str(index)

def get_circuit_chaos(circuit_id):
    deltas = []
    for year in [2023, 2024, 2025]:
        try:
            r = requests.get(f"https://api.jolpi.ca/ergast/f1/{year}/circuits/{circuit_id}/results.json", timeout=5).json()
            races = r["MRData"]["RaceTable"]["Races"]
            for race in races:
                for result in race["Results"]:
                    try:
                        grid = int(result["grid"])
                        pos = int(result["position"])
                        if grid > 0: deltas.append(abs(grid - pos))
                    except (ValueError, KeyError):
                        continue
        except Exception:
            continue
    return round(np.mean(deltas), 2) if deltas else 2.0

def get_race_weather(lat, lon, race_date_str):
    try:
        race_date = datetime.strptime(race_date_str, "%Y-%m-%d").date()
        if race_date < date_type.today():
            url = "https://archive-api.open-meteo.com/v1/archive"
        else:
            url = "https://api.open-meteo.com/v1/forecast"

        tz = "UTC" if (lat == "0" and lon == "0") else "auto"
        params = {
            "latitude": lat, "longitude": lon, "start_date": race_date_str, 
            "end_date": race_date_str, "daily": "precipitation_sum,temperature_2m_max", "timezone": tz
        }
        
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        rain = data["daily"]["precipitation_sum"][0] or 0.0
        temp = data["daily"]["temperature_2m_max"][0] or 20.0
        return rain, temp
        
    except Exception as e:
        logging.error(f"Weather fetch error: {e}")
        return 0.0, 20.0

def get_quali_grid(race_name):
    circuit_id = race_to_circuit_id.get(race_name)
    race_date = race_dates.get(race_name)

    if not circuit_id or not race_date: return None
    year = race_date[:4]
    
    try:
        search_circuit = circuit_id.capitalize()
        meetings = requests.get("https://api.openf1.org/v1/meetings", params={"year": year, "circuit_short_name": search_circuit}, timeout=10).json()
        
        if isinstance(meetings, dict) and 'detail' in meetings: return None
        if not meetings: return None
            
        meeting_key = meetings[0]["meeting_key"]
        target_session = "Sprint Qualifying" if "Sprint" in race_name else "Qualifying"

        sessions = requests.get("https://api.openf1.org/v1/sessions", params={"meeting_key": meeting_key, "session_name": target_session}, timeout=10).json()
        if isinstance(sessions, dict) and 'detail' in sessions: return None
        if not sessions: return None
            
        quali_session_key = sessions[0]["session_key"]

        positions_r = requests.get("https://api.openf1.org/v1/position", params={"session_key": quali_session_key}, timeout=10).json()
        if not positions_r or not isinstance(positions_r, list): return None

        latest = {}
        for entry in positions_r:
            num = entry["driver_number"]
            latest[num] = entry["position"]

        grid = {}
        for driver_num, pos in latest.items():
            name = driver_number_to_name.get(driver_num)
            if name: grid[name] = pos

        return grid if grid else None
    except Exception:
        return None

def get_meeting_key(session_key):
    r = requests.get(f"https://api.openf1.org/v1/sessions?session_key={session_key}", timeout=10).json()
    return r[0]["meeting_key"]

def sync_results():
    print("🔄 Fetching official final classifications...")
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

    race_name_map = {
        "Barcelona Grand Prix": "Spanish Grand Prix",
        "Belgian Grand Prix": "Belgian Grand Prix - SPA"
    }
    sprint_name_map = {
        "Chinese Grand Prix": "China Sprint",
        "Miami Grand Prix": "Miami Sprint",
        "Canadian Grand Prix": "Canada Sprint",
        "British Grand Prix": "Silverstone Sprint",
        "Dutch Grand Prix": "Dutch Sprint",
        "Singapore Grand Prix": "Singapore Sprint"
    }
    
    driver_name_map = {
        "Pérez": "Perez",
        "Hülkenberg": "Hulkenberg",
        "Lindblad": "Linblad"
    }

    for race in races_list:

        time.sleep(0.5)

        round_num = race["round"]
        raw_race_name = race["raceName"]
        main_race_name = race_name_map.get(raw_race_name, raw_race_name)
        
        # --- FETCH SPRINT ---
        sprint_url = f"https://api.jolpi.ca/ergast/f1/2026/{round_num}/sprint.json"
        try:
            sprint_res = requests.get(sprint_url).json()
            sprint_data = sprint_res["MRData"]["RaceTable"]["Races"]
            
            if len(sprint_data) > 0:
                sprint_results = sprint_data[0]["SprintResults"]
                sprint_name = sprint_name_map.get(raw_race_name, f"{main_race_name} Sprint")
                
                for entry in sprint_results:
                    raw_driver_name = entry["Driver"]["familyName"]
                    mapped_driver_name = driver_name_map.get(raw_driver_name, raw_driver_name)
                    
                    local_driver = Driver.query.filter(Driver.name.like(f"%{mapped_driver_name}%")).first()
                    if local_driver:
                        db.session.add(Result(
                            driver_id=local_driver.id,
                            race_name=sprint_name,
                            position=int(entry["position"]),
                            source="api"
                        ))
        except Exception:
            pass 
            
        results_url = f"https://api.jolpi.ca/ergast/f1/2026/{round_num}/results.json"
        try:
            res_data = requests.get(results_url).json()
            race_data = res_data["MRData"]["RaceTable"]["Races"]
            
            if len(race_data) == 0:
                continue
                
            race_results = race_data[0]["Results"]
        except Exception:
            continue

        for entry in race_results:
            raw_driver_name = entry["Driver"]["familyName"]
            mapped_driver_name = driver_name_map.get(raw_driver_name, raw_driver_name)
            
            local_driver = Driver.query.filter(Driver.name.like(f"%{mapped_driver_name}%")).first()
            if local_driver:
                db.session.add(Result(
                    driver_id=local_driver.id,
                    race_name=main_race_name,
                    position=int(entry["position"]),
                    source="api"
                ))

        db.session.commit()
        
    recalculate_all_points()
    print("✅ Local standings synchronized!")