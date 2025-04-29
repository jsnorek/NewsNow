# NewsNow

NewsNow delivers a daily news and weather feed while allowing users to filter articles based on tone, ensuring a stress-free and tailored reading experience.

![ScreenRecording2025-04-28at3 06 40PM-ezgif com-optimize](https://github.com/user-attachments/assets/bd0dfd5a-85ab-4884-9135-c91e221c646e)

## Contents
- [Features](#features)
- [API Setup](#api-setup)
- [Installation](#installation)
- [Testing](#testing)
- [Using Search](#using-search)
- [Reindexing Search](#reindexing-search-data-if-needed)
- [Weather Data Visualization](#weather-data-visualization)
- [Deployment Process](#deployment-process)
- [Learnings](#reflection-on-building-this-application)
- [Database Schema Example](#example-of-database-schema)
- [Drawing Board](#drawing-board)
- [Contributing](#contributing)
- [Stretch Goals](#stretch-goals)

## Features
[Back to Contents](#contents)
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

## API Setup
[Back to Contents](#contents)

### OpenWeatherMap API
This app uses the OpenWeatherMap API to pull the current weather. The OpenWeatherMap API needed for this project is free to use if you sign up for a student account.

https://openweathermap.org/api

Registration for an API key is neccessary. To do this, you must sign up for an account and provide student details. Once approved, log in and you can find you key under "My API keys".

### OpenAI API
This app also uses the OpenAI API to generate article summaries and assign sentiment. You can sign up for an account to get an API key and view API documentation here: https://platform.openai.com/docs/api-reference/introduction

An account is necessary, and you may need to purchase additional credits to run the API.

## Installation
[Back to Contents](#contents)

1. Clone this repository:
```
git clone git@github.com:jsnorek/e-commerce-product-aggregator.git
cd e-commerce-product-aggregator
```

2. Create and activate virtual environment

```
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies
```
pip install -r requirements.txt
```

4. Set up database
```
python -c "from models import Base, engine; Base.metadata.create_all(engine)"
```

5. Set up environment variables
   - Create a .env file in the root of the project
   - Add the following values to the .env file
```
FLASK_ENV=development
DATABASE_URL=your_database_url
DEFAULT_CITY=your_default_city
NEWS_SITE_USERNAME=your_login_email
NEWS_SITE_PASSWORD=your_login_password
WEATHER_API_KEY=your_weather_api_key
OPENAI_API_KEY
```

**Sign up for an account on** [npr.org](https://www.npr.org/login) to get your NEWS_SITE_USERNAME and NEWS_SITE_PASSWORD. These credentials are used to scrape news articles from the site.
	•	Make sure to replace your_npr_username, your_npr_password, and your_weather_api_key with your actual credentials and API key.

6. Initialize the Whoosh Search Index

Before using the search functionality, create the search index
```
python -c "from models import 
create_or_open_index;
create_or_open_index();
```
This will create an indexdir/ folder containing your Whoosh search index.

7. Run application
```
python app.py
```

And then use the link http://127.0.0.1:5000/ after starting the server to open in your browser.

## Testing
[Back to Contents](#contents)

To run test coverage report, run:
```
pytest --cov=your_module --cov-report=html
```

## Using Search
[Back to Contents](#contents)

The app provides **two advanced search options**:
1. Search across headlines & summaries
2. Wildcard or exact phrase search

To try these options, select the desired search type in the search bar and enter your query.

## Reindexing Search Data (if needed)
[Back to Contents](#contents)

If search results appear outdated or incorrect, **reindex the articles**:
```
curl http://127.0.0.1:5000/reindex
```

This removes and rebuilds the search index with all articles.

## Weather Data Visualization
[Back to Contents](#contents)

A temperature trends chart is available at:
http://127.0.0.1:5000/weather_chart

It displays a time-series plot of recorded temperatures.
This also displays on the main app homepage.

## Deployment Process
[Back to Contents](#contents)

This application is deployed on Render at this [site](https://e-commerce-product-aggregator.onrender.com/)

The deployment process includes:

1. Pushing changes to GitHub, triggering an automatic deployment on Render
2. Setting environment variables in the Render dashboard
3. Ensuring dependencies are included in `requirements.txt` for Render to install
4. Ensuring your config.py file is set up correctly to distinguish between production and local development

## Reflection on Building this Application
[Back to Contents](#contents)

It was really interesting to go back and reinvent a past project. When you aren't starting from scratch there are different factors to consider when re-imagining the project, like how to recycle/alter features to fit in with the new vision instead of just building from the ground up.

Additional Learnings:
- Deepened understanding of handling API calls, forms, and session management
- Practiced database management including structuring and querying a database
- Implemented Whoosh full-text search functionalities for advanced searching
- Learned to create simple but effective data visualization
- Practiced deployment with Render
- Practiced practically revamping and restructuring an existing project

### Example of database schema
[Back to Contents](#contents)

For Articles

<img width="1103" alt="Screenshot 2025-02-21 at 11 17 46 AM" src="https://github.com/user-attachments/assets/653233ca-3a82-4fb8-906e-b76c181b8964" />

For Community Articles

<img width="890" alt="Screenshot 2025-04-28 at 3 12 41 PM" src="https://github.com/user-attachments/assets/6f05475b-803e-4114-b19b-d4fd8204d1db" />


For Weather

<img width="377" alt="Screenshot 2025-02-21 at 11 18 41 AM" src="https://github.com/user-attachments/assets/1902430b-cf4b-478b-b62c-a99a7cc4e7ce" />

## Drawing Board
[Back to Contents](#contents)

[Trello Board](https://trello.com/b/SiEM9n7u/news-final-project)

[Final Pitch](https://docs.google.com/document/d/1krUFtzfat2If8fCW_BF1CRBsfTgYC-25NKPr6wvZ73U/edit?usp=sharing)


## Contributing
[Back to Contents](#contents)

If you'd like to contribute, please fork the repository and use a feature branch. Pull requests are warmly welcomed.

## Stretch Goals
[Back to Contents](#contents)

- Login feature
  - Ability to update user information
  - Usernames being tied to article adds
  - Users can only edit/delete articles they've added
  - User badges/achievements
  - Users can favorite articles
  - AI personalized recommendations
- Content moderation for added/edited articles
- Scraping from additional news sites


