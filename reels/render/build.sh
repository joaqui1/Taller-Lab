#!/usr/bin/env bash
# Pipeline completo: frames (Playwright) → audio (numpy) → MP4 (ffmpeg) → póster + hoja de contactos.
# Uso: ./build.sh [dir_trabajo] [id_reel ...]
#   dir_trabajo: carpeta temporal para frames/json/wav (por defecto ./out)
#   id_reel:     opcional; si se omite, procesa los 5 reels.
# Salida final: ../amoladoras/<n>-<id>.mp4 y .jpg
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="${1:-$HERE/out}"
shift || true
IDS=("$@")
DEST="$HERE/../amoladoras"
mkdir -p "$OUT" "$DEST"

# SKIP_RENDER=1 reutiliza frames/wav ya generados en $OUT (solo muxea).
if [ "${SKIP_RENDER:-0}" != "1" ]; then
  if [ ${#IDS[@]} -eq 0 ]; then
    node "$HERE/render.mjs" --out "$OUT"
    python3 "$HERE/audio.py" "$OUT"
  else
    node "$HERE/render.mjs" --out "$OUT" --reel "$(IFS=,; echo "${IDS[*]}")"
    python3 "$HERE/audio.py" "$OUT" "${IDS[@]}"
  fi
fi

n=0
for j in "$OUT"/*.json; do
  id="$(basename "$j" .json)"
  if [ ${#IDS[@]} -gt 0 ] && [[ ! " ${IDS[*]} " =~ " $id " ]]; then continue; fi
  n=$((n+1))
  fps="$(python3 -c "import json;print(json.load(open('$j'))['fps'])")"
  num="$(printf '%02d' "$n")"
  mp4="$DEST/$num-$id.mp4"
  # H.264 High 4:2:0, 30 fps, bitrate apto para Instagram/TikTok; AAC 192 kbps; moov al inicio.
  ffmpeg -y -loglevel error -framerate "$fps" -i "$OUT/$id/f%05d.jpg" -i "$OUT/$id.wav" \
    -c:v libx264 -preset slow -crf 20 -profile:v high -pix_fmt yuv420p -r "$fps" -g 60 \
    -vf "format=yuv420p" -colorspace bt709 -color_primaries bt709 -color_trc bt709 \
    -c:a aac -b:a 192k -ar 48000 -shortest -movflags +faststart "$mp4"
  # Póster: el frame del hook (≈ 1 s después del arranque).
  ffmpeg -y -loglevel error -ss 1.0 -i "$mp4" -frames:v 1 -q:v 2 "$DEST/$num-$id.jpg"
  echo "✔ $mp4 ($(du -h "$mp4" | cut -f1))"
done
