# Authorization setup

import os
import requests
import logging 
from requests.exceptions import RequestException

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load credentials securely from environment variables
USERNAME = os.getenv('NEWS_SITE_USERNAME') # Getting the username from environment variables
PASSWORD = os.getenv('NEWS_SITE_PASSWORD') # Getting the password from environment variables
LOGIN_URL = "https://www.npr.org/login" # URL for the login page

def login():
    session = requests.Session() # Creating a session object

    payload = {
        'username': USERNAME, # Setting the username in the payload
        'password': PASSWORD # Setting the password in the payload
    }

    try:

        response = session.post(LOGIN_URL, data=payload, timeout=10) # Sending a POST request to the login URL with the payload
        response.raise_for_status

        if response.ok: # Checking if the login was successful
            logging.info("YAY Login successful")
            return session # Returning the session object if login is successful
        else: 
            logging.error("Nooo login failed. Check your credentials")
            return None # Returning None if login fails
    except RequestException as e:
        logging.error(f"Network error during login: {e}")
        return None
    except Exception as e:
        logging.critical(f"Unexpected error in login(): {e}")
        return None