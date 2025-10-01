#!/usr/bin/env python3
import os, json, random, requests, asyncio, edge_tts
from moviepy.editor import *
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# -------- hard-coded keywords (30 days) ----------
KEYWORDS = [
    "Dubai mansion", "super-yacht", "Ferrari limited", "Malibu villa",
    "private jet interior", "Beverly Hills estate", "Rolex Daytona",
    "Lamborghini yacht", "Tesla Model S Plaid", "Richard Mille watch",
    "Bugatti Chiron", "penthouse Manhattan", "champagne diamond",
    "Hermes Birkin", "Cartier necklace", "Rolls-Royce Boat Tail",
    "Versace palace", "Monaco apartment", "Hennessy mansion",
    "gold-plated iPhone", "Christian Louboutin shoes", "Gulfstream G700",
    "Amsterdam canal house", "Bentley Batur", "Patek Philippe",
    "Las Vegas penthouse", "French chateau", "Italian super-car",
    "skyscraper condo", "royal jewellery"
]
# -------------------------------------------------

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_creds():
    info = json.loads(os.environ["YT_SECRET"])
    creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    return creds

def fetch_script(topic):
    # free ChatGPT tier (3/hr) – fallback dummy text
    try:
        import openai
        openai.api_key = None   # uses anonymous
        r = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"55-second countdown about expensive {topic}, hook, 3 facts, price reveal."}]
        )
        return r['choices'][0]['message']['content']
    except Exception as e:
        print("OpenAI error:", e)
        return f"Top 3 most expensive {topic} ever sold. Number 3 … (dummy text)"

async def tts(text, outfile):
    communicate = edge_tts.Communicate(text, "en-US-AriaNeural", rate="+20%")
    await communicate.save(outfile)

def fetch_clips(keyword, n=3):
    # Pixabay API – no key needed for 100 requests/hr
    url = f"https://pixabay.com/videos/api/?q={keyword}&orientation=vertical&per_page={n}"
    data = requests.get(url, timeout=15).json()
    urls = [item['videos']['tiny']['url'] for item in data.get('hits', [])][:n]
    print("Fetched clips:", urls)
    return urls

def make_video(keyword):
    script = fetch_script(keyword)
    print("Script:", script[:100], "...")
    asyncio.run(tts(script, "voice.mp3"))
    audio = AudioFileClip("voice.mp3")
    clips = []
    for url in fetch_clips(keyword):
        clip = VideoFileClip(url).resize(height=1920).crop(x_center=540, width=1080, height=1920)
        clips.append(clip)
    if not clips:
        raise RuntimeError("No clips downloaded – check internet or keyword")
    final = concatenate_videoclips(clips, method="compose").set_audio(audio)
    final.write_videofile("short.mp4", fps=30, codec="libx264", audio_codec="aac", logger=None)
    print("Video rendered: short.mp4")

def upload_yt(file, title):
    creds = get_creds()
    youtube = build("youtube", "v3", credentials=creds)
    body = {"snippet": {"title": title, "categoryId": "24", "tags": ["luxury", "expensive", "countdown"]},
            "status": {"privacyStatus": "public"}}
    media = MediaFileUpload(file, chunks=-1, resumable=True)
    response = youtube.videos().insert(part="snippet,status", body=body, media_body=media).execute()
    print("Uploaded – id:", response["id"])

def main():
    keyword = random.choice(KEYWORDS)
    print("Chosen keyword:", keyword)
    make_video(keyword)
    upload_yt("short.mp4", f"Top 3 Most Expensive {keyword} 🤯 #luxury")
    print("=== Job finished ===")

if __name__ == "__main__":
    main()
