"""Duodécimo lote editorial: nueve guías de generadores y una de hidrolavadoras."""
from pathlib import Path
import re

ROOT = Path(__file__).parent

PAGES = {
    "paginas/generadores/06-generadores-inverter.md": (
        "Matriz que separa potencia nominal/máxima y ruido documentado en generadores inverter Honda y Lüsqtoff; evita equiparar tecnología, potencia y silencio.",
        """| Modelo | Tecnología que declara la fuente | Potencia nominal publicada | Potencia máxima publicada | Ruido declarado |
| :--- | :--- | ---: | ---: | :--- |
| Honda EU22i | Inverter | 1,8 kVA | 2,2 kVA | 57 dB(A) a 7 m y plena carga, según Honda |
| Lüsqtoff LGI3.5-8 | Inverter | No localizada en la ficha consultada | 3,5 kVA | 68 dB, sin condiciones de ensayo en la ficha consultada |
| Lüsqtoff LGI3.8-8 | Inverter | 3,5 kW | 3,8 kW | 75 dB a 7 m, según la ficha Lüsqtoff |
| Lüsqtoff LG3500EXI | Inverter | No publicada en la ficha consultada | 3.500 W | La ficha no aporta condición de medición comparable |

**Dato verificado:** Honda identifica al EU22i como inverter y publica 1,8 kVA nominales, 2,2 kVA máximos y 57 dB(A) a 7 m a plena carga. Lüsqtoff identifica como inverter los modelos de la tabla y publica sus cifras en kVA o kW según modelo. No convertimos kVA a kW sin factor de potencia.

**Análisis TallerLab:** la tabla muestra que “inverter” no es una medida de potencia: EU22i, LGI3.5-8 y LGI3.8-8 publican magnitudes nominales/máximas diferentes, mientras que la ficha de LG3500EXI solo da el máximo. Tampoco se puede ordenar ruido con estos números: la ficha Honda da distancia y carga; otras fuentes omiten una o ambas condiciones. El tipo de regulación por sí solo no certifica compatibilidad con cualquier carga sensible.

**Desconocido:** no se compararon distorsión armónica total (THD), consumo a igual carga ni ruido bajo un protocolo común. Para un equipo electrónico, revisar sus límites de tensión/frecuencia y la ficha o certificación del generador exacto; no inferir THD numérica de la palabra inverter.

## Fuentes consultadas

- **Documentación primaria:** [Honda EU22i](https://pf.honda.com.ar/producto/EU22i); [Lüsqtoff LGI3.5-8](https://lusqtoff.com.ar/productos/generador-inverter-35-kva-lgi35-8); [Lüsqtoff LGI3.8-8](https://lusqtoff.com.ar/ver-producto/LGI3.8-8); [Lüsqtoff LG3500EXI](https://www.lusqtoff.com.ar/ver-producto/LG3500EXI).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/generadores/", "/generadores/portatiles/", "generadores portátiles: comparar formato y datos",
    ),
    "paginas/generadores/11-generadores-lusqtoff.md": (
        "Compara cuatro modelos Lüsqtoff exactos por potencia y autonomía publicada; deja explícita la falta de potencia nominal del LG3500EXI y la diferencia ficha/manual del LGI3.8-8.",
        """| Modelo | Tecnología / combustible | Potencia nominal publicada | Máxima publicada | Tanque / autonomía publicada |
| :--- | :--- | ---: | ---: | :--- |
| LG3500EX | Convencional, nafta | 2.450 W | 3.500 W | 15 L / aprox. 6–8 h, según consumo |
| LG3500EXI | Inverter, nafta | No publicada en ficha consultada | 3.500 W | 15 L / 11 h, sin carga de ensayo indicada allí |
| LGI2.5-8 | Inverter, nafta | 2,2 kW | 2,5 kW | 6 L; no se usa autonomía comparativa sin condición común |
| LGI3.8-8 | Inverter, nafta | Página: 3,5 kW | Página: 3,8 kW | 8 L; catálogo/manual da 27 kg frente a 28 kg en página |

**Dato verificado:** la ficha Lüsqtoff de LG3500EX separa 2.450 W nominales de 3.500 W máximos; la de EXI informa 3.500 W máximos, pero no potencia nominal en el bloque consultado. Para LGI2.5-8 el catálogo de la marca informa 2,2/2,5 kW. En LGI3.8-8, página, catálogo/manual consultados discrepan en el peso (28/27 kg); se conserva el valor por documento, sin promediar.

**Análisis TallerLab:** que LG3500EX y LG3500EXI compartan un máximo impreso de 3.500 W no demuestra igual potencia de servicio; la ficha del EXI consultada no resuelve su nominal. Los valores de autonomía tampoco son comparables sin la carga usada para medirlos. Para elegir, cotejar código de placa, potencia nominal, tensión, salida y manual de la variante vendida.

**Desconocido:** no se contrastó una muestra de precios/garantías/repuestos ni la distorsión THD de los equipos. No asignamos a toda la marca prestaciones de un modelo específico.

## Fuentes consultadas

- **Documentación primaria:** [Lüsqtoff LG3500EX](https://lusqtoff.com.ar/ver-producto/LG3500EX); [Lüsqtoff LG3500EXI](https://www.lusqtoff.com.ar/ver-producto/LG3500EXI); [catálogo Lüsqtoff 2024–2025, LGI2.5-8 y LGI3.8-8](https://www.lusqtoff.com.ar/2023/uploads/Catalogos/CAT%C3%81LOGO%20LQ%202024-2025%20-%20web%20%281%29.pdf); [Lüsqtoff LGI3.8-8](https://lusqtoff.com.ar/ver-producto/LGI3.8-8); [manual LGI3.8-8](https://www.lusqtoff.com.ar/2023/uploads/Productos/NUEVOS/GRUPOS_ELECTROGENOS/LGI38-8/LGI3-8-8.pdf).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/generadores/", "/generadores/niwa/", "generadores Niwa por código",
    ),
    "paginas/generadores/13-grupos-electrogenos-monofasicos.md": (
        "Matriz de tensión/fase para distinguir tres salidas monofásicas de 220 V de una máquina trifásica 380 V, con potencia y amperaje del código documentado.",
        """| Modelo documentado | Salida y fase | Potencia publicada | Corriente publicada | Implicación verificable |
| :--- | :--- | ---: | ---: | :--- |
| Honda EG6500CXS | 220 V CA, 50 Hz, monofásico | 5,0 kVA nominal / 5,5 kVA máxima | No en ficha citada | La ficha lo identifica como monofásico |
| Gamma GE3481AR / 6000V | 220 V CA, monofásico | 5,5 kW / 6 kW máxima | No en ficha consultada | La ficha aclara salida de 220 V CA y 12 V CC |
| Lüsqtoff LG7500EXT | 380 V CA, 50 Hz, trifásico | 6.500 W máximos | No publicada en la ficha consultada | El código es trifásico, aunque la familia también tenga otros modelos |

**Dato verificado:** Honda y Gamma publican los dos primeros modelos como equipos monofásicos de 220 V; Lüsqtoff identifica LG7500EXT como trifásico de 380 V–50 Hz con máximo de 6.500 W. No se infiere compatibilidad con una instalación solo por potencia total.

**Análisis TallerLab:** una carga que necesita 220 V monofásicos requiere verificar una salida y protección adecuadas; un generador trifásico distribuye su capacidad entre fases y la corriente/potencia disponible por fase debe comprobarse en su placa y manual. No convertimos potencia aparente kVA de Honda a potencia activa kW de Gamma sin el factor de potencia.

| Antes de comparar | Dato de placa o instalación que falta |
| :--- | :--- |
| Tensión requerida | 220 V o 380 V y esquema de conexión |
| Número de fases de la carga | Monofásica o trifásica |
| Potencia | W/kW o VA/kVA y factor de potencia |
| Corriente de arranque | Valor del equipo conectado, si aplica |

**Desconocido:** las fichas seleccionadas no indican potencia disponible por fase para todo tipo de desbalanceo. No afirmamos que un trifásico pueda alimentar cualquier combinación de cargas monofásicas.

## Fuentes consultadas

- **Documentación primaria:** [Honda EG6500CXS](https://pf.honda.com.ar/producto/EG6500CXS); [Gamma GE3481AR](https://www.gammaherramientas.com.ar/producto/grupo-electrogeno-6000v/); [Lüsqtoff LG7500EXT](https://www.lusqtoff.com.ar/ver-producto/LG7500EXT); [manual Gamma de GE3480AR/GE3481AR](https://www.gammaherramientas.com.ar/web/wp-content/uploads/2023/11/MANUAL-GE-OK_compressed.pdf).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/generadores/", "/generadores/trifasicos/", "generadores trifásicos: fases y tensión",
    ),
    "paginas/generadores/18-generadores-niwa.md": (
        "Comparación de tres grupos Niwa respaldada por documentación del importador: potencia nominal/máxima, tanque y peso por código GNW.",
        """| Modelo Niwa | Configuración publicada | Potencia promedio/nominal publicada | Máxima | Tanque / peso bruto |
| :--- | :--- | ---: | ---: | :--- |
| GNW-28-E | Monofásico, arranque eléctrico | 2,5 kVA | 2,8 kVA | 16 L / 43 kg, catálogo consultado |
| GNW-55-ER | Monofásico, eléctrico, ruedas | 5 kVA | 5,5 kVA | 25 L / 93 kg en catálogo; otras fichas dan 92 kg netos |
| GNW-70-ER | Monofásico, eléctrico, ruedas | 6 kVA | 7 kVA | 25 L / 95 kg bruto |

**Dato verificado:** el catálogo Niwa distribuido por Grupo Rumbo publica para GNW-55-ER 5 kVA promedio y 5,5 kVA máximo; para GNW-70-ER, 6 kVA promedio y 7 kVA máximo. La ficha del importador identifica motores de 13 y 16 HP, 220 V–50 Hz, 25 L y 8 h de autonomía publicada para ambos. Los pesos cambian de rótulo/documento: 93 kg bruto en catálogo frente a 92 kg netos en otra ficha GNW-55-ER.

**Análisis TallerLab:** entre GNW-55-ER y GNW-70-ER la potencia promedio publicada aumenta 1 kVA (20 % sobre 5 kVA) y la máxima aumenta 1,5 kVA (27,3 % sobre 5,5 kVA); el tanque se mantiene en 25 L. Esto compara campos del catálogo y no demuestra autonomía equivalente bajo la misma carga. Para peso, se mantiene el rótulo de cada fuente y no se calcula diferencia bruto-neto.

**Desconocido:** la ficha de GNW-28-E revisada no contiene una condición de carga para las 9–10 h que aparecen en el catálogo; no comparamos esa autonomía con la de modelos mayores. Precio, garantía regional y disponibilidad deben confirmarse por código.

## Fuentes consultadas

- **Documentación del importador y catálogo de línea:** [Grupo Rumbo, ficha GNW-70-ER](https://www.rumbosrl.com.ar/printficha.php?product_id=128); [catálogo Niwa de Grupo Rumbo](https://www.comercialyenergia.com.ar/wp-content/uploads/2020/12/niwa.pdf); [manual Niwa para GNW-28/E, GNW-55/E/ER y GNW-70ER/73ER](https://shesarg.com/uploads/products/pdfs/manuales/1025552_om.pdf).
- **Información comercial para contraste de peso:** [GNW-55-ER, ficha de distribuidor con peso bruto](https://elranquel.com.ar/productos/productos-de-fuerza/generacin/grupos-electrogenos-nafteros/grupo-electrogeno-naftero-niwa-gnw-55-er-1025552).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/generadores/", "/generadores/lusqtoff/", "modelos Lüsqtoff por código",
    ),
    "paginas/generadores/05-generador-para-casa.md": (
        "Hoja de carga de vivienda con datos de arranque de motor tomados de manual Lüsqtoff y modelos de salida monofásica; muestra qué valores debe aportar el usuario.",
        """### Plantilla documental para sumar cargas de una vivienda

| Carga identificada | Potencia de marcha según placa/manual | Corriente o potencia de arranque | Tensión/fase | Fuente que debe consultarse |
| :--- | :--- | :--- | :--- | :--- |
| Iluminación u otra carga resistiva | Dato del aparato | Puede coincidir con marcha solo si placa/manual lo indica | 220 V, si corresponde | Etiqueta del artefacto |
| Heladera o carga con motor | Dato de placa/manual | Consultar pico de arranque; no reemplazarlo por regla universal | Tensión/fase del artefacto | Manual del motor/artefacto |
| Bomba o aire acondicionado | Dato de placa/manual | Dato de arranque del fabricante o instalador | Tensión/fase del equipo | Manual y placa exactos |

**Dato verificado:** el manual Lüsqtoff LG2500 incluye un cuadro de ejemplo donde una heladera de 150 W aparece con 450–750 VA de arranque y 300 VA en trabajo; una lámpara fluorescente de 40 W aparece con 80 VA de arranque y 60 VA en trabajo. El propio manual presenta estas cifras como estimadas. No son valores universales de todas las heladeras o lámparas.

### Contraste con generadores documentados

| Modelo | Salida | Potencia nominal publicada | Potencia máxima publicada |
| :--- | :--- | ---: | ---: |
| Honda EG6500CXS | 220 V monofásica | 5,0 kVA | 5,5 kVA |
| Gamma GE3481AR | 220 V monofásica | 5,5 kW | 6 kW |

**Análisis TallerLab:** para armar un escenario de emergencia hay que completar las cuatro columnas de la plantilla con los aparatos reales, sumar las cargas de marcha en unidades compatibles y luego cotejar sus picos con el manual del generador. La tabla Lüsqtoff funciona como advertencia de que un motor puede pedir más potencia aparente al arrancar; no alcanza para prometer que un grupo concreto sostendrá una combinación de cargas domésticas.

**Desconocido:** sin inventario, placa, picos de arranque, factor de potencia y tensión de cada vivienda, no existe una potencia única que se pueda recomendar para “una casa”. Esta guía no valida una conexión de generador a la instalación fija; el proyecto de transferencia y protecciones requiere técnico calificado según normativa local.

## Fuentes consultadas

- **Documentación primaria:** [manual Lüsqtoff LG2500, tabla ilustrativa de cargas](https://lusqtoff.com.ar/2023/uploads/Productos/9.%20GRUPOS%20ELECTR%C3%93GENOS/LG2500/LG2500.pdf); [Honda EG6500CXS](https://pf.honda.com.ar/producto/EG6500CXS); [Gamma GE3481AR](https://www.gammaherramientas.com.ar/producto/grupo-electrogeno-6000v/).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/generadores/", "/generadores/monofasicos/", "generadores monofásicos: fase y tensión",
    ),
    "paginas/generadores/15-generadores-portatiles.md": (
        "Tabla que compara dos generadores Honda portátiles: cuantifica peso y potencia máxima publicados, pero deja visibles sus diferencias de tanque y autonomía.",
        """| Modelo | Potencia nominal / máxima | Peso en seco | Combustible / tanque | Autonomía publicada |
| :--- | ---: | ---: | :--- | :--- |
| Honda EU22i | 1,8 / 2,2 kVA | 21 kg | Nafta, 3,6 L | 8,1 h en ECO-THROTTLE; ficha también indica 3,2 h en otra condición |
| Honda EU30is | 2,8 / 3,0 kVA | 59 kg | Nafta, 13 L | 20 h en ECO-THROTTLE; 7,1 h en otra condición de la ficha |

**Dato verificado:** ambas fichas Honda identifican modelos portátiles monofásicos, con salida de 220 V y tecnología inverter. EU30is declara 0,8 kVA más de máximo que EU22i, mientras pesa 38 kg más; sus tanques son 13 L y 3,6 L, respectivamente. La marca publica dos valores de uso continuo según condición en cada ficha.

**Análisis TallerLab:** esta pareja muestra una compensación documental entre capacidad máxima y masa: la diferencia de peso equivale a 181 % del peso seco del EU22i, mientras el máximo sube 36,4 % respecto de 2,2 kVA. Es una división de datos de ficha, no una medida de facilidad real de traslado o rendimiento por kilogramo. Autonomías y tanque no se ordenan sin una carga común.

**Desconocido:** no se estimó una autonomía para camping, motorhome o uso móvil sin conocer cargas, picos, ventilación, combustible disponible y condiciones de operación. Confirmar accesorios, ruido, normativa del sitio de uso y garantía de la unidad ofrecida.

## Fuentes consultadas

- **Documentación primaria:** [Honda EU22i](https://pf.honda.com.ar/producto/EU22i); [ficha Honda EU22i](https://pf.honda.com.ar/descargar/ficha_tecnica/EU22i.pdf); [Honda EU30is](https://pf.honda.com.ar/producto/EU30is); [catálogo oficial de generadores Honda Argentina](https://pf.honda.com.ar/categoria-producto/generadores).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/generadores/", "/generadores/inverter/", "generadores inverter: tecnología y límites",
    ),
    "paginas/generadores/02-precios-de-grupos-electrogenos.md": (
        "Captura fechada de cuatro precios PVP publicados por Lüsqtoff para comparar cómo documentar precios por modelo, sin mezclarlos con cuotas o inferir valor por watt.",
        """| Modelo que publica Lüsqtoff | Tecnología / combustible | Potencia visible en esa ficha | PVP visto el 27/09/2026 | Límite para comparar |
| :--- | :--- | :--- | ---: | :--- |
| LG3500EX | Convencional, nafta | 2.450 W nominal / 3.500 W máximo | $875.199 | La ficha publica ambos regímenes |
| LGI3.8-8 | Inverter, nafta | 3,5 kW nominal / 3,8 kW máximo | $1.049.699 | Otro tanque, formato y documentación |
| LGI3.5-8 | Inverter, nafta | 3,5 kVA máximo; nominal no publicado en la página consultada | $1.339.499 | kVA no se convierte a kW sin factor de potencia |
| LG3500EXI | Inverter, nafta | 3.500 W máximo; nominal no publicado en la página consultada | $1.968.699 | La ficha no detalla condición del precio ni nominal |

**Dato verificado:** estos importes aparecen como PVP en las páginas oficiales de Lüsqtoff consultadas durante la revisión indicada. Son una captura de precios publicados para códigos concretos, no una cotización, precio de mercado promedio ni garantía de disponibilidad.

**Análisis TallerLab:** aunque LG3500EX y LG3500EXI muestran 3.500 W máximos, sus fichas difieren en tecnología y no aportan el mismo dato de potencia nominal. Por eso no dividimos precio por watts máximos ni lo presentamos como una comparación de costo por capacidad útil. Las otras dos filas muestran tecnologías/capacidades diferentes y tampoco forman una comparación equivalente.

### Cómo actualizar esta comparación

Al recotizar, registrar fecha y hora, vendedor, código exacto, precio de lista, condición por transferencia, cuotas, envío, stock y garantía. Comparar primero potencia nominal bajo la misma unidad y combustible; separar después instalación, tablero ATS, batería, accesorios y servicio. No combinar PVP del fabricante con precio financiado de un distribuidor como si fueran el mismo tipo de importe.

**Desconocido:** no se muestreó el mercado completo ni se verificó precio final con envío, cuotas, descuento bancario o stock local. Los importes pueden cambiar y deben confirmarse antes de comprar.

## Fuentes consultadas

- **Precios oficiales publicados por fabricante:** [Lüsqtoff LG3500EX](https://lusqtoff.com.ar/ver-producto/LG3500EX); [Lüsqtoff LGI3.8-8](https://lusqtoff.com.ar/ver-producto/LGI3.8-8); [Lüsqtoff LGI3.5-8](https://lusqtoff.com.ar/productos/generador-inverter-35-kva-lgi35-8); [Lüsqtoff LG3500EXI](https://www.lusqtoff.com.ar/ver-producto/LG3500EXI).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/generadores/", "/generadores/lusqtoff/", "generadores Lüsqtoff por código",
    ),
    "paginas/generadores/16-generadores-silenciosos.md": (
        "Clasifica tres lecturas de ruido de generadores según distancia y carga especificadas; evita ordenar valores dB(A) que no comparten condiciones documentadas.",
        """| Modelo | Ruido publicado | Distancia indicada | Carga indicada | Comparabilidad |
| :--- | ---: | ---: | :--- | :--- |
| Honda EU22i | 57 dB(A) | 7 m | Plena carga | Condición y distancia explícitas en la página Honda |
| Honda EU30is | 58 dB(A) | La ficha consultada no la identifica en el campo de ruido | No indicada junto al valor | No se declara comparable con EU22i |
| Gamma GE3480AR / 3000V | 70 dB en manual de serie V | No localizada | No localizada | Medición sin geometría/carga publicadas en el fragmento |
| Lüsqtoff LGI3.8-8 | 75 dB a 7 m | 7 m | No localizada | La distancia aparece, carga no |

**Dato verificado:** Honda especifica para EU22i 57 dB(A) a 7 m a plena carga. Gamma registra 70 dB para GE3480AR en su manual de serie V, pero el extracto no indica distancia o carga. Lüsqtoff publica 75 dB a 7 m para LGI3.8-8. Conservamos dB/dB(A) tal como aparecen en cada fuente.

**Análisis TallerLab:** el dato de EU22i tiene más contexto de medición que las otras filas; una resta directa de 57 frente a 70 o 75 dB no produciría una comparación controlada porque faltan condiciones comunes. Los decibeles son una magnitud logarítmica: tampoco interpretamos una diferencia numérica como porcentaje de “ruido”. La etiqueta comercial “silencioso” no reemplaza el protocolo y la posición de medición.

**Desconocido:** no se obtuvo una serie de mediciones de estos modelos en vacío, media carga y plena carga con el mismo sonómetro, distancia y entorno. Esta guía no evalúa molestia acústica en un domicilio ni normativa municipal.

## Fuentes consultadas

- **Documentación primaria:** [Honda EU22i](https://pf.honda.com.ar/producto/EU22i); [Honda EU30is](https://pf.honda.com.ar/producto/EU30is); [manual Gamma GE3480AR/GE3481AR](https://www.gammaherramientas.com.ar/web/wp-content/uploads/2023/11/MANUAL-GE-OK_compressed.pdf); [Lüsqtoff LGI3.8-8](https://lusqtoff.com.ar/ver-producto/LGI3.8-8).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/generadores/", "/generadores/inverter/", "generadores inverter y sus datos de ruido",
    ),
    "paginas/generadores/07-generadores-trifasicos.md": (
        "Matriz de potencia, tensión y fase de tres generadores trifásicos de combustibles distintos; separa kW de kVA y muestra la salida por código.",
        """| Modelo | Combustible | Tensión/fases publicadas | Potencia publicada | Dato adicional |
| :--- | :--- | :--- | :--- | :--- |
| Lüsqtoff LG7500EXT | Nafta | 380 V, 50 Hz, trifásico | 6.500 W máximo | 15 HP; arranque eléctrico; tanque 25 L |
| Honda ET12000 | Nafta | 380 V y 220 V; trifásico y monofásico | 11 kVA máximo | La ficha no se usa como equivalente directo de 6.500 W |
| Gamma GE3494AR | Gas natural / GLP | 380 V, tres fases | 17 kW nominal / 18,7 kW máximo con GLP; 16/17,6 kW con GN | Consumo cambia por combustible y carga |

**Dato verificado:** las páginas de fabricante identifican los códigos anteriores como salidas trifásicas. Gamma GE3494AR distingue expresamente potencia nominal y máxima según gas: 17/18,7 kW con GLP y 16/17,6 kW con GN. Honda ET12000 publica 11 kVA máximo, no kW; Lüsqtoff LG7500EXT especifica 6.500 W máximo a 380 V.

**Análisis TallerLab:** este cuadro evita comparar solo el nombre comercial: las unidades y combustibles cambian, y la potencia trifásica total debe leerse junto con tensión, conexión y corriente por fase que indique la placa. Un tablero con cargas monofásicas también requiere conocer el desbalance permitido; la potencia total publicada no responde sola a esa pregunta.

**Desconocido:** no se igualan kVA de Honda a kW de Gamma/Lüsqtoff sin factor de potencia, ni se infiere potencia disponible por fase a partir de una división simple entre tres. La selección y conexión a una instalación fija debe hacerla personal habilitado conforme a las normas eléctricas locales.

## Fuentes consultadas

- **Documentación primaria:** [Lüsqtoff LG7500EXT](https://www.lusqtoff.com.ar/ver-producto/LG7500EXT); [Honda ET12000](https://pf.honda.com.ar/producto/ET12000); [Gamma GE3494AR, grupo estacionario 17 kW](https://www.gammaherramientas.com.ar/producto/grupo-estacionario-17kw/); [manual Gamma GE3493AR/GE3494AR](https://gammaherramientas.com.ar/web/wp-content/uploads/2025/12/GE3493AR_GE3494AR_MANUAL_web.pdf).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/generadores/", "/generadores/monofasicos/", "grupos monofásicos: cómo distinguir la salida",
    ),
    "paginas/hidrolavadoras/18-hidrolavadora-150-bar.md": (
        "Tabla que contrasta presión máxima permitida y presión de trabajo en tres modelos marcados 150 bar; incluye caudal por modo para Lüsqtoff HL100-8.",
        """| Modelo | Cómo nombra los 150 bar | Presión de trabajo publicada | Caudal publicado | Potencia eléctrica |
| :--- | :--- | ---: | ---: | ---: |
| Lüsqtoff HL100-8 | Máxima permitida: 150 bar | 100 bar | 6,0 L/min de trabajo; 7,5 L/min máximo | 2.000 W |
| Gamma 150 Elite G2514AR | Presión máxima admisible: 150 bar | No localizada en la ficha consultada | 400 L/h (6,67 L/min), sin condición de presión rotulada | 1.800 W |
| Niwa HDNW-700 | Presión máxima: 150 bar | No localizada en la ficha consultada | Máximo 450 L/h (7,5 L/min) | No confirmada en la ficha consultada |

**Dato verificado:** las fuentes llaman a 150 bar máximo/máximo permitido, no necesariamente presión de trabajo. El manual Lüsqtoff distingue claramente HL100-8: 100 bar de trabajo, 150 bar permitidos y 6,0 L/min de caudal de trabajo (7,5 L/min máximo). Gamma publica 150 bar máximos y 400 L/h; Grupo Rumbo publica para Niwa HDNW-700 150 bar máximos y 450 L/h.

**Análisis TallerLab:** las cifras revelan que leer solo «150 bar» oculta diferencias de rotulación: en HL100-8 los 150 bar no son el valor de trabajo; para Gamma y Niwa las fichas consultadas no informan una presión de trabajo comparable. Tampoco ordenamos los caudales porque las dos fichas resumen caudal sin una condición de presión común. Antes de elegir, pedir presión de trabajo y caudal bajo esa presión para el código exacto.

**Desconocido:** no se compararon unidades de limpieza, cobertura, duración, temperatura del agua ni desempeño sobre una superficie. La cifra máxima no basta para concluir compatibilidad con una tarea; respetar presión/caudal de entrada y límites del manual.

## Fuentes consultadas

- **Documentación primaria:** [manual Lüsqtoff HL100-8](https://lusqtoff.com.ar/2023/uploads/Productos/4.%20HIDROLAVADORAS/HL100-8/MANUAL/Manual%20HL100-8-pdf%20curvas_compressed.pdf); [Lüsqtoff, catálogo de hidrolavadoras 2024–2025](https://lusqtoff.com.ar/2023/uploads/Catalogos/CAT%C3%81LOGO%20LQ%202024-2025%20-%20web%20%281%29.pdf); [Gamma 150 Elite G2514AR](https://www.gammaherramientas.com.ar/producto/hidrolavadora-150-elite/).
- **Información del importador Niwa:** [Grupo Rumbo, HDNW-700](https://www.rumbosrl.com.ar/productos/productos-de-limpieza/hidrolavadoras-y-accesorios/hidrolavadoras-electricas/hidrolavadora-electrica-niwa-hdnw-700-1040700).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/hidrolavadoras/", "/hidrolavadoras/160-bar/", "hidrolavadoras de 160 bar: presión y caudal",
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
