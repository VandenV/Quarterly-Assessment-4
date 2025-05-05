import os
import requests
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

# Load environment variables from .env file
load_dotenv()

# API keys
nyt_api_key = os.getenv("NYT_API_KEY")
# Email credentials
sender_email = os.getenv("EMAIL_ADDRESS")
sender_password = os.getenv("EMAIL_PASSWORD")

def get_nyt_articles(query, max_results=5):
    """Fetch articles from the NYT Article Search API."""
    url = "https://api.nytimes.com/svc/search/v2/articlesearch.json"
    params = {
        "q": query,
        "sort": "newest",
        "api-key": nyt_api_key
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        articles = data.get("response", {}).get("docs", [])[:max_results]

        return [
            {
                "headline": article.get("headline", {}).get("main", "No headline"),
                "abstract": article.get("abstract", "No abstract available."),
                "url": article.get("web_url", "#")
            }
            for article in articles
        ]
    except Exception as e:
        print("❌ Failed to fetch NYT articles:", e)
        return []

# Placeholder summarizer if OpenAI quota exceeded
def summarize_text(text, model="gpt-3.5-turbo"):
    return "🧪 This is a placeholder summary (OpenAI quota exceeded)."

def send_email(subject, summaries, recipient_email, sender_email, sender_password):
    """Send formatted summary email via Gmail SMTP."""
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # Create an HTML body with a bulleted list
    body = "<h2>NYT Article Summaries</h2><ul>"
    for article in summaries:
        body += f"<li><strong>{article['headline']}</strong><br>{article['summary']}<br><a href='{article['url']}'>Read full article</a></li><br>"
    body += "</ul>"

    msg.attach(MIMEText(body, 'html'))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print("✅ Email sent successfully.")
    except Exception as e:
        print("❌ Failed to send email:", e)

def main():
    query = input("Enter a search topic for NYT articles: ")
    articles = get_nyt_articles(query)

    summaries = []
    for i, article in enumerate(articles, start=1):
        print(f"\nArticle {i}: {article['headline']}\nURL: {article['url']}")
        summary = summarize_text(article['abstract'])
        print(f"Summary: {summary}")
        summaries.append({
            "headline": article['headline'],
            "summary": summary,
            "url": article['url']
        })

    recipient_email = input("\nEnter recipient email address: ")
    send_email(
        subject=f"NYT Article Summaries: {query}",
        summaries=summaries,
        recipient_email=recipient_email,
        sender_email=sender_email,
        sender_password=sender_password
    )

if __name__ == "__main__":
    main()

print("Email:", sender_email)
print("Password:", sender_password)
