import os
from dotenv import load_dotenv

# Load environment variables from .env in local development
if os.getenv("FLASK_ENV") != "production":
    load_dotenv()

class Config:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///news.db")
    NEWS_SITE_USERNAME = os.getenv("NEWS_SITE_USERNAME", "")
    NEWS_SITE_PASSWORD = os.getenv("NEWS_SITE_PASSWORD", "")
    DEFAULT_CITY = "Sonoma"
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")