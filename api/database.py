from flask import current_app
from api.models import db, Measurement

def init_db():
    with current_app.app_context():
        db.create_all()

def get_all_measurements():
    return Measurement.query.all()

def get_measurements_by_city(city):
    return Measurement.query.filter_by(city=city).all()

def get_measurement(id):
    measurement = Measurement.query.get(id)
    return measurement 

def add_measurement(city, temperature, wind_speed, power_output):
    measurement = Measurement(
        city=city,
        temperature=temperature,
        wind_speed=wind_speed,
        power_output=power_output
    )
    db.session.add(measurement)
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
