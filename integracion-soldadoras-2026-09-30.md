# Afiliados de soldadoras — 30/09/2026

Integración local de **31 productos únicos, 66 CTA en 27 guías**. El referido Bremen 8240 repetido en la lista se registró una sola vez. Cada oferta aparece una sola vez por guía, en las ubicaciones editoriales de la tabla adjunta; los grupos MMA/Flux/MIG/TIG se mantienen separados cuando corresponde. No se realizó despliegue externo.

Los bloques conservan las fichas y tablas originales. Los enlaces abren en otra pestaña con `nofollow sponsored noopener noreferrer`, aviso de afiliación y registro de clics. Se suprimen los estantes y notas comerciales automáticos de estas rutas para evitar repetición.

La guía principal se muestra abierta dentro del hub `/soldadoras/`, con las cuatro ofertas inmediatamente después de «Qué soldadora elegir según el trabajo». Sus enlaces internos se corrigieron al prefijo `/soldadoras/`. Se añadió una aclaración de análisis documental a seis guías con ofertas que no cumplían el filtro editorial del servidor por carecer de «Análisis TallerLab»; no se declara nueva comprobación física ni verificación de publicaciones.

## Diferencias frente a las presentaciones previstas

- Conarco 7018 de 2,5 mm: el referido recibido dice **1 kg**, no 5 kg.
- Conarco 7018 de mayor diámetro: se rotula **3,2 mm**, según el título recibido, sin convertirlo a 3,25 mm.
- ESAB/Conarco macizo: por corrección del usuario, la tarjeta industrial de **1,6 mm × 18 kg** se reemplazó por **ER70S-6 / OK Autrod 12.51 · 0,8 mm × 5 kg**, conservando el referido `https://meli.la/1fzxaCM`. Según la publicación actual indicada por el usuario, declara **AWS A5.18 ER70S-6, Ø0,8 mm y bobina de 5 kg**. Se mantiene junto a Bremen 8240 en la guía de alambre MIG; el catálogo y el bloque generado reflejan la corrección.
- Flux E71T-GS de 0,8 mm: la guía conserva **ESAB Gas Free · 5 kg**, ahora identificada como E71T-GS, y suma **Bremen 7992 · 1 kg** con el referido suministrado. Las dos tarjetas permiten comparar presentaciones de bobina con la misma clasificación y diámetro.
- Bremen 8240 es **ER70S-6 macizo**, no Flux.
- Las ofertas SML150-8D/SML120-8DK se presentan como alternativas actuales en las guías de SML150-8/SML130-7 discontinuadas. ST-1X tiene CTA «Ver disponibilidad y verificar lote».
- Los títulos incompletos de Iron 100 y Smart TIG requieren cotejo de código en placa. La publicación recibida para Dogo 160 declara DOG50044 / STAR 160. Los 20 A de SML150-8D y los 38 A de MIGDUAL200-9 no se usan para alterar sus fichas.
- La guía de inverter 160 A agrupa HandyArc 162i y DOG50044 como comparación MMA principal; la HandyArc MIG 160i queda debajo en un estante separado. Las tarjetas DOG50044 enlazan al referido exacto recibido para ese modelo.
- En la guía SML120-8D, la tarjeta SML150-8D tiene una descripción específica de su código, rango, ciclo y accesorios; el estante de ofertas va después del checklist de compra y las notas de 200/220 V y del kit.
- La guía de electrodos inoxidables suma dos publicaciones de 3,2 mm × 2 kg: Lastrade Infinity E308L-16 y E316L-16. No se añadió 309L.

## Pendientes

Faltan enlaces para la referencia específica ESAB/Conarco WELD ER70S-6 0,8 mm × 5 kg en la guía MIG con gas y ESAB Gas Free E71T-GS 1,0 mm × 1 kg. Están registrados en `soldadoras-ofertas.json`. La guía de alambre MIG incluye la opción ER70S-6 / OK Autrod 12.51 de 0,8 mm × 5 kg; la guía Flux ofrece ESAB y Bremen E71T-GS de 0,8 mm × 5 kg y 1 kg, respectivamente.

Punto y carro MIG conservan cero CTA. La guía de inoxidable incorpora dos ofertas E308L-16 y E316L-16; no se añadió una tercera opción 309L. No se añadieron ofertas NiFe, TIG de precisión, TAURO ni otros consumibles que el usuario no suministró.

## Validación

`python verificar_soldadoras_comerciales.py`: OK. 28 productos, 63 CTA en 26 guías, 28 rutas HTTP 200; ubicación, enlaces únicos, atributos, registro de clics, un H1 por página, IDs sin duplicación, integridad editorial e integración idempotente. Vista de escritorio comprobada en el navegador.

Validación del reemplazo de alambre: dos tarjetas en la guía, Bremen idéntica, clasificación y presentación corregidas, sin cambios en el contenido fuera del bloque ni en las otras guías. El verificador directo falla porque `HEAD` ya contiene bloques comerciales y su comparación presupone una base sin ellos. Al normalizar también la referencia de `HEAD` con los mismos marcadores y nota de análisis, pasan todas sus comprobaciones, incluidas las 28 rutas HTTP 200 y la idempotencia.

Los verificadores de sierras, hidrolavadoras y generadores también pasaron. El verificador global de hubs no ejecutó por falta de Flask accesible en `.qa-deps`. El verificador de compresores falla por la referencia previa `AV000009`; no se modificó ese catálogo en este lote.

Las consultas web a cuatro enlaces cortos (Iron 100, Gas Free, alambre ESAB/Conarco y 7018 de 2,5 mm) devolvieron destino inaccesible. Los títulos provienen del usuario: no se acredita precio, stock, vendedor, lote ni contenido actual de las publicaciones.
