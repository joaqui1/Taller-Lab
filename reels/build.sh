#!/usr/bin/env bash
# Pipeline completo: render de frames -> audio sintetizado -> mux.
set -euo pipefail
cd "$(dirname "$0")"
REELS=${*:-"reel-01 reel-02 reel-03 reel-04 reel-05 reel-06"}
node render.cjs $REELS
python3 audio.py $REELS
bash mux.sh $REELS
