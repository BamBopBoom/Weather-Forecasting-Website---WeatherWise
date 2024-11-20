from flask import Flask, render_template, request
import requests
import os
from dotenv import load_dotenv
import datetime

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
    # List of predefined cities
    cities = ['London', 'New York', 'Tokyo']
    weather_data = []

    # Fetch weather data for predefined cities
    for city in cities:
        params = {
            'q': city,
            'appid': API_KEY,
            'units': 'imperial'  # Use 'imperial' to get temperature in Fahrenheit
        }
        response = requests.get(BASE_URL, params=params)
        
        if response.status_code == 200:
            weather_data.append(response.json())
        else:
            weather_data.append(None)

    return render_template('index.html', weather_data=weather_data)

# Helper function to fetch current weather data for a given city
def fetch_current_weather(city):
    params = {
        'q': city,
        'appid': API_KEY,
        'units': 'imperial'  # Fahrenheit
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        return response.json()
    return None

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
        # Format forecast data (one entry per day)
        formatted_forecast = []
        for day in forecast_data['list']:
            date_str = day['dt_txt']
            date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            formatted_date = date_obj.strftime('%A')  # Day of the week

            # Add each day's forecast data to the list
            formatted_forecast.append({
                'date': formatted_date,
                'temp': day['main']['temp'],
                'description': day['weather'][0]['description']
            })
        return formatted_forecast
    return None

# Route for the forecast page
@app.route('/forecast', methods=['GET', 'POST'])
def forecast():
    city = request.args.get('location')  # Get city from query parameters

    if city:
        try:
            # Fetch current weather and forecast data for the given city
            current_weather = fetch_current_weather(city)
            forecast_data = fetch_forecast_data(city)
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            current_weather = None
            forecast_data = []
    else:
        current_weather = None
        forecast_data = []

    return render_template('forecast.html', current_weather=current_weather, forecast_data=forecast_data)

# Route for the radar page (current weather and air quality)
@app.route('/radar', methods=['GET'])
def radar():
    city = request.args.get('city', 'New York')  # Default to New York if no city is specified
    weather_url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=imperial'  # Using imperial units for °F
    air_quality_url = f'http://api.openweathermap.org/data/2.5/air_pollution?lat={{lat}}&lon={{lon}}&appid={API_KEY}'

    # Fetch current weather data
    weather_response = requests.get(weather_url)
    if weather_response.status_code != 200:
        return render_template('radar.html', error_message="City not found.", weather_data=None)

    weather_data = weather_response.json()

    # Fetch air quality data
    coord = weather_data['coord']
    air_quality_response = requests.get(air_quality_url.format(lat=coord['lat'], lon=coord['lon']))
    air_quality_data = air_quality_response.json()['list'][0]['components'] if air_quality_response.status_code == 200 else {}

    # Weather and air quality details
    radar_data = {
        'name': weather_data['name'],
        'wind_speed': weather_data['wind']['speed'],
        'temperature': weather_data['main']['temp'],  # Temperature in Fahrenheit
        'humidity': weather_data['main']['humidity'],
        'pressure': weather_data['main']['pressure'],
        'uv_index': weather_data.get('uvi', 'N/A'),
        'aqi': air_quality_data.get('aqi', 'N/A'),
        'sunrise': datetime.datetime.utcfromtimestamp(weather_data['sys']['sunrise']).strftime('%H:%M:%S'),
        'sunset': datetime.datetime.utcfromtimestamp(weather_data['sys']['sunset']).strftime('%H:%M:%S'),
        'coord': coord,
    }

    return render_template('radar.html', weather_data=radar_data)

# Route for the news page
@app.route('/news')
def news():
    return render_template('news.html')

# Route for the news page with a country selector
@app.route('/news/country/<country>')
def news_country(country):
    return render_template('news_country.html', country=country)

# Main execution
if __name__ == "__main__":
    app.run(debug=True)
