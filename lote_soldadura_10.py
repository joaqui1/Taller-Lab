"""Decimosexto lote editorial: fuentes ESAB y Lüsqtoff, EPP y máscaras."""
from pathlib import Path
import re

ROOT = Path(__file__).parent

PAGES = {
    "paginas/soldadoras/15-soldadora-esab.md": (
        "Comparación documental de ESAB HandyArc 162i MMA y HandyArc MIG 160i por proceso, amperaje nominal, ciclo de trabajo, alimentación y código de producto en Argentina.",
        """| Modelo/código ESAB Argentina | Procesos que publica ESAB | Corriente y ciclo publicados | Alimentación y peso |
| :--- | :--- | :--- | :--- |
| HandyArc 162i, 0409616 | MMA | 160 A/20%; 92 A/60%; 72 A/100% | 220 V ±10%, monofásica; 3,7 kg |
| HandyArc MIG 160i, 0410060 | GMAW (MIG/MAG) y MMA | GMAW: 160 A/15%, 80 A/60%, 62 A/100%; MMA: 140 A/15%, 70 A/60%, 54 A/100% | 220 V ±10%; 10,2 kg |

**Dato documentado:** la tabla copia los puntos nominales que ESAB Argentina publica para dos equipos con procesos distintos. La 162i es una fuente MMA; la MIG 160i agrega proceso GMAW y alimentación de alambre. El nombre comercial «160» no significa el mismo ciclo ni las mismas funciones en ambos modelos.

**Análisis TallerLab:** al comparar ofertas, primero identificá el proceso requerido y el código; después leé juntos corriente, tensión y porcentaje de ciclo. En MMA, la 162i llega a 72 A al 100%; en GMAW, la MIG 160i declara 62 A al 100%. Son datos de placa/ficha, no una medición de TallerLab ni una recomendación de espesor.

| Verificación de compra | Qué coincide en la documentación |
| :--- | :--- |
| Proceso | MMA para 162i; GMAW y MMA para MIG 160i |
| Red | Ambas páginas indican 220 V; comprobar placa y circuito local |
| Consumible | Electrodo revestido para MMA; alambre y configuración compatibles para GMAW |
| Paquete | Accesorios y garantía deben verificarse en la oferta del código adquirido |

**Desconocido:** la guía no confirma inventario, precio, términos de garantía por distribuidor ni el contenido de cada publicación comercial. No se revisó una muestra de compradores ni se probó una máquina.

## Fuentes consultadas

- **Documentación primaria:** [ESAB HandyArc 142i/162i, Argentina](https://esab.com/ar/sam_es/products-solutions/product/welding-equipment/stick-welders-smaw/handyarc-132i-dv-142i-162i/); [hoja técnica ES-AR HandyArc 142i/162i](https://assets.esab.com/assetbank-esab/assetfile/41560.pdf); [ESAB HandyArc MIG 160i, Argentina](https://esab.com/ar/sam_es/products-solutions/product/welding-equipment/mig-welders-gmaw/handyarc-mig-160i/).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/soldadoras/", "/soldadoras/esab-handyarc-162i/", "ficha y ciclo de trabajo ESAB HandyArc 162i",
    ),
    "paginas/soldadoras/05-guantes-para-soldar.md": (
        "Compara dos guantes ESAB concretos por norma declarada, masa y construcción: Heavy Duty Black para MMA/MIG y TIG Basic; no extrapola la certificación a todo guante de cuero.",
        """| Producto ESAB | Proceso indicado por fabricante | Construcción publicada | Norma declarada | Peso publicado |
| :--- | :--- | :--- | :--- | ---: |
| Heavy Duty Black, 0615465 | Guante de soldador general; la ficha lo agrupa con guantes Heavy Duty | Palma reforzada, pulgar palmeado y forro hasta el puño | EN 407 413X4X; EN 12477 Type A; EN 388 4134X | 350 g |
| TIG Basic, 0700500460 | TIG | Cuero vacuno dividido y piel de cabra; sin forro | EN 407 413X4X; EN 12477 Type A; EN 388 2122X | 160 g |

**Dato documentado:** las fichas ESAB publican las construcciones, masas y códigos de la tabla. La designación EN 12477 Type A y los códigos EN 388/EN 407 corresponden a esos productos concretos y a la documentación del fabricante.

**Análisis TallerLab:** la comparación muestra diferencias comprobables (190 g entre los productos y construcción forrada frente a no forrada). No demuestra que uno sea más seguro para cualquier trabajo ni permite trasladar sus valores a guantes sin código y declaración de conformidad equivalentes. Para comprar, comprobar talla, etiqueta, daños, puño y estado del par; seguir la evaluación de riesgos del puesto y las instrucciones del fabricante.

**Desconocido:** no se verificó protección térmica de guantes genéricos por espesor o tipo de cuero, temperaturas de contacto admisibles, durabilidad, stock local ni equivalencia de la nomenclatura comercial con una certificación. Una descripción de cuero o costura no reemplaza el marcado y la ficha del EPP.

## Fuentes consultadas

- **Documentación primaria:** [ESAB Guantes Heavy Duty Black](https://esab.com/pe/sam_es/products-solutions/product/ppe-safety/hands-and-body/heavy-duty-black-gloves/); [ESAB TIG Basic Glove](https://esab.com/ae/mea_en/products-solutions/product/ppe-safety/hands-and-body/tig-basic-glove/); [ESAB Heavy Duty EXL](https://esab.com/ae/mea_en/products-solutions/product/ppe-safety/hands-and-body/heavy-duty-exl/) como ficha adicional de la familia de guantes.
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/soldadoras/", "/soldadoras/mascaras-fotosensibles/", "máscaras fotosensibles: datos declarados por modelo",
    ),
    "paginas/soldadoras/21-soldadora-lusqtoff-iron-100.md": (
        "Contrasta el IRON-100 de catálogo 2020/21 con el kit MEGAIRON100-8 actual: rango/ciclo, peso y contenido de caja, dejando visible que son códigos y generaciones distintas.",
        """| Referencia Lüsqtoff | Corriente/ciclo que publica la fuente | Peso | Qué incluye la fuente citada |
| :--- | :--- | ---: | :--- |
| IRON-100, catálogo 2020/21 | Rango 10–105 A; no se transcribe un ciclo | 3,2 kg | No es una oferta de kit documentada en ese recorte |
| MEGAIRON100-8, ficha actual | Ciclo MMA 105 A al 30%; la ficha de producto no informa rango completo | No publicado en ficha de producto citada | Soldadora, máscara ST-1X y dos escuadras magnéticas |

**Dato documentado:** el catálogo histórico denomina al primer equipo IRON-100 y le asigna 220 V/50 Hz, proceso MMA, rango 10–105 A, peso 3,2 kg y garantía indicada de seis meses en esa edición. La página actual MEGAIRON100-8 describe otro código de kit, con ciclo MMA 30% a 105 A y los accesorios de la tabla. No hay evidencia de que las cifras de peso, rango y garantía de la primera referencia deban copiarse al segundo SKU.

**Análisis TallerLab:** «Iron 100» en un título de publicación puede referirse a la máquina anterior o al kit MEGAIRON100-8. Para comparar precio, peso o cobertura, confirmar código completo en placa/factura y separar fuente, máscara y escuadras. El amperaje máximo anunciado no indica por sí solo una salida continua: el kit 100-8 declara un punto de 105 A con ciclo del 30%.

**Desconocido:** la ficha consultada no detalla masa ni ciclo completo del MEGAIRON100-8, y el catálogo 2020/21 no prueba condiciones de garantía actuales. Verificar manual vigente, tensión nominal, accesorios de la caja y garantía escrita del distribuidor antes de compra.

## Fuentes consultadas

- **Documentación primaria:** [Lüsqtoff MEGAIRON100-8](https://www.lusqtoff.com.ar/ver-producto/MEGAIRON100-8); [catálogo oficial Lüsqtoff 2020/21, IRON-100](https://lusqtoff.com.ar/files/Catalogo_Lusqtoff_2020.pdf); [manual oficial MEGAIRON100-8](https://www.lusqtoff.com.ar/2023/uploads/Productos/NUEVOS/SOLDADORAS_INVERTER/MEGAIRON100-8/manual%20MEGAIRON100-8_compressed%20%281%29.pdf).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/soldadoras/lusqtoff/", "/soldadoras/lusqtoff-iron-250/", "datos publicados del kit Lusqtoff Iron 250",
    ),
    "paginas/soldadoras/18-soldadora-lusqtoff-iron-250.md": (
        "Examina la discrepancia entre el nombre MEGAIRON250/IRON-250 y la salida declarada de 180 A, además de los dos puntos de ciclo a 40 °C y contenido del kit fabricante.",
        """| Dato del kit Lüsqtoff MEGAIRON250 | Declaración del fabricante |
| :--- | :--- |
| Equipo incluido | Soldadora identificada como IRON-250 dentro de kit MEGAIRON250 |
| Tensión/frecuencia | 220 V ±15%; 50 Hz; monofásica |
| Rango de salida publicado | 20–180 A |
| Ciclo a 40 °C | 180 A / 27,2 V al 40%; 114 A / 24,2 V al 100% |
| Entrada nominal | 6,5 kW; corriente de entrada 30 A |
| Masa publicada | 5 kg |
| Accesorios del kit | Máscara ST-1X y dos escuadras magnéticas LQE-6001 |

**Dato documentado:** aunque el nombre comercial incluye «250», la ficha de MEGAIRON250 identifica la máquina como IRON-250 y declara rango de salida hasta 180 A. La misma ficha publica los dos puntos de ciclo de trabajo en la tabla. Presentamos lo que dice esa página, no una medición independiente.

**Análisis TallerLab:** para comparar equipos, la salida máxima de ficha y el ciclo de trabajo describen aspectos distintos. En este caso, el fabricante publica 180 A al 40% y 114 A al 100%; el número «250» del nombre no debe leerse como corriente de salida verificada. Los 6,5 kW y 30 A de entrada también requieren verificar el circuito según la placa y normativa local.

**Desconocido:** no se confirmó si el vendedor entrega exactamente la máscara, escuadras y configuración de la ficha, ni precio vigente, garantía aplicable, longitud/sección de cables o desempeño con un electrodo y unión particulares. Confirmar código y manual con el vendedor.

## Fuentes consultadas

- **Documentación primaria:** [Lüsqtoff MEGAIRON250, ficha oficial](https://www.lusqtoff.com.ar/ver-producto/MEGAIRON250); [catálogo Lüsqtoff 2023/24](https://lusqtoff.com.ar/2023/uploads/Catalogos/CAT%C3%81LOGO%20LQ%202024-2025%20-%20web%20%281%29.pdf); [sitio oficial de soldadoras inverter Lüsqtoff](https://lusqtoff.com.ar/ver-productos/13-soldadoras-inverter).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/soldadoras/lusqtoff/", "/soldadoras/lusqtoff-iron-100/", "kit MEGAIRON100-8: ciclo y contenidos declarados",
    ),
    "paginas/soldadoras/24-soldadora-lusqtoff-sml120-8d.md": (
        "Compara soldadora individual SML120-8D y kit SML120-8DK con diferencias de peso, procesos y accesorios publicadas por Lüsqtoff para el mismo equipo base.",
        """| Referencia | Procesos y rango publicados | Peso de ficha | Accesorios publicados |
| :--- | :--- | ---: | :--- |
| SML120-8D, unidad | FLUX 20–120 A; MMA 20–100 A; Lift TIG 20–100 A | 6,6 kg | Pinza de masa, portaelectrodos, torcha Flux y picos de contacto |
| SML120-8DK, kit | FLUX 20–120 A; MMA 20–100 A; Lift TIG 20–100 A | 8,1 kg | SML120-8D, máscara ST-1X, escuadras LQE-6001 y rollo LQFLUX045, además de pinzas |

**Dato documentado:** las dos páginas oficiales identifican los procesos y rangos de la máquina base. El kit agrega accesorios y declara 1,5 kg más que la unidad suelta; esa diferencia es el cálculo TallerLab entre masas publicadas, no el peso medido de una caja abierta.

**Análisis TallerLab:** el sufijo K diferencia una presentación de kit; no cambia los rangos de soldadura publicados para la fuente SML120-8D. El PVP visto en cada página puede variar y no garantiza que un distribuidor entregue el mismo paquete. La ficha de la unidad indica 200 V–50 Hz, por lo que conviene corroborar placa y red disponible antes de comprar.

**Desconocido:** las fuentes no publican aquí una masa separada para cada accesorio, ni confirman existencias, garantía de una oferta externa o consumibles incluidos más allá de los enumerados. No se comparó rendimiento de cordón ni se probó el equipo.

## Fuentes consultadas

- **Documentación primaria:** [Lüsqtoff SML120-8D](https://www.lusqtoff.com.ar/ver-producto/SML120-8D); [Lüsqtoff SML120-8DK](https://lusqtoff.com.ar/ver-producto/SML120-8DK); [catálogo oficial de soldadoras inverter](https://lusqtoff.com.ar/ver-productos/13-soldadoras-inverter).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/soldadoras/lusqtoff/", "/soldadoras/mig-lusqtoff/", "comparativa de soldadoras MIG Flux Lüsqtoff por modelo",
    ),
    "paginas/soldadoras/28-soldadora-lusqtoff-sml130-7.md": (
        "Contrasta ficha comercial y manual del modelo discontinuado SML130-7: ciclo, entrada, capacidad de alambre, dimensiones y discrepancia en cómo el fabricante expresa los puntos de corriente.",
        """| Campo SML130-7 | Página oficial de producto | Manual del fabricante |
| :--- | :--- | :--- |
| Estado comercial | Marcado como discontinuado | Manual de la generación publicada |
| Entrada | 220 V ±15%, 50 Hz; 3,7 kW; 17 A | 220 V/50 Hz; 3,74 kVA; 17 A |
| Salida FCAW | 25–120 A | 25–120 A |
| Ciclo publicado | 50 A/16,5 V al 60%; 120 A/20 V al 10%, a 40 °C | 120 A al 10% |
| Alambre y carrete | 0,6/0,8/0,9 mm; rollos 0,5 o 1 kg | 0,6–1,0 mm; incluye rollo flux de 0,45 kg |
| Dimensiones/peso | 485 × 290 × 310 mm; 14,7 kg | Peso 14,7 kg |

**Dato documentado:** Lüsqtoff etiqueta la página como discontinuada. Ambas fuentes identifican la SML130-7 para alambre tubular autoprotegido y muestran rango de salida 25–120 A; el manual lista un intervalo de diámetros más amplio que la ficha comercial. La página añade un punto a 50 A/60% que el extracto de manual consultado no reproduce.

**Análisis TallerLab:** para comprar o reemplazar una unidad, el manual y la etiqueta del equipo deben gobernar la compatibilidad de alambre y los ajustes. No completamos la divergencia de 0,9 frente a 1,0 mm por inferencia. Los 120 A al 10% tampoco significan uso continuo a esa corriente.

**Desconocido:** no se confirmó disponibilidad de repuestos ni garantía vigente para unidades discontinuadas. La página comercial incluye una torcha MB-15 y un rollo, mientras el manual enumera el rollo de 0,45 kg; verificar accesorios reales en la oferta.

## Fuentes consultadas

- **Documentación primaria:** [Lüsqtoff SML130-7, página oficial](https://lusqtoff.com.ar/ver-producto/SML130-7); [manual de usuario SML130-7](https://lusqtoff.com.ar/2023/uploads/Productos/13.%20SOLDADORAS%20INVERTER/SML130-7/MANUAL%20FOR%20SML130-7.pdf); [familia de soldadoras inverter Lüsqtoff](https://lusqtoff.com.ar/ver-productos/13-soldadoras-inverter).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/soldadoras/mig-lusqtoff/", "/soldadoras/lusqtoff-sml120-8d/", "Lüsqtoff SML120-8D: diferencias entre unidad y kit",
    ),
    "paginas/soldadoras/02-soldadora-lusqtoff.md": (
        "Matriz de tres modelos Lüsqtoff para distinguir MMA, FCAW/Flux y tridual; compara rangos/ciclos y presenta discontinuidad de SML130-7 sin mezclar kits ni generaciones.",
        """| Modelo/código de fuente | Proceso documentado | Rango/ciclo publicado | Situación que informa la página |
| :--- | :--- | :--- | :--- |
| SML120-8D | FLUX, MMA y Lift TIG | FLUX 20–120 A; MMA/Lift TIG 20–100 A; ciclo 25% a 25 °C | Página de producto vigente en el catálogo consultado |
| SML130-7 | FCAW con tubular autoprotegido | 25–120 A; 120 A/10% y 50 A/60% a 40 °C en página | Discontinuada |
| MEGAIRON100-8 | MMA | 105 A al 30% en página; rango completo no publicado allí | Kit incluye ST-1X y escuadras |

**Dato documentado:** la tabla diferencia tres códigos según páginas/manuales de Lüsqtoff. No atribuye MIG/MMA/TIG a todos los equipos: la SML120-8D sí declara tres procesos, SML130-7 es un modelo de alambre tubular discontinuado y MEGAIRON100-8 se describe como MMA.

**Análisis TallerLab:** elegí primero proceso y disponibilidad de consumibles; compará luego puntos de ciclo a la misma temperatura y condiciones. No es válido ordenar estos equipos solo por el número de amperios o por la palabra «kit»: SML130-7 figura discontinuada y los otros dos tienen procesos y presentaciones distintas. Confirmá si la ficha corresponde a máquina sola o paquete y revisá placa del ejemplar ofertado.

**Desconocido:** esta muestra no representa todo el catálogo Lusqtoff. No se verificaron disponibilidad local, precio estable, cobertura de garantía por vendedor ni resultados de soldadura. Para equipos no incluidos, el dato queda pendiente hasta localizar su ficha o manual exactos.

## Fuentes consultadas

- **Documentación primaria:** [Lüsqtoff SML120-8D](https://www.lusqtoff.com.ar/ver-producto/SML120-8D); [Lüsqtoff SML130-7](https://lusqtoff.com.ar/ver-producto/SML130-7); [manual SML130-7](https://lusqtoff.com.ar/2023/uploads/Productos/13.%20SOLDADORAS%20INVERTER/SML130-7/MANUAL%20FOR%20SML130-7.pdf); [Lüsqtoff MEGAIRON100-8](https://www.lusqtoff.com.ar/ver-producto/MEGAIRON100-8); [catálogo de soldadoras](https://lusqtoff.com.ar/ver-productos/13-soldadoras-inverter).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/soldadoras/", "/soldadoras/mig-lusqtoff/", "soldadoras MIG Flux Lüsqtoff por modelo y ciclo",
    ),
    "paginas/soldadoras/27-mascara-lusqtoff-st-1x.md": (
        "Compara especificaciones históricas publicadas para máscara Lüsqtoff ST-1X con la ST-1B actual: visor, sensores, tono y velocidad nominal; documenta cambio de versión y límites de vigencia.",
        """| Modelo | Área de visión | Sensores | Tono declarado | Velocidad declarada | Estado en fuente consultada |
| :--- | ---: | ---: | :--- | :--- | :--- |
| ST-1X | 92 × 42 mm | 2 | DIN 4/9–13 | 1/15.000 s | Catálogo oficial 2020/21; aparece incluida en algunos kits actuales |
| ST-1B | 98 × 43 mm | 4 | DIN 4/9–13 | 1/25.000 s | Ficha actual de producto |

**Dato documentado:** los datos ST-1X proceden del catálogo oficial histórico de Lüsqtoff; los ST-1B, de su página de producto actual. Lüsqtoff también identifica ST-1X como parte de ciertos kits de soldadora, pero eso no confirma que la máscara suelta conserve idénticas especificaciones o garantía.

**Análisis TallerLab:** los números permiten distinguir dos filtros comercializados con códigos distintos; no equivalen a una prueba comparativa de protección, calidad óptica o tiempo real de respuesta. La rapidez indicada es una cifra nominal de ficha y depende de que el equipo esté intacto, ajustado y dentro de sus condiciones de operación.

**Desconocido:** no se encontró ficha de producto vigente independiente para ST-1X ni se confirmó disponibilidad, certificación actual o garantía para una unidad suelta. Antes de comprar, comprobar el código impreso en filtro/casco, marcado de conformidad, tono, repuestos y fecha/lote.

## Fuentes consultadas

- **Documentación primaria:** [catálogo Lüsqtoff 2020/21, ST-1X](https://lusqtoff.com.ar/files/Catalogo_Lusqtoff_2020.pdf); [ficha actual Lüsqtoff ST-1B](https://lusqtoff.com.ar/ver-producto/ST-1B); [kit actual SML150-8D que lista ST-1X](https://www.lusqtoff.com.ar/ver-producto/SML150-8D).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/soldadoras/mascaras-fotosensibles/", "/soldadoras/lusqtoff-sml120-8d/", "qué accesorios enumera el kit SML120-8DK",
    ),
    "paginas/soldadoras/09-mascara-de-soldar-fotosensible.md": (
        "Compara filtros automáticos Lüsqtoff ST-1N, ST-1E y ST-1B por tono, sensores, área visible, alimentación y respuesta nominal, con especificaciones tomadas de fichas de cada modelo.",
        """| Modelo Lüsqtoff | Área visible | Sensores | Tono declarado | Alimentación/cambio de batería | Datos adicionales publicados |
| :--- | ---: | ---: | :--- | :--- | :--- |
| ST-1N | 90 × 35 mm | 2 | DIN 4/11 | Celda solar y batería integrada | Respuesta 1/10.000 s; tono/sensibilidad automáticos |
| ST-1E | 92 × 42 mm | 2 | DIN 4/9–13 | Celda solar y CR2032 reemplazable | Respuesta 1/15.000 s; controles internos/externos según función |
| ST-1B | 98 × 43 mm | 4 | DIN 4/9–13 | Celda solar y CR2450 reemplazable | Respuesta 1/25.000 s; función amolado declarada |

**Dato documentado:** las tres filas reproducen fichas oficiales de los modelos, no una norma universal para máscaras fotosensibles. Todas las velocidades están presentadas como las publica Lüsqtoff; el fabricante no describe aquí una medición realizada por TallerLab.

**Análisis TallerLab:** la matriz ayuda a verificar si un filtro ofrece tono regulable o fijo, cuántos sensores declara, el tamaño visible y si su batería se reemplaza. Más sensores, ventana mayor o respuesta nominal diferente no prueban por sí solos mejor protección ni compatibilidad con una aplicación concreta. Elegí el filtro dentro del rango de sombra requerido por el proceso y corriente, según instrucciones del fabricante y evaluación de seguridad del trabajo.

**Desconocido:** no se verificaron certificados independientes de cada lote, estado de filtros usados, desempeño con sensores parcialmente cubiertos ni protección efectiva ante fallas. Revisá marcado, manual, test del filtro, batería y mica externa; no uses una máscara con daños o conmutación irregular.

## Fuentes consultadas

- **Documentación primaria:** [Lüsqtoff ST-1N](https://lusqtoff.com.ar/ver-producto/ST-1N); [Lüsqtoff ST-1E](https://lusqtoff.com.ar/ver-producto/ST-1E); [Lüsqtoff ST-1B](https://lusqtoff.com.ar/ver-producto/ST-1B); [catálogo oficial de máscaras fotosensibles](https://lusqtoff.com.ar/ver-productos/14-mascaras-fotosensibles).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/soldadoras/", "/soldadoras/mascara-lusqtoff-st-1x/", "datos históricos de máscara Lüsqtoff ST-1X",
    ),
    "paginas/soldadoras/22-soldadora-mig-lusqtoff.md": (
        "Matriz de tres Lüsqtoff MIG/FCAW por proceso, amperaje, ciclo y consumible según fichas/manuales, con advertencia de discontinuidad y variante de kit para evitar homogeneizar la gama.",
        """| Modelo | Proceso/consumible documentado | Salida y ciclo publicados | Diferencia práctica documentada |
| :--- | :--- | :--- | :--- |
| SML120-8D | FLUX, MMA y Lift TIG | FLUX 20–120 A; MMA y Lift TIG 20–100 A; 25% a 25 °C | Tres procesos declarados; masa de máquina 6,6 kg |
| SML130-7 | FCAW con tubular autoprotegido | 25–120 A; 120 A/10% y 50 A/60% a 40 °C | Fabricante la marca discontinuada; torcha MB-15 incluida en página |
| SML150-8D | FLUX y MMA | MIG 20–120 A; MMA 20–100 A; STICK 20% a 100 A | Kit/ficha incluye rollo de 0,45 kg, máscara ST-1X y escuadras |

**Dato documentado:** cada fila procede de la página o manual del código indicado. La etiqueta «MIG» que Lüsqtoff usa para estas unidades no significa que todas requieran o acepten alambre macizo con gas: SML130-7 se describe para alambre tubular autoprotegido; SML120-8D y SML150-8D identifican modo FLUX.

**Análisis TallerLab:** para comparar, identificá el código y el proceso antes de mirar amperaje máximo. Las fichas expresan el ciclo en condiciones distintas (25 °C frente a 40 °C y puntos distintos), así que no conviene ordenarlas por porcentaje sin homogeneizar condiciones. También separá máquina suelta de kit: la ST-1X y el rollo figuran en algunas configuraciones, no necesariamente en todas las publicaciones.

**Desconocido:** no se confirmaron disponibilidad local de SML130-7, garantía actual de equipos discontinuados, diferencias internas entre cada sufijo de kit ni aplicación para espesores específicos. No se probó ninguna unión ni se revisó una muestra de compradores.

## Fuentes consultadas

- **Documentación primaria:** [Lüsqtoff SML120-8D](https://www.lusqtoff.com.ar/ver-producto/SML120-8D); [Lüsqtoff SML130-7](https://lusqtoff.com.ar/ver-producto/SML130-7); [manual SML130-7](https://lusqtoff.com.ar/2023/uploads/Productos/13.%20SOLDADORAS%20INVERTER/SML130-7/MANUAL%20FOR%20SML130-7.pdf); [Lüsqtoff SML150-8D](https://www.lusqtoff.com.ar/ver-producto/SML150-8D); [manual SML150-8](https://lusqtoff.com.ar/2023/uploads/Productos/13.%20SOLDADORAS%20INVERTER/SML150-8/SML150-8.pdf).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/soldadoras/lusqtoff/", "/soldadoras/lusqtoff-sml130-7/", "ficha y manual del modelo discontinuado SML130-7",
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
        f"**Dato documentado:** las especificaciones se atribuyen al fabricante y al modelo/código indicado. Los cálculos se identifican como **Análisis TallerLab**; lo no confirmado queda como **Desconocido**. Esta guía es documental, sin prueba física ni muestra de opiniones.\n\n"
        f"## Cómo investigamos esta guía\n\n"
        f"- Tipo de análisis: documental\n- Prueba física de TallerLab: no\n- Especificaciones contrastadas: sí\n- Opiniones de compradores: no\n- Fuentes primarias: sí\n- Última revisión: 27/09/2026\n\n"
        f"{body}\n\n"
        f"Para seguir comparando: [{sibling_title}]({sibling}).\n\n"
        f"Para conocer el criterio editorial: [Ver metodología de TallerLab](/como-trabajamos/).\n\n"
        f"Para explorar la categoría: [guías relacionadas]({hub}).\n"
    )
    path.write_text(f"---\n{front}\n---\n\n{newbody}", encoding="utf-8")
    print(relpath)
