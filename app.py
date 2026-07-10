import os 
from flask import Flask
from dotenv import load_dotenv
from extensions import db
from routes import main, init_race_index
from models import Driver, Result
from utils import sync_results
from data import driver_to_team

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    app.register_blueprint(main)

    return app

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        
        if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
            
            if Driver.query.count() == 0:
                print("Populating empty database with drivers...")
                for name, team in driver_to_team.items():
                    db.session.add(Driver(name=name, team=team, points=0))
                db.session.commit()
                print("Drivers loaded.")
                
            try:
                init_race_index()
                sync_results()
                print("Initial sync complete on boot.")
            except Exception as e:
                print(f"Sync failed: {e}")
            
    app.run(port=3000, debug=True)