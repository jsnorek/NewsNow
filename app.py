# Routes

from flask import Flask, redirect, render_template, request, url_for, flash 
from models import Weather, session, NewsArticle
from weather import get_weather
import logging

app = Flask(__name__) 
app.secret_key = 'secret'

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

@app.before_request
def refresh_session():
    session.close()  # Rollback any pending transactions
    session.expire_all()  # Ensure fresh data is loaded

# Root for homepage
@app.route('/')
# Index function to execute when user navigates to root URL
def index():
    try:
        session.expire_all() # Ensures the session fetches fresh data
        # Queries NewsArticle table in the database to retrieve all records and stores in news_article variable as a list of NewsArticle objects 
        news_articles = session.query(NewsArticle).all()
        # Fetch weather data
        weather_data = session.query(Weather).first()
        # Returns rendered HTML template and passes news_articles to template as articles
        return render_template('index.html', articles=news_articles, weather=weather_data)
    except Exception as e:
        logging.error(f"Error loading homepage: {e}")
        flash("An error occurred while loading the page. Please try again", "error")
        return render_template('index.html', articles=[], weather=[])


# Route to update the current weather
@app.route('/update_weather', methods=['POST'])
# Function to update the weather
def update_weather():
    try:
        # Call  get_weather to run API GET request
        get_weather()
        flash("Weather updated successfully!", "success")
        # Returns rendered HTML template 
    except Exception as e:
        logging.error(f"Error updating weather: {e}")
        flash("Failed to update weather data. Please try again.", "error")
    return redirect(url_for('index'))

# Route for search bar to allow users to search articles by headline
@app.route('/search', methods = ['GET'])
def search():
    query = request.args.get('query', '') # Retrieves the value of the query parameter named 'query' from the request. Default is an empty string
    try:
        if query: # If search term was entered
            results = session.query(NewsArticle).filter(NewsArticle.headline.contains(query)).all() # If search term entered, it queries the database for NewsArticle entries where headling contains the search term
            if not results:
                flash("No articles found for your search.", "info")
        else:
            results = [] # If no search term entered results is assigned empty list
            flash("Please enter a search term.", "warning")
        return render_template('index.html', articles=results) # Renders index.html and passes results to the template for display
    except Exception as e:
        logging.error(f"Error searching articles: {e}")
        flash("An error occurred during search. Please try again.", "error")
        return render_template('index.html', articles=[])
    
# Route to re-scrape for updated articlees
@app.route('/scrape', methods = ['POST'])
def scrape():
    try:
        session.expire_all() # Tells SQLAlchemy session to expire all instances it has loaded 
        session.commit() # Commits pending transactions to the database to ensure the session is clean

        from scraper import scrape_news # Imports scrape_news
        scrape_news() # Calls scrape_news functoin to re-scrape for articles
        flash("Yay! News articles updated successfully!", "success")
        # session.expire_all()
        # session.commit() # Ensures the database updates before redirecting
    except Exception as e:
        logging.error(f"Error scraping articles: {e}")
        flash("Failed to update news articles. Please try again.", "error")
        return redirect(url_for('index')) # Redirect to the homepage

# Route to add new articles 
@app.route('/add', methods=['GET', 'POST'])
def add_article():
    if request.method == 'POST': # Checks if the request method is POST which means the form has been submitted
        try:
            # Retrieves the values from the submitted form data
            headline = request.form['headline']
            summary = request.form['summary']
            link = request.form['link']
        
            # Checks if headline or link are missing. If either is missing it returns an error message and 400 status code
            if not headline or not link:
                flash("Headline and link are required!", "error")
                return render_template('add_article.html')

            # Creates new NewsArticle object with the inputed headline, summary, and link.
            new_article = NewsArticle(headline=headline, summary=summary, link=link)
            session.add(new_article) # Adds the new article to the database session
            session.commit() # Commits the session to save the new article to the database
            
            flash("Article added successfully!", "success")
            return redirect(url_for('index')) # Redirect to the homepage
        
        except Exception as e:
            session.rollback() # Rollback in case of error
            logging.error(f"Error adding article: {e}")
            flash("Failed to add article. Please try again.", "error")
            return render_template('add_article.html')

    return render_template('add_article.html') # If the request method is GET, it renders the add_article.html template

# Route to edit an article based on id
@app.route('/edit/<int:id>', methods = ['GET', 'POST'])
def edit_article(id):
    try:
        article = session.query(NewsArticle).get(id) # Gets the article from the database with the specified id

        if not article: # If the article does not exist, it returns error message and 404 status code
            flash("Article not found!", "error")
            return redirect(url_for('index')) # Redirect to the homepage

        if request.method == 'POST': # Checks if the request method is POST which means the form was submitted
            # Retrieves the values from the submitted form data
            article.headline = request.form['headline']
            article.summary = request.form['summary']
            article.link = request.form['link']
            session.commit() # Commits the session to save the updated article to the database
            flash("Article updated successfully!", "success")
            return redirect(url_for('index')) # Redirect to the homepage
    
        return render_template('edit_article.html', article=article) # If the request method is GET, it renders the edit_article.html template and passes article object to the template
    except Exception as e:
        logging.error(f"Error editing article {id}: {e}")
        flash("An error occurred while updating the article.", "error")
        return redirect(url_for('index')) # Redirect to the homepage

# Route to delete an article by id
@app.route('/delete/<int:id>', methods=['POST'])
def delete_article(id):
    try:
        # if request.form.get('_method') == 'DELETE': # checks if the form includes hidden _method field with the value 'DELETE' to emulate HTTP DELETE request
        article = session.query(NewsArticle).get(id) # Retrieves article from the database with the specified id 
            # Checks if the article exists, then deletes article from session
        if article:
            session.delete(article)
            session.commit() # Commits the session
            flash("Article deleted successfully!", "success")
        else:
            flash("Article not found!", "error") 
    except Exception as e:
        logging.error(f"Error deleting article {id}: {e}")
        flash("An error occurred while deleting the article. Please try again.", "error")
    return redirect(url_for('index')) # Redirects to the homepage

if __name__ == "__main__":
    app.run(debug=True)