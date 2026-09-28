"""Segundo lote de diez guías de sierras, revisadas contra fuentes técnicas."""
from pathlib import Path
import re

ROOT = Path(__file__).parent / "paginas" / "sierras"
PAGES = {
"25-caladoras-black-decker.md": ("BES603 y BES602: velocidad variable y variante", "Comparamos las versiones B2 de 220 V publicadas por Black+Decker Brasil. El sufijo y la tensión son parte de la identificación: no damos por trasladada la garantía brasileña a una compra argentina.", """| Dato verificado | BES603-B2 | BES602-B2 |
| :--- | :--- | :--- |
| Potencia | 400 W | 400 W |
| Control de velocidad | Variable, hasta 3.000 carreras/min | La ficha informa 3.000 carreras/min |
| Profundidad máxima declarada en madera | 65 mm | 65 mm |
| Profundidad máxima declarada en metal | 6 mm | 6 mm |
| Sujeción de hoja | Tipo T | Tipo T |

**Análisis TallerLab.** En las fichas consultadas, la diferencia funcional documentada es el control variable en la BES603. Las capacidades máximas de corte publicadas coinciden; no permiten afirmar que una máquina obtenga mejor acabado que la otra. Una menor velocidad puede ser relevante al adaptar avance y material, pero el fabricante no da en estas páginas un protocolo de comparación de resultados.

**Declaración del fabricante.** Ambas fichas listan cambio de hoja sin llave. La BES603-B2 informa extracción de polvo integrada. No verificamos el caudal ni la eficacia de extracción.

**Desconocido.** La documentación consultada no establece si las unidades ofrecidas en Argentina tienen el mismo sufijo, kit o garantía. Antes de comprar, pedí foto de placa, código completo y tensión. Para una comparativa de capacidades de otras familias, mirá la [guía general de caladoras](/sierras/caladoras/).

## Fuentes consultadas

- **Documentación primaria:** [BES603-B2](https://br.blackanddecker.global/produto/bes603-b2/serra-tico-tico-400w-220v-vvr); [BES602-B2](https://br.blackanddecker.global/produto/bes602-b2/serra-tico-tico-400w-220v).
- **Opiniones:** no se revisó una muestra verificable.
"""),
"18-caladora-einhell.md": ("Tres caladoras Einhell según alimentación y capacidad", "Las fichas argentinas permiten comparar dos modelos con cable y una versión a batería Solo; esta última se vende sin batería ni cargador.", """| Dato verificado | TC-JS 85 | TE-JS 100 | TC-JS 18 Li Solo |
| :--- | :--- | :--- | :--- |
| Alimentación | Cable | Cable | Batería 18 V |
| Potencia / velocidad máxima | 620 W / 3.000 carreras/min | 750 W / 3.000 carreras/min | 2.700 carreras/min |
| Corte máximo en madera | 85 mm | 100 mm | 70 mm |
| Corte máximo en acero | 8 mm | 10 mm | 8 mm |
| Peso publicado | 1,91 kg | 2,3 kg | 1,62 kg sin batería |
| Batería y cargador incluidos | — | — | No |

**Análisis TallerLab.** La TE-JS 100 declara 15 mm más de capacidad en madera que la TC-JS 85, y pesa 0,39 kg más. La inalámbrica TC-JS 18 Li declara 15 mm menos que la TC-JS 85 y 0,29 kg menos antes de sumar la batería. Estas restas comparan cifras de ficha; no miden velocidad ni calidad del corte.

**Declaración del fabricante.** La TE-JS 100 permite hojas con vástago T y U; las dos caladoras a batería incluidas en las fuentes usan vástago T. Confirmá el encastre exacto de la máquina antes de comprar hojas.

**Desconocido.** No se midió autonomía real; dependerá de batería, carga y material. La TC-JS 18 Li Solo no trae batería/cargador, por lo que su costo de entrada cambia si todavía no tenés Power X-Change.

## Fuentes consultadas

- **Documentación primaria:** [Einhell TC-JS 85](https://www.einhell.com.ar/p/4321140-tc-js-85/); [TE-JS 100](https://www.einhell.com.ar/p/4321160-te-js-100/); [TC-JS 18 Li Solo](https://www.einhell.com.ar/p/4321209-tc-js-18-li-solo/).
- **Opiniones:** no se revisó una muestra verificable.
"""),
"04-sierra-caladora.md": ("Comparación por capacidad declarada, no por watts", "**Dato verificado:** los límites de corte de la tabla aparecen en las fichas oficiales enlazadas. Son capacidades declaradas por sus fabricantes, no espesores recomendados para cualquier hoja, material o acabado.", """| Modelo documentado | Madera máxima | Acero máximo | Alimentación |
| :--- | ---: | ---: | :--- |
| Black+Decker BES603-B2 | 65 mm | 6 mm | 400 W, cable, 220 V |
| Einhell TC-JS 85 | 85 mm | 8 mm | 620 W, cable |
| Einhell TE-JS 100 | 100 mm | 10 mm | 750 W, cable |

**Análisis TallerLab.** La tabla ordena las capacidades máximas de menor a mayor; entre BES603-B2 y TE-JS 100 la diferencia declarada es 35 mm en madera y 4 mm en acero. No significa que una caladora sea “mejor”: las capacidades pueden variar con hoja, geometría, material y condiciones del fabricante. Medí el espesor real y buscá una hoja indicada para él.

Antes de comparar precios, comprobá si la caladora permite regular velocidad, si tiene movimiento pendular, qué vástago acepta (T o U) y qué incluye la caja. No atribuyas 100 mm de capacidad a toda caladora de 750 W: la cifra de la tabla pertenece al código TE-JS 100 documentado.

**Desconocido.** Esta guía no prueba los modelos ni cubre caladoras de banco. Tampoco presenta una capacidad universal para MDF, melamina o aluminio: las fichas enlazadas no publican los mismos materiales y protocolos en todos los casos.

## Fuentes consultadas

- **Documentación primaria:** [Black+Decker BES603-B2](https://br.blackanddecker.global/produto/bes603-b2/serra-tico-tico-400w-220v-vvr); [Einhell TC-JS 85](https://www.einhell.com.ar/p/4321140-tc-js-85/); [Einhell TE-JS 100](https://www.einhell.com.ar/p/4321160-te-js-100/).
- **Opiniones:** no se revisó una muestra verificable.
"""),
"17-sierra-circular-black-and-decker.md": ("Códigos B+D: tensión y hoja incluida", "Comparamos CS1004B2 de 220 V con CS1024-BR de 127 V, según fichas oficiales regionales. Es una comparación de códigos, no una recomendación de conectar una variante de 127 V a la red argentina.", """| Dato verificado | CS1004B2 | CS1024-BR |
| :--- | :--- | :--- |
| Tensión indicada | 220 V | 127 V |
| Potencia anunciada | 1.400 W | 1.500 W |
| Disco anunciado | 184 mm (7-1/4 in) | 184 mm (7-1/4 in) |
| Hoja incluida | 18 dientes | 18 dientes |
| Garantía publicada en la ficha regional | 1 año | 1 año |

**Análisis TallerLab.** El modelo CS1024 anuncia 100 W más, pero su ficha es para 127 V. La CS1004B2 indica 220 V, por lo que es el código eléctricamente coincidente con una red nominal argentina de 220 V. No traslades otras prestaciones de un código regional al otro.

**Dato verificado.** Black+Decker lista un disco de accesorio 71-727 de 184 mm, agujero 5/8 in, compatible con CS1004 y CS1024. Para la variante argentina concreta, contrastá el diámetro interior y la placa/manual antes de comprar; el modelo del accesorio no reemplaza esa comprobación.

**Desconocido.** Las fichas brasileñas consultadas no documentan profundidad máxima ni peso para ambos códigos. No afirmamos que CS1004B2 sea idéntico a todas las versiones vendidas localmente.

## Fuentes consultadas

- **Documentación primaria:** [CS1004B2, 220 V](https://br.blackanddecker.global/produto/cs1004b2/serra-circular-7-14-184mm-1400w-220v); [CS1024-BR, 127 V](https://br.blackanddecker.global/produto/cs1024-br/serra-circular-7-14-184mm-1500w-127v); [disco 71-727 y compatibilidad publicada](https://br.blackanddecker.global/produto/71-727/disco-para-serra-circular).
- **Opiniones:** no se revisó una muestra verificable.
"""),
"20-sierra-circular-lusqtoff.md": ("CSL1500-8 y SCL2200-8: capacidades documentadas", "La ficha vigente muestra SCL2200-8; su manual descargable conserva el orden CSL2200-8. También difieren el peso declarado y la medida del disco en el título y el detalle. Registramos esas discrepancias en lugar de mezclarlas.", """| Dato verificado | CSL1500-8 | SCL2200-8 |
| :--- | ---: | ---: |
| Potencia / tensión | 1.500 W / 220 V | 2.200 W / 220 V |
| Diámetro máximo publicado | 185 mm | Título: 230 mm; detalle/manual: 235 mm |
| Velocidad en vacío | 5.500 rpm | 4.100 rpm |
| Profundidad a 90° / 45° | 63,5 / 46 mm | 84 / 56 mm |
| Peso publicado | 4,40 kg | Ficha actual: 4,75 kg; manual: 16 kg |

**Análisis TallerLab.** Según las fichas actuales, SCL2200-8 declara 20,5 mm más de profundidad a 90° que CSL1500-8. El detalle y manual informan disco máximo de 235 mm, aunque el título de ficha dice 230 mm. La ficha actual informa 4,75 kg; el manual asociado declara 16 kg, y llama al equipo CSL2200-8. Al existir discrepancias en código, peso y título de diámetro, no usamos esos valores para asegurar compatibilidad de repuestos: pedí una foto de placa y confirmación escrita del fabricante/vendedor para la unidad.

El disco de 235 mm no entra en una sierra que admite 185 mm. Además de diámetro, verificá eje, RPM máximas, espesor y guarda. La ficha de CSL1500-8 especifica eje de 20 mm en el accesorio circular compatible enlazado; no trasladamos ese eje al modelo mayor sin una fuente específica.

**Desconocido.** No probamos calidad de corte, calentamiento ni compatibilidad real de discos de terceros.

## Fuentes consultadas

- **Documentación primaria:** [ficha Lusqtoff CSL1500-8](https://www.lusqtoff.com.ar/ver-producto/CSL1500-8); [manual CSL1500-8](https://www.lusqtoff.com.ar/2023/uploads/Productos/11.%20HERRAMIENTAS%20EL%C3%89CTRICAS%20DE%20MANO/CSL1500-8/CSL1500-8.pdf); [ficha SCL2200-8](https://lusqtoff.com.ar/ver-producto/SCL2200-8); [manual SCL/CSL2200-8](https://lusqtoff.com.ar/2023/uploads/Productos/11.%20HERRAMIENTAS%20EL%C3%89CTRICAS%20DE%20MANO/SCL2200-8/SCL2200-8.pdf).
- **Opiniones:** no se revisó una muestra verificable.
"""),
"01-sierra-circular.md": ("Diámetro y espesor: dos límites separados", "**Dato verificado:** la matriz resume medidas que aparecen en manuales y fichas oficiales de estos tres modelos; no es una prueba comparativa. Muestra por qué el nombre comercial en pulgadas no basta para elegir disco o capacidad.", """| Modelo exacto | Disco máximo documentado | Corte a 90° documentado | Eje/documentación |
| :--- | ---: | ---: | ---: |
| Stanley SC16-AR | 190 mm en manual; ficha comercial indica 180 mm | 65 mm en manual | 16 mm en manual |
| Bosch GKS 150 | 184 mm | 64 mm | 20 mm |
| Lüsqtoff CSL1500-8 | 185 mm | 63,5 mm | Verificar manual y placa para el eje |

**Análisis TallerLab.** El mayor corte a 90° de esta tabla es 65 mm y el menor 63,5 mm: una diferencia de 1,5 mm entre los valores publicados de modelos distintos. No alcanza para concluir cuál corta más rápido o con mejor terminación. En la SC16-AR, además, el manual y la página comercial dan 190 y 180 mm para el disco; por seguridad, no resuelvas esa diferencia por conversión de pulgadas.

Al elegir, anotá por separado: espesor máximo de la pieza, disco admitido por la máquina, diámetro del eje y RPM máximas del disco. El diámetro comercial (7-1/4 in) no es una medida de profundidad de corte ni confirma compatibilidad.

**Desconocido.** No existe una “potencia adecuada” universal por material en las fuentes comparadas. La guía no califica corte, durabilidad ni precisión.

## Fuentes consultadas

- **Documentación primaria:** [manual y ficha Stanley SC16-AR](https://www.toolservicenet.com/i/STANLEY/GLOBALBOM/B3/SC16D2/1/Instruction_Manual/EN/N611276_SC16_T1_LAG.pdf) y [página comercial](https://ar.stanleytools.global/producto/sc16-ar/sierra-circular-7-14-pulg-180mm-1600w); [manual Bosch GKS 150](https://www.bosch-professional.com/binary/manualsmedia/o406577v21_160992A8F5_202212.pdf); [ficha Lusqtoff CSL1500-8](https://www.lusqtoff.com.ar/ver-producto/CSL1500-8).
- **Opiniones:** no se revisó una muestra verificable.
"""),
"09-sierra-de-banco-einhell.md": ("TC-TS 2025/2 U y 2225 U: diferencias publicadas", "La descripción histórica mencionaba la TE-CC 250 UF; esta comparativa se limita a dos códigos actuales con fichas argentinas accesibles, para no mantener afirmaciones sin respaldo.", """| Dato verificado | TC-TS 2025/2 U (4340490) | TC-TS 2225 U (4340515) |
| :--- | ---: | ---: |
| Hoja | 250 × 30 mm, 24 dientes | 254 mm, 48 dientes |
| Potencia publicada | 1.800 W S1 / 2.000 W S6 | 2.200 W S6 |
| Velocidad en vacío | 5.000 rpm | 4.250 rpm |
| Altura de corte a 90° / 45° | 85 / 65 mm | 80 / 55 mm |
| Peso | 19,24 kg | 22,09 kg |

**Análisis TallerLab.** La TC-TS 2025/2 U declara 5 mm más de altura a 90° y 10 mm más a 45°, con 2,85 kg menos. La 2225 U trae hoja de 48 dientes frente a 24 en la 2025/2 U. Esos datos describen configuración y capacidad, no la calidad del acabado: para reemplazar hoja se requiere respetar diámetro, eje, velocidad y uso indicado.

Las cifras de potencia usan condiciones distintas (S1 frente a S6 en una misma ficha, y S6 en la otra). Por eso no ordenamos el rendimiento con una resta simple de watts. Ambas fichas indican tope paralelo, aspiración y hoja de 250/254 mm; la fijación del tope de la 2225 U se publica adelante y atrás.

**Desconocido.** No medimos paralelismo, vibración ni tolerancia de corte. El borrador refería a la TE-CC 250 UF, que no forma parte de esta comparación revisada.

## Fuentes consultadas

- **Documentación primaria:** [TC-TS 2025/2 U](https://www.einhell.com.ar/p/4340490-tc-ts-2025-2-u/); [TC-TS 2225 U](https://www.einhell.com.ar/p/4340515-tc-ts-2225-u/); [catálogo Einhell con alturas publicadas](https://www.einhell.com.ar/fileadmin/corporate-media/services/catalogues/pdf-es/einhell-services-catalogues-complete-assortment-2022-es.pdf).
- **Opiniones:** no se revisó una muestra verificable.
"""),
"06-sierra-de-banco.md": ("Elegir una sierra de banco por corte y apoyo", "**Dato verificado:** comparamos dos fichas oficiales de equipos de banco y hoja cercana a 250 mm. Sirve para dimensionar pieza y espacio; no mide seguridad, estabilidad ni precisión real.", """| Criterio de decisión | Einhell TC-TS 2025/2 U | Lüsqtoff SML2000-8 |
| :--- | ---: | ---: |
| Hoja | 250 × 30 mm | 255 × 30 mm |
| Corte máximo publicado a 90° / 45° | 85 / 65 mm | 85 / 65 mm |
| Peso publicado | 19,24 kg | 21,5 kg |
| Extensiones informadas | 165 mm a cada lado | 165 mm de ancho adicional a izquierda y derecha |
| Guía / accesorio declarado | Tope paralelo y tope angular | Regla lateral, compás, guarda y barra de empuje |

**Análisis TallerLab.** Las fichas declaran la misma altura máxima a 90° y 45°. El disco Lüsqtoff es 5 mm mayor de diámetro y el conjunto pesa 2,26 kg más. No deducimos por eso mayor rigidez ni mejor acabado. La diferencia crítica para comprar repuesto está en el diámetro: hojas de 250 y 255 mm no son intercambiables si exceden el máximo admitido por la máquina.

Antes de decidir, medí la pieza más alta, el ancho a rasgar y el espacio disponible para apoyar la tabla. Confirmá si la extensión suma superficie de apoyo o capacidad de corte y qué accesorios vienen efectivamente en caja. No uses una mesa extensible como sustituto de soportes adecuados para piezas largas.

**Seguridad.** OSHA describe resguardos autoajustables, bastón de empuje para piezas pequeñas y manos fuera de la línea de corte para sierras de mesa en su guía laboral estadounidense. Es una referencia técnica general, no una norma argentina ni reemplaza el manual del equipo.

## Fuentes consultadas

- **Documentación primaria:** [Einhell TC-TS 2025/2 U](https://www.einhell.com.ar/p/4340490-tc-ts-2025-2-u/); [Lüsqtoff SML2000-8](https://lusqtoff.com.ar/ver-producto/SML2000-8); [OSHA: resguardos para sierras de mesa](https://www.osha.gov/etools/machine-guarding/saws/table).
- **Opiniones:** no se revisó una muestra verificable.
"""),
"15-disco-para-sierra-circular.md": ("Compatibilidad de hoja: diámetro, eje, RPM y material", "Una hoja se elige por cuatro límites de compatibilidad antes de mirar cantidad de dientes: máquina, agujero, velocidad y aplicación documentada.", """| Comprobación | Ejemplo de ficha | Qué validar en tu máquina |
| :--- | :--- | :--- |
| Diámetro | Bosch publica variantes de 184 y 190 mm | El diámetro máximo permitido y la guarda |
| Eje (calibre) | 20 mm en Bosch GKS 150; 5/8 in en B+D 71-727 | Medida de eje y buje exactos |
| Velocidad máxima del disco | Bosch lista límites de RPM por variante | Que la máquina no supere ese límite |
| Dientes / geometría | Bosch publica opciones ATB y TCG | Material y tipo de corte indicado |

**Análisis TallerLab.** El diámetro y el eje son condiciones de montaje; la velocidad máxima es una condición de operación. Un buje reductor solo resuelve la diferencia de agujero cuando el fabricante del disco lo permite: no corrige diámetro externo incompatible, espesor inadecuado o velocidad nominal insuficiente.

Para ver cómo cambia una especificación sin generalizar, Bosch lista una hoja 254 × 30 mm, 24 dientes ATB, 6.000 rpm máximas, y otra variante de 254 mm con 80 dientes TCG y agujero de 16 mm, también con límite de 6.000 rpm. No es prueba de que ATB o TCG siempre sean la mejor opción para un material; seguí la aplicación indicada para cada producto.

**Dato verificado.** Black+Decker identifica su disco 71-727 como 7-1/4 in, agujero 5/8 in y compatible con CS1004 y CS1024. Para Stanley SC16-AR el manual da un eje de 16 mm; no tomes el disco B+D como compatible.

**Desconocido.** No ensayamos cortes ni recomendamos un número universal de dientes por material.

## Fuentes consultadas

- **Documentación primaria:** [Bosch PRO Wood 254 mm](https://www.bosch-professional.com/ar/es/hoja-de-sierra-circular-pro-wood-a-cable-para-sierras-ingletadoras-3089783-ocs-ac/); [Bosch PRO Multi Material 254 mm](https://www.bosch-professional.com/ar/es/hoja-de-sierra-circular-a-cable-pro-multi-material-para-sierras-ingletadoras-3089785-ocs-ac/); [disco B+D 71-727](https://br.blackanddecker.global/produto/71-727/disco-para-serra-circular); [manual Stanley SC16](https://www.toolservicenet.com/i/STANLEY/GLOBALBOM/B3/SC16D2/1/Instruction_Manual/EN/N611276_SC16_T1_LAG.pdf).
- **Opiniones:** no se revisó una muestra verificable.
"""),
"11-guia-para-sierra-circular.md": ("Guía paralela, regla y riel: no son lo mismo", "**Dato verificado:** las páginas de fabricante enumeran compatibilidad por modelo. Una ranura o una base que parece similar no demuestra que encastre con un riel de otra marca.", """| Sistema | Qué documenta la fuente | Para qué decisión sirve |
| :--- | :--- | :--- |
| Tope paralelo | Bosch lista topes compatibles con familias y modelos específicos | Cortes paralelos a un borde, dentro del alcance del tope |
| Riel guía | Bosch declara modelos GKS compatibles con FSN; otra sierra puede declarar explícitamente que no es compatible | Cortes rectos guiados sobre un carril del sistema indicado |
| Regla externa sujeta | No es un accesorio propietario de la sierra | Alternativa que requiere medir el desplazamiento entre borde de base y hoja |

**Análisis TallerLab.** La [Bosch GKS 150](/sierras/bosch-gks-150/) declara “no” para carril guía en su ficha. La página Bosch para GKS 18V-57 G declara compatibilidad con carriles Bosch, Mafell, Festool y Makita. Eso demuestra que la compatibilidad es específica de modelo/sistema; no prueba que cualquier carril de esas marcas funcione con cualquier sierra.

Si usás regla externa, medí la distancia entre el borde apoyado de la base y el lado de la hoja que define el corte, y sumá esa medida al marcado. Sujetá la regla y probá el ajuste con la máquina desconectada. Para un tope paralelo, revisá el modelo de accesorio en la lista oficial de compatibilidad.

**Desconocido.** No medimos desviación, repetibilidad ni calidad del borde con guías de terceros. No afirmamos que una guía “universal” encaje sin verificar su manual.

## Fuentes consultadas

- **Documentación primaria:** [compatibilidad de carriles Bosch GKS 18V-57 G](https://www.bosch-professional.com/es/es/products/gks-18v-57-g-06016A2101); [compatibilidad de topes paralelos Bosch](https://www.bosch-professional.com/es/es/guias-paralelas-para-sierras-circulares-portatiles-2869030-ocs-ac); [ficha Bosch GKS 150](https://www.bosch-professional.com/ar/es/products/gks-150-06016B30H0).
- **Opiniones:** no se revisó una muestra verificable.
"""),
}

