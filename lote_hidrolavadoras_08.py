"""Decimocuarto lote editorial: diez guías de hidrolavadoras."""
from pathlib import Path
import re

ROOT = Path(__file__).parent

PAGES = {
    "paginas/hidrolavadoras/02-hidrolavadora-inalambrica.md": (
        "Compara dos limpiadoras a batería con fichas de fabricante: tensión, presión máxima, caudal, capacidad de autosucción y autonomía publicada; distingue una hidrolavadora Bosch de baja presión Lüsqtoff.",
        """| Modelo | Batería/tensión | Presión máxima publicada | Caudal | Autosucción / autonomía |
| :--- | :--- | ---: | ---: | :--- |
| Bosch UniversalAquatak 36V-100, 06008C7002 | 36 V; kit de ficha con 4 Ah | 100 bar | 1,7–3,1 L/min | Succión hasta 0,5 m; 45 min publicados |
| Lüsqtoff LAPL3.6-8BK | 18 V; incluye 2 baterías de 2 Ah | 30 bar | Máx. 3,6 L/min | Toma agua desde recipiente; duración no publicada |

**Dato verificado:** Bosch publica para el kit UniversalAquatak 36V-100 número 06008C7002 batería de 4 Ah, 45 min de autonomía, 100 bar máximos, caudal de 1,7–3,1 L/min y autosucción de hasta 0,5 m. Lüsqtoff publica para LAPL3.6-8BK 18 V, dos baterías de 2 Ah, 30 bar máximos, caudal máximo de 3,6 L/min y 4 kg; la ficha permite tomar agua de un balde o canilla.

**Análisis TallerLab:** el máximo de presión publicado para Bosch supera en 70 bar al del Lüsqtoff, mientras el caudal máximo de este último es 0,5 L/min mayor. Son puntos máximos de fichas distintas y no prueban presión/caudal simultáneos ni capacidad de limpieza comparable. La cifra de 45 min corresponde a la configuración de batería indicada por Bosch; Lüsqtoff no publica un tiempo de funcionamiento contrastable.

**Desconocido:** no hay ensayo común de autonomía, caudal bajo carga, temperatura o tiempo de recarga. Los catálogos consultados no confirman el kit, garantía o disponibilidad actuales de cada código en Argentina; revisar si la oferta incluye batería y cargador exactos.

## Fuentes consultadas

- **Documentación primaria:** [Bosch UniversalAquatak 36V-100, página y especificaciones](https://www.bosch-diy.com/es/es/p/universalaquatak-36v-100-06008c7002); [Lüsqtoff LAPL3.6-8BK](https://www.lusqtoff.com.ar/productos/hidrolavadora-a-bateria-lapl36-8bk).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/hidrolavadoras/karcher-k2/", "/hidrolavadoras/para-autos/", "qué especificaciones revisar al limpiar un auto",
    ),
    "paginas/hidrolavadoras/08-hidrolavadora-karcher-k2.md": (
        "Ficha comparativa de Kärcher K2 Basic Black argentino y K3 Black Edition: código, presión, caudal, peso, manguera y contenido publicado; evita tratar nombres de kits regionales como modelos equivalentes.",
        """| Producto exacto en Kärcher Argentina | Presión que publica la ficha | Caudal | Potencia | Manguera / peso sin accesorios |
| :--- | ---: | ---: | ---: | :--- |
| K 2 Basic Black, 19943220 | 110 bar | 280 L/h | 1.200 W | 3 m / 3,8 kg |
| K 3 Black Edition, 93983550 | 120 bar | 330 L/h | 1.500 W | No indicada en la ficha consultada / 7,3 kg |

**Dato verificado:** Kärcher Argentina lista para K 2 Basic Black (19943220) 110 bar, 280 L/h, 220 V, 1.200 W, peso sin accesorios de 3,8 kg y manguera de 3 m. Para K 3 Black Edition (93983550) publica 120 bar, 330 L/h, 1.500 W y 7,3 kg. La ficha K2 incluye filtro de agua y accesorios indicados en su página; los paquetes Car/Home de otros mercados no se dan por incluidos.

**Análisis TallerLab:** en estos dos SKU locales, la ficha K3 suma 10 bar y 50 L/h sobre la K2, y declara 300 W más. El peso sin accesorios crece 3,5 kg. Esta comparación usa cifras de catálogo; presión y caudal máximos no son por sí solos una prueba de rendimiento sobre una superficie.

**Desconocido:** no se verificaron versiones K2 Car/Home comercializadas hoy en Argentina ni que compartan accesorios con productos extranjeros del mismo nombre. Si una publicación ofrece un kit, comprobar el SKU y la lista de contenido de caja.

## Fuentes consultadas

- **Documentación primaria:** [Kärcher Argentina K 2 Basic Black](https://www.kaercher.com/ar/home-garden/hidrolavadora/k-2-basic-black-19943220.html); [Kärcher Argentina K 3 Black Edition](https://www.kaercher.com/ar/home-garden/hidrolavadora/k-3-black-edition-93983550.html).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/hidrolavadoras/karcher/", "/hidrolavadoras/karcher-k3/", "Kärcher K3: diferencias de ficha frente a K2",
    ),
    "paginas/hidrolavadoras/12-hidrolavadora-karcher-k3.md": (
        "Compara las fichas Kärcher Argentina de K3 Black Edition y K4 Power Control: presión, caudal, tensión, manguera y peso por SKU, y deja visibles campos ausentes.",
        """| Producto Kärcher Argentina | SKU | Presión publicada | Caudal máx. | Manguera / peso sin accesorios |
| :--- | :--- | ---: | ---: | :--- |
| K 3 Black Edition | 93983550 | 120 bar | 330 L/h | Longitud no indicada / 7,3 kg |
| K 4 Power Control | 16034020 | 20–máx. 130 bar | 420 L/h | 8 m / 12,4 kg |

**Dato verificado:** la ficha local del K3 publica 120 bar, 330 L/h y 7,3 kg sin accesorios. Kärcher Argentina informa para el K4 Power Control tensión de 220 V–50 Hz, presión de 20 a 130 bar, caudal máximo de 420 L/h, manguera de 8 m y 12,4 kg sin accesorios; también describe motor de inducción refrigerado por agua y tres niveles de presión.

**Análisis TallerLab:** entre los SKU citados, el K4 declara 10 bar más de presión máxima y 90 L/h más de caudal máximo que el K3, junto con 5,1 kg de peso adicional. No se calculan diferencias de largo de manguera porque el dato del K3 no está en la ficha consultada. La presión mínima de 20 bar que muestra Kärcher para K4 tampoco es una medición de presión nominal sostenida.

**Desconocido:** no se cotejaron versiones K3 Confort/Car/Home disponibles en Argentina ni configuraciones de la aplicación por región. Verificar SKU y accesorios exactos en la publicación.

## Fuentes consultadas

- **Documentación primaria:** [Kärcher Argentina K 3 Black Edition](https://www.kaercher.com/ar/home-garden/hidrolavadora/k-3-black-edition-93983550.html); [Kärcher Argentina K 4 Power Control](https://www.kaercher.com/ar/home-garden/hidrolavadora/k-4-power-control-16034020.html).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/hidrolavadoras/karcher-k2/", "/hidrolavadoras/karcher-k4/", "Kärcher K4: ficha y accesorios publicados",
    ),
    "paginas/hidrolavadoras/17-hidrolavadora-karcher-k4.md": (
        "Compara los SKU Kärcher Argentina K4 Power Control y K5: potencia documental, presión tal como la rotula cada ficha, caudal, manguera y peso.",
        """| Producto Kärcher Argentina | SKU | Presión como la publica la fuente | Caudal | Potencia / manguera / peso sin accesorios |
| :--- | :--- | ---: | ---: | :--- |
| K 4 Power Control | 16034020 | 20–máx. 130 bar | Máx. 420 L/h | No indicada / 8 m / 12,4 kg |
| K 5 | 93982950 | 2.100 psi (≈144,8 bar, conversión) | 420 L/h | 1.900 W / 6 m / 13,3 kg |

**Dato verificado:** la ficha argentina de K4 Power Control lista presión 20–máx. 130 bar, caudal máximo 420 L/h, manguera de 8 m, motor de inducción refrigerado por agua y peso sin accesorios de 12,4 kg. La página de K5 (93982950) lista 2.100 psi, 420 L/h, 1.900 W, manguera de 6 m y peso de 13,3 kg.

**Análisis TallerLab:** 2.100 psi equivalen aproximadamente a 144,8 bar mediante conversión de unidades; Kärcher no rotula ese campo del K5 como presión de servicio en la página consultada. El K4 y K5 declaran igual caudal máximo; el K4 informa una manguera 2 m más larga, mientras el K5 declara 1 kg adicional. La diferencia convertida de presión no permite afirmar una diferencia de limpieza.

**Desconocido:** la página K5 consultada no ofrece en el extracto presión de servicio ni tensión/frecuencia. No se infiere que las versiones K4 Compact/Premium o K5 Power Control/Smart Control tengan los mismos SKU o componentes que los comercializados en otros países.

## Fuentes consultadas

- **Documentación primaria:** [Kärcher Argentina K 4 Power Control](https://www.kaercher.com/ar/home-garden/hidrolavadora/k-4-power-control-16034020.html); [Kärcher Argentina K 5](https://www.kaercher.com/ar/home-garden/hidrolavadora/k-5-93982950.html).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/hidrolavadoras/karcher-k3/", "/hidrolavadoras/karcher-k5/", "Kärcher K5: cifras de la ficha argentina",
    ),
    "paginas/hidrolavadoras/09-hidrolavadora-karcher-k5.md": (
        "Compara las fichas argentinas K5 y K4 Power Control por código, presión en unidad original, caudal, manguera y peso; convierte psi a bar solo como cálculo identificado.",
        """| Producto exacto | SKU | Presión de catálogo | Caudal | Manguera | Peso sin accesorios |
| :--- | :--- | ---: | ---: | ---: | ---: |
| Kärcher K 4 Power Control | 16034020 | 20–máx. 130 bar | Máx. 420 L/h | 8 m | 12,4 kg |
| Kärcher K 5 | 93982950 | 2.100 psi (≈144,8 bar calculados) | 420 L/h | 6 m | 13,3 kg |

**Dato verificado:** Kärcher Argentina identifica el K5 con motor de inducción, cabezal de aluminio, potencia de entrada de 1.900 W y los valores del cuadro. La ficha muestra 2.100 psi, no publica en el bloque consultado la presión de servicio en bar. K4 Power Control informa presión de 20 a 130 bar y el mismo caudal máximo de 420 L/h.

**Análisis TallerLab:** la conversión 2.100 ÷ 14,5038 da aproximadamente 144,8 bar. Con los datos listados, ambas páginas declaran igual caudal máximo; K4 ofrece 2 m más de manguera y K5 pesa 0,9 kg más. Las diferencias son de ficha, no prueban productividad ni duración relativa.

**Desconocido:** la página argentina consultada no identifica el sufijo comercial «Power Control» o «Smart Control» para el SKU K5 analizado. No se completa presión de servicio, garantía o precio final si no aparece en documentación del código o la oferta.

## Fuentes consultadas

- **Documentación primaria:** [Kärcher Argentina K 5, SKU 93982950](https://www.kaercher.com/ar/home-garden/hidrolavadora/k-5-93982950.html); [Kärcher Argentina K 4 Power Control, SKU 16034020](https://www.kaercher.com/ar/home-garden/hidrolavadora/k-4-power-control-16034020.html).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/hidrolavadoras/karcher-k4/", "/hidrolavadoras/karcher/", "guía de familia Kärcher: K2 a K5",
    ),
    "paginas/hidrolavadoras/21-hidrolavadoras-karcher.md": (
        "Tabla de cuatro fichas Kärcher Argentina (K2 Basic Black, K3 Black Edition, K4 Power Control y K5) con SKU, potencia, presión original, caudal y manguera; evita trasladar datos europeos a modelos locales.",
        """| Línea/producto argentino | SKU | Potencia | Presión como la rotula Kärcher | Caudal | Manguera |
| :--- | :--- | ---: | ---: | ---: | ---: |
| K 2 Basic Black | 19943220 | 1.200 W | 110 bar | 280 L/h | 3 m |
| K 3 Black Edition | 93983550 | 1.500 W | 120 bar | 330 L/h | No indicada |
| K 4 Power Control | 16034020 | No publicada | 20–máx. 130 bar | Máx. 420 L/h | 8 m |
| K 5 | 93982950 | 1.900 W | 2.100 psi | 420 L/h | 6 m |

**Dato verificado:** las fichas de Kärcher Argentina identifican estos SKU y sus cifras. En K5, la unidad publicada para presión es psi; no sustituimos el dato original. Las páginas de K2/K3/K4/K5 corresponden a configuraciones distintas y no garantizan que nombres como «Car», «Home», «Compact», «Premium» o «Smart Control» describan el mismo paquete en cada mercado.

**Análisis TallerLab:** entre estos cuatro productos locales aumenta la potencia informada de 1.200 W en K2 a 1.900 W en K5, aunque K4 no publica ese campo en la página revisada. K2–K4 muestran en bar máximo de 110, 120 y 130; K5 figura en psi y puede convertirse aritméticamente a ≈144,8 bar, sin que esa conversión añada una etiqueta de presión de servicio. El caudal máximo pasa de 280 a 420 L/h entre extremos, pero K4 y K5 declaran ambos 420 L/h.

**Desconocido:** no se verificó un precio comparable ni disponibilidad de cada kit en el mismo vendedor/fecha. La lista no es un ranking de limpieza: no hay ensayo común y cambian manguera, accesorios y documentación.

## Fuentes consultadas

- **Documentación primaria:** [Kärcher Argentina K2 Basic Black](https://www.kaercher.com/ar/home-garden/hidrolavadora/k-2-basic-black-19943220.html); [K3 Black Edition](https://www.kaercher.com/ar/home-garden/hidrolavadora/k-3-black-edition-93983550.html); [K4 Power Control](https://www.kaercher.com/ar/home-garden/hidrolavadora/k-4-power-control-16034020.html); [K5](https://www.kaercher.com/ar/home-garden/hidrolavadora/k-5-93982950.html).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/hidrolavadoras/comparativa-general/", "/hidrolavadoras/profesionales/", "criterios documentales para equipos de uso frecuente",
    ),
    "paginas/hidrolavadoras/03-hidrolavadoras-lusqtoff.md": (
        "Compara cuatro códigos Lüsqtoff de catálogo por potencia, presión de trabajo y admisible, caudal de trabajo/máximo y peso; deja los modelos a nafta fuera cuando la fuente primaria no resuelve sus datos.",
        """| Modelo/código | Potencia | Presión de trabajo | Presión máxima permitida | Caudal trabajo / máximo | Peso publicado |
| :--- | ---: | ---: | ---: | ---: | ---: |
| HL-120 | 1.200 W | 70 bar | 105 bar | 5,5 / 6,8 L/min | 5,2 kg |
| HL100-8 | 2.000 W | 100 bar | 150 bar | 6 / 7,5 L/min | 10,5 kg |
| HL110-9 | 2.100 W | 110 bar | 165 bar | 6 / 7,5 L/min | 21 kg |
| HL130-9 | 3.200 W | 150 bar | 225 bar | 7,5 / 9 L/min | 25 kg |

**Dato verificado:** el catálogo Lüsqtoff 2023–2024 publica las especificaciones anteriores y separa presión de trabajo de la máxima permitida. Para HL-120, HL100-8, HL110-9 y HL130-9, la presión máxima permitida es mayor que la de trabajo; no se las toma como una sola cifra. Las medidas se asocian a los códigos del catálogo revisado.

**Análisis TallerLab:** de HL-120 a HL130-9, los datos publicados avanzan de 70 a 150 bar de trabajo y de 5,5 a 7,5 L/min de caudal de trabajo, mientras cambian potencia de 1.200 a 3.200 W y peso de 5,2 a 25 kg. Esa comparación no demuestra que toda la familia tenga bombas, ciclos o repuestos compatibles; tampoco equipara herramientas de distinto peso y uso.

**Desconocido:** no se verificaron precios actuales, disponibilidad de la gama completa, garantía por vendedor ni especificaciones de equipos a nafta. Para esos modelos se necesita la placa/manual del código exacto; no se rellena la tabla con datos de otra marca.

## Fuentes consultadas

- **Documentación primaria:** [catálogo oficial Lüsqtoff 2023–2024, fichas de hidrolavadoras](https://www.lusqtoff.com.ar/files/catalog-lusqtoff-2023-2024.pdf); [manual Lüsqtoff HL110-9](https://lusqtoff.com.ar/2023/uploads/Productos/4.%20HIDROLAVADORAS/HL110-9/MANUAL/Manual%20HL110-9_compressed.pdf); [manual Lüsqtoff HL100-8](https://lusqtoff.com.ar/2023/uploads/Productos/4.%20HIDROLAVADORAS/HL100-8/MANUAL/Manual%20HL100-8-pdf%20curvas_compressed.pdf).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/hidrolavadoras/karcher/", "/hidrolavadoras/niwa/", "Niwa: presión y caudal por código",
    ),
    "paginas/hidrolavadoras/20-hidrolavadoras-niwa.md": (
        "Compara hidrolavadoras Niwa eléctricas axiales y a explosión por modelo/código del importador Grupo Rumbo: presión máxima, caudal, potencia y peso; no mezcla generaciones de catálogo.",
        """| Modelo/código del catálogo Grupo Rumbo | Alimentación/motor | Potencia | Presión máxima | Caudal | Peso |
| :--- | :--- | ---: | ---: | ---: | ---: |
| HDNW-200, 1040200 | Eléctrica axial, carbón | 1.400 W | 110 bar | 5,5 L/min | 5,2 kg |
| HDNW-500, 1040500 | Eléctrica axial, carbón | 1.800 W | 130 bar | 7,0 L/min | 8 kg |
| LNW-65, 1040065 | Nafta, 4T, axial | 6,5 HP | 180 bar | 8,3 L/min | 41,8 kg |
| LNW-130, 1040130 | Nafta, 4T, cigüeñal | 13 HP | 252 bar | 18 L/min | 63 kg |

**Dato verificado:** el catálogo Niwa de Grupo Rumbo publica para HDNW-200 y HDNW-500 las potencias, presiones máximas y caudales de la tabla. Para LNW-65 y LNW-130 publica motores nafteros de 6,5/13 HP, presiones máximas de 180/252 bar, caudales de 8,3/18 L/min y pesos de 41,8/63 kg. Son datos del catálogo del importador; no indican presión de trabajo para todos los modelos.

**Análisis TallerLab:** las versiones a explosión de la tabla pesan aproximadamente 8,0 y 12,1 veces lo publicado para HDNW-200 (41,8/5,2 y 63/5,2); también declaran caudales superiores, con otra fuente de energía, construcción y escala. Es una división de cifras nominales del catálogo, no una evaluación de movilidad o productividad. No se infiere equivalencia entre los 252 bar máximos de LNW-130 y presión sostenida de servicio.

**Desconocido:** no se comprobó que los códigos de este catálogo 2022 continúen a la venta ni que sus kits y repuestos sean intercambiables con generaciones nuevas. La página de la familia no sustituye el manual del ejemplar ofertado.

## Fuentes consultadas

- **Documentación del importador oficial Niwa:** [Catálogo Niwa/Grupo Rumbo, edición 2022](https://www.rumbosrl.com.ar/uploads/resources/Niwa-catalogo-4000_ED202208.pdf); [ficha de Grupo Rumbo HDNW-500, código 1040550](https://www.rumbosrl.com.ar/productos/productos-de-limpieza/hidrolavadoras-y-accesorios/hidrolavadoras-electricas/hidrolavadora-electrica-niwa-hdnw-500-1040550).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/hidrolavadoras/lusqtoff/", "/hidrolavadoras/profesionales/", "hidrolavadoras profesionales: magnitudes y conexión",
    ),
    "paginas/hidrolavadoras/22-hidrolavadoras-para-autos.md": (
        "Tabla de dos equipos recomendados/documentados para limpieza vehicular que compara presión máxima, caudal, manguera, boquillas y accesorios de detergente por SKU; no presenta esas cifras como prueba de seguridad sobre pintura.",
        """| Modelo/código | Presión publicada | Caudal publicado | Manguera | Elementos de fábrica citados |
| :--- | ---: | ---: | ---: | :--- |
| Kärcher K 2 Basic Black, 19943220 | 110 bar | 280 L/h | 3 m | Filtro de agua; boquillas y pistola detalladas en ficha |
| Niwa HDNW-500, 1040550 | Máx. 130 bar; promedio 100 bar en ficha del importador | Nominal 360 L/h; máximo 420 L/h | 5 m | Pistola con boquilla spray y botella de detergente |

**Dato verificado:** Kärcher enumera la K2 Basic Black con uso ocasional, manguera de alta presión de 3 m, 110 bar y 280 L/h. Grupo Rumbo publica para Niwa HDNW-500 los códigos y valores de la tabla, con caudal máximo y nominal distinguidos y presión «de caudal promedio» de 100 bar. Los kits dependen del producto exacto y pueden variar por país.

**Análisis TallerLab:** la HDNW-500 declara 2 m más de manguera que la K2 del SKU citado, pero también mayor peso (8 kg frente a 3,8 kg sin accesorios de Kärcher) y una fuente llama explícitamente «máximo» a parte de sus cifras. La tabla ayuda a comprobar alcance físico y accesorios publicados para una tarea en vehículo; no prueba que el chorro de cualquier boquilla sea adecuado para una pintura, calco, burlete o superficie dañada.

**Desconocido:** no hay pruebas comparables de remoción, tiempo de lavado, consumo real ni daño potencial sobre acabados. Consultar el manual del vehículo y de la hidrolavadora y las condiciones de la boquilla antes de usarla; no se prescribe presión/distancia universal. No se afirma que una aspiradora interior incluida en un combo comparta caudal o servicio con la hidrolavadora.

## Fuentes consultadas

- **Documentación primaria y del importador:** [Kärcher Argentina K2 Basic Black](https://www.kaercher.com/ar/home-garden/hidrolavadora/k-2-basic-black-19943220.html); [Grupo Rumbo Niwa HDNW-500](https://www.rumbosrl.com.ar/productos/productos-de-limpieza/hidrolavadoras-y-accesorios/hidrolavadoras-electricas/hidrolavadora-electrica-niwa-hdnw-500-1040550).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/hidrolavadoras/inalambricas/", "/hidrolavadoras/karcher-k2/", "Kärcher K2: SKU y accesorios locales",
    ),
    "paginas/hidrolavadoras/11-hidrolavadora-profesional.md": (
        "Matriz de dos modelos profesionales Comet comercializados por Gamma que separa presión nominal/máxima, caudal y requisitos eléctricos; explicita las diferencias de temperatura de salida y fases.",
        """| Modelo Gamma/Comet | Alimentación y potencia | Presión nominal | Presión máxima | Caudal nominal / máximo |
| :--- | :--- | ---: | ---: | ---: |
| KP Pro Classic 3.10 10/150 M, C2585AR | 230 V monofásica; 2,2 kW | 140 bar | 150 bar | 9 / 10 L/min |
| KM Extra 8.16 16/200 T, C2586AR | 400 V trifásica; 6,5 kW | 190 bar a salida ≤108 °C | 200 bar a ≤108 °C; 32 bar máx. a ≤140 °C | 15 / 16 L/min |

**Dato verificado:** Gamma publica para KP Pro Classic 3.10 10/150 M tensión monofásica de 230 V, presión nominal de 140 bar, máxima de 150 bar, caudal nominal de 9 L/min y máximo de 10 L/min. La KM Extra 8.16 16/200 T requiere 400 V trifásicos y 6,5 kW; su página detalla presión nominal/máxima y caudales diferenciados en la tabla. La máxima presión cambia con la temperatura de salida especificada por el fabricante.

**Análisis TallerLab:** la KM declara 50 bar más de presión nominal y 6 L/min más de caudal nominal que la KP, pero exige suministro trifásico y una demanda eléctrica publicada mayor. La KP es monofásica, aunque sus 2,2 kW y 16 A de fusible también requieren revisar la instalación. No se debe seleccionar por presión sola: la fuente disponible, temperatura, caudal de alimentación, ciclo requerido y accesorios son parámetros distintos.

**Desconocido:** las páginas consultadas no definen aquí el régimen de trabajo continuo para todas las condiciones ni dimensionan una instalación eléctrica existente. Confirmar placa, manual completo, protección y montaje con un electricista/técnico habilitado; no realizar una conexión trifásica a partir de esta tabla.

## Fuentes consultadas

- **Documentación primaria/importador:** [Gamma/Comet KP Pro Classic 3.10 10/150 M, C2585AR](https://www.gammaherramientas.com.ar/producto/hidrolavadora-comet-kp-pro-classic-3-10-10-150-m/); [Gamma/Comet KM Extra 8.16 16/200 T, C2586AR](https://www.gammaherramientas.com.ar/producto/hidrolavadora-comet-km-extra-8-16-16-200-t/).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/hidrolavadoras/karcher/", "/hidrolavadoras/200-bar/", "hidrolavadoras de 200 bar: condiciones de ficha",
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
        f"**Dato verificado:** las cifras se atribuyen al documento indicado en cada tabla. Los cálculos se identifican como **Análisis TallerLab**; lo no confirmado queda como **Desconocido**. Esta guía es documental y no incluye prueba física.\n\n"
        f"## Cómo investigamos esta guía\n\n"
        f"- Tipo de análisis: documental\n- Prueba física de TallerLab: no\n- Especificaciones contrastadas: sí\n- Opiniones de compradores: no\n- Fuentes primarias: sí\n- Última revisión: 27/09/2026\n\n"
        f"{body}\n\n"
        f"Para seguir comparando: [{sibling_title}]({sibling}).\n\n"
        f"Para conocer el criterio editorial: [Ver metodología de TallerLab](/como-trabajamos/).\n\n"
        f"Para explorar la categoría: [guías relacionadas]({hub}).\n"
    )
    path.write_text(f"---\n{front}\n---\n\n{newbody}", encoding="utf-8")
    print(relpath)
