import os
import requests
import json
from datetime import datetime

API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY fehlt!")

url = (
    "https://generativelanguage.googleapis.com/v1beta/"
    "models/gemini-2.5-flash:generateContent"
)

prompt = """
Create one highly engaging English Stickman story for TikTok.

Requirements:
- 105 to 115 spoken words.
- Exactly 5 scenes.
- A powerful hook in the first sentence.
- A surprising twist at the end.
- Each scene must contain a visual description.
- Narration should be exciting and easy to understand.

Return ONLY valid JSON in this format:
{
  "title": "Story title",
  "scenes": [
    {
      "narration": "Spoken text",
      "visual": "Stickman visual description"
    }
  ]
}
"""

response = requests.post(
    url,
    params={"key": API_KEY},
    json={
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    },
    timeout=60
)

response.raise_for_status()

result = response.json()
text = result["candidates"][0]["content"]["parts"][0]["text"]

text = text.strip()
if text.startswith("```"):
    text = text.split("\n", 1)[1].rsplit("```", 1)[0]

story = json.loads(text)

if len(story["scenes"]) != 5:
    raise ValueError("Die Geschichte muss genau 5 Szenen haben.")

os.makedirs("output", exist_ok=True)

with open("output/story.json", "w", encoding="utf-8") as file:
    json.dump(story, file, ensure_ascii=False, indent=2)

print("Geschichte erfolgreich erstellt:", story["title"])
