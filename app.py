from flask import Flask, render_template, request
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Set your OpenWeatherMap API key
API_KEY = os.getenv('WEATHER_API_KEY')  # Ensure this is in your .env file
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast"

# Route for the home page
@app.route('/')
def index():
    cities = ['London', 'New York', 'Tokyo', 'Paris', 'Sydney']  # Cities to fetch weather for
    weather_data = []  # Initialize an empty list to store weather data

    # Fetch weather data for each city
    for city in cities:
        params = {
            'q': city,
            'appid': API_KEY,
            'units': 'imperial'
        }
        response = requests.get(BASE_URL, params=params)
        
        if response.status_code == 200:
            weather_data.append(response.json())  # Append the weather data to the list
        else:
            weather_data.append(None)  # Append None if there's an error fetching data

    return render_template('index.html', weather_data=weather_data)

# Helper function to fetch 5-day forecast data for a given city
def fetch_forecast_data(city):
    params = {
        'q': city,
        'appid': API_KEY,
        'units': 'imperial'  # Fahrenheit
    }
    response = requests.get(FORECAST_URL, params=params)
    if response.status_code == 200:
        forecast_data = response.json()
        formatted_forecast = []
        for day in forecast_data['list']:
            date_str = day['dt_txt']
            formatted_forecast.append({
                'date': date_str.split(" ")[0],  # Extract the date part
                'temp': day['main']['temp'],
                'description': day['weather'][0]['description'],
                'icon': day['weather'][0]['icon']  # Weather icon
            })
        return formatted_forecast
    return None

# Route for the forecast page
@app.route('/forecast', methods=['GET', 'POST'])
def forecast():
    city = request.args.get('location')  # Get city from query parameters

    if city:
        try:
            # Fetch forecast data for the given city
            forecast_data = fetch_forecast_data(city)
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            forecast_data = []
    else:
        forecast_data = []

    return render_template('forecast.html', forecast_data=forecast_data)

# Route for the radar page (current weather)
@app.route('/radar', methods=['GET'])
def radar():
    city = request.args.get('city', 'New York')  # Default to New York if no city is specified
    weather_url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=imperial'

    # Fetch current weather data
    weather_response = requests.get(weather_url)
    if weather_response.status_code != 200:
        return render_template('radar.html', error_message="City not found.", weather_data=None)

    weather_data = weather_response.json()

    radar_data = {
        'name': weather_data['name'],
        'wind_speed': weather_data['wind']['speed'],
        'temperature': weather_data['main']['temp'],  # Temperature in Fahrenheit
        'humidity': weather_data['main']['humidity'],
        'icon': weather_data['weather'][0]['icon']
    }

    return render_template('radar.html', weather_data=radar_data)

if __name__ == "__main__":
    app.run(debug=True)
