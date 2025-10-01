#!/usr/bin/env python3
import os, json, random, requests, asyncio
from moviepy.editor import *

KEYWORDS = [
    "Dubai mansion","super-yacht","Ferrari limited","Malibu villa",
    "private jet interior","Beverly Hills estate","Rolex Daytona",
    "Lamborghini yacht","Tesla Model S Plaid","Richard Mille watch",
    "Bugatti Chiron","penthouse Manhattan","champagne diamond",
    "Hermes Birkin","Cartier necklace","Rolls-Royce Boat Tail",
    "Versace palace","Monaco apartment","Hennessy mansion",
    "gold-plated iPhone","Christian Louboutin shoes","Gulfstream G700",
    "Amsterdam canal house","Bentley Batur","Patek Philippe",
    "Las Vegas penthouse","French chateau","Italian super-car",
    "skyscraper condo","royal jewellery"
]

def fetch_script(topic):
    # free ChatGPT tier (3/hr) – fallback dummy
    try:
        import openai
        openai.api_key = None
        r = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"55-second countdown about expensive {topic}, hook, 3 facts, price reveal."}]
        )
        return r['choices'][0]['message']['content']
    except Exception as e:
        print("OpenAI fail – dummy text:", e)
        return f"Top 3 most expensive {topic} ever sold … (dummy text)"

async def tts(text, outfile):
    engine = pyttsx3.init()
    engine.setProperty('rate', 180)  # speed
    engine.save_to_file(text, outfile)
    engine.runAndWait()

def fetch_clips(keyword, n=3):
    url = f"https://pixabay.com/videos/api/?q={keyword}&orientation=vertical&per_page={n}"
    data = requests.get(url, timeout=15).json()
    return [item['videos']['tiny']['url'] for item in data.get('hits', [])][:n]

def make_video(keyword):
    script = fetch_script(keyword)
    print("Script:", script[:100], "...")
    tts(script, "voice.mp3")
    audio = AudioFileClip("voice.mp3")
    clips = []
    for url in fetch_clips(keyword):
        clip = VideoFileClip(url).resize(height=1920).crop(x_center=540, width=1080, height=1920)
        clips.append(clip)
    if not clips:
        raise RuntimeError("No clips downloaded – check internet or keyword")
    final = concatenate_videoclips(clips, method="compose").set_audio(audio)
    final.write_videofile("short.mp4", fps=30, codec="libx264", audio_codec="aac", logger=None)
    print("Video ready: short.mp4")

def upload_tt(file, title):
    url = "https://open-api.tiktok.com/share/video/upload/"
    headers = {"Authorization": f"Bearer {os.environ['TT_ACCESS_TOKEN']}"}
    files = {"video": open(file, "rb")}
    data = {"description": title}
    r = requests.post(url, headers=headers, files=files, data=data, timeout=30)
    print("TikTok upload:", r.status_code, r.text)

def main():
    keyword = random.choice(KEYWORDS)
    print("Keyword:", keyword)
    make_video(keyword)
    upload_tt("short.mp4", f"Top 3 Most Expensive {keyword} 🤯 #luxury #fyp")
    print("=== Finished ===")

if __name__ == "__main__":
    main()
