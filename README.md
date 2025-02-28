# News & Weather Aggregator

This is a simple web application that scrapes news articles and fetches weather data, allowing users to search articles and track weather trends.

## Features
-  **Scrapes news articles** from the web and stores them in a SQLite database  
- **Fetches real-time weather data** from OpenWeather API  
- **Advanced full-text search** using Whoosh:  
  - Search across both **headlines and summaries**  
  - Use **wildcards** and **exact phrases**  
- **Pagination** to display 5 articles per page  
- **Data visualization**: Displays a weather temperature trends chart

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

2. Install dependencies
```
pip install flask sqlalchemy requests
```

3. Set up database
```
python -c "from models import Base, engine; Base.metadata.create_all(engine)"
```

4. Initialize the Whoosh Search Index
Before using the search functionality, create the search index
```
python -c "from models import 
create_or_open_index;
create_or_open_index();
```

5. Run application
```
python app.py
```

And then use the link to open in your browser.

## Using Search 
The app provides **two advanced search options**:
1. Search across headlines & summaries
2. Wildcard or exact phrase search

To try these options, select the desired search type in the search bar and enter your query.

## Reindexing Search Data (if needed)
If search results appear outdated or incorrect, **reindex the articles**:
```
curl http://127.0.0.1:5000/reindex
```

This removes and rebuilds the search index with all articles.

## Weather Data Visualization
A temperature trends chart is available at:
http://127.0.0.1:5000/weather_chart

It displays a time-series plot of recorded temperatures.
This also displays on the main app homepage.

### Example of database schema
For Articles

<img width="1103" alt="Screenshot 2025-02-21 at 11 17 46 AM" src="https://github.com/user-attachments/assets/653233ca-3a82-4fb8-906e-b76c181b8964" />

For Weather

<img width="377" alt="Screenshot 2025-02-21 at 11 18 41 AM" src="https://github.com/user-attachments/assets/1902430b-cf4b-478b-b62c-a99a7cc4e7ce" />

