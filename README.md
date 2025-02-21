# News & Weather Aggregator

This is a simple web application that scrapes news articles and fetches weather data.

## Features
- Scrapes news articles from the web
- Ability to search through articles
- Fetches real-time weather data from OpenWeather API
- Stores news and weather data in a SQLite database
- Displays news alongside the latest weather information
- Uses pagination to display 5 articles per page

![ezgif com-optimize (6)](https://github.com/user-attachments/assets/de3e7dea-8abc-4308-b10c-810aa12a37eb)


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

### Example of database schema
For Articles

<img width="1103" alt="Screenshot 2025-02-21 at 11 17 46 AM" src="https://github.com/user-attachments/assets/653233ca-3a82-4fb8-906e-b76c181b8964" />

For Weather

<img width="377" alt="Screenshot 2025-02-21 at 11 18 41 AM" src="https://github.com/user-attachments/assets/1902430b-cf4b-478b-b62c-a99a7cc4e7ce" />

