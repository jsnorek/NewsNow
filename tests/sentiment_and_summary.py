import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_sentiment_and_summary(title, content):
    # Combine the title and content into a single string
    text = f"{title}\n\n{content}"

    # Construct the prompt
    prompt = f"""
    Analyze the following news article and provide:
    1. A brief 1 sentence summary
    2. The sentiment (Positive, Neutral, or Negative)

    Article:
    {text}

    Format:
    Summary: ...
    Sentiment: ...
    """

    # Make the API call
    response = client.chat.completions.create(
        model="gpt-4o", 
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes news articles and detects sentiment."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )

    # Extract the AI's response
    content = response.choices[0].message.content

    # Parse the summary and sentiment
    summary = ""
    sentiment = ""
    for line in content.splitlines():
        if line.lower().startswith("summary:"):
            summary = line.split(":", 1)[1].strip()
        elif line.lower().startswith("sentiment:"):
            sentiment = line.split(":", 1)[1].strip()

    return {
        "summary": summary,
        "sentiment": sentiment
    }
