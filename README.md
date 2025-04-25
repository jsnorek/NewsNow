# NewsNow

NewsNow delivers a daily news and weather feed while allowing users to filter articles based on tone, ensuring a stress-free and tailored reading experience.

## Contents
- [Features](#features)
- [API Setup](#api-setup)
- [Installation](#installation)
- [Using Search](#using-search)
- [Reindexing Search](#reindexing-search-data-if-needed)
- [Weather Data Visualization](#weather-data-visualization)
- [Deployment Process](#deployment-process)
- [Learnings](#learnings-from-building-this-application)
- [Database Schema Example](#example-of-database-schema)
- [Contributing](#contributing)
- [Stretch Goals](#stretch-goals)

## Features
- **News Tab**
  - Scrapes news articles from NPR.org and stores them in a SQLite database 
  - AI-powered summarization + sentiment analysis on button click
  - Add, edit, and delete articles
  - Advanced full-text search using Whoosh:  
    - Search across both headlines and summaries 
    - Use wildcards and exact phrases  
- **Community News Articles Tab** that lets users share/add important news articles  
- **Fetches real-time weather data** for specific location from OpenWeather API  
- **Pagination** to display 5 articles per page  
- **Data visualization**: Displays a weather temperature trends chart
- **Secure backend login authorization** for controlled and protected access to data sources.

![ezgif com-optimize (6)](https://github.com/user-attachments/assets/de3e7dea-8abc-4308-b10c-810aa12a37eb)

**New search queries options and data chart**
![Screenshot 2025-02-28 at 9 12 53 AM](https://github.com/user-attachments/assets/f1564279-cacf-4ab9-90cd-3c211b703844)


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

1. Install dependencies
```
pip install -r requirements.txt
```

2. Set up database
```
python -c "from models import Base, engine; Base.metadata.create_all(engine)"
```

3. Set up environment variables
   - Create a .env file in the root of the project
   - Add the following values to the .env file
```
FLASK_ENV=development
DATABASE_URL=your_database_url
NEWS_SITE_USERNAME=your_login_email
NEWS_SITE_PASSWORD=your_login_password
WEATHER_API_KEY=your_weather_api_key
```

**Sign up for an account on** [npr.org](https://www.npr.org/login) to get your NEWS_SITE_USERNAME and NEWS_SITE_PASSWORD. These credentials are used to scrape news articles from the site.
	•	Make sure to replace your_npr_username, your_npr_password, and your_weather_api_key with your actual credentials and API key.

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

## Deployment Process
This application is deployed on Render at this [site](https://e-commerce-product-aggregator.onrender.com/)

The deployment process includes:

1. Pushing changes to GitHub, triggering an automatic deployment on Render
2. Setting environment variables in the Render dashboard
3. Ensuring dependencies are included in `requirements.txt` for Render to install
4. Ensuring your config.py file is set up correctly to distinguish between production and local development

## Learnings from Building this Application
- Deepened understanding of handling API calls, forms, and session management
- Practiced database management including structuring and querying a database
- Implemented Whoosh full-text search functionalities for advanced searching
- Learned to create simple but effective data visualization
- Practiced deployment with Render

### Example of database schema
For Articles

<img width="1103" alt="Screenshot 2025-02-21 at 11 17 46 AM" src="https://github.com/user-attachments/assets/653233ca-3a82-4fb8-906e-b76c181b8964" />

For Weather

<img width="377" alt="Screenshot 2025-02-21 at 11 18 41 AM" src="https://github.com/user-attachments/assets/1902430b-cf4b-478b-b62c-a99a7cc4e7ce" />

## Contributing

If you'd like to contribute, please fork the repository and use a feature branch. Pull requests are warmly welcomed.

## Stretch Goals

- Login feature
  - Ability to update user information
  - Usernames being tied to article adds
  - Users can only edit/delete articles they've added
  - User badges/achievements
  - Users can favorite articles
  - AI personalized recommendations
- Content moderation for added/edited articles
- Scraping from additional news sites


