
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

data = None

for attempt in range(5):
    try:
        print(f"Gemini Anfrage: Versuch {attempt + 1}/5")

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
            timeout=(20, 180)
        )

        if response.ok:
            data = response.json()
            break

        if response.status_code not in [408, 429, 500, 502, 503, 504]:
            raise RuntimeError(
                f"Gemini API Fehler {response.status_code}: "
                f"{response.text[:1500]}"
            )

        print(f"Gemini Fehler: {response.status_code}")

    except requests.RequestException as error:
        print(f"Verbindungsfehler: {error}")

    if attempt < 4:
        wait = min(15 * (2 ** attempt), 60)
        print(f"Warte {wait} Sekunden...")
        time.sleep(wait)

if data is None:
    raise RuntimeError(
        "Gemini konnte nach 5 Versuchen nicht antworten."
    )

try:
    answer = data["candidates"][0]["content"]["parts"][0]["text"]
    story = json.loads(answer)

except (KeyError, IndexError, TypeError, json.JSONDecodeError) as error:
    raise RuntimeError(
        f"KI-Antwort konnte nicht gelesen werden: {data}"
    ) from error

if not isinstance(story, dict):
    raise ValueError("Die Geschichte ist kein gültiges JSON-Objekt.")

scenes = story.get("scenes")

if not isinstance(scenes, list) or len(scenes) != 5:
    raise ValueError("Die Geschichte hat nicht genau 5 Szenen.")

for i, scene in enumerate(scenes):
    if not isinstance(scene, dict):
        raise ValueError(f"Szene {i + 1} ist ungültig.")

    if not scene.get("narration") or not scene.get("visual"):
        raise ValueError(f"Szene {i + 1} ist unvollständig.")

os.makedirs("output", exist_ok=True)

with open("output/story.json", "w", encoding="utf-8") as file:
    json.dump(story, file, ensure_ascii=False, indent=2)

print("Geschichte erfolgreich erstellt:", story.get("title"))
