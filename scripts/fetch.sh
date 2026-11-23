#!/usr/bin/env bash
# Usage: fetch.sh <youtube-url>
# Downloads metadata + captions (no video), cleans the transcript, extracts metadata.
# Prints WORK=<dir>. Exit codes: 0 ok, 1 tool/download error, 2 no captions.
set -euo pipefail

URL="${1:?usage: fetch.sh <youtube-url>}"
HERE="$(cd "$(dirname "$0")" && pwd)"

command -v yt-dlp >/dev/null || { echo "ERROR: yt-dlp not installed (brew install yt-dlp)"; exit 1; }
command -v python3 >/dev/null || { echo "ERROR: python3 not installed"; exit 1; }

WORK="$(mktemp -d -t ytsum.XXXXXX)"
ARGS=(--skip-download --write-info-json --write-subs --write-auto-subs
      --sub-langs "en.*,en" --sub-format vtt -o "$WORK/v.%(ext)s")

if ! yt-dlp "${ARGS[@]}" "$URL" >"$WORK/yt-dlp.log" 2>&1; then
  echo "yt-dlp failed, retrying with Chrome cookies..."
  if ! yt-dlp "${ARGS[@]}" --cookies-from-browser chrome "$URL" >>"$WORK/yt-dlp.log" 2>&1; then
    echo "ERROR: yt-dlp failed. Last lines of log:"
    tail -n 5 "$WORK/yt-dlp.log"
    exit 1
  fi
fi

[ -f "$WORK/v.info.json" ] || { echo "ERROR: no metadata downloaded"; exit 1; }

# Prefer plain English, then any English variant, then anything.
VTT=""
for pattern in "v.en.vtt" "v.en-*.vtt" "v.*.vtt"; do
  match=$(ls "$WORK"/$pattern 2>/dev/null | head -n 1 || true)
  if [ -n "$match" ]; then VTT="$match"; break; fi
done

python3 "$HERE/meta.py" "$WORK/v.info.json" "$WORK/meta.json" >/dev/null

if [ -z "$VTT" ]; then
  echo "WORK=$WORK"
  echo "NO_CAPTIONS: this video has no English captions."
  exit 2
fi

python3 "$HERE/clean_vtt.py" "$VTT" > "$WORK/transcript.txt"

echo "WORK=$WORK"
echo "captions: $(basename "$VTT")"
echo "transcript: $WORK/transcript.txt ($(wc -w < "$WORK/transcript.txt" | tr -d ' ') words)"
echo "meta: $WORK/meta.json"
