# Authorization setup

import os
import requests

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

    response = session.post(LOGIN_URL, data=payload) # Sending a POST request to the login URL with the payload

    if response.ok: # Checking if the login was successful
        print("YAY Login successful")
        return session # Returning the session object if login is successful
    else: 
        print("Nooo login failed. Check your credentials")
        return None # Returning None if login fails