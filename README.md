# 🏎️ F1 2026 Season Simulator

A full-stack web application to simulate, track, and predict the 2026 Formula 1 World Championship. Built with Flask, SQLAlchemy, and a custom-trained XGBoost ML model.

## Features

- **Race Input** — Click-to-place driver cards to input predicted finishing orders race by race
- **Live Sync** — Auto-sync real 2026 race results from OpenF1 API with source tracking (manual/api/simulation)
- **Points Tracking** — Full F1 scoring system including sprint weekends (8/7/6... for sprints, 25/18/15... for races)
- **Driver Standings** — Real-time championship table with medal indicators 🥇🥈🥉
- **Constructor Standings** — Team points aggregated from driver results
- **Edit Past Races** — Go back and change any previous result with full points recalculation
- **Statistics** — Chart.js points progression, driver form heatmap, and head-to-head teammate comparison
- **Circuit Guide** — Sky Sports-style stat cards per circuit (length, laps, lap record, recent winner, location map)
- **Next Race Prediction** — XGBoost ML model predicting the upcoming race with 1000 Monte Carlo simulations, live quali grid integration via OpenF1, podium % per driver, and real-time weather from Open-Meteo
- **Season Simulation** — Full remaining season simulation with projected driver and constructor championships, title win percentages, and probabilistic noise
- **Season Finale** — Celebration page with confetti, driver podium, and constructor championship cards triggered after the final race
- **Weather Integration** — Open-Meteo API for race day forecasts and historical weather, used as ML model features
- **Saturday Quali Integration** — Fetches live qualifying grid from OpenF1 to replace estimated grid in race predictions
- **Dynamic Chaos Factor** — Circuit-specific prediction noise calculated from historical grid-to-finish deltas via Jolpica API

## ML Model

- XGBoost regressor trained on weighted 2023–2026 data (2026 weighted 5x)
- Features: grid position, driver form, constructor form (teammate average), cumulative points, circuit average, rain (mm), temperature (°C)
- MAE: ~2.18 positions
- Retrain anytime with `python3 train_model.py`

## Tech Stack

- **Backend** — Python, Flask, SQLAlchemy
- **Database** — PostgreSQL via Supabase
- **Frontend** — Bootstrap 5, custom CSS, Barlow Condensed + Inter fonts, Chart.js
- **ML** — XGBoost, scikit-learn, pandas, numpy, joblib
- **APIs** — OpenF1 (live 2026 data), Jolpica/Ergast (historical data), Open-Meteo (weather)