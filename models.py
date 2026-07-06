from extensions import db

class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    team = db.Column(db.String(100), nullable=False)
    points = db.Column(db.Integer, default=0)

class Result(db.Model):
    source = db.Column(db.String(20), default="manual")
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable=False)
    race_name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    
    driver = db.relationship('Driver', backref=db.backref('results', lazy=True))