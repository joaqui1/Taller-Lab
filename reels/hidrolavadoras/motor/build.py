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
    # masterización: medir LUFS integrado con ebur128, llevar a -14 LUFS y limitar a -2 dB de techo
    def lufs(path):
        p = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True)
        import re
        return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', p.stderr)[-1]), float(re.findall(r'Peak:\s+(-?[\d.]+) dBFS', p.stderr)[-1])
    i0, tp0 = lufs(wav)
    run([sys.executable, os.path.join(HERE, 'audio.py'), '--master', wav, '--gain-db', f'{-14.0 - i0:.2f}'])
    i1, tp1 = lufs(wav)
    print(f'loudness: {i0:.1f} -> {i1:.1f} LUFS, pico real {tp0:.1f} -> {tp1:.1f} dBTP')
    out = os.path.join(SALIDA, f'reel-{reel:02d}-{meta["slug"]}.mp4')
    run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-i', video, '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-level', '4.1',
         '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest', '-movflags', '+faststart', out])
    cover = os.path.join(PORTADAS, f'reel-{reel:02d}-{meta["slug"]}.jpg')
    run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-ss', str(COVER_T[reel]), '-i', video, '-frames:v', '1', '-q:v', '2', cover])
    print('LISTO', out)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--reel', type=int); ap.add_argument('--all', action='store_true'); ap.add_argument('--force', action='store_true')
    a = ap.parse_args()
    for r in (range(1, 7) if a.all else [a.reel]):
        build(r, a.force)
