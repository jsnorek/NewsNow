# API GET request for weather data

import requests
from config import WEATHER_API_KEY, DEFAULT_CITY
from models import Weather, session 
from datetime import datetime, timezone

def get_weather():
    # Define the API endpoint URL
    url = f"http://api.openweathermap.org/data/2.5/weather?q={DEFAULT_CITY}&appid={WEATHER_API_KEY}&units=imperial" # use DEFAULT_CITY and WEATHER_API_KEY from config file
    # Send GET request to the endpoint URL
    response = requests.get(url) 
    # Check if the response code equals 200 to indicate success
    if response.status_code == 200:
        # Parse the response data 
        data = response.json()
        # Extract relevant weather data
        weather_info = {
            "temp": data["main"]["temp"],
            "city": data["name"],
            "description": data["weather"][0]["description"],
            "last_updated": datetime.now(timezone.utc)
        }

        # Create new weather record
        new_weather = Weather(**weather_info)
        session.add(new_weather)

        # Query the database for the first weather data record
        # existing_weather = session.query(Weather).first()
        # Keeping as reference - if you wanted to only store one set of weather data 
        # Check if data is already in the database
        # if existing_weather:
        #     # Update the record with current weather information
        #     existing_weather.temp = weather_info["temp"]
        #     existing_weather.city = weather_info["city"]
        #     existing_weather.description = weather_info["description"]
        #     existing_weather.last_updated = weather_info["last_updated"]
        # else:
        #     new_weather = Weather(**weather_info)
        #     session.add(new_weather)

        # Commit changes to database
        session.commit()
    else:
        # Print error message if API request fails
        print("Failed to fetch weather data")