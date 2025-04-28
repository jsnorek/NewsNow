# API GET request for weather data

import requests
import logging
# from config import WEATHER_API_KEY, DEFAULT_CITY
from models import Weather, session 
from datetime import datetime, timezone
from requests.exceptions import RequestException

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_weather():
    from config import Config
    # Define the API endpoint URL
    url = f"http://api.openweathermap.org/data/2.5/weather?q={Config.DEFAULT_CITY}&appid={Config.WEATHER_API_KEY}&units=imperial"
    try:
        # Send GET request to the endpoint URL
        response = requests.get(url, timeout=10)
        response.raise_for_status() # Raises HTTP errors for bad responses

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

        logging.info(f"Added new weather data for {weather_info['city']} at {weather_info['last_updated']}")
    except requests.exceptions.RequestException as e:
        # Print error message if API request fails
        logging.error(f"Failed to fetch weather data: {e}")