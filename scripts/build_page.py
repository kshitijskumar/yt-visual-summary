"""Usage: build_page.py <meta.json> <body.html> [--out-dir DIR] [--no-open]

Wraps a body fragment into a self-contained HTML page:
- inlines assets/style.css
- adds the header (title, channel, duration, upload date) from meta.json
- turns [[mm:ss]] / [[h:mm:ss]] markers into timestamp links to the video
- refuses to write if the body loads any external resource
Prints the output path and opens it unless --no-open."""
import argparse
import datetime
import html
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

p = argparse.ArgumentParser()
p.add_argument("meta")
p.add_argument("body")
p.add_argument("--out-dir", default=str(Path.home() / "yt-summaries"))
p.add_argument("--no-open", action="store_true")
a = p.parse_args()

meta = json.load(open(a.meta, encoding="utf-8"))
body = Path(a.body).read_text(encoding="utf-8")
css = (HERE.parent / "assets" / "style.css").read_text(encoding="utf-8")
vid = meta["id"]
watch = f"https://www.youtube.com/watch?v={vid}"


def to_secs(stamp):
    parts = [int(x) for x in stamp.split(":")]
    while len(parts) < 3:
        parts.insert(0, 0)
    h, m, s = parts
    return h * 3600 + m * 60 + s


body = re.sub(
    r"\[\[(\d{1,2}(?::\d{2}){1,2})\]\]",
    lambda m: f'<a class="ts" href="{watch}&t={to_secs(m.group(1))}s">{m.group(1)}</a>',
    body,
)

# Only links to the video itself are allowed as external URLs; nothing may be loaded.
bad = [
    u for u in re.findall(r'(?:src|href)\s*=\s*["\'](https?://[^"\']+)', body)
    if not re.match(r"https?://(www\.)?(youtube\.com|youtu\.be)/", u)
]
bad += re.findall(r'src\s*=\s*["\'](//[^"\']+)', body)
bad += re.findall(r"@import|url\(\s*['\"]?https?://", body)
if bad:
    print("ERROR: body references external resources:", *bad, sep="\n  ")
    sys.exit(1)

dur = meta.get("duration") or 0
h, rem = divmod(int(dur), 3600)
dur_s = f"{h}h {rem // 60}m" if h else f"{rem // 60} min"
up = meta.get("upload_date") or ""
up_s = datetime.datetime.strptime(up, "%Y%m%d").strftime("%d %b %Y") if len(up) == 8 else ""
title = html.escape(meta.get("title") or "Untitled")
channel = html.escape(meta.get("channel") or "")
meta_line = " · ".join(x for x in [channel, dur_s, up_s] if x)

page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
{css}
</style>
</head>
<body>
<main>
<header>
<h1><a href="{watch}">{title}</a></h1>
<p class="meta">{meta_line}</p>
</header>
{body}
<footer class="meta">Summary generated from the video's captions · <a href="{watch}">Watch on YouTube</a></footer>
</main>
</body>
</html>
"""

slug = re.sub(r"[^a-z0-9]+", "-", (meta.get("title") or vid).lower()).strip("-")[:60] or vid
out_dir = Path(a.out_dir).expanduser()
out_dir.mkdir(parents=True, exist_ok=True)
out = out_dir / f"{datetime.date.today():%Y-%m-%d}-{slug}.html"
out.write_text(page, encoding="utf-8")
print(out)

if not a.no_open:
    opener = "open" if sys.platform == "darwin" else "xdg-open"
    try:
        subprocess.run([opener, str(out)], check=False)
    except FileNotFoundError:
        pass
