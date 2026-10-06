#!/usr/bin/env python3
"""Pipeline completo de un reel: video (Playwright) + audio (numpy) + mezcla final con loudnorm.

    python3 build.py --reel 1            # usa el video ya renderizado si existe
    python3 build.py --reel 1 --force    # vuelve a renderizar los fotogramas
    python3 build.py --all
"""
import argparse, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(HERE, '..', 'salida')
TMP = os.path.join(SALIDA, 'tmp')
PORTADAS = os.path.join(SALIDA, 'portadas')
COVER_T = {1: 2.9, 2: 2.4, 3: 3.1, 4: 2.9, 5: 2.9, 6: 3.2}


def run(cmd, **kw):
    print('$', ' '.join(cmd)); subprocess.run(cmd, check=True, **kw)


def build(reel, force=False):
    os.makedirs(PORTADAS, exist_ok=True)
    video = os.path.join(TMP, f'reel-{reel}-video.mp4')
    if force or not os.path.exists(video):
        run(['node', os.path.join(HERE, 'render.mjs'), '--reel', str(reel), '--video'])
    run([sys.executable, os.path.join(HERE, 'audio.py'), '--reel', str(reel)])
    meta = json.load(open(os.path.join(TMP, f'reel-{reel}-events.json')))['meta']
    wav = os.path.join(TMP, f'reel-{reel}-audio.wav')
    # loudnorm en dos pasadas (objetivo Instagram/TikTok: -14 LUFS, pico real -1 dBTP)
    p = subprocess.run(['ffmpeg', '-hide_banner', '-i', wav, '-af', 'loudnorm=I=-14:TP=-1:LRA=9:print_format=json', '-f', 'null', '-'], capture_output=True, text=True)
    j = json.loads(p.stderr[p.stderr.rfind('{'):])
    ln = (f"loudnorm=I=-14:TP=-1:LRA=9:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}"
          f":measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true:print_format=summary")
    out = os.path.join(SALIDA, f'reel-{reel:02d}-{meta["slug"]}.mp4')
    run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-i', video, '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-level', '4.1',
         '-af', ln, '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest', '-movflags', '+faststart', out])
    cover = os.path.join(PORTADAS, f'reel-{reel:02d}-{meta["slug"]}.jpg')
    run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-ss', str(COVER_T[reel]), '-i', video, '-frames:v', '1', '-q:v', '2', cover])
    print('LISTO', out)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--reel', type=int); ap.add_argument('--all', action='store_true'); ap.add_argument('--force', action='store_true')
    a = ap.parse_args()
    for r in (range(1, 7) if a.all else [a.reel]):
        build(r, a.force)
