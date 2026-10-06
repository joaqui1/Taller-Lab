# Reels TallerLab

Producción de reels verticales (1080 × 1920, 30 fps) con la identidad visual del sitio, generados por código para que
cada pieza sea reproducible, editable y fiel a los datos de las guías.

- `amoladoras/` → los 5 reels terminados (`.mp4`) con su portada (`.jpg`).
- `guiones-amoladoras.md` → guion por segundo, copy y hashtags de cada reel, notas de publicación.
- `render/` → el pipeline:
  - `engine.html` + `engine.js`: motor determinista. `seek(t)` deja el DOM exactamente como corresponde al instante `t`
    (titulares palabra a palabra, paneles con clip, stickers Caveat, tablas de specs, contadores, discos SVG girando,
    chispas en canvas, grano, wipes naranja, sacudida y flash de cámara en los impactos).
  - `reels.mjs`: la definición de cada reel (timeline, textos, datos, eventos de audio).
  - `render.mjs`: captura los frames con Playwright/Chromium y exporta la lista de eventos.
  - `audio.py`: sintetiza música y sound design (numpy + scipy) a partir de esos eventos. Sin samples externos.
  - `build.sh`: frames → audio → `ffmpeg` → MP4 H.264/AAC con `faststart`, póster y numeración.
  - `fonts/`: Plus Jakarta Sans, Caveat y JetBrains Mono (licencia OFL), las mismas familias que usa el sitio.

## Regenerar

Requisitos: Node 22 con Playwright y Chromium instalados, Python 3 con `numpy` y `scipy`, `ffmpeg`.

```bash
cd reels/render
./build.sh                       # los 5 reels
./build.sh ./out r3-disco-equivocado   # uno solo
SKIP_RENDER=1 ./build.sh ./out   # solo volver a muxear con frames/wav ya generados
node render.mjs --out ./out --reel r1-115-o-125 --preview 0.9,2.8,6.2   # PNG de QA en instantes dados
```

`render.mjs` toma Playwright de `/opt/node-tools/node_modules/playwright`; si está en otro lado, ajustá el `import`
o exportá `CHROMIUM_PATH`.

## Cómo editar un reel

1. Cambiá textos, tiempos o datos en `reels.mjs` (cada `E.shot(t0, t1, …)` es una escena; los componentes reciben
   tiempos locales a la escena).
2. Verificá con `--preview` los instantes clave.
3. Corré `build.sh`. El audio se vuelve a componer solo: cada componente emite sus eventos (`word`, `tick`, `impact`,
   `whoosh`, `spinup`, `grind`, `check`, `logo`…) y `audio.py` los convierte en sonido sincronizado.

Los datos que se muestran deben seguir saliendo de `/paginas` y de las fichas de fabricante citadas allí.
