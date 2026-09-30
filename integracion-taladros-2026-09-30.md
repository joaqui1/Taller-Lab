# Enlaces comerciales de taladros — 30/09/2026

Integración local de **32 productos únicos y 32 CTA en las 17 rutas propuestas por el usuario**. Los textos de los botones y sus destinos se conservan según la tabla recibida. No se realizó despliegue externo.

Las ofertas aparecen después de la comparación o sección que explica su función, con aviso comercial y atributos `nofollow sponsored noopener noreferrer`. Se desactivan las notas y estantes comerciales automáticos en esas 17 rutas para evitar repetir los nuevos CTA. Los enlaces previos del cuerpo, como la oferta Omaha en taladros de banco, se conservan.

## Distribución aplicada

| Ruta | Productos |
| :--- | :--- |
| `/taladros/bosch-inalambrico/` | GSR 120-LI, GSB 18V-50 |
| `/taladros/black-decker/` | BCD702C1-AR, BLD783D1 |
| `/taladros/einhell-inalambrico/` | TE-CD 18/40 Li Solo, TP-CD 18/50 con sufijo Li-i a confirmar |
| `/taladros/rotomartillo-bosch/` | GBH 220, GBH 2-26 DRE, GBH 180-LI |
| `/taladros/percutores/` | GSB 550 RE |
| `/taladros/taladro-de-banco/` | TBL16-7, TBL710-9D |
| `/taladros/atornillador-impacto-dewalt/` | DCF887B, DCF850B |
| `/taladros/dewalt-inalambrico/` | DCD796D2, DCD805B |
| `/taladros/para-durlock/` | GTB 650, DCF620B |
| `/taladros/rotomartillo-einhell/` | TC-RH 620 4F, TE-RH 28/1 5F |
| `/taladros/rotomartillo-dewalt/` | DCH273B |
| `/taladros/mecha-porcelanato/` | Bosch EXPERT HEX-9 6 mm, RUBI EASYGRES 6 mm |
| `/taladros/milwaukee/` | M12 FUEL 3404-20, M18 FUEL 2904-20 y kit 2904-259A |
| `/taladros/lusqtoff-inalambrico/` | TIL23-8B, TAL60-9B, TIL45131-8BK |
| `/taladros/brocas-ceramica/` | Bosch CYL-9 6 mm |
| `/taladros/stanley/` | SDH700, SBD715C2K |
| `/taladros/mechas-escalonadas/` | Bosch HSS 4–20 mm, 2608597519 |

## Identidad y variantes

Las fichas y tablas existentes se conservan. Estas diferencias se explican en las tarjetas:

- **TBL16-7 / TB-16:** el título de la oferta no confirma el modelo TB-16 documentado; no se trasladan velocidades, recorrido ni peso.
- **TBL710-9D:** el título recibido dice 230 W; la ficha de la guía declara 710 W nominales y 900 W S2/5 min. Se pide cotejar placa y modelo.
- **TP-CD 18/50:** el título omite «Li-i»; la percusión documentada requiere confirmar modelo y código 4513942.
- **TE-RH 28/1 5F:** Einhell confirma el modelo separado con código 4257972. Se actualizó la guía para distinguirlo del TE-RH 28 5F (4257970), con sus datos de ficha y CTA con código; verificar que la publicación comercial corresponda a esa variante.
- **GBH 180-LI:** se presenta como otro modelo, sin heredar las cifras de GBH 18V-26 D.
- **DCD805B:** herramienta sola; no hereda las dos baterías ni el contenido del kit DCD805D2.
- **Milwaukee 2904-259A:** se identifica como bundle del taladro técnico 2904-20; se actualizan la guía y el CTA, con verificación pendiente del contenido exacto de la publicación.
- **CYL-9:** se identifica la familia Soft Ceramic para cerámica blanda; «EXPERT» en el título no acredita aptitud para porcelanato duro.
- **Bosch escalonada:** la oferta identifica 2608597519 y la tabla 2608597524; se pide confirmar vástago, diámetros y espesor de la referencia ofrecida.

El GSB 18V-50 conserva la URL directa de Mercado Libre recibida, incluyendo sus parámetros. No se lo convierte en enlace corto ni se acredita su condición de referido.

## Rutas y registro de clics

Las 23 guías de taladros estaban fuera del listado público del servidor por carecer de las etiquetas «Dato documentado» y «Análisis TallerLab» exigidas por su filtro editorial, pese a sus metadatos de publicación. Se añadieron aclaraciones sobre atribución de cifras, análisis documental y alcance de las ofertas. No se cambió la fecha de revisión de las fuentes ni se declaró una prueba física. También se añadió un acceso a la guía de inalámbricos en el hub, que ocultaba el grupo general.

`assets/commerce.js` omite filtros/comparadores en bloques que solo tienen tarjetas, evitando un error que interrumpía la instalación del registro de clics. También registra enlaces con `data-affiliate-placement`, incluido el destino directo del GSB 18V-50. Se actualizó la versión del recurso a `v=3`.

## Validación

- `python verificar_taladros_comerciales.py`: OK. 32 productos y CTA, 17 distribuciones, 23 rutas GET/HEAD 200, redirecciones con query, integridad de textos y tablas originales, ubicaciones, ausencia de nuevos CTA duplicados, atributos, API de clics, sitemap e idempotencia.
- Guía Bosch comprobada en navegador con pantalla estrecha: CTA legibles y sin errores JavaScript. Clic real del GSB 18V-50 registrado en el servidor con su URL completa y ubicación `taladros-contextual`.
- Verificadores de soldadoras, sierras, generadores e hidrolavadoras: OK.
- `git diff --check` y comprobación de sintaxis de `assets/commerce.js`: OK.
- La comprobación global `verificar_hubs.py` falla por un problema previo de la portada: `KeyError: '/amoladoras/bosch/'`, guía ausente del listado público. Este lote no modifica esa categoría ni la portada.

Las consultas web a las publicaciones TP-CD, TBL16-7, TE-RH 28/1 y GSB 18V-50 no permitieron acceder a su contenido. Los títulos comerciales proceden del usuario: precio, stock, vendedor, garantía y contenido actual permanecen sin verificar.

La configuración reproducible está en `taladros-ofertas.json`; el catálogo y los puntos de inserción, en `taladros_comerciales.py`.
