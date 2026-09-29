# Afiliación de compresores — 29/09/2026

Integración local: 26 referidos registrados, 25 usados en las ubicaciones solicitadas. Se añadieron 33 cards en 16 guías, con enlaces en las filas correspondientes y CTAs por página. Se conservaron JD Extreme 107 y los registros previos; para las ofertas nuevas de Nictom IE01 y AA-5000K se usan los referidos recibidos en esta solicitud.

Las páginas de mangueras, acoples rápidos, aceite y filtros no muestran enlaces afiliados ni cards. Las cards se insertan dentro del contenido en el punto editorial indicado, sin una segunda estantería al pie.

## Modelos que requieren referido

No se encontraron enlaces afiliados para estos diez modelos en el repositorio ni en la lista recibida. Sus filas documentales se conservan; no se crean enlaces de compra ni cards vacías.

- Gadnic AV000009.
- Gamma G2802AR y G2802KAR.
- Fengda FD-186K, AS-186 y AS-196.
- Einhell TE-AC 270/50 Silent y TE-AC 430/90/10.
- Lüsqtoff LC-40200.
- BTA CSA-50-2, código 272009.2.

Las asignaciones y los pendientes por URL están en `compresores-ofertas.json`. Para completarlos, agregar las ofertas exactas a `OFFERS` en `compresores_comerciales.py` y ejecutar `python integrar_compresores_comerciales.py`.

## Correspondencia de modelos

- El BTA 272057.2 recibido es D-CA2-50-6, de 50 L y 2 HP. Está registrado, pero no se coloca como CSA-50-2 sin aceite: la guía identifica este último como 272009.2 y 1,5 HP. No hay una ubicación solicitada para el primero.
- Gadnic AV37-TY tiene su propio referido y se muestra en doble pistón; no se reutiliza para AV000009.
- La oferta LC-2550BK no incluye el sufijo -8 en el título suministrado. Su card señala que se debe confirmar placa y kit antes de atribuirle las especificaciones de LC2550BK-8.
- El Stanley FCCC404STC005 recibido anuncia 50 L; la publicación histórica citada en la guía describe 24 L para ese código. La card se ubica en disponibilidad local, con la discrepancia visible, y no toma datos del D210 histórico.
- El IE01 recibido anuncia negro; no se utiliza como foto exacta la imagen gris del registro anterior.

No se verificaron precio ni stock. Los tres enlaces cortos consultados para aclarar variantes no fueron accesibles con la herramienta web. Las descripciones nuevas se atribuyen a los títulos recibidos; las cards usan imágenes ilustrativas identificadas, sin presentar fotografías genéricas como fotos del modelo.

## Publicación y validación

Diez guías marcadas `published: true` eran excluidas por el servidor por falta de etiquetas de atribución. Se completaron las notas documentales y de análisis ausentes. Acoples también necesitaba el encabezado exacto `Fuentes consultadas`, que ahora contiene sus referencias originales. No se cambiaron los datos técnicos.

Validaciones realizadas:

- `python verificar_compresores_comerciales.py`: 19 asignaciones, 33 cards en 16 guías, CTAs, posición editorial, enlaces internos, atributos de afiliación y eventos válidos.
- Las 23 URLs de compresores responden HTTP 200 en el servidor local.
- Segunda ejecución de la integración: cero cambios; no duplica columnas, enlaces ni cards.
- `git diff --check`: sin errores de espacios.

Limitaciones de otras comprobaciones: `verificar_seleccion.py` contiene una expectativa antigua de 72 recursos frente a los 74 actuales; `verificar_integracion_comercial.py` exige guías de otras categorías que el servidor ya excluye. Esos controles no validan esta integración. La entrada Flask no pudo comprobarse porque sus dependencias locales no eran accesibles. No se realizó despliegue ni revisión visual en navegador.
