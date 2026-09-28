"""Tercer lote: nueve guías restantes de sierras y una comparativa Bosch."""
from pathlib import Path
import re

ROOT = Path(__file__).parent
PAGES = {
"paginas/sierras/10-caladora-skil.md": ("SKIL 4380 y 4550: separar tensión de prestaciones", "**Dato documentado:** el catálogo de servicio distingue variantes de 127 V y 220 V para ambos códigos; una ficha técnica del 4550 documenta sus prestaciones. No completamos las del 4380 con datos de vendedores.", """| Dato documentado | SKIL 4380 | SKIL 4550 |
| :--- | :--- | :--- |
| Código de variante 127 V | F0124380AB | F0124550AB |
| Código de variante 220 V | F0124380JA | F0124550JA |
| Potencia documentada | Desconocida en las fuentes consultadas | 550 W |
| Velocidad documentada | Desconocida | 800–3.000 carreras/min |
| Acción pendular | Desconocida | 3 posiciones, según ficha técnica |

**Análisis TallerLab.** La primera comprobación útil de una oferta argentina es la terminación del código: el catálogo de servicio diferencia 127 V de 220 V con sufijos distintos. La ficha de SKIL 4550 especifica capacidades, pero no transferimos sus prestaciones a la 4380 solo porque ambos sean modelos de caladora.

**Desconocido.** No hallamos una ficha primaria actual que confirme potencia y capacidad máxima de corte de la 4380. Por eso retiramos las cifras del borrador que no pudimos verificar. La hoja también debe coincidir con el vástago de la variante y con el uso indicado por su fabricante.

## Fuentes consultadas

- **Documentación primaria:** [catálogo Bosch/Skil de repuestos con variantes 4380 y 4550](https://www.bosch-professional.com/br/media/country_content/service/after_sales_service/catalogues/catalogo_reposicao2_verso_final.pdf); [ficha técnica SKIL 4550 de Robert Bosch LLC](https://www.grainger.com.mx/static/ft/20028399_TD.PDF).
- **Opiniones:** no se revisó una muestra verificable.
"""),
"paginas/sierras/13-ingletadora-dewalt.md": ("DWS713 y DWS780: cabezal fijo o deslizante", "**Dato documentado:** comparamos las capacidades y características que DeWalt publica para DWS713 y DWS780 en su catálogo estadounidense. No asumimos disponibilidad ni compatibilidad eléctrica local.", """| Dato publicado | DWS713 | DWS780 |
| :--- | :--- | :--- |
| Diseño | Fija, bisel simple | Deslizante, doble bisel |
| Disco | 10 in (254 mm) | 12 in (305 mm) |
| Capacidad a 90° | Madera 2 × 6 in | Madera 2 × 14 in |
| Capacidad a 45° | Madera 2 × 4 in | Madera 2 × 10 in |
| Bisel | 0–48° izquierda; 0–3° derecha | 49° izquierda y derecha |

**Análisis TallerLab.** En las capacidades publicadas a 90°, DWS780 agrega 8 in de ancho nominal frente a DWS713; a 45°, agrega 6 in. Es una diferencia de ficha y no una prueba de corte. El carro deslizante y el disco mayor son relevantes si la pieza supera el límite del modelo fijo; si no, agregan volumen sin resolver una necesidad de capacidad.

**Declaración del fabricante.** DeWalt ofrece DWS780 con sistema XPS de alineación de línea de corte; DWS713 utiliza topes de inglete y bisel simple. No medimos precisión de ninguno.

**Desconocido.** La fuente estadounidense lista DWS779 como discontinuada. Los códigos DWS713 y DWS780 consultados no son una validación de venta argentina; verificá placa, tensión, garantía y manual del producto ofrecido. El DWS780 de la ficha consultada indica 110 V.

## Fuentes consultadas

- **Documentación primaria:** [DeWalt DWS713](https://www.dewalt.com/en-us/product/dws713/15a-10-single-bevel-compound-miter-saw); [DeWalt DWS780](https://www.dewalt.com/en-us/product/dws780/12-double-bevel-sliding-compound-miter-saw); [catálogo DeWalt de ingletadoras, con estado de DWS779](https://www.dewalt.com/en-us/products/power-tools/saws/miter-saws).
- **Opiniones:** no se usaron las reseñas visibles en las páginas de producto.
"""),
"paginas/sierras/14-ingletadora-total.md": ("Dos códigos Total y una capacidad distinta", "La tabla compara dos códigos incluidos en el catálogo TOTAL 2026. El borrador mezclaba el TS42182552 con una supuesta versión deslizante; mantenemos los modelos que aparecen identificados en documentación técnica.", """| Dato documentado en catálogo | TS42142107 | TS42182553 |
| :--- | ---: | ---: |
| Potencia | 1.400 W | 1.800 W |
| Disco / eje | 210 × 25,4 mm | 254 × 30 mm |
| Capacidad máxima a 90° | 60 × 120 mm | 75 × 130 mm |
| Peso publicado | 7,4 kg | 17,3 kg |
| Ajuste de inglete | 45° a izquierda y derecha | 52° a izquierda y derecha |
| Bisel | 45° a izquierda | 45° a izquierda |

**Análisis TallerLab.** La TS42182553 publica 15 mm más de altura y 10 mm más de ancho máximo a 90°; su peso de catálogo supera al de TS42142107 en 9,9 kg. Son dos escalas y capacidades distintas. El disco de 254 mm no es reemplazo del de 210 mm y los ejes también difieren: 30 frente a 25,4 mm.

**Desconocido.** El catálogo no confirma stock, kit o garantía de estos códigos en Argentina. No identificamos aquí una ficha primaria cotejada para la TS42182557 que figuraba en el borrador; no la tratamos como telescópica ni le atribuimos especificaciones. Pedí foto de placa y manual de la oferta concreta.

## Fuentes consultadas

- **Documentación primaria:** [catálogo TOTAL 2026, códigos TS42142107 y TS42182553](https://amig.es/export_fr/downloadcatalogues/download?id=TOTAL+2026+FR.pdf&type=Catalogues+et+brochures); [ficha técnica regional TS42182552, con capacidad publicada](https://totalmalaysia.my/ts42182552-mitre-saw/) — se incluye para distinguir el código similar, no como sustituto del 2553.
- **Opiniones:** no se revisó una muestra verificable.
"""),
"paginas/sierras/29-sensitiva-total.md": ("TS223558: código base y ficha de fábrica", "La ficha de TOTAL documenta el modelo TS223558. En Argentina se encuentra una oferta rotulada TS223558-4; ese sufijo necesita confirmación de placa antes de trasladar datos o garantía.", """| Dato documentado para TS223558 | Especificación |
| :--- | :--- |
| Tensión / frecuencia | 220–240 V / 50–60 Hz |
| Potencia | 2.200 W |
| Velocidad en vacío | 3.700 rpm |
| Disco | 355 × 25,4 mm |
| Capacidad máxima declarada | Redondo 100 mm; cuadrado 100 × 100 mm; rectangular 120 × 100 mm; barra 50 mm |
| Disco incluido | 1 disco de 355 mm |

**Análisis TallerLab.** El disco de 355 mm no representa la sección que la máquina puede cortar. La tabla de TOTAL declara límites por geometría; no los extrapolamos a otras formas, cortes en ángulo o materiales. El sufijo -4 aparece en una publicación argentina de un vendedor, mientras la ficha técnica de fábrica consultada usa TS223558. Confirmá el código completo y garantía del importador.

**Desconocido.** La ficha de fábrica no publica aquí peso, ciclo de trabajo ni contenido completo de caja. No afirmamos uso continuo ni “industrial”. Para contrastarla con otra sensitiva, consultá la [CM-14K de Lüsqtoff](/sierras/sensitivas-lusqtoff/) y compará capacidad por forma, no solo potencia.

## Fuentes consultadas

- **Documentación primaria:** [ficha de fábrica TOTAL TS223558](https://www.totalbusiness.com/ae/product/cut-off-saw/TS223558).
- **Información comercial argentina:** [publicación identificada como TS223558-4](https://articulo.mercadolibre.com.ar/MLA-1469785943-sierra-sensitiva-total-355mm-2200w-incluye-disco-ts223558-4-_JM) — útil para verificar sufijo local, no como fuente de capacidad.
- **Opiniones:** no se revisó una muestra verificable.
"""),
"paginas/sierras/02-sensitiva.md": ("Capacidad por perfil: no la deduzcas del diámetro", "**Dato documentado:** las dos fichas oficiales publican máximos diferentes para los perfiles listados. Las capacidades dependen de la forma de la pieza; no se extrapolan a otros cortes.", """| Modelo documentado | Disco | Tubo redondo | Sección cuadrada/rectangular publicada |
| :--- | ---: | ---: | :--- |
| Lüsqtoff CM-14K | 355 mm; eje 1 in | 110 mm | Cuadrado 100 × 100 mm; ángulo 120 × 120 mm |
| TOTAL TS223558 | 355 × 25,4 mm | 100 mm | Cuadrado 100 × 100 mm; rectangular 120 × 100 mm |

**Análisis TallerLab.** La diferencia publicada para tubo redondo es 10 mm. En cuadrados, ambas fichas declaran 100 × 100 mm. Las categorías rectangulares no son idénticas: Lüsqtoff informa ángulo, Total rectangular. No convertimos estos renglones en un ganador general. Antes de elegir, identifica el perfil exacto y el ángulo del corte.

Los dos ejes publicados como 1 pulgada y 25,4 mm representan la misma medida nominal. Aun así, verificá el disco permitido, el espesor y las RPM máximas impresas en la hoja. Una hoja abrasiva y una hoja de carburo para corte en frío no se deben comparar como si fueran el mismo consumible.

**Desconocido.** No probamos rebaba, escuadra, calentamiento o duración del disco. Las capacidades máximas de catálogo no equivalen a una recomendación para todos los materiales.

## Fuentes consultadas

- **Documentación primaria:** [Lüsqtoff CM-14K](https://www.lusqtoff.com.ar/ver-producto/CM-14K); [manual CM-14K](https://www.lusqtoff.com.ar/2023/uploads/Productos/12.%20HERRAMIENTAS%20DE%20PIE%20Y%20BANCO/CM-14K/MANUAL/CM-14k.pdf); [TOTAL TS223558](https://www.totalbusiness.com/ae/product/cut-off-saw/TS223558).
- **Opiniones:** no se revisó una muestra verificable.
"""),
"paginas/sierras/03-sierra-sable.md": ("Cable o batería: dos fichas Bosch comparables", "Las fichas argentinas de GSA 1100 E y GSA 18V-24 publican el mismo máximo de corte en madera. La diferencia documentada está en alimentación, carrera, peso del cuerpo y velocidad sin carga.", """| Dato documentado | GSA 1100 E | GSA 18V-24 |
| :--- | ---: | ---: |
| Alimentación | Cable, 1.100 W | Batería 18 V |
| Carrera | 28 mm | 24 mm |
| Velocidad sin carga | 0–2.700 carreras/min | 0–3.100 carreras/min |
| Corte máximo en madera | 230 mm | 230 mm |
| Peso publicado | 3,6 kg | 1,7 kg sin batería |

**Análisis TallerLab.** El cuerpo de la inalámbrica pesa 1,9 kg menos que el dato publicado para la GSA 1100 E, pero la cifra no incluye batería. Los máximos declarados en madera coinciden (230 mm); eso no demuestra igual velocidad, autonomía o resultado en el mismo material. Para corte repetido, evaluá batería disponible y ciclos de trabajo, datos no comparados aquí.

**Declaración del fabricante.** Bosch indica que la GSA 18V-24 incluye motor sin escobillas, velocidad variable, encastre SDS, apoyo pivotante y LED. No los convertimos en una afirmación de más precisión o menos fatiga medida por TallerLab.

**Desconocido.** Esta comparación cubre dos modelos Bosch; no define prestaciones de todas las sierras sable con cable o a batería. El corte en acero/tubo requiere consultar la tabla de capacidad del manual para el diámetro y hoja específicos.

## Fuentes consultadas

- **Documentación primaria:** [Bosch GSA 1100 E](https://www.bosch-professional.com/py/es/products/gsa-1100-e-0601640800); [manual Bosch GSA 1100 E](https://www.bosch-professional.com/binary/manualsmedia/o109402v21_1619929L78_201207.pdf); [Bosch GSA 18V-24 Argentina](https://www.bosch-professional.com/ar/es/products/gsa-18v-24-06016A51E0).
- **Opiniones:** no se revisó una muestra verificable.
"""),
"paginas/sierras/19-sierra-sable-inalambrica.md": ("Carrera, tensión y batería incluida", "Comparamos una Bosch de 18 V publicada para Argentina y una DeWalt estadounidense marcada 20V MAX. DeWalt aclara que esa cifra máxima equivale a 18 V nominales; ambas fichas exigen confirmar si la batería viene en el kit.", """| Dato documentado | Bosch GSA 18V-24 | DeWalt DCS380B |
| :--- | ---: | ---: |
| Etiqueta de plataforma | 18 V | 20V MAX; 18 V nominales |
| Carrera | 24 mm | 1-1/8 in (28,6 mm) |
| Velocidad sin carga | 0–3.100 carreras/min | 0–3.000 carreras/min |
| Peso publicado | 1,7 kg sin batería | No informado en la ficha consultada |
| Incluye batería | Revisar el kit; la ficha muestra variante/caja | No; herramienta sola |

**Análisis TallerLab.** La carrera nominal de DeWalt supera a la de Bosch en 4,6 mm; Bosch declara 100 carreras/min más de velocidad máxima sin carga. Son dos variables geométricas/de ficha y no permiten concluir cuál corta más rápido: hoja, material y condiciones también intervienen. “20V MAX” es la tensión inicial sin carga; la nota de DeWalt informa 18 V nominales, así que no es una batería de sistema distinto por esa etiqueta sola.

**Desconocido.** No hay una prueba directa de autonomía ni rendimiento en madera o metal. No compares peso a mano: falta una cifra de peso en la ficha DCS380B y la Bosch excluye batería. Confirmá plataforma, capacidad de batería, cargador incluido, código regional y servicio antes de comprar.

## Fuentes consultadas

- **Documentación primaria:** [Bosch GSA 18V-24](https://www.bosch-professional.com/ar/es/products/gsa-18v-24-06016A51E0); [DeWalt DCS380B, ficha y nota de voltaje nominal](https://www.dewalt.com/en-us/product/dcs380b/20v-max-cordless-reciprocating-saw-tool-only).
- **Opiniones:** no se revisó una muestra verificable.
"""),
"paginas/sierras/05-sierra-sin-fin-para-madera.md": ("Altura, garganta y repuestos: tres datos distintos", "Contrastamos la SFL250-8 compacta con la SFL1100-9 de banco grande. La SFL300-8 aparece listada, pero no encontramos una ficha de capacidad suficiente para compararla.", """| Dato documentado | SFL250-8 | SFL300-8 | SFL1100-9 |
| :--- | ---: | ---: | ---: |
| Estado | Discontinuada | Listada como banco 200 mm | Ficha vigente consultada |
| Altura máxima de corte | 80 mm | Desconocida | 206 mm |
| Garganta | 200 mm | Desconocida | 305 mm |
| Hoja | 1.400 × 6,5 × 0,35 mm | Desconocida | 2.360 mm de longitud |
| Peso | 16,5 kg ficha; catálogo antiguo 15,5 kg | Desconocido | 84 kg |

**Análisis TallerLab.** Entre SFL250-8 y SFL1100-9 hay 126 mm de diferencia en altura publicada y 67,5 kg de diferencia tomando la ficha consultada para el modelo pequeño. No son máquinas equivalentes de escala. Una garganta mayor aumenta la distancia disponible entre hoja y columna; no aumenta la altura de pieza: son dimensiones distintas.

La ficha actual marca SFL250-8 como discontinuada. El catálogo de 2024–2025 publica 15,5 kg mientras su ficha de producto publica 16,5 kg; usamos la cifra de ficha y mostramos la discrepancia. Antes de comprar una unidad usada, revisá largo, ancho y grosor de hoja compatibles y disponibilidad de repuestos.

**Desconocido.** La página comercial enumera SFL300-8 como “200 mm”, pero no confirma que sea altura máxima de corte. No interpretamos el nombre como especificación.

## Fuentes consultadas

- **Documentación primaria:** [Lüsqtoff SFL250-8](https://www.lusqtoff.com.ar/ver-producto/SFL250-8); [catálogo Lüsqtoff 2024–2025](https://www.lusqtoff.com.ar/2023/uploads/Catalogos/CAT%C3%81LOGO%20LQ%202024-2025%20-%20web%20%281%29.pdf); [catálogo de modelos de banco y taller](https://www.lusqtoff.com.ar/ver-productos/12-herramientas-de-pie-y-banco); [SFL1100-9](https://lusqtoff.com.ar/ver-producto/SFL1100-9).
- **Opiniones:** no se revisó una muestra verificable.
"""),
"paginas/sierras/07-sierra-sin-fin-para-metal.md": ("Portátil o de banco: definir sección y entorno", "**Dato documentado:** las dos referencias de la tabla son sierras de banda portátiles Milwaukee con capacidades publicadas. No equivalen a una sierra horizontal de banco y no son una recomendación de marca.", """| Modelo documentado | Capacidad máxima publicada | Alimentación / uso de la ficha |
| :--- | :--- | :--- |
| Milwaukee M12 2429-20 | 1-5/8 × 1-5/8 in (41,3 × 41,3 mm) | Batería M12; herramienta sola |
| Milwaukee M18 2829-20 | 3-1/4 × 3-1/4 in (82,6 × 82,6 mm) | Batería M18; herramienta sola |

**Análisis TallerLab.** La capacidad lineal publicada para el modelo M18 es el doble de la M12 (3,25 frente a 1,625 pulgadas). Esa comparación sirve si el perfil supera el límite de la compacta; no mide velocidad, autonomía o precisión. Ambas son portátiles: no las equiparamos con una sierra horizontal de banco con prensa, refrigerante o avance automático.

Al evaluar un equipo para metal, anotá primero el mayor diámetro o sección, si el corte es recto o angular, y cómo se sujeta la pieza. Después verificá hoja (largo, ancho y TPI), tensión de batería y disponibilidad local. No afirmamos una recomendación de fluido de corte universal: el material y el manual determinan el procedimiento.

**Desconocido.** No se relevaron modelos argentinos de sierra horizontal de banco en este análisis. Las fichas Milwaukee son del mercado estadounidense; disponibilidad, baterías compatibles y garantía local deben confirmarse por código regional.

## Fuentes consultadas

- **Documentación primaria:** [Milwaukee M12 2429-20](https://www.milwaukeetool.com/2429-20); [Milwaukee M18 compacta 2829-20](https://www.milwaukeetool.com/products/details/m18-fuel-compact-band-saw-tool-only/2829-20).
- **Opiniones:** no se revisó una muestra verificable.
"""),
"paginas/10-amoladoras-bosch.md": ("Tres amoladoras Bosch con límites de variante", "Reemplazamos la comparación previa por tres variantes con ficha Bosch Argentina: GWS 700, GWS 9-125 S y GWS 180-LI. La 9-125 S consultada corresponde a 127 V; no la presentamos como opción lista para enchufar en una instalación de 220 V.", """| Dato documentado | GWS 700 | GWS 9-125 S (0 601 396 1D0) | GWS 180-LI |
| :--- | ---: | ---: | ---: |
| Alimentación | Cable | 127 V en la variante consultada | Batería 18 V |
| Potencia / equivalencia declarada | 710 W | 900 W absorbidos; 450 W de salida | Bosch declara rendimiento equivalente a 700 W con cable |
| Diámetro de disco | 115 mm | 125 mm | 125 mm |
| Velocidad sin carga | 12.000 rpm | 2.800–11.000 rpm | 11.000 rpm |
| Peso | 1,7 kg | 1,9 kg | 1,6 kg sin batería; 2,2 kg con batería |

**Análisis TallerLab.** GWS 9-125 S agrega un disco nominal 10 mm mayor que GWS 700 y permite regular velocidad; sin embargo, el código consultado es 127 V. El nombre GWS 9-125 S incluye más de una variante y no se debe trasladar ese voltaje a otro código de pedido. GWS 180-LI pesa 0,6 kg menos que GWS 700 sin batería, pero 0,5 kg más con batería instalada, según las dos fichas.

**Declaración del fabricante.** Bosch describe el motor de la GWS 180-LI como equivalente a una herramienta con cable de 700 W. No es una medición comparativa de TallerLab y la ficha no declara que el rendimiento sea idéntico bajo cualquier carga.

**Desconocido.** No se comparó durabilidad, calentamiento, tiempo de trabajo ni contenido de batería/cargador en una oferta local. Confirmá código, tensión, tamaño permitido, guarda y accesorios antes de comprar.

## Fuentes consultadas

- **Documentación primaria:** [Bosch GWS 700 Argentina](https://www.bosch-professional.com/ar/es/products/gws-700-06013A30H0); [Bosch GWS 9-125 S Argentina y variantes](https://www.bosch-professional.com/ar/es/products/gws-9-125-s-06013961D0); [Bosch GWS 180-LI Argentina](https://www.bosch-professional.com/ar/es/products/gws-180-li-06019H90E0).
- **Opiniones:** no se revisó una muestra verificable.
"""),
}

