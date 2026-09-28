"""Decimotercer lote editorial: diez guías de hidrolavadoras."""
from pathlib import Path
import re

ROOT = Path(__file__).parent

PAGES = {
    "paginas/hidrolavadoras/19-hidrolavadora-200-bar.md": (
        "Contraste documental entre presión nominal, máxima y modo térmico en dos hidrolavadoras Gamma/Comet cuyo nombre comercial incluye 200; distingue una máquina trifásica calentadora de una Omega con presión máxima de 150 bar.",
        """| Modelo/código | Tipo y alimentación | Presión de trabajo/nominal publicada | Máxima publicada | Caudal publicado |
| :--- | :--- | ---: | ---: | ---: |
| Comet KM Extra 8.16 16/200 T, C2586AR | Agua caliente, 400 V trifásica | 190 bar nominales hasta 108 °C | 200 bar hasta 108 °C; 32 bar máx. hasta 140 °C | 15 L/min nominales; 16 L/min máx. |
| Gamma Omega Hynox 200, G2028AR | Con caldera; alimentación trifásica | La ficha publica 14,5 MPa | 15 MPa (150 bar) | No localizada en ficha consultada |

**Dato documentado:** Gamma publica para la Comet KM Extra 8.16 presión nominal de 190 bar y máxima de 200 bar con salida hasta 108 °C; al elevar la temperatura máxima de salida a 140 °C, la ficha indica presión máxima de 32 bar. Para Gamma Omega Hynox 200, la ficha lista 14,5 MPa de presión y 15 MPa de presión máxima (150 bar). El «200» de este segundo nombre no corresponde a una presión de 200 bar en la ficha consultada.

**Análisis TallerLab:** el cuadro encuentra dos datos que impiden decidir por la cifra del título: la Comet sí publica 200 bar, pero es trifásica y calentadora; la Omega «200» no llega a 200 bar según su ficha. Presión, temperatura, tensión y caudal describen equipos distintos y no son sustitutos entre sí. Para una instalación residencial, comprobar alimentación eléctrica, caudal disponible y manual del código exacto antes de comparar.

**Desconocido:** no se encontró una ficha primaria que confirme una hidrolavadora portátil a nafta de 200 bar para el mercado argentino entre los modelos revisados. No afirmamos que la presión máxima sea adecuada para una superficie concreta ni que la máquina sea compatible con una instalación doméstica.

## Fuentes consultadas

- **Documentación primaria:** [Gamma/Comet KM Extra 8.16 16/200 T, C2586AR](https://www.gammaherramientas.com.ar/producto/hidrolavadora-comet-km-extra-8-16-16-200-t/); [Gamma Omega Hynox 200, G2028AR](https://www.gammaherramientas.com.ar/producto/hidrolavadora-omega-hynox-200/).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/hidrolavadoras/150-bar/", "/hidrolavadoras/150-bar/", "hidrolavadoras de 150 bar: presión de trabajo",
    ),
    "paginas/hidrolavadoras/07-hidrolavadoras-black-decker.md": (
        "Compara dos códigos BLACK+DECKER de la serie BXPW por potencia, presión de trabajo frente a máxima y caudal máximo según el manual; conserva la variante regional como límite.",
        """| Modelo | Potencia | Presión de trabajo en manual | Presión máxima | Caudal de trabajo / máximo |
| :--- | ---: | ---: | ---: | ---: |
| BXPW1300E | 1.300 W | 67 bar | 100 bar | 5 / 6,5 L/min |
| BXPW1400E | 1.400 W | 74 bar | 110 bar | 5 / 6,5 L/min |

**Dato documentado:** el manual BLACK+DECKER para la familia BXPW distingue presión de trabajo y máxima. Para 1300E informa 67/100 bar y para 1400E 74/110 bar; ambos indican caudal de trabajo de 5 L/min y máximo de 6,5 L/min. La ficha del 1400E en el sitio de BLACK+DECKER España menciona kit de accesorios y garantía de un año en esa región.

**Análisis TallerLab:** entre estos dos códigos, el manual aumenta 100 W de potencia y 10 bar en cada campo de presión, mientras conserva los caudales publicados. Es una lectura de cifras de fabricante, no una medición de limpieza ni una prueba de que las versiones comercializadas en Argentina incluyan el mismo kit o garantía. Verificar sufijo, tensión/frecuencia de placa y contenido de caja de la unidad ofrecida.

**Desconocido:** el manual citado no identifica disponibilidad argentina actual ni equivalencia de accesorios por país. No se compara precio, servicio posventa local ni rendimiento sobre superficies.

## Fuentes consultadas

- **Documentación primaria:** [manual de la familia BLACK+DECKER BXPW1300E–BXPW1600E](https://www.blackanddecker.es/GLOBALBOM/QS/BXPW1400PE/1/Instruction_Manual/EN/BXPW1300E_BXPW1400E_BXPW1500E_BXPW1600E_BX1700E_T1_TR.pdf); [página BLACK+DECKER BXPW1400E](https://www.blackanddecker.es/producto/bxpw1400e/1400w-hidrolimpiadora-de-alta-presion).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/hidrolavadoras/bosch/", "/hidrolavadoras/comparativa-general/", "comparativa de hidrolavadoras: presión y caudal",
    ),
    "paginas/hidrolavadoras/06-hidrolavadoras-bosch.md": (
        "Tabla por código Bosch Easy, Universal y AdvancedAquatak con presión máxima, potencia, caudal, peso y temperatura de entrada; deja explícitos el mercado español de las fichas y los datos máximos.",
        """| Código/modelo Bosch | Potencia | Presión máx. publicada | Caudal máx. | Peso publicado | Temp. máx. de entrada |
| :--- | ---: | ---: | ---: | ---: | ---: |
| EasyAquatak 120, 06008A7901 | 1.500 W | 120 bar | 5,8 L/min | 5,1 kg (máquina) | 40 °C |
| UniversalAquatak 130 | 1.700 W | 130 bar | 7 L/min | 8,4 kg | No indicada en la ficha de familia consultada |
| AdvancedAquatak 150 | 2.200 W | 150 bar | 8,5 L/min | 22,1 kg | No indicada en la ficha de familia consultada |

**Dato documentado:** la página oficial Bosch DIY España publica los datos de la tabla. Para EasyAquatak 120, la página de producto identifica el número de pedido 06008A7901 e incluye manguera de 5 m y boquillas variable, rotativa y de detergente de alta presión. Los valores de presión/caudal del cuadro son máximos publicados; no se rotulan como presión de trabajo.

**Análisis TallerLab:** en esta selección la cifra máxima sube de 120 a 150 bar, pero también cambian caudal, peso y configuración. Las fichas consultadas corresponden al catálogo español: no confirman que códigos, tensión, accesorios, garantía o disponibilidad sean idénticos en Argentina. La comparación sirve para discriminar códigos y campos; no determina cuál limpia mejor una superficie.

**Desconocido:** no se contrastó garantía argentina ni kits locales de UniversalAquatak 130 y AdvancedAquatak 150. No se atribuyen especificaciones a modelos Bosch con el mismo nombre comercial pero distinto número de pedido.

## Fuentes consultadas

- **Documentación primaria:** [Bosch EasyAquatak 120, ficha de producto](https://www.bosch-diy.com/es/es/p/easyaquatak-120-06008a7901); [catálogo oficial Bosch DIY de hidrolimpiadoras](https://www.bosch-diy.com/es/es/herramientas-de-limpieza/limpiadoras-de-alta-presion); [manual Bosch UniversalAquatak 130](https://www.bosch-diy.com/storage/en-sa/universalaquat-135-100043728-original-pdf-404665-en-sa.pdf).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/hidrolavadoras/comparativa-general/", "/hidrolavadoras/einhell/", "Einhell: comparación de modelos por ficha",
    ),
    "paginas/hidrolavadoras/01-hidrolavadoras.md": (
        "Comparativa derivada de cuatro manuales Gamma: separa presión máxima admisible y presión de servicio, y cuantifica los cambios de potencia/caudal entre códigos 127, 130, 150 y 170.",
        """| Modelo y código | Potencia | Máxima admisible publicada | Máxima de servicio publicada | Caudal |
| :--- | ---: | ---: | ---: | ---: |
| Gamma 127 Red Line, G2509AR | 1.400 W | 100 bar | 65 bar | 330 L/h (5,5 L/min) |
| Gamma 130 Red Line, G2513AR | 1.600 W | 130 bar | 90 bar | 360 L/h (6 L/min) |
| Gamma 150 Red Line, G2514AR | 1.800 W | 150 bar | 100 bar | 400 L/h (6,67 L/min) |
| Gamma 170 Elite, G2515AR | No localizada en página consultada | 170 bar | No localizada | 400 L/h (6,67 L/min) |

**Dato documentado:** los manuales de Gamma 127, 130 y 150 usan dos campos distintos: máxima admisible y máxima de servicio. En los códigos citados, el valor de servicio es inferior al máximo admisible. Para Gamma 170, la página de producto publica 170 bar máximos admisibles y 400 L/h, pero no se halló allí el campo de servicio.

**Análisis TallerLab:** del modelo 127 al 150, la potencia publicada aumenta 400 W y el caudal 70 L/h; la presión máxima de servicio pasa de 65 a 100 bar. En el 170, la cifra de 170 bar no alcanza para calcular el valor de servicio. Esta comparación entre documentos no demuestra superioridad ni predice el resultado sobre una tarea. El número del nombre comercial no es una escala común de presión de trabajo.

| Antes de elegir | Dato que debe verificarse |
| :--- | :--- |
| Presión | Si el valor es nominal/de servicio o máximo admisible |
| Caudal | Si es nominal, de trabajo o máximo |
| Conexión | Tensión y frecuencia de la variante exacta |
| Accesorios | Boquilla y longitud de manguera incluidas para ese código |

**Desconocido:** no se compararon precios vigentes, repuestos, niveles sonoros ni pruebas de limpieza bajo una superficie y método iguales.

## Fuentes consultadas

- **Documentación primaria:** [manual Gamma 127, G2509AR](https://www.gammaherramientas.com.ar/web/wp-content/uploads/hidrolavadoras-para-agua-fria_hidrolavadora-127-gamma-elite_G2509AR-102-manual.pdf); [manual Gamma 130, G2513AR](https://www.gammaherramientas.com.ar/web/wp-content/uploads/hidrolavadoras-para-agua-fria_hidrolavadora-130-elite_G2513AR-102-manual.pdf); [manual Gamma 150, G2514AR](https://www.gammaherramientas.com.ar/web/wp-content/uploads/hidrolavadoras-para-agua-fria_hidrolavadora-150-elite_G2514AR-102-manual.pdf); [Gamma 170 Elite, ficha de producto](https://www.gammaherramientas.com.ar/producto/hidrolavadora-170-elite/).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/hidrolavadoras/150-bar/", "/hidrolavadoras/gamma/", "Gamma: códigos y campos de presión",
    ),
    "paginas/hidrolavadoras/13-hidrolavadoras-einhell.md": (
        "Contrasta la compacta TC-HP 90 y la TE-HP 140 por presión máxima, caudal, potencia, manguera y peso; separa presión admisible de presión de trabajo en el modelo TE.",
        """| Modelo | Potencia | Presión máxima admisible | Presión de trabajo máxima | Caudal máx. | Manguera / peso |
| :--- | ---: | ---: | ---: | ---: | :--- |
| TC-HP 90, art. 4140740 | 1.200 W | 90 bar | No publicada en ficha consultada | 372 L/h | 3 m / 4,3 kg |
| TE-HP 140, art. 4140760 | 1.900 W | 140 bar | 100 bar | 420 L/h | 5 m / 10,56 kg |

**Dato documentado:** las hojas de producto Einhell identifican para TC-HP 90 el artículo 4140740, 90 bar máximos, 372 L/h, manguera de 3 m y peso de 4,3 kg. La página oficial de TE-HP 140 distingue 140 bar máximos admisibles de 100 bar de trabajo, publica 420 L/h y 1.900 W, y enumera manguera de 5 m y peso de producto de 10,56 kg.

**Análisis TallerLab:** los códigos comparados difieren en 700 W, 50 bar de máximo admisible, 48 L/h de caudal máximo, 2 m de manguera y 6,26 kg de peso declarado. El manual/ficha consultados no dan una presión de trabajo para TC-HP 90, por eso no se enfrenta ese campo con los 100 bar de TE-HP 140. El caudal y presión máximos no representan necesariamente el mismo punto de funcionamiento.

**Desconocido:** las fichas consultadas son de Einhell Europa y no prueban disponibilidad, kit o garantía argentina. La referencia «Power X-Change» no se aplica a estos dos modelos con cable; esta tabla no cubre una variante a batería.

## Fuentes consultadas

- **Documentación primaria:** [hoja de datos Einhell TC-HP 90](https://www.data.einhell.nl/productsheet/4140740.pdf); [página y datos técnicos Einhell TE-HP 140](https://www.einhell.de/en/p/4140760-te-hp-140/).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/hidrolavadoras/gamma-130/", "/hidrolavadoras/bosch/", "Bosch: comparación por modelo y código",
    ),
    "paginas/hidrolavadoras/14-hidrolavadora-gamma-130.md": (
        "Coteja los manuales Gamma 130 G2513AR y Gamma 150 G2514AR: diferencia presión máxima admisible de servicio y calcula cambios de potencia y caudal entre ambos códigos.",
        """| Modelo/código | Potencia | Presión máxima admisible | Presión máxima de servicio | Caudal |
| :--- | ---: | ---: | ---: | ---: |
| Gamma 130 Red Line, G2513AR | 1.600 W | 130 bar | 90 bar | 360 L/h (6 L/min) |
| Gamma 150 Red Line, G2514AR | 1.800 W | 150 bar | 100 bar | 400 L/h (6,67 L/min) |

**Dato documentado:** los manuales Gamma asignan 130/90 bar (admisible/servicio) al G2513AR y 150/100 bar al G2514AR. También publican 1.600 frente a 1.800 W y 360 frente a 400 L/h. Ambos documentos permiten agua de entrada entre 5 °C y 35 °C e indican manguera de 5 m.

**Análisis TallerLab:** respecto del G2513AR, el G2514AR agrega 200 W, 20 bar de máximo admisible, 10 bar de presión de servicio y 40 L/h de caudal publicado. Las diferencias son cálculos sobre valores del fabricante; no significan que el equipo «150» limpie 20 bar mejor en una condición real. El dato de presión de servicio sigue siendo distinto del límite máximo admisible.

**Desconocido:** no se verificaron con la misma medición consumos, duración, repuestos ni resultados por tipo de superficie. Antes de comprar, confirmar que la placa diga G2513AR y revisar boquillas y kit incluidos.

## Fuentes consultadas

- **Documentación primaria:** [manual Gamma 130, G2513AR](https://www.gammaherramientas.com.ar/web/wp-content/uploads/hidrolavadoras-para-agua-fria_hidrolavadora-130-elite_G2513AR-102-manual.pdf); [manual Gamma 150, G2514AR](https://www.gammaherramientas.com.ar/web/wp-content/uploads/hidrolavadoras-para-agua-fria_hidrolavadora-150-elite_G2514AR-102-manual.pdf); [Gamma 130 Elite, catálogo de producto](https://www.gammaherramientas.com.ar/categoria-producto/hidrolavadoras/).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/hidrolavadoras/gamma/", "/hidrolavadoras/gamma-150/", "Gamma 150: diferencias documentadas con Gamma 130",
    ),
    "paginas/hidrolavadoras/10-hidrolavadora-gamma-150.md": (
        "Explica con el manual G2514AR que los 150 bar son presión máxima admisible y muestra los 100 bar de servicio junto con el caudal y los datos del código Gamma 130 comparado.",
        """| Código | Potencia | Presión máxima admisible | Presión máxima de servicio | Caudal publicado |
| :--- | ---: | ---: | ---: | ---: |
| Gamma 130 Red Line G2513AR | 1.600 W | 130 bar | 90 bar | 360 L/h (6 L/min) |
| Gamma 150 Red Line G2514AR | 1.800 W | 150 bar | 100 bar | 400 L/h (6,67 L/min) |

**Dato documentado:** el manual del Gamma 150 G2514AR define 150 bar como presión máxima admisible y 100 bar como presión máxima de servicio. También informa motor de 1.800 W, caudal de 400 L/h, alimentación 220 VCA–50 Hz, agua de entrada entre 5 °C y 35 °C y manguera de 5 m. La tabla reproduce el manual de Gamma 130 para la fila comparativa.

**Análisis TallerLab:** llamar al equipo «Gamma 150» no equivale a decir que trabaje continuamente a 150 bar: el propio manual separa ese límite de los 100 bar de servicio. Frente al G2513AR, el código G2514AR declara 200 W y 40 L/h más, y 10 bar más de servicio. Son diferencias entre fichas, no evidencia de un resultado de limpieza ni del tiempo de vida.

**Desconocido:** la documentación consultada no determina cuál sirve mejor para un material o una suciedad concreta, ni establece precio final o garantía vigente de una oferta. Verificar código, accesorios y condiciones de venta local.

## Fuentes consultadas

- **Documentación primaria:** [manual Gamma 150 Red Line, G2514AR](https://www.gammaherramientas.com.ar/web/wp-content/uploads/hidrolavadoras-para-agua-fria_hidrolavadora-150-elite_G2514AR-102-manual.pdf); [manual Gamma 130 Red Line, G2513AR](https://www.gammaherramientas.com.ar/web/wp-content/uploads/hidrolavadoras-para-agua-fria_hidrolavadora-130-elite_G2513AR-102-manual.pdf); [Gamma 150 Elite, página oficial](https://www.gammaherramientas.com.ar/producto/hidrolavadora-150-elite/).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/hidrolavadoras/gamma-130/", "/hidrolavadoras/gamma/", "Gamma: comparación de varios códigos",
    ),
    "paginas/hidrolavadoras/04-hidrolavadoras-gamma.md": (
        "Compara cuatro modelos Gamma por código con presión de servicio y máxima admisible cuando el manual da ambas; expone que el rótulo Gamma 170 no permite inferir presión de trabajo.",
        """| Modelo/código | Potencia | Máxima admisible | Máxima de servicio | Caudal publicado |
| :--- | ---: | ---: | ---: | ---: |
| Gamma 127 Red Line G2509AR | 1.400 W | 100 bar | 65 bar | 330 L/h |
| Gamma 130 Red Line G2513AR | 1.600 W | 130 bar | 90 bar | 360 L/h |
| Gamma 150 Red Line G2514AR | 1.800 W | 150 bar | 100 bar | 400 L/h |
| Gamma 170 Elite G2515AR | No localizada | 170 bar | No localizada | 400 L/h |

**Dato documentado:** los manuales de los modelos 127, 130 y 150 distinguen dos presiones: máxima admisible y máxima de servicio. La página oficial del modelo 170 publica 170 bar admisibles y 400 L/h; la ficha consultada no da el valor de servicio. Las cifras corresponden a códigos y documentos específicos, no a todas las hidrolavadoras Gamma.

**Análisis TallerLab:** al recorrer G2509AR, G2513AR y G2514AR suben los valores de potencia (1.400, 1.600 y 1.800 W), caudal (330, 360 y 400 L/h) y presión de servicio (65, 90 y 100 bar). El modelo 170 publica 400 L/h, igual que el 150, pero no aporta presión de servicio en la página revisada. No hay base aquí para deducir que el 170 entregue mayor caudal ni para comparar limpieza real.

**Desconocido:** precios, disponibilidad, garantía por vendedor, repuestos y duración no se verificaron. Tampoco se compararon modelos discontinuados con ofertas activas.

## Fuentes consultadas

- **Documentación primaria:** [manual Gamma 127 G2509AR](https://www.gammaherramientas.com.ar/web/wp-content/uploads/hidrolavadoras-para-agua-fria_hidrolavadora-127-gamma-elite_G2509AR-102-manual.pdf); [manual Gamma 130 G2513AR](https://www.gammaherramientas.com.ar/web/wp-content/uploads/hidrolavadoras-para-agua-fria_hidrolavadora-130-elite_G2513AR-102-manual.pdf); [manual Gamma 150 G2514AR](https://www.gammaherramientas.com.ar/web/wp-content/uploads/hidrolavadoras-para-agua-fria_hidrolavadora-150-elite_G2514AR-102-manual.pdf); [Gamma 170 G2515AR](https://www.gammaherramientas.com.ar/producto/hidrolavadora-170-elite/).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/hidrolavadoras/comparativa-general/", "/hidrolavadoras/gamma-130/", "Gamma 130: datos del manual y del código",
    ),
    "paginas/hidrolavadoras/23-hidrolavadora-para-aire-acondicionado.md": (
        "Matriz de compatibilidad documental que separa equipos cuya ficha declara presión de servicio de instrucciones de limpieza de serpentines; aporta el límite práctico de no dirigir un chorro de alta presión a las aletas.",
        """| Comprobación para limpiar un aire acondicionado | Qué establece la documentación consultada | Decisión documental |
| :--- | :--- | :--- |
| Serpentín exterior con aletas | Carrier indica aplicar agua con detergente usando un rociador de baja presión y seguir instrucciones del fabricante del equipo | No se justifica usar el chorro de una hidrolavadora de consumo sobre las aletas |
| Serpentín de aletas Cu/Al en Daikin UATYA | El manual indica enjuagar con agua potable a baja presión (3–5 barg) y prohíbe chorros de alta presión | Dato específico de esa unidad/familia, no un ajuste universal |
| Presión de una hidrolavadora | En Gamma 150, el manual distingue 100 bar de servicio y 150 bar admisibles | La cifra nominal de la hidrolavadora no define un ajuste seguro para el serpentín |
| Unidad interior y componentes eléctricos | La página Carrier consultada describe limpieza de serpentín exterior; no da procedimiento para la unidad interior | No extrapolar estas instrucciones al interior ni a partes eléctricas |

**Dato documentado:** Carrier recomienda aplicar una solución de detergente suave y agua con un rociador de baja presión para la bobina/serpentín y remite a las indicaciones del fabricante. El manual Daikin UATYA especifica, para serpentines tradicionales con aletas Cu/Al, enjuague con agua potable a 3–5 barg y prohíbe chorros de alta presión. El manual Gamma 150 separa presión máxima admisible de presión de servicio; no presenta esa máquina como herramienta para limpiar aires acondicionados.

**Análisis TallerLab:** una hidrolavadora puede concentrar un chorro cuya presión publicada no está expresada como un ajuste de limpieza HVAC validado. Por eso esta guía no recomienda un modelo, boquilla ni distancia universal para serpentines. La documentación encontrada apoya baja presión y consulta del manual específico; si no se conoce el procedimiento, solicitar limpieza a un técnico de climatización.

**Desconocido:** no se verificó un rango universal de presión para todas las marcas de aire acondicionado, ni compatibilidad de boquillas/adaptadores. Tampoco se inspeccionó un equipo ni se realizaron pruebas. Desconectar la alimentación y seguir el procedimiento del fabricante del aire acondicionado antes de cualquier mantenimiento.

## Fuentes consultadas

- **Fabricante de climatización:** [Carrier, limpieza de serpentines de aire acondicionado](https://www.carrier.com/residential/en/ca/products/air-conditioners/air-conditioner-maintenance/air-conditioner-coil-cleaning/); [manual oficial Daikin UATYA, limpieza exterior de serpentines](https://www.daikin.eu/content/dam/document-library/installation-manuals/ac/rooftop/uatya-bbay1/UATYA_BBAY1_BFC2Y1_BFC3Y1_Installation%20use%20and%20maintenance%20manual_4PEN645202-2%20_English.pdf).
- **Documentación primaria de hidrolavadora:** [manual Gamma 150 G2514AR](https://www.gammaherramientas.com.ar/web/wp-content/uploads/hidrolavadoras-para-agua-fria_hidrolavadora-150-elite_G2514AR-102-manual.pdf).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/hidrolavadoras/150-bar/", "/hidrolavadoras/comparativa-general/", "comparativa general: presión y caudal publicados",
    ),
    "paginas/hidrolavadoras/15-hidrolavadoras-hyundai.md": (
        "Compara tres códigos Hyundai del catálogo del distribuidor oficial británico por presión máxima, caudal y potencia; advierte que son variantes regionales y no confirman la ficha de Hyundai Argentina.",
        """| Modelo Hyundai | Mercado de la fuente | Potencia | Presión máx. de catálogo | Caudal de catálogo |
| :--- | :--- | ---: | ---: | ---: |
| HYW1600E | Reino Unido | 1.600 W | 135 bar | 7,1 L/min |
| HYW2000E | Reino Unido | 2.000 W | 150 bar | 7,5 L/min |
| HYW2400E | Reino Unido | 2.400 W | 180 bar | 8 L/min |

**Dato documentado:** el catálogo de Hyundai Power Products vendido por su distribuidor oficial británico lista HYW1600E, HYW2000E y HYW2400E con las cifras de la tabla. Son presiones máximas promocionadas en la ficha comercial; no se atribuyen como presión nominal/de servicio porque la página de catálogo consultada no da esa separación.

**Análisis TallerLab:** entre las tres fichas británicas, la potencia aumenta en pasos de 400 W y la presión máxima publicada en pasos de 15 bar para los dos primeros códigos y 30 bar entre HYW2000E y HYW2400E; el caudal sube 0,4 y luego 0,5 L/min. Es una comparación de catálogo regional, no una evaluación de limpieza ni prueba de compatibilidad entre países.

**Desconocido:** no se encontró documentación primaria suficiente para confirmar que los códigos HYPW mencionados en publicaciones locales correspondan a estos HYW ni que compartan motor, bomba, tensión, garantía o accesorios. No se afirma disponibilidad de ninguno de estos tres modelos en Argentina.

## Fuentes consultadas

- **Catálogo del distribuidor oficial Hyundai Reino Unido:** [gama de hidrolavadoras eléctricas Hyundai](https://hyundaipowerequipment.co.uk/collections/outdoor-garden-garden-power-tools-pressure-washers-electric-pressure-washers); [catálogo general Hyundai Pressure Washers](https://hyundaipowerequipment.co.uk/collections/pressure-washers).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/hidrolavadoras/comparativa-general/", "/hidrolavadoras/black-decker/", "BLACK+DECKER: presión de servicio y máxima",
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
