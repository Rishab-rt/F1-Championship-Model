# F1-Championship-Calculator

# 🏎️ Formula 1 2026 Championship Simulator

A fully interactive, command-line Python simulation that recreates the 2024 Formula 1 season, round by round. This tool lets you manually input finishing positions for each race and sprint, calculate and update **Driver (WDC)** and **Constructor (WCC)** standings, and view dynamic rankings after each round.

Built with modular logic and real-world accuracy, this project reflects official F1 points distribution and simulates a full 31-event calendar, including Sprints and Grand Prix events.

---

## 📌 Key Features

- 🏁 **Simulate all 31 official 2026 F1 events** — including Sprints and GPs
- 🎯 **Points system based on real F1 rules** (25–18–15… for GPs; 8–7–6… for Sprints)
- 👥 **20 drivers** mapped to **10 constructor teams**
- 📊 Real-time standings updates for both WDC and WCC
- 🔁 Option to view updated standings after any race or sprint
- 🧩 Intuitive CLI experience using Python’s built-in functions
- 📚 Easy to extend with future improvements (GUI, data storage, etc.)

---

## 🎮 How It Works

At launch, the simulator walks the user through the 2024 F1 calendar:

- At each event, you’re prompted to enter the **top 10 finishers** (or top 8 for sprints).
- The simulator awards points according to F1 rules.
- After each round, you can optionally view:
  - **WDC standings**: driver rankings based on points
  - **WCC standings**: team rankings based on both drivers’ combined points
- At the end of all 31 rounds, the final championship results are displayed.

---

## 🏆 Points System

### 🏁 Grand Prix Points

| Position | Points |
|----------|--------|
| 1st      | 25     |
| 2nd      | 18     |
| 3rd      | 15     |
| 4th      | 12     |
| 5th      | 10     |
| 6th      | 8      |
| 7th      | 6      |
| 8th      | 4      |
| 9th      | 2      |
| 10th     | 1      |

### ⚡ Sprint Points

| Position | Points |
|----------|--------|
| 1st      | 8      |
| 2nd      | 7      |
| 3rd      | 6      |
| 4th      | 5      |
| 5th      | 4      |
| 6th      | 3      |
| 7th      | 2      |
| 8th      | 1      |
