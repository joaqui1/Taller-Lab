# Afiliados de soldadoras — 30/09/2026

Integración local de **28 productos únicos, 63 CTA en 26 guías**. El referido Bremen 8240 repetido en la lista se registró una sola vez. Cada oferta aparece una sola vez por guía, en las ubicaciones editoriales de la tabla adjunta; los grupos MMA/Flux/MIG/TIG se mantienen separados cuando corresponde. No se realizó despliegue externo.

Los bloques conservan las fichas y tablas originales. Los enlaces abren en otra pestaña con `nofollow sponsored noopener noreferrer`, aviso de afiliación y registro de clics. Se suprimen los estantes y notas comerciales automáticos de estas rutas para evitar repetición.

La guía principal se muestra abierta dentro del hub `/soldadoras/`, con las cuatro ofertas inmediatamente después de «Qué soldadora elegir según el trabajo». Sus enlaces internos se corrigieron al prefijo `/soldadoras/`. Se añadió una aclaración de análisis documental a seis guías con ofertas que no cumplían el filtro editorial del servidor por carecer de «Análisis TallerLab»; no se declara nueva comprobación física ni verificación de publicaciones.

## Diferencias frente a las presentaciones previstas

- Conarco 7018 de 2,5 mm: el referido recibido dice **1 kg**, no 5 kg.
- Conarco 7018 de mayor diámetro: se rotula **3,2 mm**, según el título recibido, sin convertirlo a 3,25 mm.
- ESAB/Conarco macizo: el recibido dice **E70-S6, 1,6 mm × 18 kg**. Se incluye como presentación industrial distinta sólo en la guía de alambre MIG; debe confirmarse clasificación en etiqueta y alimentador compatible. No se vincula como consumible para las máquinas compactas ni reemplaza el WELD ER70S-6 previsto.
- ESAB Gas Free: se incluye el recibido de **0,8 mm × 5 kg** en la guía de Flux, sin atribuirle AWS ni parámetros no incluidos en el título.
- Bremen 8240 es **ER70S-6 macizo**, no Flux.
- Las ofertas SML150-8D/SML120-8DK se presentan como alternativas actuales en las guías de SML150-8/SML130-7 discontinuadas. ST-1X tiene CTA «Ver disponibilidad y verificar lote».
- Los títulos incompletos de Iron 100, Smart TIG y Dogo 160/180 requieren cotejo de código en placa. Los 20 A de SML150-8D y los 38 A de MIGDUAL200-9 no se usan para alterar sus fichas.

## Pendientes

Faltan enlaces para ESAB/Conarco WELD ER70S-6 0,8 mm × 5 kg, Bremen E71T-GS 0,8 mm × 1 kg y ESAB Gas Free E71T-GS 1,0 mm × 1 kg. Están registrados en `soldadoras-ofertas.json`.

Punto, carro MIG e inoxidable conservan cero CTA. La guía de inoxidable sigue fuera de publicación por un requisito editorial previo; esta integración no altera esa página. No se añadieron ofertas NiFe, TIG de precisión, TAURO ni consumibles inoxidables que el usuario no suministró.

## Validación

`python verificar_soldadoras_comerciales.py`: OK. 28 productos, 63 CTA en 26 guías, 28 rutas HTTP 200; ubicación, enlaces únicos, atributos, registro de clics, un H1 por página, IDs sin duplicación, integridad editorial e integración idempotente. Vista de escritorio comprobada en el navegador.

Los verificadores de sierras, hidrolavadoras y generadores también pasaron. El verificador global de hubs no ejecutó por falta de Flask accesible en `.qa-deps`. El verificador de compresores falla por la referencia previa `AV000009`; no se modificó ese catálogo en este lote.

Las consultas web a cuatro enlaces cortos (Iron 100, Gas Free, alambre ESAB/Conarco y 7018 de 2,5 mm) devolvieron destino inaccesible. Los títulos provienen del usuario: no se acredita precio, stock, vendedor, lote ni contenido actual de las publicaciones.
