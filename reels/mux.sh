#!/usr/bin/env bash
# Une video + audio con normalización de loudness para redes (-14 LUFS, pico -1 dBTP).
set -euo pipefail
cd "$(dirname "$0")"
declare -A NOMBRE=( [reel-01]="heladera-arranque" [reel-02]="inverter-no-es-silencioso" [reel-03]="decibeles-sin-condicion" [reel-04]="honda-6500-nominal-vs-maxima" [reel-05]="nafta-consumo-por-carga" [reel-06]="estacion-portatil-vs-generador" )
for n in "$@"; do
  out="salida/${n}-${NOMBRE[$n]}.mp4"
  ffmpeg -y -loglevel error -i "salida/$n.video.mp4" -i "salida/$n.wav" \
    -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -ar 48000 \
    -af "loudnorm=I=-14:TP=-1.0:LRA=9" -shortest -movflags +faststart "$out"
  echo "listo: $out"
done
