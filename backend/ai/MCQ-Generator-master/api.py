import os
import requests
import json
from dotenv import load_dotenv

# 🔄 Load environment variables from .env
load_dotenv()

# 🔐 Get API key securely
API_KEY = os.getenv("GEMINI_API_KEY")

# API endpoint
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

# Example prompt
prompt = "Generate a multiple-choice question from this paragraph:\nThe Great Wall of China stretches over 13,000 miles and is one of the greatest structures ever built."

# Payload for Gemini API
payload = {
    "contents": [
        {
            "parts": [
                {"text": prompt}
            ]
        }
    ]
}

# Headers
headers = {
    "Content-Type": "application/json"
}

# Send request
response = requests.post(url, headers=headers, data=json.dumps(payload))

# Output response
if response.status_code == 200:
    reply = response.json()
    print("🧠 Gemini Response:\n", reply["candidates"][0]["content"]["parts"][0]["text"])
else:
    print("❌ Error:", response.status_code, response.text)
