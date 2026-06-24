from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import requests
import pandas as pd
import numpy as np

def fetch_season(year):
    url = f"https://api.jolpi.ca/ergast/f1/{year}/results.json?limit=100"
    response = requests.get(url)
    data = response.json()
    races = data["MRData"]["RaceTable"]["Races"]
    
    rows = []
    for race in races:
        for result in race["Results"]:
            rows.append({
                "season": year,
                "race_name": race["raceName"],
                "driver_code": result["Driver"]["code"],
                "constructor": result["Constructor"]["name"],
                "grid": result["grid"],
                "position": result["position"],
                "status": result["status"],
            })
    return pd.DataFrame(rows)

def add_features(df):
    # Convert to numeric
    df["grid"] = pd.to_numeric(df["grid"], errors="coerce")
    df["position"] = pd.to_numeric(df["position"], errors="coerce")
    
    # Drop DNFs — position is unreliable for retired cars
    df = df[df["status"] == "Finished"].copy()
    
    # Rolling driver form — average finishing position over last 3 races
    df = df.sort_values(["driver_code", "season"])
    df["driver_form"] = (
        df.groupby("driver_code")["position"]
        .transform(lambda x: x.shift(1).rolling(3, min_periods=1).mean())
    )
    
    # Rolling constructor form — average finishing position over last 3 races
    df["constructor_form"] = (
        df.groupby("constructor")["position"]
        .transform(lambda x: x.shift(1).rolling(3, min_periods=1).mean())
    )
    
    # Championship position proxy — cumulative points per driver
    points_map = {1:25,2:18,3:15,4:12,5:10,6:8,7:6,8:4,9:2,10:1}
    df["points_scored"] = df["position"].map(points_map).fillna(0)
    df["cumulative_points"] = df.groupby(["season", "driver_code"])["points_scored"].cumsum().shift(1).fillna(0)

    df["circuit_avg"] = (df.groupby(["driver_code", "race_name"])["position"].transform(lambda x: x.shift(1).rolling(3, min_periods=1).mean()))
    # Fill NaN with overall driver form for new circuits
    df["circuit_avg"] = df["circuit_avg"].fillna(df["driver_form"])

    # Drop rows with NaN features
    df = df.dropna(subset=["grid", "position", "driver_form", "constructor_form","circuit_avg"])
    
    return df


# Fetch all seasons and combine into one DataFrame
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
print(df_all[["driver_code", "grid", "position", "driver_form", "constructor_form", "cumulative_points"]].head(10))

# --- Define features and target ---
X = df_all[["grid", "driver_form", "constructor_form", "cumulative_points","circuit_avg"]]
y = df_all["position"]
weights = df_all["weight"]

# --- Split into train and test ---
X_train, X_test, y_train, y_test, w_train, w_test = train_test_split(
    X, y, weights, test_size=0.2, random_state=42
)

# --- Train the model ---
model = XGBRegressor(n_estimators=400, learning_rate=0.1, max_depth=4)
model.fit(X_train, y_train, sample_weight=w_train)

# --- Evaluate ---
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
print(f"MAE: {mae:.2f} positions")

# --- Save model ---
import joblib
joblib.dump(model, "f1_model.pkl")
print("Model saved to f1_model.pkl")