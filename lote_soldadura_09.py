"""Decimoquinto lote editorial: una guía STIHL y nueve de soldadura."""
from pathlib import Path
import re

ROOT = Path(__file__).parent

PAGES = {
    "paginas/hidrolavadoras/05-hidrolavadoras-stihl.md": (
        "Comparación de tres fichas STIHL Argentina por referencia, tensión/potencia, peso y PVP sugerido capturado el 27/09/2026; separa datos actuales de presión/caudal no publicados en todos los modelos.",
        """| Modelo / referencia en STIHL Argentina | Potencia publicada | Peso operacional publicado | Presión o caudal publicados en la página consultada | PVP sugerido capturado 27/09/2026 |
| :--- | ---: | ---: | :--- | ---: |
| RE 80 X, RE020114551 | 1,70 kW | 7 kg | Página consultada sin presión/caudal | $191.909,30 |
| RE 90, RE020114544 | 2,10 kW | 8 kg | Máx. 100 bar; manguera 6 m | $232.396,70 |
| RE 110, 49500114529 | 1,70 kW | 17,6 kg | El texto indica 110 bar; manguera 7 m | $676.955,30 |

**Dato documentado:** las páginas STIHL Argentina publican las referencias, potencias, pesos operacionales y precios sugeridos de la tabla. La página de RE 90 indica presión entre 10 y 100 bar y manguera de 6 m; la de RE 110 anuncia 110 bar y manguera de 7 m, además de motor de inducción y cabezal de aluminio. Las fichas consultadas no muestran el mismo conjunto de campos para todos los modelos.

**Análisis TallerLab:** el cuadro sirve para comprobar la referencia y comparar los campos publicados, no para ordenar limpieza. Por ejemplo, las páginas muestran 2,10 kW para RE 90 y 1,70 kW para RE 110, mientras anuncian 100 y 110 bar, respectivamente; esos rótulos no son un ensayo común. El precio es PVP sugerido con IVA visto en páginas oficiales el 27/09/2026, no cotización, precio final de concesionario ni garantía de stock.

**Desconocido:** la página RE 80 X revisada no permitió verificar presión/caudal comparables; tampoco se confirmó equivalencia con antiguas variantes RE 80/RE 91 X de catálogos anteriores. Los PVP pueden cambiar. Confirmar referencia, contenido de caja, garantía y disponibilidad en concesionario oficial.

## Fuentes consultadas

- **Documentación primaria:** [STIHL RE 80 X](https://www.stihl.com.ar/es/ap/re-80-x-141950); [STIHL RE 90](https://www.stihl.com.ar/es/p/hidrolavadoras-re-90-141963); [STIHL RE 110](https://www.stihl.com.ar/es/ap/re-110-81523); [catálogo oficial de hidrolavadoras STIHL Argentina](https://www.stihl.com.ar/es/c/hidrolavadoras-98132).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/hidrolavadoras/", "/hidrolavadoras/comparativa-general/", "comparativa general de hidrolavadoras: presión y caudal",
    ),
    "paginas/soldadoras/00-soldadoras.md": (
        "Matriz de elección que enlaza proceso, consumible, gas y datos que debe confirmar la ficha: separa MMA, MIG/MAG, tubular autoprotegido, TIG y resistencia por alcance documental.",
        """| Proceso | Consumible/documento de referencia | Gas de protección | Dato que cambia la elección |
| :--- | :--- | :--- | :--- |
| MMA/SMAW | Electrodo revestido, p. ej. E6013 o E7018 del fabricante exacto | No requiere gas externo | Tipo de metal base, clasificación completa, diámetro, corriente y posición |
| MIG/MAG/GMAW con alambre macizo | ER70S-6; ESAB publica gases C1 y M21 para su producto | Sí; gas especificado por alambre/procedimiento | Composición/gas, diámetro, alimentación y rango de la fuente |
| Alambre tubular autoprotegido (FCAW-S) | Ejemplos de fabricante: E71T-GS y E71T-11 | El producto indicado se clasifica como autoprotegido; sin gas externo | Clasificación completa, diámetro, polaridad y límite de aplicación del fabricante |
| TIG/GTAW | Varilla de aporte si corresponde y antorcha TIG | Gas externo según consumible/procedimiento | Corriente AC/DC, material y control térmico |
| Soldadura por resistencia/punto | Electrodos de cobre de la máquina | No usa alambre/electrodo consumible revestido | Espesor, geometría, presión/corriente/tiempo que especifique el equipo |

**Dato documentado:** ESAB identifica la HandyArc MIG 160i para MIG/MAG, alambre tubular y electrodo; su familia HandyArc 162i se especifica para MMA. ESAB Weld 70S-6 declara clasificación ER70S-6 y gas C1/M21; Lincoln identifica productos E71T-GS y E71T-11 como alambres tubulares autoprotegidos. Las fuentes citadas documentan esos productos concretos, no todos los consumibles con nombres similares.

**Análisis TallerLab:** empezar por material y unión, luego verificar el proceso que permite controlar el equipo disponible y, por último, el consumible compatible con su polaridad/rango. La sigla del proceso no determina por sí sola el espesor soldable ni la calidad de una unión. Esta tabla orienta a la documentación necesaria; no es un procedimiento de soldadura ni reemplaza un WPS, código de construcción o calificación cuando aplique.

**Desconocido:** sin material base, espesor, preparación, posición, servicio y norma del trabajo no se puede indicar un proceso, amperaje o consumible universal. No se evaluaron resultados de soldadura ni productos físicamente.

## Fuentes consultadas

- **Fabricantes:** [ESAB HandyArc MIG 160i](https://esab.com/ar/sam_es/products-solutions/product/welding-equipment/mig-welders-gmaw/handyarc-mig-160i/); [ESAB HandyArc 142i/162i](https://esab.com/ar/sam_es/products-solutions/product/welding-equipment/stick-welders-smaw/handyarc-132i-dv-142i-162i/); [ESAB Weld 70S-6](https://esab.com/mx/nam_es/products-solutions/product/filler-metals/mild-steel/mig-wires-tig-rods-gmaw-gtaw/weld-70s-6/); [Lincoln Electric Steelcore 71T-GS](https://ch-delivery.lincolnelectric.com/api/public/content/4b116c2b3b5f46fdaa024bac101c8e4b?v=e32391fd); [Lincoln Electric Innershield NR-211-MP](https://ch-delivery.lincolnelectric.com/api/public/content/f5e38ae6ebf441829d73d7b1a404818b?v=84bee2da).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/soldadoras/", "/soldadoras/esab-handyarc-162i/", "ficha ESAB HandyArc 162i por número de producto",
    ),
    "paginas/soldadoras/13-alambre-flux.md": (
        "Compara dos alambres tubulares autoprotegidos concretos, Lincoln Steelcore 71T-GS y Innershield NR-211-MP E71T-11, por clasificación, polaridad, rangos de diámetro y límite de espesor que cada ficha publica.",
        """| Producto/fuente | Clasificación publicada | Diámetro y rango publicado | Polaridad | Espesor máximo indicado por fabricante |
| :--- | :--- | :--- | :--- | :--- |
| Lincoln Steelcore 71T-GS | AWS A5.20 E71T-GS | 0,8 mm: 60–150 A; 0,9 mm: 60–180 A | DC− | 5 mm en ficha australiana |
| Lincoln Innershield NR-211-MP | AWS E71T-11 | 0,8–1,1 mm; rango y parámetros dependen del diámetro | La tabla de la ficha específica define el ajuste | Hasta 7,9 mm para diámetros ≤1,1 mm en documento citado |

**Dato documentado:** Lincoln identifica ambos productos como alambres tubulares autoprotegidos; la ficha Steelcore especifica E71T-GS y DC−, mientras NR-211-MP se clasifica E71T-11. Las tablas y límites de espesor de la matriz pertenecen a las fichas de fabricante enlazadas y a sus configuraciones concretas.

**Análisis TallerLab:** que ambos se vendan como «flux» o «sin gas» no los vuelve intercambiables. La clasificación, el diámetro, la polaridad, la máquina y el espesor publicado deben coincidir con la ficha del alambre ofertado. El límite de espesor no es una garantía de unión estructural ni una recomendación para cualquier posición, preparación o código.

**Desconocido:** las fichas consultadas corresponden a mercados de Australia/EE. UU.; no confirman homologación, disponibilidad o parámetros de la bobina vendida en Argentina. No extrapolamos sus rangos a alambres genéricos E71T-GS o E71T-11.

## Fuentes consultadas

- **Documentación primaria:** [Lincoln Electric Steelcore 71T-GS, ficha técnica](https://ch-delivery.lincolnelectric.com/api/public/content/4b116c2b3b5f46fdaa024bac101c8e4b?v=e32391fd); [Lincoln Electric Innershield NR-211-MP, ficha técnica](https://ch-delivery.lincolnelectric.com/api/public/content/f5e38ae6ebf441829d73d7b1a404818b?v=84bee2da); [manual Telwin de soldadora por resistencia](https://www.telwin.com/ExternalAssets/risc6000/954534_L.PDF).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/soldadoras/", "/soldadoras/alambre-para-soldadura-mig/", "alambre MIG macizo: clasificación y gas",
    ),
    "paginas/soldadoras/08-alambre-para-soldadura-mig.md": (
        "Tabla de alambre macizo ESAB Weld 70S-6 por diámetro, corriente, tensión, velocidad de alimentación, deposición y gases publicados; separa ficha de producto de compatibilidad universal.",
        """| Diámetro Weld 70S-6 | Corriente de ficha | Tensión | Velocidad de alimentación | Tasa de deposición | Gas especificado |
| :--- | ---: | ---: | ---: | ---: | :--- |
| 0,9 mm | 80–175 A | 17–22 V | 2,5–6,4 m/min | 0,7–1,8 kg/h | C1 (CO₂) o M21 |
| 1,14 mm | 145–200 A | 19–21 V | 3,2–5,1 m/min | 1,5–2,5 kg/h | C1 (CO₂) o M21 |

**Dato documentado:** ESAB clasifica Weld 70S-6 como alambre macizo ER70S-6 y publica gases de protección C1/M21 en su ficha. Los rangos por diámetro reproducen la tabla de depósito de ese producto y mercado; no describen todos los alambres ER70S-6 ni establecen un único ajuste para una máquina concreta.

**Análisis TallerLab:** al pasar de 0,9 a 1,14 mm, la ficha del producto desplaza los intervalos de corriente y velocidad a valores mayores. En una instalación real también deben coincidir rodillos/guía, rango de la fuente, transferencia, gas y preparación de junta. No convertimos los datos de depósito de catálogo en velocidad de avance de la antorcha.

**Desconocido:** la fuente mexicana consultada no confirma formatos de bobina ni disponibilidad local; los rangos para 0,6/0,8 mm no se completan con datos de otra marca. La clasificación del alambre no reemplaza el WPS ni valida una aplicación estructural.

## Fuentes consultadas

- **Documentación primaria:** [ESAB Weld 70S-6, ficha en español](https://esab.com/mx/nam_es/products-solutions/product/filler-metals/mild-steel/mig-wires-tig-rods-gmaw-gtaw/weld-70s-6/); [ESAB Weld 70S-6, página técnica de producto](https://esab.com/us/nam_en/products-solutions/product/filler-metals/mild-steel/mig-wires-tig-rods-gmaw-gtaw/weld-70s-6/).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/soldadoras/alambre-flux/", "/soldadoras/electrodo-6013/", "E6013: rangos de corriente de un producto específico",
    ),
    "paginas/soldadoras/25-carro-para-soldadora-mig.md": (
        "Compara dos carros documentados por fabricante, Telwin Federal 803091 y Lincoln K520, con huella, peso y límite de cilindro/carga cuando la documentación lo publica; permite cotejar medidas reales del taller.",
        """| Carro/código | Dimensiones publicadas | Peso | Cilindro publicado | Carga admitida publicada |
| :--- | :--- | ---: | :--- | :--- |
| Telwin Federal 803091 | 980 × 500 × 1.040 mm | 23,24 kg | Compartimento para cilindro; capacidad/tamaño no publicados en esa página | No publicado |
| Lincoln K520/K520-1 | No localizado en manual citado | No localizado | Diámetro exterior máx. 20,6 cm; altura máx. 117 cm; peso máx. 45 kg | 45 kg soldadora sola; 90 kg soldadora + cilindro |

**Dato documentado:** Telwin describe el modelo Federal 803091 con cuatro ruedas (dos giratorias), compartimento para cilindro y soporte de alimentador, e informa 980 × 500 × 1.040 mm y 23,24 kg. Lincoln documenta para K520/K520-1 los límites de cilindro y carga de la tabla.

**Análisis TallerLab:** antes de elegir, medir la huella de la máquina con conectores, la base y diámetro real del cilindro, el espacio de mangueras/cables y el recorrido de las ruedas. La tabla muestra dos diseños: Telwin publica dimensiones externas pero no capacidad; Lincoln sí pone límites de carga y cilindro en el manual consultado. No se debe inferir resistencia máxima para el Telwin por su peso propio.

| Medida del taller | Comprobación propia antes de comprar |
| :--- | :--- |
| Bandeja superior | Ancho × fondo útil versus base de la máquina y espacio de cables |
| Cilindro | Diámetro, altura, masa y sujeción admitidos por fabricante |
| Carga | Suma de máquina, alimentador, cilindro y consumibles versus carga máxima declarada |
| Circulación | Ancho total, radio de giro, umbral y estabilidad con el cilindro asegurado |

**Desconocido:** no se verificó disponibilidad argentina, compatibilidad de montaje por modelo de soldadora, precio, frenos o capacidad nominal del Telwin Federal. Confirmar esas condiciones con el manual del carro exacto.

## Fuentes consultadas

- **Documentación primaria:** [Telwin Federal 803091](https://www.telwin.com/intl/en/products/trolleys/803091-trolley-federal); [manual Lincoln K520/K520-1](https://ch-delivery.lincolnelectric.com/api/public/content/0543dfa0438b451096025e84d666a015?v=a71a7ecf).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/soldadoras/", "/soldadoras/esab-handyarc-162i/", "dimensiones y corriente de la ESAB HandyArc 162i",
    ),
    "paginas/soldadoras/10-electrodo-6013.md": (
        "Compara amperajes por diámetro de dos referencias ESAB E6013 (Sureweld 6013 y LBL BW E6013); deja claro que la clasificación por sí sola no fija el amperaje para todas las marcas.",
        """| Producto de fabricante | Diámetro | Corriente publicada |
| :--- | ---: | ---: |
| ESAB Sureweld 6013 | 2,4 mm | 60–90 A |
| ESAB Sureweld 6013 | 3,2 mm | 120–135 A |
| ESAB LBL BW E6013 | 2,5 mm | 70–90 A |
| ESAB LBL BW E6013 | 3,2 mm | 95–125 A |

**Dato documentado:** ambas fuentes identifican sus productos como E6013 y publican los rangos de corriente listados. Aunque las clasificaciones coinciden, las tablas son de líneas comerciales distintas y usan diámetros/presentaciones propios.

**Análisis TallerLab:** para 3,2 mm, los dos rangos publicados se superponen entre 120 y 125 A, pero sus extremos difieren. Esto muestra por qué la corriente debe tomarse de la caja/ficha del fabricante del electrodo y ajustarse a la fuente y aplicación; no se puede formar una tabla universal sumando marcas. No se recomienda un amperaje para una pieza desconocida.

**Desconocido:** las páginas ESAB citadas corresponden a referencias de EE. UU. y Bangladesh; no prueban que esos SKU sean los que se venden en Argentina ni sustituyen la ficha de Conarco u otra marca. Para el ejemplar local, verificar diámetro, polaridad/corriente permitida, posición y clasificación en el envase.

## Fuentes consultadas

- **Documentación primaria:** [ESAB Sureweld 6013](https://esab.com/us/nam_en/products-solutions/product/filler-metals/mild-steel/stick-electrodes-smaw/sureweld-6013/); [ESAB LBL BW E6013](https://esab.com/bd/ind_en/products-solutions/product/filler-metals/mild-steel/stick-electrodes-smaw/lbl-bw-e6013/); [ESAB Weld 6013](https://esab.com/au/apc_en/products-solutions/product/filler-metals/mild-steel/stick-electrodes-smaw/weld-6013/).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/soldadoras/", "/soldadoras/electrodo-7018/", "E7018: datos del fabricante y almacenamiento",
    ),
    "paginas/soldadoras/01-electrodo-7018.md": (
        "Tabla de corriente ESAB Atom Arc 7018 por diámetro y contraste con la corriente nominal de HandyArc 162i por ciclo de trabajo; separa consumible, fuente y almacenamiento sin generalizar los valores.",
        """| Referencia documentada | Diámetro de electrodo | Rango del fabricante |
| :--- | ---: | ---: |
| ESAB Atom Arc 7018, hoja México | 2,4 mm | 70–110 A |
| ESAB Atom Arc 7018, hoja México | 3,2 mm | 90–160 A |
| ESAB Atom Arc 7018, hoja México | 4,0 mm | 130–220 A |
| ESAB HandyArc 162i, salida MMA | Corriente máxima de fuente | 160 A al 20 %; 92 A al 60 %; 72 A al 100 % |

**Dato documentado:** ESAB clasifica Atom Arc 7018 como E7018 H4R y publica los rangos por diámetro de la tabla. La ficha de HandyArc 162i publica corriente nominal de salida de 160 A al 20 % de ciclo, 92 A al 60 % y 72 A al 100 % a 220 V.

**Análisis TallerLab:** los 160 A máximos de la máquina no son un ajuste continuo: el ciclo publicado baja a 92 A/60 % y 72 A/100 %. Además, el rango de 4,0 mm de la ficha del electrodo se extiende a 220 A, por encima de la salida máxima de esta máquina. Eso compara dos hojas técnicas, no dicta que un diámetro sea adecuado para una junta o que una fuente produzca el resultado requerido.

**Desconocido:** Atom Arc 7018 H4R es un producto concreto y su rango no se aplica automáticamente a cualquier E7018, marca o lote local. No se indica un procedimiento de secado/horneado universal; seguir etiqueta, empaque y manual del consumible exacto, especialmente para electrodos bajo hidrógeno.

## Fuentes consultadas

- **Documentación primaria:** [ESAB Atom Arc 7018, ficha México](https://esab.com/mx/nam_es/products-solutions/product/filler-metals/mild-steel/stick-electrodes-smaw/atom-arc-7018/); [ESAB HandyArc 142i/162i, ficha Argentina](https://esab.com/ar/sam_es/products-solutions/product/welding-equipment/stick-welders-smaw/handyarc-132i-dv-142i-162i/); [ESAB 7018, datos de otro producto regional](https://esab.com/us/nam_en/products-solutions/product/filler-metals/mild-steel/stick-electrodes-smaw/esab-7018/).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/soldadoras/electrodo-6013/", "/soldadoras/electrodo-para-acero-inoxidable/", "electrodos inoxidables: clasificación y metal base",
    ),
    "paginas/soldadoras/16-electrodo-para-acero-inoxidable.md": (
        "Matriz de tres referencias ESAB para 308L, 316L y 309L que conecta clasificación publicada con el tipo de metal base indicado por el fabricante; evita proponer una aleación única para todo inoxidable.",
        """| Referencia ESAB | Clasificación | Uso descrito por el fabricante en la ficha consultada | Dato de corriente de producto |
| :--- | :--- | :--- | :--- |
| OK 308L | AWS A5.4 E308L-16 | Aceros del tipo 19Cr10Ni; la ficha menciona aceros estabilizados de composición similar con límite específico | No se incorpora rango sin cotejar la variante local |
| Cromarco 316L-16 Premium | AWS A5.4 E316L-16 | AISI 316/316L | 2,4 mm: 40–80 A; 3,2 mm: 70–110 A; 4,0 mm: 100–145 A |
| OK 67.61 N | SFA/AWS A5.4 E309L-16 | Clasificación confirmada en la página ESAB Argentina; no se extrapola aquí un procedimiento de unión disímil | Verificar corriente en la ficha/paquete del diámetro local |

**Dato documentado:** las páginas de producto ESAB identifican las clasificaciones de la tabla. La ficha de Cromarco 316L-16 Premium señala uso en AISI 316/316L y publica corrientes por diámetro; OK 308L se describe para aceros 19Cr10Ni. Para OK 67.61 N, la página ESAB Argentina confirma E309L-16.

**Análisis TallerLab:** los sufijos y la clasificación cambian el metal de aporte; no basta decir «electrodo inoxidable». La tabla ayuda a cruzar el metal base con la descripción del producto exacto. Compatibilidad química, temperatura de servicio, corrosión, preparación y calificación requieren consultar el código/procedimiento aplicable; esta matriz no aprueba una unión para servicio crítico.

**Desconocido:** no se confirmaron equivalencias entre marcas ni designaciones AWS/EN para los electrodos ofrecidos localmente, tampoco precio o disponibilidad actual. No se prescribe un E309L para toda unión inoxidable–acero al carbono ni una polaridad sin manual del producto.

## Fuentes consultadas

- **Documentación primaria:** [ESAB OK 308L](https://esab.com/au/apc_en/products-solutions/product/filler-metals/stainless-steel/stick-electrodes-smaw/ok-308l/); [ESAB Cromarco 316L-16 Premium](https://esab.com/co/sam_es/products-solutions/product/filler-metals/stainless-steel/stick-electrodes-smaw/cromarco-316l-16-premium/); [ESAB OK 67.61 N, Argentina](https://esab.com/ar/sam_es/products-solutions/product/filler-metals/stainless-steel/stick-electrodes-smaw/ok-67-61-n/).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/soldadoras/electrodo-7018/", "/soldadoras/electrodo-para-fundicion/", "electrodo para fundición: Ni-CI y NiFe-CI",
    ),
    "paginas/soldadoras/12-electrodo-para-fundicion.md": (
        "Compara dos electrodos ESAB clasificados ENi-CI y ENiFe-CI con porcentaje de níquel, unión descrita y rangos por diámetro; aporta criterios de clasificación sin reemplazar un procedimiento de reparación.",
        """| Producto / clasificación | Familia de aleación publicada | Aplicación que indica ESAB | Corriente publicada por diámetro |
| :--- | :--- | :--- | :--- |
| OK Ni-CI, AWS A5.15 ENi-CI | Base níquel; análisis típico 94 % Ni en ficha | Reparación/unión de fundiciones grises, dúctiles y maleables; también hierro fundido con acero | 2,5 mm: 55–110 A; 3,2 mm: 80–140 A |
| OK NiFe-CI, AWS A5.15 ENiFe-CI | Níquel-hierro; análisis típico 53 % Ni y 44 % Fe en ficha | Producto ESAB para fundición; confirmar el caso exacto en hoja técnica | 2,5 mm: 60–100 A; 3,2 mm: 80–150 A |

**Dato documentado:** ESAB clasifica OK Ni-CI como ENi-CI y OK NiFe-CI como ENiFe-CI. Sus páginas informan composiciones típicas y rangos de corriente específicos para cada diámetro. ESAB describe OK Ni-CI para ciertos grados normales de fundición y uniones con acero; esas indicaciones corresponden a ese producto.

**Análisis TallerLab:** la tabla permite comprobar clasificación y contenido nominal de aleación antes de comprar. No convierte «níquel puro» o «ferroníquel» en una selección suficiente: la fundición, contaminación, geometría, restricción y servicio de la pieza pueden cambiar el método requerido. Una reparación de componente presurizado, de seguridad o con carga exige procedimiento y personal calificado.

**Desconocido:** no se identificó composición de la pieza a reparar ni se ensayaron cordones. No se recomienda universalmente soldar «en frío» o precalentar a una temperatura fija; aplicar solo las instrucciones del consumible, el código y la evaluación técnica de la pieza.

## Fuentes consultadas

- **Documentación primaria:** [ESAB OK Ni-CI](https://esab.com/au/apc_en/products-solutions/product/filler-metals/nickel/stick-electrodes-smaw/ok-ni-ci/); [ESAB OK NiFe-CI](https://esab.com/es/eur_es/products-solutions/product/filler-metals/other/repair-and-maintenance/ok-nife-ci/).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/soldadoras/electrodo-para-acero-inoxidable/", "/soldadoras/esab-handyarc-162i/", "fuente MMA y rango de corriente de ESAB HandyArc",
    ),
    "paginas/soldadoras/26-esab-handyarc-162i.md": (
        "Tabla de ESAB HandyArc 162i, código 0409616: corriente MMA por ciclo de trabajo, rango, tensión, potencia aparente y generador recomendado; distingue máximo intermitente de salida continua.",
        """| Parámetro HandyArc 162i (0409616) | Dato publicado por ESAB Argentina |
| :--- | :--- |
| Alimentación | 220 V ±10 %, monofásica, 50/60 Hz |
| Rango de corriente MMA | 20–160 A |
| Salida nominal al 20 % | 160 A / 26,4 V |
| Salida nominal al 60 % | 92 A / 23,7 V |
| Salida nominal al 100 % | 72 A / 22,9 V |
| Potencia aparente | 7,04 kVA |
| Generador recomendado por ESAB | 10,5 kVA |
| Protección / norma | IP21S / IEC 60974-1 |

**Dato documentado:** ESAB Argentina publica los datos anteriores para HandyArc 162i, número de producto 0409616. El ciclo de trabajo identifica puntos distintos de corriente/tensión nominal; 160 A aparece al 20 %, mientras que la salida indicada al 100 % es 72 A.

**Análisis TallerLab:** la relación de la propia tabla impide interpretar «162» o «160 A» como corriente sostenida: el amperaje publicado varía según ciclo. El generador de 10,5 kVA es una recomendación de ESAB para el producto y no verifica por sí sola el tamaño de cualquier instalación, alargue o generador disponible.

| Antes de comprar | Confirmación necesaria |
| :--- | :--- |
| Identidad | Modelo HandyArc 162i y código 0409616, no la 142i ni HandyArc MIG 160i |
| Red eléctrica | Tensión, protección y sección de conductores según placa/manual y normativa local |
| Consumible | Diámetro, clasificación, polaridad y amperaje de la ficha del electrodo |
| Accesorios/garantía | Lista de entrega, distribuidor, cobertura y servicio vigentes |

**Desconocido:** no se inspeccionó unidad física, precio local, contenido de una oferta ni resultados de soldadura. La página comercial no basta para confirmar qué pinza, cable u otros accesorios incluye cada paquete.

## Fuentes consultadas

- **Documentación primaria:** [ESAB HandyArc 142i/162i, página oficial Argentina](https://esab.com/ar/sam_es/products-solutions/product/welding-equipment/stick-welders-smaw/handyarc-132i-dv-142i-162i/); [hoja técnica ESAB HandyArc 162i](https://assets.esab.com/assetbank-esab/assetfile/41560.pdf).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/soldadoras/", "/soldadoras/electrodo-7018/", "amperajes de electrodos E7018 según ficha",
    ),
}

for relpath, (asset, body, hub, sibling, sibling_title) in PAGES.items():
    path = ROOT / relpath
    old = path.read_text(encoding="utf-8")
    match = re.match(r"---\r?\n(.*?)\r?\n---\r?\n", old, re.S)
    if not match:
        raise RuntimeError(f"No se encontró frontmatter en {path}")
    front = match.group(1)
    h1_match = re.search(r"(?m)^h1:\s*(?:\"(.*?)\"|'(.*?)'|(.+))$", front)
    if not h1_match:
        raise RuntimeError(f"No se encontró H1 en {path}")
    h1_value = next(value for value in h1_match.groups() if value is not None)
    title_before = re.search(r"(?m)^title:.*$", front).group(0)
    url_before = re.search(r"(?m)^url:.*$", front).group(0)
    escaped = asset.replace('"', '\\"')
    front = re.sub(r"(?m)^description:.*$", f'description: "{escaped}"', front)
    values = {
        "research_type": '"documental"', "physical_test": '"no"',
        "specifications_contrasted": '"sí"', "buyer_opinions": '"no"',
        "primary_sources": '"sí"', "information_asset": '"' + escaped + '"',
        "asset_status": '"verificado"', "reviewed": '"27/09/2026"', "published": "true",
    }
    for key, value in values.items():
        if re.search(rf"(?m)^{key}:", front):
            front = re.sub(rf"(?m)^{key}:.*$", f"{key}: {value}", front)
        else:
            front += f"\n{key}: {value}"
    if title_before != re.search(r"(?m)^title:.*$", front).group(0) or url_before != re.search(r"(?m)^url:.*$", front).group(0):
        raise RuntimeError(f"Cambió title o URL al preparar {path}")
    newbody = (
        f"# {h1_value}\n\n<!-- AUDITORIA_EDITORIAL_178 -->\n\n"
        f"**Dato documentado:** las cifras se atribuyen al documento indicado en cada tabla. Los cálculos se identifican como **Análisis TallerLab**; lo no confirmado queda como **Desconocido**. Esta guía es documental y no incluye prueba física.\n\n"
        f"## Cómo investigamos esta guía\n\n"
        f"- Tipo de análisis: documental\n- Prueba física de TallerLab: no\n- Especificaciones contrastadas: sí\n- Opiniones de compradores: no\n- Fuentes primarias: sí\n- Última revisión: 27/09/2026\n\n"
        f"{body}\n\n"
        f"Para seguir comparando: [{sibling_title}]({sibling}).\n\n"
        f"Para conocer el criterio editorial: [Ver metodología de TallerLab](/como-trabajamos/).\n\n"
        f"Para explorar la categoría: [guías relacionadas]({hub}).\n"
    )
    path.write_text(f"---\n{front}\n---\n\n{newbody}", encoding="utf-8")
    print(relpath)
