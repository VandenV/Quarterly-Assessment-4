from dotenv import load_dotenv
import os

load_dotenv()

nyt_api_key = os.getenv("NYT_API_KEY")
openai_key = os.getenv("OPENAI_API_KEY")

if not nyt_api_key:
    raise RuntimeError("❌ NYT_API_KEY is missing or not loading.")
else:
    print(f"✅ NYT API Key loaded: {nyt_api_key[:6]}...")

if not openai_key:
    raise RuntimeError("❌ OPENAI_API_KEY is missing or not loading.")
