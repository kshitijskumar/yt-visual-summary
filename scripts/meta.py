"""Usage: meta.py <v.info.json> <out meta.json>
Extracts the fields the summary needs from yt-dlp's info.json and prints them."""
import json
import sys

src, dst = sys.argv[1], sys.argv[2]
d = json.load(open(src, encoding="utf-8"))

def mmss(t):
    t = int(t or 0)
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"

meta = {
    "id": d.get("id"),
    "url": d.get("webpage_url") or f"https://www.youtube.com/watch?v={d.get('id')}",
    "title": d.get("title"),
    "channel": d.get("channel") or d.get("uploader"),
    "duration": d.get("duration"),
    "upload_date": d.get("upload_date"),
    "chapters": [
        {"start": mmss(c.get("start_time")), "title": c.get("title")}
        for c in (d.get("chapters") or [])
    ],
    "description": (d.get("description") or "")[:1500],
}

json.dump(meta, open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(meta, ensure_ascii=False, indent=1))
