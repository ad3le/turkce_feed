# make_episode.py — pip install edge-tts feedgen
import asyncio, json, sys, datetime, subprocess
import edge_tts
from pathlib import Path
from feedgen.feed import FeedGenerator

BASE = "https://ad3le.github.io/turkce_feed"  # ← your Pages URL
ROOT = Path(__file__).parent
AUDIO = ROOT / "audio"; AUDIO.mkdir(exist_ok=True)
META = ROOT / "episodes.json"

def slug():
    return datetime.datetime.now().strftime("%Y%m%d-%H%M")

def make_audio(text, name, voice="tr-TR-EmelNeural"):
    out = AUDIO / f"{name}.mp3"
    async def _run():
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(out))
    asyncio.run(_run())
    return out

def build_feed():
    eps = json.loads(META.read_text(encoding="utf-8")) if META.exists() else []
    fg = FeedGenerator(); fg.load_extension("podcast")
    fg.title("Türkçe Hikayeler"); fg.link(href=BASE)
    fg.description("My Turkish learning stories"); fg.language("tr")
    for ep in eps:                      # newest first handled by app
        fe = fg.add_entry()
        fe.id(ep["url"]); fe.title(ep["title"])
        fe.enclosure(ep["url"], str(ep.get("size", 0)), "audio/mpeg")
        fe.pubDate(ep["date"])
    fg.rss_file(str(ROOT / "feed.xml"), pretty=True)

if __name__ == "__main__":
    title = sys.argv[1] if len(sys.argv) > 1 else "Hikaye"
    text = Path(sys.argv[2]).read_text(encoding="utf-8")  # text file path
    name = slug()
    out_path = make_audio(text, name, "tr-TR-EmelNeural")
    eps = json.loads(META.read_text(encoding="utf-8")) if META.exists() else []
    eps.insert(0, {
        "title": title,
        "url": f"{BASE}/audio/{name}.mp3",
        "date": datetime.datetime.now().astimezone().isoformat(),
        "size": out_path.stat().st_size,      # ← add this line
    })
    META.write_text(json.dumps(eps, indent=2, ensure_ascii=False), encoding="utf-8")
    build_feed()
    print(f"Added '{title}'. Now: git add -A && git commit -m '{title}' && git push")