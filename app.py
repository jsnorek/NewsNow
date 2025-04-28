# Routes

import io
import os
import shutil
from flask import Flask, Response, jsonify, redirect, render_template, request, url_for, flash 
from models import Weather, add_article_to_index, create_or_open_index, search_articles_complex_1, search_articles_complex_2, session, NewsArticle, CommunityArticle
from sentiment_and_summary import get_sentiment_and_summary
from summary import get_summary
from weather import get_weather
import logging
from models import search_articles
import matplotlib.pyplot as plt
import base64
import matplotlib
matplotlib.use('Agg') 
from config import Config

app = Flask(__name__) 
app.secret_key = 'secret'


app.config["DATABASE_URL"] = Config.DATABASE_URL
app.config["NEWS_SITE_USERNAME"] = Config.NEWS_SITE_USERNAME
app.config["NEWS_SITE_PASSWORD"] = Config.NEWS_SITE_PASSWORD

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
        page = request.args.get('page', 1, type=int) # Retrieves the page query parameter from the URL
        per_page = 5 # Number of articles per page

        #Fetch paginated news articles
        total_articles = session.query(NewsArticle).count() # Counts all articles
        total_pages = (total_articles + per_page - 1) // per_page # Calculate total pages and round up when needed

        # Queries NewsArticle table in the database to retrieve subset of records and stores in news_article variable as a list of NewsArticle objects 
        news_articles = session.query(NewsArticle).offset((page - 1) * per_page).limit(per_page).all() # Offset skips the articles that appear on previous page and limit fetches the 5 per page
        community_articles = session.query(CommunityArticle).order_by(CommunityArticle.created_at.desc()).all()
        
        # Fetch weather data
        weather_data = session.query(Weather).order_by(Weather.last_updated.desc()).first()
        # Returns rendered HTML template and passes news_articles to template as articles
        return render_template(
            'index.html', articles=news_articles, weather=weather_data, community_articles=community_articles,
            page=page, total_articles=total_articles, per_page=per_page, total_pages=total_pages
        )
    except Exception as e:
        logging.error(f"Error loading homepage: {e}")
        flash("An error occurred while loading the page. Please try again", "error")
        return render_template('index.html', articles=[], weather=[], page=1, total_articles=0, per_page=5, total_pages=1)


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
    search_type = request.args.get('search_type', 'headline_summary')  # Retrieves the selected search type (default: 'headline_summary')
    try:
        if query: # If search term was entered
            
            # Call the appropriate search function based on the search type selected
            if search_type == 'headline_summary':
                results = search_articles_complex_1(query)  # Search across headline & summary
            elif search_type == 'wildcard_phrase':
                results = search_articles_complex_2(query)  # Search with wildcards or phrase
            else:
                results = []
                flash("Invalid search type selected.", "error")
            if not results:
                flash("No articles found for your search.", "info")
        else:
            results = [] # If no search term entered results is assigned empty list
            flash("Please enter a search term.", "info")
        
        # Fetch weather data so it's always available
        weather_data = session.query(Weather).first()

        # Ensure pagination variables are always passed, even for searches
        total_articles = len(results)
        per_page = 5 # Keep it consistent with the main page
        total_pages = (total_articles + per_page - 1) // per_page
        page = 1 # Default to the first page when searching 

        # Renders index.html and passes results to the template for display
        return render_template('index.html', articles=results, weather=weather_data, 
                                page=page, total_articles=total_articles, 
                                per_page=per_page, total_pages=total_pages) 
    except Exception as e:
        logging.error(f"Error searching articles: {e}")
        flash("An error occurred during search. Please try again.", "error")
        return render_template('index.html', articles=[], page=1, total_articles=0, per_page=5, total_pages=1)
    
# Route to re-scrape for updated articlees
@app.route('/scrape', methods = ['POST'])
def scrape():
    try:
        session.expire_all() # Tells SQLAlchemy session to expire all instances it has loaded 
        session.commit() # Commits pending transactions to the database to ensure the session is clean

        from scraper import scrape_news # Imports scrape_news
        # scrape_news() # Calls scrape_news function to re-scrape for articles
        scraped_articles = scrape_news()

        for article in scraped_articles:
            add_article_to_index(article)  # Add each scraped article to the Whoosh index

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
            
            # Add the new article to the Whoosh index
            add_article_to_index(new_article)
            
            flash("Article added successfully!", "success")
            return redirect(url_for('index')) # Redirect to the homepage
        
        except Exception as e:
            session.rollback() # Rollback in case of error
            logging.error(f"Error adding article: {e}")
            flash("Failed to add article. Please try again.", "error")
            return render_template('add_article.html')

    return render_template('add_article.html') # If the request method is GET, it renders the add_article.html template

