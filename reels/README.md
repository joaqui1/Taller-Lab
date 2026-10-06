# Reels de TallerLab

Reels verticales (1080×1920, 30 fps, 15–16 s) con la estética de la portada de tallerlab.com.ar:
misma paleta (`#faf9f6`, `#20272b`, naranja `#ff5a0a`), mismas tipografías (Plus Jakarta Sans,
JetBrains Mono para los "kickers", Caveat para los stickers manuscritos) y los mismos componentes
(panel oscuro con borde naranja, tarjetas claras, chips, punto de estado).

Cada reel es un HTML animado con CSS. El renderizador recorre la línea de tiempo cuadro por cuadro,
saca una captura con Chromium y arma el MP4 con ffmpeg. Al no haber audio, la pista musical se
agrega al publicar (Instagram/TikTok) con la biblioteca de la propia app.

## Reels

| Archivo | Tema | Dura | CTA |
| --- | --- | --- | --- |
| `01-manifiesto.html` | Presentación de la marca: título de portada, foto del taller, 8 categorías, 179 guías | 16 s | tallerlab.com.ar |
| `02-ficha-vs-nombre.html` | "Elite 200" declara 180 A; 160 A al 20 % vs 72 A al 100 % (ESAB HandyArc 162i) | 16 s | /soldadoras/ |
| `03-watts-casa.html` | Marcha vs arranque con el ejemplo del manual Lüsqtoff LG2500 | 16 s | /generadores/para-casa/ |
| `04-precios.html` | Observatorio: precio publicado y stock día por día, historial descargable | 15 s | /datos/precios-herramientas-argentina/ |
| `05-taladro-checklist.html` | Tres preguntas antes de comprar un taladro inalámbrico | 15 s | /taladros/inalambricos/ |
| `06-compresor-tanque.html` | Tanque (L) vs caudal (L/min) a la misma presión | 15 s | /compresores/50-litros/ |

Todos los datos que aparecen salen de fichas ya documentadas en el sitio
(`tallerlab_data/catalog_data/soldadoras_generadores.py`, `lote_generadores_06.py`, `home.py`).
La curva del reel 04 está marcada como ilustrativa y no representa un precio real.

## Vista previa

Abrí cualquier `NN-*.html` en Chrome o Edge: el reel se reproduce en bucle escalado a la ventana.
Un clic reinicia la reproducción.

## Renderizar

Requiere Node 18+, Playwright con Chromium y ffmpeg en el PATH.

```bash
npm i -D playwright && npx playwright install chromium   # una sola vez
node reels/render.cjs            # todos → reels/salida/NN-*.mp4 (+ NN-*-portada.jpg)
node reels/render.cjs 02 05      # solo algunos, por prefijo
FPS=30 PARALLEL=2 node reels/render.cjs
```

Cada MP4 sale en H.264 (yuv420p, CRF 19) listo para subir. La portada (`-portada.jpg`) se toma
en el segundo indicado por `<meta name="reel-poster">` de cada reel.

## Hacer un reel nuevo

1. Copiá el HTML que más se parezca y cambiá `<meta name="reel-duration">`.
2. Cada `<section class="scene">` es una escena: `--s` segundo de entrada, `--e` segundo de salida.
3. Los elementos entran con las clases `in-up`, `in-left`, `in-right`, `in-pop`, `in-clip`,
   `in-wipe`, `grow-x`, `grow-y`, `float` y el retraso `--d` (en segundos, absoluto en la línea de tiempo).
4. Un número que cuenta: `<span data-count="desde,hasta,segInicio,segFin">`.
5. Dejá libres los 300 px de abajo y los 150 px de arriba: ahí van los controles de la app.
   La marca va arriba (`.brand`) y la URL abajo (`.url`).
