#!/usr/bin/env bash
# Vuelve a mezclar la pista declarada en cada reel sobre el MP4 ya renderizado, sin re-renderizar el video.
# Uso: bash reels/musica/remezclar_audio.sh 07 08 ...
set -euo pipefail
DIR="$(cd "$(dirname "$0")/.." && pwd)"
for pre in "$@"; do
  for html in "$DIR"/"$pre"-*.html; do
    name="$(basename "$html" .html)"
    track="$(grep -o 'name="reel-music" content="[^"]*"' "$html" | sed 's/.*content="//; s/"$//')"
    [ -n "$track" ] || { echo "$name: sin pista"; continue; }
    mp4="$DIR/salida/$name.mp4"
    ffmpeg -y -loglevel error -i "$mp4" -i "$DIR/musica/$track" -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart "$mp4.tmp.mp4"
    mv "$mp4.tmp.mp4" "$mp4"
    echo "$name ← $track"
  done
done
