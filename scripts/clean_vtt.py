import html, re, sys

def secs(stamp):
    parts = stamp.strip().split(":")
    parts = [float(p) for p in parts]
    while len(parts) < 3:
        parts.insert(0, 0.0)
    h, m, s = parts
    return int(h * 3600 + m * 60 + s)

def mmss(t):
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"

cues, last, cur = [], None, 0
for raw in open(sys.argv[1], encoding="utf-8"):
    line = raw.rstrip("\n")
    if "-->" in line:
        cur = secs(line.split("-->")[0].split()[0])
        continue
    s = line.strip()
    if not s or s.startswith(("WEBVTT", "Kind:", "Language:", "NOTE")) or s.isdigit():
        continue
    text = html.unescape(re.sub(r"<[^>]+>", "", s)).strip()
    if not text or text == last:
        continue
    cues.append((cur, text))
    last = text

# group into ~30s paragraphs
block = int(sys.argv[2]) if len(sys.argv) > 2 else 30
para_start, buf = None, []
for t, text in cues:
    if para_start is None:
        para_start = t
    if t - para_start >= block and buf:
        print(f"[{mmss(para_start)}] {' '.join(buf)}")
        para_start, buf = t, []
    buf.append(text)
if buf:
    print(f"[{mmss(para_start)}] {' '.join(buf)}")
