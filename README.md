# 🏎️ F1 2026 Season Simulator

A full-stack web application to simulate, track, and predict the 2026 Formula 1 World Championship. Built with Flask, SQLAlchemy, and a custom-trained XGBoost ML model.

## Features

- **Race Input** — Click-to-place driver cards to input predicted finishing orders race by race
- **Live Sync** — Auto-sync real 2026 race results from OpenF1 API with source tracking (manual/api/simulation)
- **Driver Standings** — Real-time championship table with medal indicators 🥇🥈🥉
- **Constructor Standings** — Team points aggregated from driver results
- **Edit Past Races** — Go back and change any previous result with full points recalculation
- **Statistics** — Chart.js points progression, driver form heatmap, and head-to-head teammate comparison
- **Circuit Guide** — Sky Sports-style stat cards per circuit (length, laps, lap record, recent winner, location map)
- **Next Race Prediction** — XGBoost ML model predicting the upcoming race with 1000 Monte Carlo simulations, live quali grid integration via OpenF1, podium % per driver, and real-time weather from Open-Meteo
- **Season Simulation** — Full remaining season simulation with projected driver and constructor championships, title win percentages, and probabilistic noise
- **Weather Integration** — Open-Meteo API for race day forecasts and historical weather, used as ML model features
- **Saturday Quali Integration** — Fetches live qualifying grid from OpenF1 to replace estimated grid in race predictions
- **Dynamic Chaos Factor** — Circuit-specific prediction noise calculated from historical grid-to-finish deltas via Jolpica API

## ML Model

- XGBoost regressor trained on weighted 2023–2026 data (2026 weighted 5x)
- Features: grid position, driver form, constructor form (teammate average), cumulative points, circuit average, rain (mm), temperature (°C)
- MAE: ~1.9 positions
- Retrain anytime with `python3 train_model.py`

## Tech Stack

- **Backend** — Python, Flask, SQLAlchemy
- **Database** — PostgreSQL via Supabase
- **Frontend** — Bootstrap 5, custom CSS, Barlow Condensed + Inter fonts, Chart.js
- **ML** — XGBoost, scikit-learn, pandas, numpy, joblib
- **APIs** — OpenF1 (live 2026 data), Jolpica/Ergast (historical data), Open-Meteo (weather)

## How to Run

- **Step 1** — 
- Run the following commands in your terminal: 
    - git clone https://github.com/Rishab-rt/F1-Championship-Model
    - cd F1-Championship-Model

- **Step 2** — Create your Virtual Environment
    - Windows
        - python -m venv venv
          venv\Scripts\activate
    - Mac
        - python3 -m venv venv
          source venv/bin/activate

- **Step 3** - Install Dependencies:
    - Run: pip install -r requirements.txt

- **Step 4** - Set up Local db
    - Create a new file in the project folder called .env. Open it and add the following line so the app creates a private database just for you on your machine: DATABASE_URL=sqlite:///f1_local_data.db

- **Step 5** - Train the Model
    - Run: python train_model.py or Run: python3 train_model.py

- **Step 6** - Run the App
    - Run: python app.py or Run: python3 app.py

- **Step 7** - View the App
    - Go to your browser and paste: http://127.0.0.1:3000

- **Enjoy and Leave Feedback at** - https://forms.gle/VfGBejQggBmMwdgX8