# Route to add new community articles
@app.route('/add_community', methods=['GET', 'POST'])
def add_community_article():
    if request.method == 'POST': # Checks if the request method is POST, indicating form submission
        try:
            # Retrieves the values from the submitted form data
            username = request.form['username'] # Username of the community member submitting the article
            title = request.form['title'] # Title of the community article
            content = request.form['content'] # Main content/body of the article
            link = request.form['link'] # Reference link or additional resource URL
            author = request.form['author'] # Author of the content

            # Checks if any required fields are missing; if so, it returns an error message
            if not username or not title or not content or not link or not author:
                flash("All fields are required", "error")
                return render_template('add_community_article.html')
            
            # Creates a new CommunityArticle object with the provided data
            new_article = CommunityArticle(username=username, title=title, content=content, link=link, author=author)
            session.add(new_article) # Adds the new article to the database session
            session.commit() # Commits the session to save the new article in the database

            # Flash a success message upon successful addition of the article
            flash("Community article added successfully!", "success")
            return redirect(url_for('index')) # Redirects the user to the homepage
        
        except Exception as e:
            session.rollback() # Rolls back the session to prevent partial commits
            logging.error(f"Error adding community article: {e}") # Logs the error for debugging purposes
            flash("Failed to add article. Please try again.", "error") # Displays an error message to the user
            return render_template('add_community_article.html')  # Re-renders the add community article form
        
    return render_template('add_community_article.html') # If the request method is GET, render the add_community_article.html template

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

@app.route('/reindex', methods=['GET'])
def reindex():
    index_dir = "indexdir"

    # Delete the index directory to remove duplicates
    if os.path.exists(index_dir):
        shutil.rmtree(index_dir)
        print("Index deleted.")

    # Recreate the index
    ix = create_or_open_index()  
    writer = ix.writer()

    # Add fresh articles to the index
    articles = session.query(NewsArticle).all()
    for article in articles:
        writer.add_document(
            id=str(article.id),
            headline=article.headline,
            summary=article.summary or '',
            link=article.link
        )

    writer.commit()
    print("Reindexing completed.")
    return redirect(url_for('index'))

# Route for generating the weather chart
@app.route('/weather_chart')
def weather_chart():
    try:
        # Query weather data
        weather_entries = session.query(Weather).order_by(Weather.last_updated).all()

        if not weather_entries:
            return "No weather data available.", 404

        # Extract data
        dates = [entry.last_updated for entry in weather_entries]
        temps = [entry.temp for entry in weather_entries]

        # Create a plot
        plt.figure(figsize=(8, 4))
        plt.plot(dates, temps, marker='o', linestyle='-', color='b', label='Temperature')
        plt.xlabel('Date')
        plt.ylabel('Temperature (°C)')
        plt.title('Weather Temperature Trends for Sonoma')
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Save plot to a buffer
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plt.close()  # Close the plot to free memory

        # Return the image as a response
        return Response(img.getvalue(), mimetype='image/png')

    except Exception as e:
        print(f"Error generating weather chart: {e}")
        return "Failed to generate weather chart.", 500

# Route to call and save article sentiment and summary from OpenAI API function
@app.route('/api/sentiment-and-summary', methods=['POST'])
def sentiment_and_summary():
    # Extract JSON data from the incoming request
    data = request.get_json()
    article_title = data.get('title') # Get the article title from the request
    article_content = data.get('content') # Get the article content from the request

    print(f"Received Article: {article_title}") # Debugging output to confirm received title

    try:
        # Get sentiment and summary from AI
        result = get_sentiment_and_summary(article_title, article_content)

        print(f"AI Summary: {result['summary']}")  # Debugging output
        print(f"Sentiment: {result['sentiment']}")  # Debugging output

        if result["summary"] and result["sentiment"]: # Verify AI provided both sentiment and summary
            # Find the article in the database by title
            article = session.query(NewsArticle).filter_by(headline=article_title).first()

            if article: # If the article exists in the database
                print("Updating article in the database...")
                # Update the article with the sentiment and summary
                article.ai_summary = result["summary"]
                article.sentiment = result["sentiment"]

                # Commit the changes to the database
                session.commit()
                print("Database updated successfully!")

                # Return the AI-generated summary and sentiment as a JSON response
                return jsonify({
                    "ai_summary": result["summary"],
                    "sentiment": result["sentiment"]
                })
            else:
                # If the article is not found, return an error message
                print("Error: Article not found in database.")
                return jsonify({"error": "Article not found"}), 404
        else:
            # Handle incomplete AI responses
            return jsonify({"error": "Incomplete AI response"}), 500
    except Exception as e:
        # Log errors and return an internal server error response
        print(f"Error generating sentiment and summary: {e}")
        return jsonify({"error": "Internal server error"}), 500

# Route to call and save only article summary from OpenAI API function    
@app.route('/api/summary', methods=['POST'])
def summary():
    # Extract JSON data from the incoming request
    data = request.get_json()
    article_title = data.get('title') # Get the article title from the request
    article_content = data.get('content') # Get the article content from the request

    try:
        # Use AI to generate a summary for the article
        result = get_summary(article_title, article_content)

        if result: # If the AI provides a summary
            # Return the summary as a JSON response
            return jsonify({"summary": result}), 200
        else:
            # Handle incomplete AI responses
            return jsonify({"error": "Incomplete AI response"}), 500
    except Exception as e:
        # Log errors and return an internal server error response
        print(f"Error generating summary: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(debug=True)