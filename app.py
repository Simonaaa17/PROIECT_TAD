from flask import Flask, render_template, request, redirect
import requests
from api.database import *
from api.routes import api_bp
from api.models import db

app = Flask(__name__)

# Configurația bazei de date Neon (PostgreSQL)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://neondb_owner:npg_LpvWrB2cnIP1@ep-red-field-a8h742ze-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inițializare SQLAlchemy cu app
db.init_app(app)

# Înregistrarea blueprint-ului
app.register_blueprint(api_bp)

# Creare tabele dacă nu există
with app.app_context():
    db.create_all()

# Cheile tale de API
OPENWEATHER_API_KEY = "0d4670297bbe630f2b203299b369cd66"
UNSPLASH_API_KEY = "CTfT2VmYo9OMOvH2_L3zHnWDG4nWY8-H5fnDMNO-6yw"

@app.route('/')
def index():
    measurements = get_all_measurements()
    return render_template('index.html', measurements=measurements)

@app.route('/city', methods=['POST'])
def city():
    city = request.form['city']

    # OpenWeather API
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={OPENWEATHER_API_KEY}"
    weather = None
    try:
        response = requests.get(weather_url)
        if response.status_code == 200:
            weather = response.json()
    except Exception as e:
        print(f"OpenWeather error: {e}")
        weather = None

    # Unsplash API
    image_url = None
    try:
        unsplash_url = f"https://api.unsplash.com/search/photos?query={city}&per_page=1&client_id={UNSPLASH_API_KEY}"
        r = requests.get(unsplash_url)
        if r.status_code == 200:
            data = r.json()
            if data['results']:
                image_url = data['results'][0]['urls']['regular']
    except Exception as e:
        print(f"Unsplash error: {e}")
        image_url = None

    measurements = get_measurements_by_city(city)
    return render_template('city.html', city=city, weather=weather, image_url=image_url, measurements=measurements)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        city = request.form['city']
        temperature = float(request.form['temperature'])
        wind_speed = float(request.form['wind_speed'])
        power_output = float(request.form['power_output'])

        add_measurement(city, temperature, wind_speed, power_output)
        return redirect('/')
    return render_template('add.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    measurement = get_measurement(id)
    if not measurement:
        return "Measurement not found", 404

    if request.method == 'POST':
        temperature = float(request.form['temperature'])
        wind_speed = float(request.form['wind_speed'])
        power_output = float(request.form['power_output'])

        update_measurement(id, temperature, wind_speed, power_output)
        return redirect('/')
    return render_template('edit.html', measurement=measurement)

@app.route('/delete/<int:id>')
def delete(id):
    delete_measurement(id)
    return redirect('/')

@app.route('/delete_all', methods=['POST'])
def delete_all():
    api_url = 'http://localhost:5000/api/measurements'
    try:
        requests.delete(api_url)
    except Exception as e:
        print(f"Delete all error: {e}")
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
