# News & Weather Aggregator

This is a simple web application that scrapes news articles and fetches weather data.

## Features
- Scrapes news articles from the web
- Fetches real-time weather data from OpenWeather API
- Stores news and weather data in a SQLite database
- Displays news alongside the latest weather information

## API Setup

This weather app uses the OpenWeatherMap API to pull the current weather. The OpenWeatherMap API needed for this project is free to use if you sign up for a student account.

https://openweathermap.org/api

Registration for an API key is neccessary. To do this, you must sign up for an account and provide student details. Once approved, log in and you can find you key under "My API keys".

## Installation
1. Clone this repository:
```
git clone git@github.com:jsnorek/e-commerce-product-aggregator.git
cd e-commerce-product-aggregator
```

2. Install dependecies
```
pip install flask sqlalchemy requests
```

3. Set up database
```
python -c "from models import Base, engine; Base.metadata.create_all(engine)"
```

4. Run application
```
python app.py
```

And then use the link to open in your browser.