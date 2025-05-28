from flask import Flask, render_template, request, redirect
import requests
from api.database import *
from api.routes import api_bp
from api.models import db
from datetime import datetime
import pytz

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    "postgresql://neondb_owner:npg_LpvWrB2cnIP1@"
    "ep-red-field-a8h742ze-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.register_blueprint(api_bp)

with app.app_context():
    db.create_all()

OPENWEATHER_API_KEY = "0d4670297bbe630f2b203299b369cd66"
UNSPLASH_API_KEY = "CTfT2VmYo9OMOvH2_L3zHnWDG4nWY8-H5fnDMNO-6yw"
FOURSQUARE_API_KEY = "fsq30zjP2W670XWsjbYYn+xmjKtPYricBp+3JVSYmgy/xv8="

def get_air_quality(city):
    geocode_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={OPENWEATHER_API_KEY}"
    try:
        geocode_resp = requests.get(geocode_url)
        geocode_resp.raise_for_status()
        geo_data = geocode_resp.json()
        if not geo_data:
            print("Nu s-au găsit coordonate pentru oraș.")
            return None
        lat = geo_data[0]['lat']
        lon = geo_data[0]['lon']
    except requests.RequestException as e:
        print(f"Eroare geocodare: {e}")
        return None

    air_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}"
    try:
        air_resp = requests.get(air_url)
        air_resp.raise_for_status()
        air_data = air_resp.json()
        return air_data
    except requests.RequestException as e:
        print(f"Eroare API calitate aer: {e}")
        return None

def convert_utc_to_local(utc_dt):
    tz_local = pytz.timezone('Europe/Bucharest')
    if utc_dt is None:
        return None
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=pytz.utc)
    return utc_dt.astimezone(tz_local)

def get_restaurants_in_city(city, limit=5):
    url = "https://api.foursquare.com/v3/places/search"
    headers = {
        "Accept": "application/json",
        "Authorization": FOURSQUARE_API_KEY
    }
    params = {
        "query": "restaurant",
        "near": city,
        "limit": limit,
        "categories": "13065"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json().get("results", [])
    except requests.RequestException as e:
        print(f"Eroare Foursquare: {e}")
        return []

def fetch_unsplash_images(city, num_images=4):
    url = "https://api.unsplash.com/search/photos"
    params = {
        "query": city,
        "per_page": num_images,
        "client_id": UNSPLASH_API_KEY
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return [photo['urls']['regular'] for photo in response.json().get('results', [])]
    except requests.RequestException as e:
        print(f"Eroare Unsplash: {e}")
        return []


@app.route('/')
def index():
    measurements = get_all_measurements()
    return render_template('index.html', measurements=measurements)

@app.route('/city', methods=['POST'])
def city():
    city = request.form.get('city')
    if not city:
        return redirect('/')

    weather = None
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={OPENWEATHER_API_KEY}"
    try:
        response = requests.get(weather_url)
        response.raise_for_status()
        weather = response.json()
    except requests.RequestException as e:
        print(f"Eroare OpenWeather: {e}")

    image_urls = fetch_unsplash_images(city)

    restaurants = get_restaurants_in_city(city)

    measurements = get_measurements_by_city(city)

    air_quality = get_air_quality(city)

    for m in measurements:
        if isinstance(m, dict) and isinstance(m.get('timestamp'), str):
            try:
                dt_utc = datetime.strptime(m['timestamp'], '%Y-%m-%d %H:%M:%S')
                m['timestamp'] = convert_utc_to_local(dt_utc)
            except Exception as e:
                print(f"Eroare la convertirea timestamp-ului: {e}")
                m['timestamp'] = None
        elif hasattr(m, 'timestamp') and m.timestamp:
            m.timestamp = convert_utc_to_local(m.timestamp)

    return render_template(
        'city.html',
        city=city,
        weather=weather,
        image_urls=image_urls,
        measurements=measurements,
        restaurants=restaurants,
        air_quality=air_quality
    )

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        try:
            city = request.form['city']
            temperature = float(request.form['temperature'])
            wind_speed = float(request.form['wind_speed'])
            power_output = float(request.form['power_output'])

            add_measurement(city, temperature, wind_speed, power_output)
            return redirect('/')
        except (ValueError, KeyError) as e:
            print(f"Eroare la adăugarea măsurătorii: {e}")

    return render_template('add.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    measurement = get_measurement(id)
    if not measurement:
        return "Measurement not found", 404

    if request.method == 'POST':
        try:
            temperature = float(request.form['temperature'])
            wind_speed = float(request.form['wind_speed'])
            power_output = float(request.form['power_output'])

            update_measurement(id, temperature, wind_speed, power_output)
            return redirect('/')
        except (ValueError, KeyError) as e:
            print(f"Eroare la editarea măsurătorii: {e}")

    return render_template('edit.html', measurement=measurement)

@app.route('/delete/<int:id>')
def delete(id):
    delete_measurement(id)
    return redirect('/')

@app.route('/delete_all', methods=['POST'])
def delete_all_route():
    api_url = 'http://localhost:5000/api/measurements'
    try:
        response = requests.delete(api_url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Eroare la ștergerea tuturor măsurătorilor: {e}")
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
