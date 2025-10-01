import os, random, requests
from moviepy.editor import *

# -------- 30 luxury keywords ----------
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
    # same simple text
    return (f"Top 3 most expensive {topic} ever sold. "
            f"Number 3 … unknown luxury piece. "
            f"Number 2 … even bigger mystery. "
            f"Number 1 … priceless. "
            f"Like for more luxury lists!")

def make_silent_voice(duration=5):
    # 5-second silent audio (no speaker needed)
    subprocess.run([
        "ffmpeg", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", str(duration), "-q:a", "9", "-acodec", "mp3", "voice.mp3"
    ], check=True)

def fetch_clips(keyword, n=3):
    url = f"https://pixabay.com/videos/api/?q={keyword}&orientation=vertical&per_page={n}"
    data = requests.get(url, timeout=15).json()
    return [item['videos']['tiny']['url'] for item in data.get('hits', [])][:n]

def make_video(keyword):
    script = make_script(keyword)
    print("Script:", script)

    # 5-second silent MP3 – made with MoviePy (no ffmpeg call)
    silent_audio = AudioFileClip("").subclip(0, 5)  # empty = silent
    silent_audio.write_audiofile("voice.mp3", fps=44100, logger=None)

    audio = AudioFileClip("voice.mp3")
    clips = []
    for url in fetch_clips(keyword):
        clip = (VideoFileClip(url)
                .resize(height=1920)
                .crop(x_center=540, width=1080, height=1920))
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
    print("=== All done ===")

if __name__ == "__main__":
    main()
