import os
import requests
import openai
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


load_dotenv()
client = OpenAI()  # This will automatically use OPENAI_API_KEY from the .env

load_dotenv()
nyt_api_key = os.getenv("NYT_API_KEY")

if not nyt_api_key:
    raise RuntimeError("❌ NYT_API_KEY not loaded. Check your .env file.")
else:
    print(f"✅ Loaded NYT API key: {nyt_api_key[:6]}...")


# Load API keys
load_dotenv()
nyt_api_key = os.getenv("NYT_API_KEY")
print("NYT API Key:", nyt_api_key)
openai.api_key = os.getenv("OPENAI_API_KEY")



def get_nyt_articles(query, max_results=5):
    """Fetch articles from the NYT Article Search API."""
    url = "https://api.nytimes.com/svc/search/v2/articlesearch.json"
    params = {
        "q": query,
        "sort": "newest",
        "api-key": nyt_api_key
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    articles = data.get("response", {}).get("docs", [])[:max_results]

    return [
        {
            "headline": article.get("headline", {}).get("main", ""),
            "abstract": article.get("abstract", ""),
            "lead_paragraph": article.get("lead_paragraph", ""),
            "url": article.get("web_url", ""),
            "pub_date": article.get("pub_date", "")[:10]
        }
        for article in articles
    ]

#def summarize_text(text, model="gpt-3.5-turbo"):
#    """Summarize a block of text using OpenAI (new SDK syntax)."""
def summarize_text(text, model="gpt-3.5-turbo"):
    return "🧪 This is a placeholder summary (OpenAI quota exceeded)."
    if not text.strip():
        return "No content available to summarize."

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes news articles."},
            {"role": "user", "content": f"Summarize this article:\n\n{text}"}
        ],
        temperature=0.5
    )
    return response.choices[0].message.content.strip()

def send_email(subject, summaries, recipient_email, sender_email, sender_password):
    # Create email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # Format the body as a bulleted HTML list
    body = "<h2>Article Summaries</h2><ul>"
    for summary in summaries:
        body += f"<li><strong>{summary['headline']}</strong><br>{summary['summary']}<br><a href='{summary['url']}'>Read more</a></li><br>"
    body += "</ul>"

    msg.attach(MIMEText(body, 'html'))

    # Send email using Gmail SMTP (change if using another provider)
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print("✅ Email sent successfully.")
    except Exception as e:
        print("❌ Failed to send email:", e)

def format_article_summary(article, summary):
    """Format article data and summary nicely."""
    return (
        f"📰 {article['headline']}\n"
        f"📅 Published: {article['pub_date']}\n"
        f"🔗 URL: {article['url']}\n\n"
        f"📝 Summary:\n{summary}\n"
        f"{'-'*60}\n"
    )

def main():
    query = input("Enter a search topic for NYT articles: ")
    articles = get_nyt_articles(query)

    summaries = []
    for i, article in enumerate(articles, start=1):
        print(f"\nArticle {i}: {article['headline']}\nURL: {article['url']}")
        if article['abstract']:
            summary = summarize_text(article['abstract'])
            print(f"Summary: {summary}")
            summaries.append({
                "headline": article['headline'],
                "summary": summary,
                "url": article['url']
            })
        else:
            print("No abstract available to summarize.")

    # Email config
    sender_email = os.getenv("EMAIL_ADDRESS")
    sender_password = os.getenv("EMAIL_PASSWORD")
    recipient_email = input("Enter recipient email address: ")

    send_email(
        subject=f"NYT Article Summaries: {query}",
        summaries=summaries,
        recipient_email=recipient_email,
        sender_email=sender_email,
        sender_password=sender_password
    )

if __name__ == "__main__":
    main()
