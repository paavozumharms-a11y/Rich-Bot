#!/usr/bin/env python3
"""
Ultra-simple TikTok luxury bot
- silent audio (numpy)
- 3 free clips from Pixabay
- uploads to YOUR TikTok channel
"""
import os, random, requests, numpy as np
from moviepy.editor import *
from moviepy.audio.AudioClip import AudioArrayClip

# 30 luxury keywords
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

def make_script(topic):
    # simple template – no internet calls
    return (f"Top 3 most expensive {topic} ever sold. "
            f"Number 3 … unknown luxury piece. "
            f"Number 2 … even bigger mystery. "
            f"Number 1 … priceless. "
            f"Like for more luxury lists!")

def make_silent_mp3(duration=5):
    """Silent stereo MP3 – no ffmpeg, no speaker"""
    sr = 44100
    # 2 identical silent channels (stereo)
    silence = np.zeros((int(sr * duration), 2), dtype=np.float32)
    audio_clip = AudioArrayClip(silence, fps=sr)
    audio_clip.write_audiofile("voice.mp3", logger=None)

def fetch_clips(keyword, n=3):
    """Pixabay first – if empty/fail use self-made silent video"""
    # 1) try Pixabay
    try:
        url = f"https://pixabay.com/videos/api/?q={keyword}&orientation=vertical&per_page={n}"
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            data = r.json()
            urls = [item['videos']['tiny']['url'] for item in data.get('hits', [])][:n]
            if urls:
                return urls
    except Exception as e:
        print("Pixabay fail:", e)

    # 2) self-made silent 9:16 video (black) – no internet, no URL
    print("Using self-made silent video")
    return ["selfmade"]  # special flag
    
def make_video(keyword):
    script = make_script(keyword)
    print("Script:", script)
    make_silent_mp3(5)  # 5-second silent MP3

    audio = AudioFileClip("voice.mp3")
    urls = fetch_clips(keyword)

    # if we got "selfmade", create silent black video
    if urls == ["selfmade"]:
        black_clip = ColorClip(size=(1080, 1920), color=(0, 0, 0), duration=5)
        black_clip = black_clip.set_audio(AudioArrayClip(np.zeros((int(44100 * 5), 2)), fps=44100))
        black_clip.write_videofile("selfmade.mp4", fps=30, logger=None)
        clips = [VideoFileClip("selfmade.mp4")]
    else:
        clips = [VideoFileClip(u).resize(height=1920).crop(x_center=540, width=1080, height=1920) for u in urls]

    if not clips:
        raise RuntimeError("No clips – this should never happen now")

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
    print("=== All done ===")

if __name__ == "__main__":
    main()
