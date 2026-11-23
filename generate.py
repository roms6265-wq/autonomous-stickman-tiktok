
import os
import requests
import json
import time

API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY fehlt in GitHub Secrets!")

url = (
    "https://generativelanguage.googleapis.com/v1beta/"
    "models/gemini-3.8-flash:generateContent"
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

response = None

for attempt in range(3):
    try:
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

        if response.ok:
            break

        if response.status_code in [429, 500, 502, 503, 504]:
            print(
                f"Gemini Fehler {response.status_code}. "
                f"Versuch {attempt + 1}/3"
            )
            time.sleep(10)
        else:
            raise RuntimeError(
                f"Gemini API Fehler {response.status_code}: "
                f"{response.text[:1500]}"
            )

    except requests.RequestException as error:
        print(f"Verbindungsfehler: {error}")
        if attempt == 2:
            raise
        time.sleep(10)

if response is None or not response.ok:
    raise RuntimeError(
        "Gemini ist nach 3 Versuchen nicht erreichbar: "
        + (response.text[:1500] if response is not None else "Keine Antwort")
    )

data = response.json()

try:
    answer = data["candidates"][0]["content"]["parts"][0]["text"]
    story = json.loads(answer)
except (KeyError, IndexError, json.JSONDecodeError) as error:
    raise RuntimeError(
        f"KI-Antwort konnte nicht gelesen werden: {data}"
    ) from error

if len(story.get("scenes", [])) != 5:
    raise ValueError("Die Geschichte hat nicht genau 5 Szenen.")

os.makedirs("output", exist_ok=True)

with open("output/story.json", "w", encoding="utf-8") as file:
    json.dump(story, file, ensure_ascii=False, indent=2)

print("Geschichte erfolgreich erstellt:", story["title"])
