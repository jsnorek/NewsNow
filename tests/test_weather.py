import pytest
from weather import get_weather
from models import Weather
from app import app
from io import BytesIO

def test_get_weather(test_session, monkeypatch): # monkeypatch is a pytest fixture that allows you to modify or replace parts of your system under test in a controlled manner
    from models import Weather
    from datetime import datetime, timezone

    def mock_get_weather():
        return {"temp": 75, "city": "Test City", "description": "Sunny"}

    monkeypatch.setattr("weather.get_weather", mock_get_weather)

    # Store the mock data in the test database
    weather_data = mock_get_weather()
    test_session.add(Weather(
        temp=weather_data["temp"],
        city=weather_data["city"],
        description=weather_data["description"],
        last_updated=datetime.now(timezone.utc)
    ))
    test_session.commit()

    # Fetch from DB and check
    weather = test_session.query(Weather).first()
    assert weather.city == "Test City"