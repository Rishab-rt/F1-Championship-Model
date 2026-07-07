# seed.py
from app import app, db, Driver

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
    "Perez": "Cadillac", "Bottas": "Cadillac"
}

with app.app_context():
    print("Connecting to Supabase and building tables...")
    db.create_all() 
    
    print("Checking if database needs roster population...")
    if Driver.query.count() == 0:
        print("Inserting 2026 F1 driver lineup...")
        for name, team in driver_to_team.items():
            new_driver = Driver(name=name, team=team, points=0)
            db.session.add(new_driver)
        
        db.session.commit()
        print("Database successfully initialized and seeded!")
    else:
        print("Database tables exist and are already populated.")