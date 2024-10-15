from flask import Flask, render_template, request
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Set your OpenWeatherMap API key
API_KEY = os.getenv('WEATHER_API_KEY')  # Ensure this is in your .env file
CURRENT_WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast"
AIR_QUALITY_URL = "http://api.openweathermap.org/data/2.5/air_pollution"

@app.route('/')
def index():
    countries = ['London', 'New York', 'Tokyo', 'Sydney', 'Paris']
    weather_data = []

    for country in countries:
        params = {
            'q': country,
            'appid': API_KEY,
            'units': 'imperial'  # Changed to 'imperial' for Fahrenheit
        }
        response = requests.get(CURRENT_WEATHER_URL, params=params)
        
        if response.status_code == 200:
            weather_data.append(response.json())
        else:
            weather_data.append(None)

    return render_template('index.html', weather_data=weather_data)

@app.route('/forecasts', methods=['GET'])
def forecasts():
    location = request.args.get('location', 'London')  # Default location
    params = {
        'q': location,
        'appid': API_KEY,
        'units': 'imperial'  # Changed to 'imperial' for Fahrenheit
    }
    response = requests.get(CURRENT_WEATHER_URL, params=params)
    
    if response.status_code == 404:
        return render_template('error.html', message="Location not found."), 404
    elif response.status_code != 200:
        return render_template('error.html', message="Error fetching current weather."), response.status_code

    current_weather = response.json()

    # Fetch the 5-day forecast
    forecast_params = {
        'q': location,
        'appid': API_KEY,
        'units': 'imperial'  # Changed to 'imperial' for Fahrenheit
    }
    forecast_response = requests.get(FORECAST_URL, params=forecast_params)
    
    if forecast_response.status_code != 200:
        return render_template('error.html', message="Error fetching forecast."), forecast_response.status_code

    forecast_data = forecast_response.json()

    # Prepare a list to hold formatted forecast data
    formatted_forecast = {}
    
    # Loop through the forecast data and collect one entry per day
    for day in forecast_data['list']:
        date_str = day['dt_txt']  # Get the date string
        date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')  # Convert to datetime object
        formatted_date = date_obj.strftime('%A')  # Get the day of the week

        # Use the date as a key to ensure we only get the first occurrence of each day
        if formatted_date not in formatted_forecast and len(formatted_forecast) < 5:
            formatted_forecast[formatted_date] = {
                'temp': day['main']['temp'],
                'description': day['weather'][0]['description']
            }

    # Convert the dictionary to a list for rendering
    formatted_forecast_list = [{'date': date, **details} for date, details in formatted_forecast.items()]

    return render_template('forecasts.html', current_weather=current_weather, forecast_data=formatted_forecast_list)

@app.route('/radar')
def radar():
    location = request.args.get('location', 'London')  # Default location
    params = {
        'q': location,
        'appid': API_KEY,
        'units': 'imperial'  # Changed to 'imperial' for Fahrenheit
    }
    response = requests.get(CURRENT_WEATHER_URL, params=params)

    if response.status_code == 404:
        return render_template('error.html', message="Location not found."), 404
    elif response.status_code != 200:
        return render_template('error.html', message="Error fetching current weather."), response.status_code

    current_weather = response.json()
    lat = current_weather['coord']['lat']
    lon = current_weather['coord']['lon']

    # Fetch air quality data
    air_quality_params = {
        'lat': lat,
        'lon': lon,
        'appid': API_KEY
    }
    air_quality_response = requests.get(AIR_QUALITY_URL, params=air_quality_params)

    if air_quality_response.status_code != 200:
        return render_template('error.html', message="Error fetching air quality data."), air_quality_response.status_code

    air_quality_data = air_quality_response.json()

    # Extract necessary air quality information
    try:
        aqi = air_quality_data['list'][0]['main']['aqi']
        components = air_quality_data['list'][0]['components']
    except (IndexError, KeyError):
        aqi = 'N/A'
        components = {}

    # Define AQI description based on AQI value
    aqi_description = {
        1: "Good",
        2: "Fair",
        3: "Moderate",
        4: "Poor",
        5: "Very Poor"
    }.get(aqi, "N/A")

    # Fetch UV index using One Call API (requires subscription; using placeholder if not available)
    # For demonstration purposes, we'll set UV index as 'N/A'
    uv_index = 'N/A'  # Placeholder

    wind_speed = current_weather['wind']['speed']  # Wind speed in mph

    return render_template('radar.html',
                           weather_data=current_weather,
                           wind_speed=wind_speed,
                           uv_index=uv_index,
                           air_quality=components,
                           aqi=aqi_description)

@app.route('/news')
def news():
    # Placeholder for news content
    return render_template('news.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', message="Page not found."), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', message="Internal server error."), 500

if __name__ == "__main__":
    try:
        app.run(debug=True)
    except Exception as e:
        print(f"Error: {e}")
