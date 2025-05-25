from flask import current_app
from api.models import db, Measurement

def init_db():
    with current_app.app_context():
        db.create_all()

def get_all_measurements():
    measurements = Measurement.query.all()
    return [m.to_dict() for m in measurements]

def get_measurements_by_city(city):
    measurements = Measurement.query.filter_by(city=city).all()
    return [m.to_dict() for m in measurements]

def get_measurement(id):
    measurement = Measurement.query.get(id)
    return measurement.to_dict() if measurement else None

def add_measurement(city, temperature, wind_speed, power_output):
    m = Measurement(city=city, temperature=temperature, wind_speed=wind_speed, power_output=power_output)
    db.session.add(m)
    db.session.commit()

def update_measurement(id, temperature, wind_speed, power_output):
    m = Measurement.query.get(id)
    if m:
        m.temperature = temperature
        m.wind_speed = wind_speed
        m.power_output = power_output
        db.session.commit()

def delete_measurement(id):
    m = Measurement.query.get(id)
    if m:
        db.session.delete(m)
        db.session.commit()

def delete_all():
    Measurement.query.delete()
    db.session.commit()