DESCRIPTIONS = {
    "25-caladoras-black-decker.md": "Comparación documental de Black+Decker BES603-B2 y BES602-B2: velocidad, capacidades de ficha y diferencias de variante.",
    "18-caladora-einhell.md": "Compará TC-JS 85, TE-JS 100 y TC-JS 18 Li Solo por capacidades publicadas, peso y alimentación.",
    "04-sierra-caladora.md": "Guía documental para comparar capacidad declarada, hoja, velocidad y alimentación en caladoras concretas.",
    "17-sierra-circular-black-and-decker.md": "Comparamos CS1004B2 de 220 V y CS1024-BR de 127 V con fichas oficiales regionales.",
    "20-sierra-circular-lusqtoff.md": "Datos documentados de las circulares Lusqtoff CSL1500-8 y SCL2200-8, con diferencias de capacidad y código.",
    "01-sierra-circular.md": "Guía de selección documental: disco admitido, eje y profundidad de corte publicados por modelo.",
    "09-sierra-de-banco-einhell.md": "Comparación de las sierras de banco Einhell TC-TS 2025/2 U y TC-TS 2225 U por hoja y corte declarado.",
    "06-sierra-de-banco.md": "Criterios documentales para elegir una sierra de banco por corte, hoja, peso y superficie de apoyo.",
    "15-disco-para-sierra-circular.md": "Cómo validar diámetro, eje, RPM y aplicación de un disco circular con ejemplos de fichas oficiales.",
    "11-guia-para-sierra-circular.md": "Diferencias entre tope paralelo, riel de guía y regla sujeta; comprobación de compatibilidad por modelo.",
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
    fields = {
        "research_type": "documental", "physical_test": "no",
        "specifications_contrasted": "sí", "buyer_opinions": "no",
        "primary_sources": "sí", "information_asset": section,
        "asset_status": "verificado", "reviewed": "27/09/2026", "published": "true",
    }
    for key, value in fields.items():
        line = f'{key}: "{value}"' if key != "published" else "published: true"
        if re.search(rf'^{key}:.*$', front, re.M):
            front = re.sub(rf'^{key}:.*$', lambda _: line, front, flags=re.M)
        else:
            front += "\n" + line
    body = f"# {h1}\n\n{lead}\n\n## {section}\n\n{content.strip()}\n\n[Ver todas las guías de sierras](/sierras/).\n"
    path.write_text(f"---\n{front}\n---\n\n{body}", encoding="utf-8")
print(f"Revisadas {len(PAGES)} páginas")
