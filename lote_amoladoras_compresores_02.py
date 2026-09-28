"""Octavo lote editorial: seis guías de amoladoras y cuatro de compresores."""
from pathlib import Path
import re

ROOT = Path(__file__).parent

PAGES = {
    "paginas/07-amoladoras-makita.md": (
        "Comparación por código de dos amoladoras Makita angulares y límites de variantes.",
        """| Modelo | Potencia absorbida | Disco | Velocidad en vacío | Peso publicado | Interruptor |
| :--- | ---: | ---: | ---: | :--- | :--- |
| GA4534 | 720 W | 115 mm | 11.000 rpm | 1,98–2,31 kg | Paleta |
| 9557HPG | 840 W | 115 mm | 11.000 rpm | 1,7–2,2 kg | Paleta |

**Dato verificado:** la ficha argentina de Makita identifica esos valores para GA4534 y 9557HPG. El borrador mencionaba GA4530 como modelo de 720 W; la documentación local consultada identifica como GA4534 a la variante de 720 W. No transferimos automáticamente las especificaciones entre códigos parecidos.

**Análisis TallerLab:** en estas dos fichas, 9557HPG declara 120 W más de potencia absorbida que GA4534 —un 16,7 % respecto de 720 W—, mientras que ambas comparten diámetro y velocidad en vacío publicada. Esa cuenta compara datos de placa; no predice velocidad bajo carga, rapidez de corte ni vida útil. Los rangos de peso se superponen y no permiten establecer una diferencia exacta sin fijar la configuración y el método de medición.

**Declaración del fabricante:** Makita describe la 9557HPG con interruptor de paleta, cuerpo delgado y barniz protector contra polvo o residuos; la ficha de GA4534 también enumera interruptor de paleta. Son características declaradas por la marca, no observaciones de una prueba de TallerLab.

## Qué revisar antes de comprar

| Comprobación | Motivo documental |
| :--- | :--- |
| Código completo y tensión | La familia y la terminación del código pueden identificar variantes diferentes. |
| Diámetro y agujero del disco | La ficha local consultada publica diámetro de 115 mm; confirmá montaje y dimensiones en el manual de la unidad. |
| Peso de la configuración | Makita publica rangos, no un único peso para todos los paquetes. |
| Contenido y garantía | Confirmalos en la publicación y con el distribuidor local; la ficha técnica citada no respalda el contenido de cada kit ni su garantía comercial. |

**Desconocido:** no se verificaron disponibilidad actual de cada variante, precios, opiniones de una muestra definida, rendimiento comparativo ni la equivalencia entre GA4530 y GA4534.

## Fuentes consultadas

- **Documentación primaria:** [Makita Argentina, GA4534](https://makita.com.ar/producto/386-amoladora-makita-115mm-4-1-2-720-w/); [Makita Argentina, 9557HPG](https://makita.com.ar/producto/387-amoladora-makita-115mm-4-1-2-840-w/); [catálogo Makita Argentina 2025](https://makita.com.ar/wp-content/uploads/2025/09/CATALOGO-2025-v2.pdf).
- **Seguridad:** usar disco, guarda y velocidad permitidos por el manual del código exacto.
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "Comparación documental GA4534 vs 9557HPG; detecta y separa la diferencia de código GA4530/GA4534.",
        "/amoladoras/", "/amoladoras/dewalt/", "comparación de amoladoras DeWalt",
    ),
    "paginas/05-amoladora-recta.md": (
        "Comparación de dos amoladoras rectas eléctricas y requisitos aún no documentados para neumáticas.",
        """| Modelo eléctrico | Potencia absorbida | Velocidad en vacío | Peso | Dato de sujeción publicado |
| :--- | ---: | ---: | ---: | :--- |
| Bosch GGS 28 L, 0 601 224 0H0 | 500 W | 33.000 rpm | 1,4 kg | La página consultada no detalla el diámetro de pinza en el resumen |
| Makita GD0600 | 400 W | 25.000 rpm | Desconocido en la ficha consultada | Desconocido en la ficha consultada |

**Dato verificado:** Bosch presenta la GGS 28 L como rectificadora eléctrica de 500 W y 33.000 rpm; Makita Argentina publica 400 W y 25.000 rpm para GD0600. La ficha Bosch incluye un manual descargable para confirmar accesorios y montaje. No completamos la fila de Makita por analogía con otras rectas de la marca.

**Análisis TallerLab:** en estos dos ejemplos con cable, la ficha Bosch declara 100 W más (25 % sobre 400 W) y 8.000 rpm más en vacío (32 % sobre 25.000 rpm). Son diferencias aritméticas de especificaciones, no una prueba de capacidad de desbaste. Pinza, accesorio admitido y velocidad máxima del accesorio deben cotejarse por herramienta y operación.

## Eléctrica y neumática: qué cambia y qué falta comprobar

| Variable de selección | Eléctrica | Neumática |
| :--- | :--- | :--- |
| Fuente de energía | Red eléctrica; los modelos citados usan cable | Aire comprimido de una instalación o compresor |
| Datos que deben compararse | Potencia, rpm, pinza, peso y tensión del código | Consumo de aire, presión de trabajo, rpm, pinza y conexión del código |
| Evidencia reunida para esta guía | Dos fichas de fabricante enlazadas abajo | No se encontró documentación primaria de un modelo neumático concreto en esta revisión |

**Análisis TallerLab:** la comparación eléctrica sí tiene códigos y cifras rastreables; una conclusión sobre cuál neumática iguala a una eléctrica requeriría fichas de ambos modelos y datos de suministro de aire en condiciones comparables. Caudal nominal del compresor no sustituye el consumo declarado de la herramienta.

**Desconocido:** no afirmamos caudal o presión neumáticos universales, accesorios compatibles por mera forma ni superioridad de una alimentación. Confirmá en el manual el rango de pinza, los accesorios permitidos, las rpm máximas y el resguardo correspondiente.

## Fuentes consultadas

- **Documentación primaria:** [Bosch Professional Argentina, GGS 28 L](https://www.bosch-professional.com/ar/es/products/ggs-28-l-06012240H0); [Makita Argentina, GD0600](https://makita.com.ar/producto/434-amoladora-recta-makita-400-w/).
- **Seguridad:** ficha Bosch ofrece el manual de GGS 28 L; verificar también el manual exacto de cualquier herramienta neumática elegida.
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "Matriz eléctrica con diferencias calculadas y una lista explícita de evidencia neumática faltante.",
        "/amoladoras/", "/amoladoras/de-banco/", "amoladoras de banco",
    ),
    "paginas/13-amoladora-skil-830w.md": (
        "Comparación de ficha de Skil 9004 y manual 9002; diferencia nominal de 130 W.",
        """| Modelo | Potencia absorbida | Disco | Velocidad en vacío | Peso publicado |
| :--- | ---: | ---: | ---: | ---: |
| Skil 9004 | 830 W | 115 mm | 11.000 rpm | 1,8 kg |
| Skil 9002 | 700 W | 115 mm | 11.000 rpm | 1,8 kg |

**Dato verificado:** el catálogo Skil Argentina 2019 consultado lista 830 W para 9004 y 700 W para 9002, además de diámetro, velocidad y peso. Un manual Skil/Bosch alojado por un distribuidor contiene instrucciones conjuntas para los modelos 9002 y 9004. La publicación de Sodimac para 9004 también indica 830 W, aunque su ficha de peso es peso embalado y no se usa para la comparación de peso neto.

**Análisis TallerLab:** la diferencia nominal de entrada es 130 W, equivalente a 18,6 % respecto de 700 W; la velocidad y el diámetro son iguales en el catálogo consultado. La diferencia no demuestra que el modelo 9004 corte más rápido: para eso harían falta condiciones y una prueba comparativa controlada. La coincidencia de peso publicado (1,8 kg) tampoco incorpora variaciones por accesorios o mercado.

| Comprobación de compra | Resultado de la documentación |
| :--- | :--- |
| Código exacto | 9004: tipo F012 9004 AK en el catálogo; 9002: tipo F012 9002 AK |
| Medida nominal | 115 mm (4½ pulgadas) en ambas referencias |
| Velocidad publicada | 11.000 rpm en ambas referencias |
| Diferencia de potencia nominal | 130 W; cálculo TallerLab a partir de 830 y 700 W |
| Kit y garantía | Pueden cambiar según sufijo/país; verificar unidad y vendedor |

**Declaración del fabricante:** el catálogo atribuye a 9004 cuerpo con soft grip y a ambos modelos interruptor resistente al polvo. Se conserva como descripción de marca, no como evaluación independiente del agarre ni de la vida de servicio.

**Desconocido:** la documentación consultada no prueba rendimiento bajo carga, duración, nivel de vibración o compatibilidad de cada disco con cada tarea. La página comercial consultada informa certificación y garantía para una publicación específica; no se extrapolan esos datos a todas las variantes.

## Fuentes consultadas

- **Documentación primaria:** [catálogo Skil 2019, copia consultada](https://descargas.bulonfer.com.ar/otros/SkilCat%C3%A1logo_2019.pdf); [manual Skil 9002/9004](https://cdn.leroymerlin.com.br/medias/document-89382741-user-manual-esmerilhadeira-angular-4-1-2--115mm--700w-9002-127v--110v--100percent-rolamentada-skil.pdf).
- **Información comercial:** [ficha de publicación Sodimac, Skil 9004](https://www.sodimac.com.ar/sodimac-ar/product/2355264/amoladora-angular-electrica-830-w-con-5-discos/2355264/); se usa solo como contraste comercial, no para datos del peso neto.
- **Seguridad:** leer el manual de la variante, comprobar guarda, disco y tensión antes de usar.
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "Cálculo comparable de diferencia de potencia Skil 9004/9002 y control de peso embalado frente a peso neto.",
        "/amoladoras/", "/amoladoras/makita/", "amoladoras Makita por código",
    ),
    "paginas/15-amoladoras-stanley.md": (
        "Comparación por código de Stanley STGS7115 y SG7115 con discrepancia regional a la vista.",
        """| Código exacto | Fuente y mercado | Potencia publicada | Diámetro | Velocidad | Peso |
| :--- | :--- | ---: | ---: | ---: | ---: |
| STGS7115 | Página Stanley Perú | 710 W | 115 mm | No indicada en la página consultada | No indicada |
| SG7115 | Manual Stanley, variantes listadas | 750 W | 115 mm | 12.000 rpm | 1,7 kg |

**Dato verificado:** Stanley publica STGS7115 como amoladora de 710 W y 115 mm. El manual de SG7115, que lista tensiones y frecuencias para varias regiones, informa 750 W, 12.000 rpm, eje M14 y 1,7 kg para esa familia.

**Análisis TallerLab:** la diferencia aparente es de 40 W, pero los códigos no son idénticos y las fuentes describen variantes/regiones distintas. Por eso no se presenta como una evolución lineal ni como comparación de dos equipos locales equivalentes. La primera comprobación útil es leer la placa y el sufijo del producto ofrecido, y después usar el manual que coincide con tensión y código.

**Declaración del fabricante:** Stanley describe STGS7115 con engranajes en espiral y publica garantía de dos años en su página de Emiratos; la ficha de Perú muestra accesorios incluidos, pero no especifica allí la garantía. La garantía extranjera no demuestra cobertura argentina.

## Qué cubre esta guía y qué no

El material verificable reunido cubre dos modelos compactos de 115 mm. No se encontraron fichas primarias suficientes para completar en esta revisión una comparación homogénea de amoladoras Stanley de 9 pulgadas o de la plataforma V20. Sus potencias, baterías, peso, contenido de kit y garantía quedan **desconocidos** aquí; no trasladamos datos entre familias.

| Antes de comparar avisos | Verificación necesaria |
| :--- | :--- |
| Código | STGS7115, SG7115 u otro; conservar todas las letras y sufijos |
| Red eléctrica | Tensión y frecuencia que figuran en la placa |
| Disco y rosca | Medida y montaje que corresponden al código exacto |
| Garantía | Confirmación por escrito del vendedor o representante del país |

## Fuentes consultadas

- **Documentación primaria:** [Stanley Perú, STGS7115](https://pe.stanleytools.global/producto/stgs7115/esmeriladora-angular-de-4-12-115mm-de-710w); [manual Stanley SG7115/SG6115](https://www.toolservicenet.com/i/STANLEY/GLOBALBOM/B3/SG7115KD/1/Instruction_Manual/EN/NA007921_SG6115_SG7115.pdf).
- **Información regional:** [página Stanley Emiratos, STGS7115](https://www.stanleytools.ae/product/stgs7115/710-w-115-mm-slider-small-angular-grinder), consultada para identificar la afirmación de garantía de ese mercado.
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "Comparación documental STGS7115/SG7115 que expone potencia y diferencias de código y mercado.",
        "/amoladoras/", "/amoladoras/total/", "amoladoras Total de 115 mm",
    ),
    "paginas/22-amoladoras-total.md": (
        "Tabla de una misma referencia Total con tensión y rpm que varían entre fichas regionales.",
        """| Referencia | Fuente consultada | Potencia | Disco | Velocidad en vacío | Tensión publicada |
| :--- | :--- | ---: | ---: | ---: | :--- |
| TG10711576 | Distribuidor autorizado Namibia | 710 W | 115 mm | 12.000 rpm | 220–240 V, 50/60 Hz |
| TG10711576 | Sitio oficial Total Túnez | 710 W | 115 mm | 11.000 rpm | 230 V |

**Dato verificado:** ambas fichas identifican el código TG10711576, 710 W y disco de 115 mm; difieren en las rpm publicadas (12.000 frente a 11.000) y describen su propio mercado/tensión. El dato de rosca M14 aparece en ambas fichas consultadas.

**Análisis TallerLab:** la diferencia de 1.000 rpm es una discrepancia documental que no se resuelve promediando cifras. Sin una ficha que identifique la variante vendida en Argentina, no elegimos una cifra como universal. La tabla vuelve visible por qué el código de catálogo y la placa de la unidad importan tanto como el nombre de marca.

| Al revisar una publicación | Qué cotejar |
| :--- | :--- |
| Código completo | TG10711576 y cualquier sufijo local del envase o la placa |
| Red eléctrica | La tensión de la ficha debe coincidir con la instalación y el producto |
| Límite de giro | Disco marcado para una velocidad máxima compatible con la herramienta |
| Paquete | Las fichas consultadas listan mango auxiliar; confirmá guarda, llave y discos en el kit vendido |
| Garantía | No se deduce de la ficha internacional; verificar cobertura argentina |

**Desconocido:** no se verificó una ficha técnica del importador argentino que resuelva las rpm de esta unidad, ni una comparación de rendimiento, peso o vida de servicio. No se atribuyen estas diferencias a una falla del fabricante; pueden corresponder a variantes regionales o a documentación distinta.

## Fuentes consultadas

- **Documentación de producto por mercado:** [Total Tools, catálogo de productos](https://www.totalbusiness.com/kw-en/products/power-tools), donde figura la referencia TG10711576; [sitio Total Tools Túnez, ficha TG10711576](https://totaltunisia.com/products/meule-ang-115-710w-tg10711576).
- **Distribuidor autorizado:** [Total Tools Namibia, TG10711576](https://totaltools.com.na/shop/total-tools/power-tools-cordless-total-tools/angle-grinder-tg10711576/).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "Contraste del mismo código TG10711576 entre dos fichas regionales que discrepan en 1.000 rpm.",
        "/amoladoras/", "/amoladoras/velocidad-variable/", "amoladoras de velocidad variable",
    ),
    "paginas/18-amoladora-velocidad-variable.md": (
        "Comparación de rango de velocidad documentado en Bosch GWS 9-125 S y Dowen Pagio 9993224.2.",
        """| Modelo | Potencia absorbida | Disco | Rango de velocidad en vacío | Otras especificaciones publicadas |
| :--- | ---: | ---: | ---: | :--- |
| Bosch GWS 9-125 S | 900 W | 125 mm | 2.800–11.000 rpm | M14; peso 1,9 kg; la ficha argentina consultada selecciona variante 127 V |
| Dowen Pagio 9993224.2 | 900 W | 115/125 mm | 4.000–12.000 rpm | Regulador variable según página del producto |

**Dato verificado:** las fichas y catálogos enlazados declaran ambos rangos ajustables. Para Bosch, la página argentina muestra una variante de 127 V; el código y la tensión deben cotejarse antes de aplicar esos datos a otra versión. La página Dowen identifica los diámetros 115/125 mm y anuncia regulador variable.

**Análisis TallerLab:** los rangos no son equivalentes: el extremo inferior publicado para Bosch es 1.200 rpm menor y el superior de Dowen es 1.000 rpm mayor. La cuenta compara límites de ficha, no certifica exactitud del selector ni rpm bajo carga. Tampoco vuelve intercambiables los discos: cada accesorio debe respetar diámetro, velocidad máxima y aplicación indicados por su fabricante.

## Cuándo sirve la regulación: criterio limitado

La regulación es una característica medible de la herramienta. Para decidir si una velocidad es apropiada hay que contrastar el material, el accesorio y las instrucciones de ambos fabricantes. Esta guía no recomienda una rpm concreta para acero inoxidable, madera, resina o pulido porque las fuentes reunidas no validan un ajuste universal para esos trabajos.

| Paso documental | Dato que debe coincidir |
| :--- | :--- |
| Identificar herramienta | Código, tensión y variante |
| Identificar accesorio | Tipo, diámetro y velocidad máxima |
| Leer ambos manuales | Material, montaje, protección y límites de operación |
| Elegir ajuste | Dentro del rango de la herramienta y sin superar el límite del accesorio |

**Declaración del fabricante:** Bosch describe selección de revoluciones para trabajar con varios materiales; Dowen Pagio presenta un regulador de velocidad variable. Son características anunciadas, no resultados de ensayos de TallerLab.

**Desconocido:** no se midió estabilidad de rpm, temperatura, calidad del acabado, vibraciones ni diferencias de corte frente a modelos de velocidad fija. No afirmamos que bajar las rpm evite por sí solo quemaduras, deformación o accidentes.

## Fuentes consultadas

- **Documentación primaria:** [Bosch Professional Argentina, GWS 9-125 S](https://www.bosch-professional.com/ar/es/products/gws-9-125-s-06013961D0); [Dowen Pagio 9993224.2](https://dowenpagioweb.com.ar/producto/amoladora-angular-115-125-mm); [catálogo Dowen Pagio 2025](https://www.dowenpagioweb.com.ar/inventario/Catalogo-Dowen-Pagio-2025.pdf).
- **Seguridad:** verificar tensión, guarda, accesorio y rpm máxima en el manual de la variante exacta.
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "Comparación aritmética entre rangos de rpm publicados en dos modelos de 900 W con variantes claramente identificadas.",
        "/amoladoras/", "/amoladoras/115-o-125/", "comparación entre discos de 115 y 125 mm",
    ),
    "paginas/compresores/11-compresor-de-100-litros.md": (
        "Comparación de caudal de placa en dos compresores de 100 L y rectificación de valores heredados no verificados.",
        """| Modelo | Tanque | Motor/alimentación | Caudal publicado | Presión máxima publicada | Peso publicado |
| :--- | ---: | :--- | ---: | ---: | ---: |
| Lüsqtoff LC-30100 | 100 L | 3 HP; 220 V; a correa; bicilíndrico | 335 L/min | 115 psi | 115 kg en manual; 85 kg en catálogo 2023–24 |
| Gamma G2803AR | 100 L | 3 HP; 220 V; bicilíndrico | 250 L/min | 116 psi | No indicada en la ficha consultada |

**Dato verificado:** ambas marcas publican depósito de 100 litros y motor de 3 HP. Lüsqtoff documenta 335 L/min en su manual LC-30100, mientras Gamma publica 250 L/min para G2803AR. Lüsqtoff publica dos pesos distintos en documentos consultados: el manual indica 115 kg y el catálogo 2023–2024 indica 85 kg.

**Análisis TallerLab:** la diferencia aritmética de caudal publicado es 85 L/min (34 % respecto del valor Gamma). No equivale a una diferencia comprobada de caudal efectivo entregado: las páginas no identifican el mismo método de medición ni publican FAD a una presión de trabajo común. La discrepancia de peso de LC-30100 también impide mostrar un único valor sin más contexto; verificá placa, revisión del manual y unidad ofrecida.

## Cómo leer una ficha de 100 litros

| Campo | Qué demuestra | Qué no demuestra por sí solo |
| :--- | :--- | :--- |
| Capacidad del tanque | Volumen nominal de almacenamiento declarado | Caudal sostenido de salida |
| Caudal en L/min | Cifra del fabricante para el modelo citado | FAD comparable si no se declara método/condición |
| Presión máxima | Límite de presión especificado | Presión útil y consumo de cada herramienta |
| Potencia del motor | Potencia indicada para la variante | Ciclo continuo o consumo eléctrico bajo carga |

**Desconocido:** no se localizaron fuentes primarias para respaldar los caudales FAD, ciclo de trabajo, nivel sonoro, horas de vida útil, corriente de arranque ni secciones de cable del borrador anterior; se retiraron esos valores. Tampoco recomendamos conectar herramientas por la sola capacidad del tanque: cotejá consumo y presión de la herramienta con un caudal de salida comparable, y respetá instalación y manuales.

## Fuentes consultadas

- **Documentación primaria:** [manual Lüsqtoff LC-30100](https://lusqtoff.com.ar/2023/uploads/Productos/16.%20COMPRESORES/LC-30100/MANUAL/LC-30100.pdf); [catálogo Lüsqtoff 2023–2024](https://www.lusqtoff.com.ar/files/catalog-lusqtoff-2023-2024.pdf); [Gamma G2803AR](https://www.gammaherramientas.com.ar/producto/compresor-bicilindrico-de-100-litros/); [manual Gamma G2803AR](https://www.gammaherramientas.com.ar/web/wp-content/uploads/2017/07/Compresores_compresor-bicilindrico-de-100-litros_G2803AR-102-manual_Rev01.pdf).
- **Seguridad:** seguir el manual del compresor y de cada accesorio; el dimensionamiento eléctrico debe hacerlo una persona competente según instalación y normativa local.
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "Tabla de dos modelos de 100 L con caudales de placa, junto con una discrepancia documental de 30 kg en el LC-30100.",
        "/compresores/", "/compresores/50-litros/", "compresor de 50 litros",
    ),
    "paginas/compresores/23-compresor-12v-doble-piston.md": (
        "Comparación de fichas Gadnic AV000009 y AV000012: caudal anunciado, ciclo declarado y discrepancia de AV000012.",
        """| Modelo Gadnic | Tensión | Presión máxima | Caudal publicado | Cilindros | Uso continuo declarado |
| :--- | ---: | ---: | ---: | :---: | :--- |
| AV000009 | 12 V | 150 PSI | 85 L/min | Doble | 30 min recomendado; 40 min máximo |
| AV000012 | 12 V | 150 PSI | Título: 60 L/min; especificación: 35–60 L/min (la descripción también menciona 72 L/min) | Doble | 30 min recomendado; 40 min máximo |

**Dato verificado:** la tienda Gadnic publica estas cifras y ambos productos indican conexión directa a batería. AV000009 lista 23 A máximos, manguera de 0,25 m más extensión de 5 m y peso de 2,54 kg. AV000012 lista 23 A máximos, cable de 3 m, manguera de 0,60 m más extensión de 2,90 m y peso de 1,4 kg.

**Análisis TallerLab:** no comparamos AV000009 y AV000012 por rapidez de inflado. Para AV000012 el caudal aparece como 60, 35–60 y 72 L/min en distintas partes de la misma ficha; además, las páginas no precisan presión y método para hacer comparables los caudales. La discrepancia queda expuesta, no promediada. Un máximo de 150 PSI tampoco indica el tiempo para inflar una rueda concreta.

## Lista de comprobación para uso móvil

| Comprobación | Dato disponible | Límite |
| :--- | :--- | :--- |
| Alimentación | 12 V; conexión directa a batería en ambas fichas | Confirmar método y polaridad en el manual |
| Corriente | 23 A máximos publicados | No se deduce compatibilidad con cualquier toma de encendedor |
| Ciclo | 30 min recomendado y 40 min máximo publicados | Seguir pausas y condiciones del manual |
| Accesorios | Mangueras y adaptadores listados por modelo | Verificar contenido del paquete adquirido |
| Caudal | 85 L/min en AV000009; cifras divergentes en AV000012 | No equivale a un ensayo de tiempo de inflado |

**Declaración del fabricante/vendedor:** la ficha comercial de Gadnic presenta ambos como infladores portátiles de doble cilindro. Las recomendaciones de uso y las prestaciones quedan atribuidas a esa ficha; TallerLab no probó los equipos.

**Desconocido:** no hay un ensayo propio de presión alcanzada, temperatura, tiempo por neumático ni comportamiento con una fuente eléctrica específica. Tampoco se revisó una muestra de opiniones para resumir experiencias de compradores. No se deben usar cifras de presión máxima como criterio único de compatibilidad.

## Fuentes consultadas

- **Información de producto:** [Gadnic AV000009, 85 L/min](https://www.gadnic.com.ar/infladores-y-compresores/compresor-de-aire-12v-85l-min); [Gadnic AV000012, ficha 60 L/min](https://www.gadnic.com.ar/infladores-y-compresores/compresor-de-aire-85l-min).
- **Seguridad:** seguir el manual de cada código respecto de conexión a batería, ciclo de trabajo y enfriamiento.
- **Opiniones de compradores:** visibles en la página comercial de AV000009, pero no se extrajo ni analizó una muestra; por eso no se atribuye un patrón de experiencia a TallerLab.""",
        "Comparación de dos fichas 12 V y detección de tres caudales contradictorios publicados para Gadnic AV000012.",
        "/compresores/", "/compresores/para-auto/", "compresores de aire para auto",
    ),
    "paginas/compresores/16-compresor-de-200-litros.md": (
        "Comparación de reserva nominal, caudal y alimentación: el Schulz CSV 20/200 declara tanque de 172,8 L.",
        """| Modelo | Tanque declarado | Potencia/tensión | Caudal o desplazamiento | Presión máxima | Peso neto |
| :--- | ---: | :--- | ---: | ---: | ---: |
| Lüsqtoff LC-30200 | 200 L | 3 HP; 220 V monofásico | 335 L/min | 115 psi | 95 kg (catálogo 2024–25) |
| Schulz CSV 20/200, código 922.9303-0 | 172,8 L | 5 HP; 220 V | 566 L/min de desplazamiento teórico | 175 psi / 12,0 bar | 133,1 kg |

**Dato verificado:** Lüsqtoff identifica LC-30200 como tanque de 200 L, 3 HP y 335 L/min en su catálogo 2025. Schulz comercializa CSV 20/200, pero la ficha técnica del código 922.9303-0 declara volumen de reservorio de 172,8 L y desplazamiento teórico de 566 L/min. Por tanto, la etiqueta “20/200” no basta para inferir que el calderín mida exactamente 200 L.

**Análisis TallerLab:** el desplazamiento teórico Schulz supera en 231 L/min el caudal publicado para Lüsqtoff, pero las fuentes no confirman una metodología común ni un caudal efectivo en herramienta; esta resta no es un ranking de entrega útil. La comparación sirve para separar volumen nominal/anunciado, desplazamiento y presión, que son magnitudes distintas.

**Desconocido:** un catálogo Lusqtoff antiguo (2020/21) consignaba 415 L/min para LC-30200, frente a 335 L/min en el catálogo 2025. No se encontró una explicación que determine si cambió la ficha, el modelo o la medición, así que para este cuadro se cita el documento más reciente y se deja registrada la diferencia. La misma fuente antigua lista LC-40200 como 4 HP y 380 V; no se combina con la variante monofásica ni se recomienda una conexión eléctrica.

## Qué verificar para dimensionar el equipo

| Requisito del taller | Comprobación documental |
| :--- | :--- |
| Tanque | Litros reales declarados para el código y revisión exactos |
| Herramienta | Caudal requerido a presión de trabajo, en unidad/método comparables |
| Alimentación | Tensión y número de fases de la placa frente a la instalación |
| Ciclo de trabajo | Límite del fabricante; desconocido para los modelos en esta matriz |
| Instalación | Manual, protección y normativa local con instalador competente |

## Fuentes consultadas

- **Documentación primaria:** [catálogo Lüsqtoff 2024–2025](https://www.lusqtoff.com.ar/2023/uploads/Catalogos/CAT%C3%81LOGO%20LQ%202024-2025%20-%20web%20%281%29.pdf); [catálogo antiguo Lüsqtoff 2020–2021](https://lusqtoff.com.ar/files/Catalogo_Lusqtoff_2020.pdf); [ficha técnica Schulz CSV 20/200](https://www.schulz.com.br/wp-content/uploads/2020/09/Super-Catalogo-Geral-fev25-MI.pdf); [producto Schulz, familia 20/200](https://www.schulz.com.br/es/produtos/ver/922.9241-0/ME).
- **Seguridad:** dimensionamiento eléctrico, puesta en servicio y mantenimiento deben seguir el manual de la variante y la normativa aplicable.
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "Comparación documental que descubre el desfase entre la designación Schulz 20/200 y los 172,8 L del tanque publicado.",
        "/compresores/", "/compresores/100-litros/", "compresores de 100 litros",
    ),
    "paginas/compresores/18-compresor-de-24-litros.md": (
        "Comparación de dos compresores realmente documentados de 24 L y corrección del código LC-2024, que corresponde a 40 L.",
        """| Modelo | Tanque | Motor/potencia | Presión máxima | Caudal publicado | Peso |
| :--- | ---: | :--- | ---: | ---: | ---: |
| Gamma G2860AR | 24 L | 1.500 W; 220 V; sin aceite | 8 bar / 116 psi | 236 L/min, descrito como flujo continuo | 21,3 kg |
| Lüsqtoff LC-0122 | 24 L | 1 HP / 750 W; 220 V; sin aceite | 115 psi | 180 L/min | 24 kg |

**Dato verificado:** las fichas de Gamma y Lüsqtoff identifican tanque de 24 L y publican los valores de la tabla. Gamma declara presión de conexión de 6 bar y desconexión a 8 bar; Lüsqtoff describe una unidad monofásica de pistón y mando directo.

**Análisis TallerLab:** las fichas publican una diferencia de 56 L/min y 750 W entre estos ejemplos, pero Gamma llama a su cifra “flujo continuo” y Lüsqtoff la llama “caudal”; no se especifican condiciones comunes suficientes para tratar esa resta como ventaja efectiva. El dato de presión máxima tampoco prueba que una herramienta mantenga su caudal durante una operación continua.

**Dato verificado sobre la intención de búsqueda:** el modelo Lüsqtoff LC-2024 que aparecía en el borrador no es de 24 L: la página de fabricante lo identifica como modelo discontinuado de 40 L. Se retira como ejemplo de 24 L. Como referencia cercana de tamaño, Gamma G2801AR declara 25 L, 2 HP, 2.850 rpm y 27 kg; no es un modelo de 24 L y queda fuera de la comparación principal.

| Uso que estás evaluando | Dato que conviene cotejar |
| :--- | :--- |
| Inflado/soplado ocasional | Presión y caudal de la herramienta, conexiones y ciclo del compresor |
| Pintura | Consumo de la pistola a la presión elegida frente al caudal útil verificable; las fichas consultadas no bastan para afirmar compatibilidad universal |
| Herramienta neumática continua | Caudal de salida bajo condiciones comparables y ciclo de trabajo; estos datos no están completos en ambas fichas |
| Elección entre 24 y 25 L | Diferencia de tanque de 1 L entre ejemplos Gamma; no predice por sí sola recuperación ni entrega de aire |

**Desconocido:** no se verificó FAD comparable, ruido medido bajo un estándar común, duración de ciclo ni minutos de pintura por tanque. La descripción de bajo ruido es una declaración comercial del fabricante, no una medición de TallerLab.

## Fuentes consultadas

- **Documentación primaria:** [Gamma G2860AR, ficha 24 L](https://www.gammaherramientas.com.ar/producto/compresor-sin-aceite-24-l-2-hp/); [Lüsqtoff LC-0122, ficha 24 L](https://lusqtoff.com.ar/ver-producto/LC-0122); [Lüsqtoff LC-2024, ficha y capacidad real de 40 L](https://lusqtoff.com.ar/ver-producto/LC-2024); [Gamma G2801AR, 25 L](https://www.gammaherramientas.com.ar/producto/compresor-de-25-litros/).
- **Seguridad:** usar presión, ciclo, accesorios y mantenimiento especificados por el manual del código exacto.
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "Comparación de dos modelos de 24 L y corrección del LC-2024: ficha del fabricante indica 40 L, no 24 L.",
        "/compresores/", "/compresores/50-litros/", "compresores de 50 litros",
    ),
}

for relpath, (asset, body, description, hub, sibling, sibling_title) in PAGES.items():
    path = ROOT / relpath
    old = path.read_text(encoding="utf-8")
    match = re.match(r"---\r?\n(.*?)\r?\n---\r?\n", old, re.S)
    if not match:
        raise RuntimeError(f"No se encontró frontmatter en {path}")
    front = match.group(1)
    h1 = re.search(r"(?m)^h1:\s*(?:\"(.*?)\"|'(.*?)'|(.+))$", front)
    if not h1:
        raise RuntimeError(f"No se encontró H1 en {path}")
    h1_value = next(v for v in h1.groups() if v is not None)
    front = re.sub(r"(?m)^description:.*$", 'description: "' + description.replace('"', '\\"') + '"', front)
    values = {
        "research_type": '"documental"', "physical_test": '"no"',
        "specifications_contrasted": '"sí"', "buyer_opinions": '"no"',
        "primary_sources": '"sí"', "information_asset": '"' + asset.replace('"', '\\"') + '"',
        "asset_status": '"verificado"', "reviewed": '"27/09/2026"', "published": "true",
    }
    for key, value in values.items():
        if re.search(rf"(?m)^{key}:", front):
            front = re.sub(rf"(?m)^{key}:.*$", f"{key}: {value}", front)
        else:
            front += f"\n{key}: {value}"
    newbody = (
        f"# {h1_value}\n\n<!-- AUDITORIA_EDITORIAL_178 -->\n\n"
        f"**Dato verificado:** las cifras de las matrices se transcriben de las fuentes identificadas en cada tabla; las cuentas propias se señalan como **Análisis TallerLab** y los datos sin respaldo como **Desconocido**.\n\n"
        f"{body}\n\n"
        f"Para seguir comparando: [{sibling_title}]({sibling}).\n\n"
        f"Para explorar la categoría: [guías de {('amoladoras' if '/amoladoras/' in hub else 'compresores')}]({hub}).\n"
    )
    path.write_text(f"---\n{front}\n---\n\n{newbody}", encoding="utf-8")
    print(relpath)