DESCRIPTIONS = {
    "paginas/sierras/10-caladora-skil.md": "Guía de caladoras SKIL 4380 y 4550: variantes de tensión documentadas y prestaciones confirmadas para cada modelo.",
    "paginas/sierras/13-ingletadora-dewalt.md": "Comparación documental de las DeWalt DWS713 y DWS780: capacidad publicada, bisel y diferencias de cabezal.",
    "paginas/sierras/14-ingletadora-total.md": "Comparación de los códigos Total TS42142107 y TS42182553 con capacidades y discos publicados en catálogo.",
    "paginas/sierras/29-sensitiva-total.md": "Datos de fábrica de la sensitiva Total TS223558 y comprobaciones para distinguir el sufijo de la oferta local.",
    "paginas/sierras/02-sensitiva.md": "Comparación documental de sensitivas de 355 mm por capacidad de corte según geometría del perfil.",
    "paginas/sierras/03-sierra-sable.md": "Comparación de sierras sable Bosch con cable y batería por carrera, velocidad, peso y capacidad declarada.",
    "paginas/sierras/19-sierra-sable-inalambrica.md": "Qué comparar en sierras sable inalámbricas: carrera, velocidad, tensión nominal y batería incluida.",
    "paginas/sierras/05-sierra-sin-fin-para-madera.md": "Compara altura de corte, garganta, hoja y peso publicados para sierras sin fin Lüsqtoff.",
    "paginas/sierras/07-sierra-sin-fin-para-metal.md": "Guía para diferenciar capacidades de sierras de banda portátiles para metal según sección de pieza.",
    "paginas/10-amoladoras-bosch.md": "Compará GWS 700, GWS 9-125 S y GWS 180-LI por disco, alimentación, velocidad y peso documentados.",
}

