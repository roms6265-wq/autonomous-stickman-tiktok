import json
import os
import asyncio
import subprocess
from PIL import Image, ImageDraw, ImageFont
import edge_tts

os.makedirs("output", exist_ok=True)

with open("output/story.json", encoding="utf-8") as f:
    story = json.load(f)

W, H = 1080, 1920
SCENE_SECONDS = 8
VOICE = "en-US-GuyNeural"

async def make_voice(text, filename):
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(filename)

def make_scene(scene, index):
    img = Image.new("RGB", (W, H), "#111827")
    draw = ImageDraw.Draw(img)

    draw.text((70, 100), f"SCENE {index + 1}", fill="white")

    # Simple animated-stickman starting frame
    cx, cy = W // 2, H // 2
    draw.ellipse((cx-45, cy-250, cx+45, cy-160),
                 outline="white", width=12)
    draw.line((cx, cy-160, cx, cy+100), fill="white", width=12)
    draw.line((cx, cy-80, cx-100, cy+10), fill="white", width=12)
    draw.line((cx, cy-80, cx+100, cy+10), fill="white", width=12)
    draw.line((cx, cy+100, cx-90, cy+250), fill="white", width=12)
    draw.line((cx, cy+100, cx+90, cy+250), fill="white", width=12)

    font = ImageFont.load_default(size=48)
    draw.text((70, 1550), scene["narration"][:100],
              fill="white", font=font)

    img.save(f"output/scene_{index}.png")

async def main():
    for i, scene in enumerate(story["scenes"]):
        make_scene(scene, i)
        await make_voice(
            scene["narration"],
            f"output/voice_{i}.mp3"
        )

    with open("output/list.txt", "w") as f:
        for i in range(len(story["scenes"])):
            f.write(
                f"file 'scene_{i}.png'\n"
                f"duration {SCENE_SECONDS}\n"
            )
        f.write(f"file 'scene_{len(story['scenes'])-1}.png'\n")

    print("Szenen und Stimmen erstellt.")

asyncio.run(main())
