import sys, os
from PIL import Image, ImageFilter
import numpy as np
from collections import deque

def cutout(src, dst, thr=235):
    im = Image.open(src).convert('RGB')
    a = np.asarray(im).astype(np.int16)
    h, w, _ = a.shape
    near = (a.min(axis=2) >= thr)  # near-white pixels
    # flood fill from borders over near-white region
    mask = np.zeros((h, w), bool)
    q = deque()
    for x in range(w):
        for y in (0, h-1):
            if near[y, x] and not mask[y, x]: mask[y, x] = True; q.append((y, x))
    for y in range(h):
        for x in (0, w-1):
            if near[y, x] and not mask[y, x]: mask[y, x] = True; q.append((y, x))
    while q:
        y, x = q.popleft()
        for ny, nx in ((y-1,x),(y+1,x),(y,x-1),(y,x+1)):
            if 0 <= ny < h and 0 <= nx < w and near[ny, nx] and not mask[ny, nx]:
                mask[ny, nx] = True; q.append((ny, nx))
    alpha = (~mask).astype(np.uint8) * 255
    # soften edge: partial alpha for light pixels adjacent to bg
    al = Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(0.8))
    al = np.asarray(al).astype(np.float32) / 255
    # un-premultiply-ish: pull light fringe toward object color
    rgb = a.astype(np.float32)
    out = np.dstack([rgb, al[..., None] * 255]).astype(np.uint8)
    img = Image.fromarray(out, 'RGBA')
    # crop to content bbox with margin
    ys, xs = np.where(al > 0.05)
    if len(ys):
        img = img.crop((max(0, xs.min()-4), max(0, ys.min()-4), min(w, xs.max()+5), min(h, ys.max()+5)))
    img.save(dst)
    print(dst, img.size)

for name in sys.argv[2:]:
    src = f"assets/productos/{name}"
    dst = os.path.join(sys.argv[1], os.path.splitext(name)[0].split('-')[0] + '.png') if not name.startswith('portada') else os.path.join(sys.argv[1], name.rsplit('-',1)[0].replace('portada-real-hidrolavadoras-','') + '.png')
    cutout(src, dst)
