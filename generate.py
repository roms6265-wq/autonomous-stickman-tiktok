import os
import requests
import json

API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY fehlt in GitHub Secrets!")

url = (
    "https://generativelanguage.googleapis.com/v1beta/"
    "models/gemini-2.5-flash:generateContent"
)

prompt = """
Create an exciting English Stickman TikTok story.

Requirements:
- Exactly 5 scenes.
- 105 to 115 words total.
- A powerful hook.
- A surprising ending.
- Each scene needs narration and visual description.

Return valid JSON only:
{
  "title": "Story title",
  "scenes": [
    {"narration": "Text", "visual": "Description"}
  ]
}
"""

response = requests.post(
    url,
    params={"key": API_KEY},
    json={
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    },
    timeout=90
)

if not response.ok:
    raise RuntimeError(
        f"Gemini API Fehler {response.status_code}: "
        f"{response.text[:1500]}"
    )

data = response.json()

try:
    answer = data["candidates"][0]["content"]["parts"][0]["text"]
    story = json.loads(answer)
except (KeyError, IndexError, json.JSONDecodeError) as error:
    raise RuntimeError(f"KI-Antwort konnte nicht gelesen werden: {data}") from error

if len(story.get("scenes", [])) != 5:
    raise ValueError("Die Geschichte hat nicht genau 5 Szenen.")

os.makedirs("output", exist_ok=True)

with open("output/story.json", "w", encoding="utf-8") as file:
    json.dump(story, file, ensure_ascii=False, indent=2)

print("Geschichte erfolgreich erstellt:", story["title"])
