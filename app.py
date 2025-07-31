from flask import Flask, render_template
app = Flask(__name__)

# ===== F1 Data Setup =====
lastNames = ["Leclerc","Hamilton","Piastri","Norris","Russel","Antonelli","Verstappen","Tsunoda","Albon","Sainz",
             "Alonso","Stroll","Ocon","Bearman","Hadjar","Lawson","Hulkenberg","Bortoleto","Gasly","Doohan"]

drivers = [0] * 20  # All start with 0 points

driver_to_team = {
    "Leclerc": "Ferrari", "Hamilton": "Ferrari",
    "Piastri": "McLaren", "Norris": "McLaren",
    "Russel": "Mercedes", "Antonelli": "Mercedes",
    "Verstappen": "Red Bull", "Tsunoda": "Red Bull",
    "Sainz": "Williams", "Albon": "Williams",
    "Alonso": "Aston Martin", "Stroll": "Aston Martin",
    "Ocon": "Haas", "Bearman": "Haas",
    "Hadjar": "Vcarb", "Lawson": "Vcarb",
    "Hulkenberg": "Kick Sauber", "Bortoleto": "Kick Sauber",
    "Gasly": "Alpine", "Doohan": "Alpine"
}

# ===== Helper Functions =====

def get_driver_standings():
    standings = list(zip(lastNames, drivers))
    standings.sort(key=lambda x: x[1], reverse=True)
    return standings

def calculate_constructor_points():
    constructor_points = {}
    for i in range(len(lastNames)):
        team = driver_to_team[lastNames[i]]
        constructor_points[team] = constructor_points.get(team, 0) + drivers[i]
    return sorted(constructor_points.items(), key=lambda x: x[1], reverse=True)

# ===== Flask Routes =====

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/standings')
def standings():
    driver_data = get_driver_standings()
    team_data = calculate_constructor_points()
    return render_template('standings.html', drivers=driver_data, teams=team_data)

if __name__ == '__main__':
    app.run(debug=True)