for filename, (section, lead, content) in PAGES.items():
    path = ROOT / filename
    original = path.read_text(encoding="utf-8")
    match = re.match(r"---\n(.*?)\n---\n", original, flags=re.S)
    if not match:
        raise RuntimeError(f"Missing front matter: {path}")
    front = match.group(1)
    h1 = re.search(r'^h1: "(.+)"$', front, re.M).group(1)
    if filename in DESCRIPTIONS:
        front = re.sub(r'^description:.*$', lambda _: f'description: "{DESCRIPTIONS[filename]}"', front, flags=re.M)
    for key, value in {
        "research_type": "documental", "physical_test": "no",
        "specifications_contrasted": "sí", "buyer_opinions": "no",
        "primary_sources": "sí", "information_asset": section,
        "asset_status": "verificado", "reviewed": "27/09/2026", "published": "true",
    }.items():
        line = f'{key}: "{value}"' if key != "published" else "published: true"
        if re.search(rf'^{key}:.*$', front, re.M):
            front = re.sub(rf'^{key}:.*$', lambda _: line, front, flags=re.M)
        else:
            front += "\n" + line
    body = f"# {h1}\n\n{lead}\n\n## {section}\n\n{content.strip()}\n\n[Ver todas las guías de sierras](/sierras/).\n"
    if filename == "paginas/10-amoladoras-bosch.md":
        body = body.replace("[Ver todas las guías de sierras](/sierras/).", "[Ver todas las guías de amoladoras](/amoladoras/).")
    path.write_text(f"---\n{front}\n---\n\n{body}", encoding="utf-8")
print(f"Revisadas {len(PAGES)} páginas")
