
import os
import requests
import json
import time

API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY fehlt in GitHub Secrets!")

MODELS = ["gemini-2.5-flash"]

prompt = """
Create an exciting English Stickman TikTok story.

Requirements:
- Exactly 5 scenes.
- 105 to 115 words total across all narration.
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

payload = {
    "contents": [{"parts": [{"text": prompt}]}],
    "generationConfig": {
        "responseMimeType": "application/json",
        "temperature": 0.9
    }
}

story = None
last_error = None

for model in MODELS:
    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        + model + ":generateContent"
    )

    for attempt in range(3):
        try:
            print(f"Gemini: {model}, Versuch {attempt + 1}/3")

            response = requests.post(
                url,
                params={"key": API_KEY},
                json=payload,
                timeout=(15, 90)
            )

            if response.ok:
                data = response.json()
                answer = data["candidates"][0]["content"]["parts"][0]["text"]
                candidate = json.loads(answer)

                if not isinstance(candidate, dict):
                    raise ValueError("Ungültiges JSON-Objekt.")

                scenes = candidate.get("scenes")

                if not isinstance(scenes, list) or len(scenes) != 5:
                    raise ValueError("Es müssen genau 5 Szenen sein.")

                for i, scene in enumerate(scenes, start=1):
                    if not isinstance(scene, dict):
                        raise ValueError(f"Szene {i} ist ungültig.")
                    if not scene.get("narration") or not scene.get("visual"):
                        raise ValueError(f"Szene {i} ist unvollständig.")

                words = sum(
                    len(scene["narration"].split())
                    for scene in scenes
                )

                if not 105 <= words <= 115:
                    raise ValueError(
                        f"Die Geschichte hat {words} Wörter."
                    )

                story = candidate
                break

            last_error = f"HTTP {response.status_code}: {response.text[:500]}"
            print(last_error)

            if response.status_code not in (408, 429, 500, 502, 503, 504):
                break

        except (
            requests.RequestException,
            ValueError,
            KeyError,
            IndexError,
            TypeError
        ) as error:
            last_error = str(error)
            print("Fehler:", last_error)

        if attempt < 2:
            wait = 10 * (2 ** attempt)
            print(f"Warte {wait} Sekunden...")
            time.sleep(wait)

    if story is not None:
        break

if story is None:
    raise RuntimeError(
        "Gemini konnte nicht antworten. Letzter Fehler: "
        + str(last_error)
    )

os.makedirs("output", exist_ok=True)

with open("output/story.json", "w", encoding="utf-8") as file:
    json.dump(story, file, ensure_ascii=False, indent=2)

print("Geschichte erfolgreich erstellt:", story.get("title"))
