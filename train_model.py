import requests
import pandas as pd
import numpy as np
from datetime import datetime
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import joblib
import time

def get_historical_weather(lat, lon, date_str, cache={}):
    key = (round(float(lat), 2), round(float(lon), 2), date_str)
    if key in cache:
        return cache[key]
    
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": date_str,
        "end_date": date_str,
        "daily": ["precipitation_sum", "temperature_2m_max"],
        "timezone": "auto"
    }
    try:
        r = requests.get(url, params=params, timeout=10).json()
        rain = r["daily"]["precipitation_sum"][0] or 0.0
        temp = r["daily"]["temperature_2m_max"][0] or 20.0
    except Exception:
        rain, temp = 0.0, 20.0
    
    cache[key] = (rain, temp)
    time.sleep(0.1)  # be polite to the API
    return rain, temp

def fetch_season(year):
    url = f"https://api.jolpi.ca/ergast/f1/{year}/results.json?limit=100"
    response = requests.get(url)
    data = response.json()
    race_list = data["MRData"]["RaceTable"]["Races"]

    rows = []
    for race in race_list:
        date_str = race["date"]
        lat = race["Circuit"]["Location"]["lat"]
        lon = race["Circuit"]["Location"]["long"]
        rain, temp = get_historical_weather(lat, lon, date_str)

        for result in race["Results"]:
            rows.append({
                "season": year,
                "race_name": race["raceName"],
                "driver_code": result["Driver"]["code"],
                "constructor": result["Constructor"]["name"],
                "grid": result["grid"],
                "position": result["position"],
                "status": result["status"],
                "date": date_str,
                "rain_mm": rain,
                "temp_c": temp,
            })
    return pd.DataFrame(rows)

def add_features(df):
    df["grid"] = pd.to_numeric(df["grid"], errors="coerce")
    df["position"] = pd.to_numeric(df["position"], errors="coerce")
    df["rain_mm"] = pd.to_numeric(df["rain_mm"], errors="coerce").fillna(0.0)
    df["temp_c"] = pd.to_numeric(df["temp_c"], errors="coerce").fillna(20.0)

    df = df[df["status"] == "Finished"].copy()

    df = df.sort_values(["driver_code", "season"])
    df["driver_form"] = (
        df.groupby("driver_code")["position"]
        .transform(lambda x: x.shift(1).rolling(3, min_periods=1).mean())
    )
    df["constructor_form"] = df.apply(lambda row: df[(df["constructor"] == row["constructor"]) & (df["driver_code"] != row["driver_code"]) & (df["season"] == row["season"]) &(df["race_name"] == row["race_name"])]["position"].mean(),axis=1).fillna(df["driver_form"])

    points_map = {1:25,2:18,3:15,4:12,5:10,6:8,7:6,8:4,9:2,10:1}
    df["points_scored"] = df["position"].map(points_map).fillna(0)
    df["cumulative_points"] = (
        df.groupby(["season", "driver_code"])["points_scored"]
        .cumsum().shift(1).fillna(0)
    )

    df["circuit_avg"] = (
        df.groupby(["driver_code", "race_name"])["position"]
        .transform(lambda x: x.shift(1).rolling(3, min_periods=1).mean())
    )
    df["circuit_avg"] = df["circuit_avg"].fillna(df["driver_form"])

    df = df.dropna(subset=["grid", "position", "driver_form", "constructor_form", "circuit_avg"])

    return df

season_weights = {2023: 1, 2024: 2, 2025: 3, 2026: 5}
all_seasons = []
for year, weight in season_weights.items():
    print(f"Fetching {year}...")
    df = fetch_season(year)
    df["weight"] = weight
    all_seasons.append(df)

df_all = pd.concat(all_seasons, ignore_index=True)
df_all = add_features(df_all)
print(f"Rows after feature engineering: {len(df_all)}")

X = df_all[["grid", "driver_form", "constructor_form", "cumulative_points", "circuit_avg", "rain_mm", "temp_c"]]
y = df_all["position"]
weights = df_all["weight"]

X_train, X_test, y_train, y_test, w_train, w_test = train_test_split(
    X, y, weights, test_size=0.2, random_state=42
)

model = XGBRegressor(n_estimators=400, learning_rate=0.1, max_depth=4)
model.fit(X_train, y_train, sample_weight=w_train)

y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
print(f"MAE: {mae:.3f} positions")

joblib.dump(model, "f1_model.pkl")
print("Model saved to f1_model.pkl")