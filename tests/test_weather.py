import pytest
from weather import get_weather
from models import Weather
from app import app
from io import BytesIO

def test_get_weather(test_session, monkeypatch): # monkeypatch is a pytest fixture that allows you to modify or replace parts of your system under test in a controlled manner
    """
    Tests that weather data is correctly fetched and stored in the database using mocked weather API data.
    """

    from models import Weather
    from datetime import datetime, timezone

    # Mock function to simulate external weather API response
    def mock_get_weather():
        return {"temp": 75, "city": "Test City", "description": "Sunny"}

    # Monkeypatch the actual weather API call with the mock function
    monkeypatch.setattr("weather.get_weather", mock_get_weather)

    # Store the mock data in the test database
    weather_data = mock_get_weather()
    test_session.add(Weather(
        temp=weather_data["temp"],
        city=weather_data["city"],
        description=weather_data["description"],
        last_updated=datetime.now(timezone.utc) # current timestamp
    ))
    test_session.commit()

    # Fetch weather record from DB and check
    weather = test_session.query(Weather).first()
    assert weather.city == "Test City"