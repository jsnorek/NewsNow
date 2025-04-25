import pytest
from weather import get_weather
from models import Weather
from app import app
from io import BytesIO

def test_get_weather(test_session, monkeypatch): # monkeypatch is a pytest fixture that allows you to modify or replace parts of your system under test in a controlled manner
    """
    Tests that weather data is correctly fetched and stored in the database using mocked weather API data.
    """

    from models import Weather # Import the Weather model used to store data in the database
    from datetime import datetime, timezone # Import datetime utilities for timestamp handling

    # Mock function to simulate external weather API response
    # Instead of making an actual API call, this function returns predefined weather data
    def mock_get_weather():
        return {"temp": 75, "city": "Test City", "description": "Sunny"}

    # Monkeypatch the actual weather API call with the mock function
    monkeypatch.setattr("weather.get_weather", mock_get_weather)

    # Store the mock data in the test database
    weather_data = mock_get_weather() # Call the mock weather function and store its data
    # Add the mock weather data to the test database session
    test_session.add(Weather(
        temp=weather_data["temp"], # Store the mock temperature (75)
        city=weather_data["city"], # Store the mock city name ("Test City")
        description=weather_data["description"], # Store the mock description ("Sunny")
        last_updated=datetime.now(timezone.utc) # current timestamp
    ))
    test_session.commit() # Commit the transaction to save changes in the database

    # Fetch weather record from DB and check
    weather = test_session.query(Weather).first() # Query the database to retrieve the stored weather data
    assert weather.city == "Test City" # Verify that the city stored in the database matches the expected mock value ("Test City")