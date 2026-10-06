# Reels TallerLab · Generadores

Seis reels verticales (1080×1920, 30 fps, 16–17 s) sobre generadores, generados por código con la estética de tallerlab.com.ar (crema `#f4f2ed`, carbón `#20272b`, naranja `#ff5a0a`, Plus Jakarta Sans + JetBrains Mono + Caveat) y datos tomados de las guías publicadas en `paginas/generadores/`.

| Reel | Hook | Guía fuente |
| :--- | :--- | :--- |
| 01 | Tu heladera dice 150 W → 750 VA al arrancar | `/generadores/para-casa/` |
| 02 | Inverter no significa silencioso | `/generadores/inverter/` |
| 03 | 63 dB no te dice nada (sin distancia ni carga) | `/generadores/silenciosos/` |
| 04 | Dice 6500, entrega 5,0 kVA | `/generadores/honda-6500/` |
| 05 | El tanque no te dice cuánto gasta | `/generadores/a-nafta/` |
| 06 | Sin motor, sin nafta: ¿alcanza? (W ≠ Wh) | `/generadores/estacion-de-energia-portatil/` |

## Cómo se generan

- `src/reel-0X.html` describe cada reel como escenas con tiempo determinista (`window.__seek(t)`), usando `src/engine.js` (tweens, tipografía cinética, contadores, barras, canvas) y `src/base.css` (tokens de la web).
- `render.cjs` abre cada HTML con Playwright/Chromium, avanza frame a frame y lo manda a ffmpeg (H.264, CRF 17). También exporta `salida/<reel>.timeline.json` con los eventos sonoros que cada escena registra (`impact`, `whoosh`, `ticks`, `blip`, `engine`, `sting`…).
- `audio.py` sintetiza con numpy/scipy la música (kick, hats, clap, sub, bajo, pad con filtro, arpegio Karplus-Strong, sidechain, reverb por convolución) por secciones `hook / build / full / outro` y el sound design sincronizado a esos eventos. No usa muestras externas.
- `mux.sh` une video y audio con `loudnorm` a −14 LUFS (estándar de redes).

```bash
cd reels
npm i -g playwright   # o usar el Chromium ya instalado
./build.sh            # todos los reels
./build.sh reel-03    # uno solo
node render.cjs reel-03 --preview 16   # 16 frames de previsualización en salida/preview-reel-03/
```

Los MP4 finales quedan en `salida/reel-0X-<nombre>.mp4`.

## Datos usados (todos de las guías)

- Heladera: 300 VA en marcha, 450–750 VA al arrancar (manual Lüsqtoff LG2500); cuenta con 3 lámparas de 100 VA → 600 VA marcha, 750–1.050 VA pico.
- Gamma GE3497AR: 63 dB al 50 % y 69 dB al 100 % a 7 m (ficha en dB, no dB(A)).
- Honda EG6500CXS 5,0 / 5,5 kVA; EZ6500CXS 5,5 / 6,5 kVA; GX390; 3,5 L/h a 3.600 rpm; tanques 24 L y 15,5 L; 8,1 h y 5,8 h.
- Gamma GE3481AR 6000V: 2,2 L/h al 50 %, 3,6 L/h al 100 % (manual); página: 10 h / 6 h con 25 L.
- EcoFlow DELTA 2: 1.024 Wh, 1.800 W / 2.700 W, 12 kg. BLUETTI AC70: 768 Wh, 1.000 W / 1.500 W, 10,2 kg; ejemplo del manual: 40 W ≈ 10,7 h.
