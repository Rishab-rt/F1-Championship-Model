# 🏎️ F1 Championship Calculator

A Flask-based web application that allows users to simulate an entire Formula 1 season by entering race results and automatically calculating both the Drivers' Championship (WDC) and Constructors' Championship (WCC) standings.

## Features

- Simulate a full Formula 1 season race-by-race

- Supports both:

  - Grand Prix events

  - Sprint races

- Automatic points allocation based on FIA scoring rules

- Live Drivers' Championship standings

- Live Constructors' Championship standings

- Validation to prevent duplicate driver selections

- Medal indicators 🥇🥈🥉 for top championship positions
---

## Scoring System

## Grand Prix                                     ### ⚡ Sprint Points

| Position | Points |                           | Position | Points |
|----------|--------|                           |----------|--------|        
| 1st      | 25     |                           | 1st      | 8      |
| 2nd      | 18     |                           | 2nd      | 7      |
| 3rd      | 15     |                           | 3rd      | 6      |
| 4th      | 12     |                           | 4th      | 5      |
| 5th      | 10     |                           | 5th      | 4      |
| 6th      | 8      |                           | 6th      | 3      |
| 7th      | 6      |                           | 7th      | 2      |
| 8th      | 4      |                           | 8th      | 1      |
| 9th      | 2      |
| 10th     | 1      |

## Technologies Used

- Python
- Flask
- Pandas
- HTML
- Bootstrap