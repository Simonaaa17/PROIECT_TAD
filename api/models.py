from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Measurement(db.Model):
    __tablename__ = 'measurements'

    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100), nullable=False)
    temperature = db.Column(db.Float)
    wind_speed = db.Column(db.Float)
    power_output = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow) 

    def to_dict(self):
        return {
            'id': self.id,
            'city': self.city,
            'temperature': self.temperature,
            'wind_speed': self.wind_speed,
            'power_output': self.power_output,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
