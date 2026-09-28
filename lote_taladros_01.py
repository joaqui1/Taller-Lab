"""Cuarto lote editorial: diez guías de taladros revisadas documentalmente."""
from pathlib import Path
import re

ROOT = Path(__file__).parent

PAGES = {
    "paginas/taladros/20-taladro-inalambrico-bosch.md": (
        "GSR 120-LI o GSB 18V-50: distinguir plataforma y percusión",
        "**Dato verificado:** esta comparación usa fichas Bosch de dos códigos concretos: GSR 120-LI (12 V) y GSB 18V-50 (18 V). No extrapolamos las cifras a toda la línea Bosch.",
        """| Dato publicado | GSR 120-LI | GSB 18V-50 |
| :--- | ---: | ---: |
| Plataforma | 12 V | 18 V |
| Función | Atornillar y perforar | Atornillar, perforar y percutir |
| Torque máximo publicado | 30 Nm (duro) | 50 Nm |
| Velocidades sin carga | 0–400 / 0–1.500 rpm | 0–460 / 0–1.800 rpm |
| Mandril | 0,8–10 mm | 1,5–13 mm, metálico |
| Peso sin batería | 0,8 kg | 1,1 kg |
| Kit documentado | Configuración depende del código | 0 601 9H5 1H0: 2 baterías de 2 Ah, cargador y L-CASE |

**Análisis TallerLab.** En estas dos fichas el GSB publica 20 Nm más de torque máximo y un mandril con apertura 3 mm mayor; también pesa 0,3 kg más sin batería. El GSB suma percusión. Estas diferencias sirven para filtrar por función y tamaño de accesorio, pero no son un ensayo de perforación ni prueban que un modelo sea mejor para cualquier tarea. El kit del GSR también cambia por número de pedido.

**Declaración del fabricante.** Bosch describe la percusión del GSB 18V-50 como una función para perforar mampostería y publica compatibilidad con baterías y cargadores Professional de 18 V. No trasladamos esa compatibilidad a la plataforma de 12 V.

**Desconocido.** Las fichas consultadas no comparan autonomía bajo una misma carga, tiempo de perforación ni resultados sobre el mismo material. Confirmá el número de pedido, baterías, cargador y tensión del kit ofrecido.

## Fuentes consultadas

- **Documentación primaria:** [Bosch Argentina GSB 18V-50](https://www.bosch-professional.com/ar/es/products/gsb-18v-50-06019H51E2); [Bosch Ecuador GSR 120-LI](https://www.bosch-professional.com/ec/es/products/gsr-120-li-06019G80G0).
- **Opiniones:** no se revisó una muestra verificable.""",
        "Comparación documental Bosch GSR 120-LI y GSB 18V-50: plataforma, torque, mandril, peso y contenido de un kit identificado.",
        "/taladros/",
    ),
    "paginas/taladros/13-taladro-inalambrico-dewalt.md": (
        "DCD794 y DCD805: separar taladro atornillador y percutor",
        "**Dato verificado:** contrastamos dos modelos identificados en el catálogo DeWalt: DCD794 y DCD805. La documentación consultada corresponde al mercado estadounidense; no confirma la disponibilidad ni garantía de cada kit en Argentina.",
        """| Dato documentado | DCD794 | DCD805 |
| :--- | :--- | :--- |
| Categoría de ficha | Taladro atornillador | Taladro percutor/atornillador |
| Plataforma de etiqueta | 20 V MAX (18 V nominales) | 20 V MAX (18 V nominales) |
| Motor | Brushless | Brushless |
| Mandril | 1/2 in (13 mm), con trinquete | 1/2 in (13 mm), metálico con trinquete |
| Velocidad sin carga | Hasta 1.650 rpm | 0–650 / 0–2.000 rpm |
| Potencia de salida publicada | 404 UWO | DeWalt informa hasta 40 % más UWO que DCD796 bajo las condiciones de batería que detalla |
| Kit consultado | DCD794B: herramienta sola | DCD805D2: 2 baterías de 2 Ah, cargador y bolso |

**Análisis TallerLab.** La diferencia funcional explícita es la percusión del DCD805; el DCD794 es un taladro atornillador. Por eso no presentamos el DCD794 como sustituto para una necesidad de percusión. Las configuraciones citadas tampoco son equivalentes: DCD794B se vende como herramienta sola y DCD805D2 incluye baterías y cargador. El dato UWO de DCD794 y la comparación promocional del DCD805 no permiten calcular una diferencia común de torque.

**Declaración del fabricante.** DeWalt aclara que 20 V MAX es el voltaje máximo inicial sin carga y que la tensión nominal es 18 V. La ficha del DCD805 describe 3 modos de iluminación LED; no inferimos precisión ni rendimiento medidos por TallerLab.

**Desconocido.** No verificamos códigos regionales ni la composición de kits argentinos. Las fichas no ofrecen una prueba de perforación común que permita comparar velocidad bajo carga, autonomía o capacidad real en mampostería. Revisá el sufijo completo y el manual de la unidad ofrecida.

## Fuentes consultadas

- **Documentación primaria:** [DeWalt DCD794B](https://www.dewalt.com/en-us/product/dcd794b/atomic-20v-max-brushless-cordless-12-drilldriver-tool-only); [DeWalt DCD805D2](https://www.dewalt.com/en-us/product/dcd805d2/20v-max-xr-brushless-cordless-12-hammer-drilldriver-kit).
- **Opiniones:** no se revisó una muestra verificable.""",
        "Comparación documental de DeWalt DCD794 y DCD805: función, alimentación, mandril, velocidad y diferencia entre herramienta sola y kit.",
        "/taladros/",
    ),
    "paginas/taladros/12-taladro-inalambrico-einhell.md": (
        "TE-CD 18/40 y TP-CD 18/50: sin y con percusión",
        "**Dato verificado:** la tabla reúne datos publicados para el Einhell TE-CD 18/40 Li y el TP-CD 18/50 Li-i BL (artículo 4513942). El sufijo del modelo y el contenido de caja importan: el TP-CD consultado es la versión Solo.",
        """| Dato documentado | TE-CD 18/40 Li | TP-CD 18/50 Li-i BL Solo |
| :--- | ---: | ---: |
| Plataforma | 18 V Power X-Change | 18 V Power X-Change |
| Torque duro declarado | 40 Nm | 50 Nm |
| Velocidad sin carga | 0–400 / 0–1.500 rpm | 0–500 / 0–1.800 rpm |
| Mandril | Hasta 13 mm | Metálico, hasta 13 mm |
| Percusión | No indicada en la ficha/manual consultado | Sí; hasta 28.800 impactos/min en velocidad 2 |
| Motor | No se declara brushless en la ficha consultada | Brushless |
| Batería/cargador | Varía por código de kit | No incluidos en la versión Solo |

**Análisis TallerLab.** El TP-CD declara 10 Nm más y agrega percusión; la velocidad máxima sin carga publicada supera a la del TE-CD en 300 rpm. Son diferencias de ficha, no una comparación de rapidez real. El TE-CD es el modelo de rotación sin percusión dentro de las fuentes citadas; el TP-CD permite seleccionar atornillado, perforación o percusión. La batería Power X-Change debe identificarse como gasto aparte cuando la oferta sea Solo.

**Declaración del fabricante.** Einhell identifica al TP-CD 18/50 Li-i BL Solo como brushless y compatible con el sistema Power X-Change. La garantía especial de motor requiere registro en los términos del fabricante; no equivale a la garantía general de la herramienta.

**Desconocido.** La ficha consultada no valida qué kits TE-CD se ofrecen hoy en Argentina ni su garantía local. No afirmamos autonomía, ventaja de durabilidad ni capacidad universal en hormigón. Confirmá código de artículo, batería y cargador antes de comparar precio.

## Fuentes consultadas

- **Documentación primaria:** [ficha técnica Einhell TE-CD 18/40 Li Solo](https://www.einhell.de/p/4513925-te-cd-18-40-li-solo/); [catálogo técnico Einhell 2026 con RPM del TE-CD 18/40](https://www.einhell.de/fileadmin/corporate-media/services/catalogues/pdf-de/einhell-services-catalogue-tools-diy-2026-de.pdf); [ficha Einhell TP-CD 18/50 Li-i BL Solo](https://www.einhell.de/p/4513942).
- **Opiniones:** no se revisó una muestra verificable.""",
        "Comparación Einhell TE-CD 18/40 y TP-CD 18/50: torque y velocidad declarados, percusión, mandril y kits Solo.",
        "/taladros/",
    ),
    "paginas/taladros/18-taladro-stanley.md": (
        "SDH600 o SDH700: 600 W y 700 W no cuentan toda la historia",
        "**Dato verificado:** los manuales Stanley para SDH600 y SDH700 publican sus prestaciones y capacidades. Las cifras corresponden a variantes con tensión regional indicada en cada manual.",
        """| Dato verificado en manual | SDH600 | SDH700 |
| :--- | ---: | ---: |
| Potencia nominal | 600 W | 700 W |
| Velocidad sin carga | 0–2.900 rpm | 0–2.900 rpm |
| Percusión máxima | 49.300 impactos/min | 49.300 impactos/min |
| Mandril | 1,5–13 mm | 1,5–13 mm |
| Capacidad declarada en concreto / metal | 13 / 13 mm | 13 / 13 mm |
| Capacidad declarada en madera | 25 mm | 30 mm |
| Peso | 1,75 kg | 1,87 kg |

**Análisis TallerLab.** El SDH700 declara 100 W más y 5 mm más de capacidad máxima en madera, pero ambos manuales publican la misma velocidad sin carga, tasa de impactos y capacidad en concreto y metal. El SDH600 pesa 0,12 kg menos según los manuales. No convertimos estas diferencias en una conclusión sobre velocidad de perforación o calidad: no hay prueba comparativa en idénticas condiciones.

**Declaración del fabricante.** Los manuales listan 220 V y 50 Hz para la variante identificada como AR. Otras terminaciones regionales indican tensiones distintas. La placa debe coincidir con la instalación y el código completo del equipo.

**Desconocido.** No cotejamos disponibilidad, accesorios o garantía de una oferta local actual. Las capacidades máximas no deben interpretarse como recomendación para cualquier broca, material o tiempo de uso; consultá el manual correspondiente.

## Fuentes consultadas

- **Documentación primaria:** [manual Stanley SDH600](https://support.stanleytools.com/hc/es/article_attachments/115004351134); [manual Stanley SDH700/SDH700K](https://support.stanleytools.com/hc/es/article_attachments/115004351114).
- **Opiniones:** no se revisó una muestra verificable.""",
        "Comparación documental Stanley SDH600 y SDH700: potencia, capacidad por material, mandril, velocidad, percusión y peso.",
        "/taladros/",
    ),
    "paginas/taladros/09-taladro-black-decker.md": (
        "LD120: ficha identificada y una precaución con 20 V MAX",
        "**Dato verificado:** el manual regional de BLACK+DECKER LD120 publica tensión de etiqueta, velocidad, torque, mandril y batería. La marca 20 V MAX no equivale a tensión nominal bajo carga.",
        """| Dato publicado para LD120 | Especificación |
| :--- | :--- |
| Alimentación indicada | 20 V MAX; 18 V nominales bajo carga según nota del manual |
| Velocidad sin carga | 0–650 rpm |
| Torque publicado | 25 Nm (18,4 ft-lb) |
| Mandril | 3/8 in (10 mm) |
| Batería especificada | LD120BAT, ion-litio, 1,5 Ah |
| Tiempo de carga publicado | 3–4 horas |
| Entrada de cargador para variante AR | 220 V, 50 Hz |

**Análisis TallerLab.** Esta ficha permite comprobar un modelo, no describir toda la oferta BLACK+DECKER ni asegurar que todas las publicaciones incluyan la misma batería y cargador. Comparar los “20 V” de LD120 con un modelo marcado 18 V sin leer la nota del fabricante puede llevar a tratar dos tensiones nominales como distintas cuando el manual explica la diferencia entre máximo inicial y voltaje nominal.

El mandril de 10 mm y la ausencia de una función percutora en las especificaciones del LD120 delimitan qué información ofrece esta ficha. No inferimos que pueda perforar mampostería ni recomendamos una aplicación que el manual no identifica.

**Desconocido.** No se confirmó si LD120 continúa en el catálogo local, qué accesorios trae una oferta actual ni la garantía disponible. Tampoco encontramos en esta revisión documentación primaria suficiente para comparar modelos actuales con cable e inalámbricos de la marca. Confirmá el código de batería y cargador impresos en el equipo.

## Fuentes consultadas

- **Documentación primaria:** [manual regional BLACK+DECKER LD120](https://support.blackanddecker.com/hc/es/article_attachments/115004285093); [ficha oficial del kit LDX120PK](https://www.blackanddecker.com/products/ldx120pk) — es un código comercial distinto y no se usa para completar el contenido de caja de LD120.
- **Opiniones:** no se revisó una muestra verificable.""",
        "Ficha documentada del BLACK+DECKER LD120: voltaje nominal y máximo, torque, velocidad, mandril, batería y cargador regional.",
        "/taladros/",
    ),
    "paginas/taladros/15-taladro-milwaukee.md": (
        "M12 3404 y M18 2904: comparar plataforma y función",
        "**Dato verificado:** comparamos los códigos Milwaukee 3404-20 (M12) y 2904-20 (M18). Las fichas estadounidenses no confirman disponibilidad, tensión de cargador ni garantía de la unidad vendida en Argentina.",
        """| Dato documentado | M12 FUEL 3404-20 | M18 FUEL 2904-20 |
| :--- | ---: | ---: |
| Plataforma | M12 | M18 |
| Función | Taladro percutor/atornillador | Taladro percutor/atornillador |
| Torque máximo publicado | 400 in-lb (≈45 Nm) | 1.400 in-lb (≈158 Nm) |
| Largo de herramienta | 6 in | 6,9 in |
| Peso publicado sin batería | 2,6 lb (≈1,18 kg) | 3,3 lb (≈1,50 kg) |
| Kit / herramienta sola | 3404-20: herramienta y clip | 2904-20: herramienta y mango lateral; la ficha de kit 2904-22 incluye 2 baterías XC5.0 y cargador |

**Análisis TallerLab.** Los valores máximos de torque publicados difieren por un factor de 3,5 y los pesos de herramienta sola por unos 0,32 kg. Convertimos unidades para facilitar lectura, no para afirmar una prueba común: las fichas no especifican un protocolo comparativo compartido. Ambos modelos tienen percusión; el 3404-20 usa batería M12 y el 2904-20 pertenece a M18. El código “-20” no debe confundirse con el contenido del kit “-22”.

**Declaración del fabricante.** Milwaukee describe el 3404-20 como brushless y parte del sistema M12. La ficha 2904-20 describe motor POWERSTATE sin escobillas y sistema M18. No inferimos autonomía ni duración a partir de la plataforma o el tipo de motor.

**Desconocido.** No cotejamos variantes argentinas, baterías incluidas en publicaciones locales ni servicio de garantía. No se hizo prueba de perforación ni comparación de rendimiento bajo carga.

## Fuentes consultadas

- **Documentación primaria:** [Milwaukee M12 FUEL 3404-20](https://www.milwaukeetool.com/products/details/m12-fuel-1-2-hammer-drill-driver/3404-20); [Milwaukee M18 FUEL 2904-20](https://www.milwaukeetool.com/products/details/m18-fuel-1-2-hammer-drill-driver-cordless-power-tool/2904-20); [contenido del kit 2904-22](https://www.milwaukeetool.com/2904-22).
- **Opiniones:** no se revisó una muestra verificable.""",
        "Comparación documental Milwaukee M12 3404-20 y M18 2904-20: torque, peso sin batería, largo, función y alcance del kit.",
        "/taladros/",
    ),
    "paginas/taladros/01-taladro-inalambrico.md": (
        "Tres criterios para comparar taladros a batería documentados",
        "**Dato verificado:** esta matriz usa tres modelos identificados y fuentes de fabricante. Los valores de torque son los publicados por cada marca; no constituyen una prueba comparativa con un método común.",
        """| Modelo y fuente | Plataforma indicada | Torque publicado | Velocidad sin carga | Mandril | Función de percusión |
| :--- | ---: | ---: | ---: | ---: | :--- |
| Bosch GSR 120-LI | 12 V | 30 Nm duro | 0–400 / 0–1.500 rpm | hasta 10 mm | No indicada para GSR |
| Einhell TE-CD 18/40 Li | 18 V | 40 Nm duro | 0–400 / 0–1.500 rpm | hasta 13 mm | No indicada en la ficha citada |
| BLACK+DECKER LD120 | 20 V MAX; 18 V nominales | 25 Nm | 0–650 rpm | 10 mm | No indicada para LD120 |

**Análisis TallerLab.** La tabla muestra por qué no alcanza con comparar voltaje o torque por sí solos: los modelos difieren en mandril, velocidades, función y plataforma. En particular, 20 V MAX del LD120 es una etiqueta de máximo inicial sin carga, no una tensión nominal superior a 18 V; lo aclara su manual. El TE-CD publica 10 Nm más que el GSR y un mandril 3 mm mayor, pero sin protocolo de medición compartido no declaramos ganador ni trasladamos esas cifras a autonomía o capacidad efectiva.

Para decidir, anotá primero si necesitás solo atornillar/perforar o también percusión; después identificá diámetro de broca, material y si ya tenés baterías compatibles. Un atornillador percutor no sustituye automáticamente a un rotomartillo para perforación repetida en hormigón. Consultá nuestra guía de [taladros percutores](/taladros/percutores/) y la de [rotomartillos](/taladros/rotomartillos/) para diferenciar esas categorías.

**Desconocido.** No comparamos autonomía, velocidad bajo carga, vibración real ni durabilidad. El kit y el cargador cambian con el código de pedido: los tres registros de esta tabla no son una comparación de precio ni disponibilidad local.

## Fuentes consultadas

- **Documentación primaria:** [Bosch GSR 120-LI](https://www.bosch-professional.com/ec/es/products/gsr-120-li-06019G80G0); [manual técnico Einhell TE-CD 18/40 Li](https://d2c5rvsfjg2eub.cloudfront.net/asset/208244749100/document_qv8gbkvg3h41l3lg9j0rh59j64/4257239_21023_002_SPK7-1.pdf); [manual BLACK+DECKER LD120](https://support.blackanddecker.com/hc/es/article_attachments/115004285093).
- **Opiniones:** no se revisó una muestra verificable.""",
        "Matriz TallerLab de tres taladros inalámbricos documentados: voltaje nominal, torque publicado, velocidad, mandril y percusión.",
        "/taladros/",
    ),
    "paginas/taladros/19-atornillador-de-impacto-dewalt.md": (
        "DCF809 y DCF887: torque máximo y control no son lo mismo",
        "**Dato verificado:** las cifras de la tabla proceden de manuales DeWalt para DCF809 y DCF887. Los valores de torque son máximos publicados por el fabricante, no valores de apriete que TallerLab haya medido en un tornillo.",
        """| Dato de manual | DCF809 | DCF887 |
| :--- | ---: | ---: |
| Torque máximo declarado | 190 Nm | 205 Nm |
| Niveles/modos de velocidad | Gatillo de velocidad variable | 3 modos: 0–1.000 / 0–2.800 / 0–3.250 rpm |
| Torque indicado por modo | No se detalla por modo en el dato citado | 27 / 170 / 205 Nm |
| Portapuntas | Hexagonal de cambio rápido, 1/4 in | Hexagonal de 1/4 in |
| Etiqueta de plataforma | 20 V MAX (18 V nominales) | 20 V MAX |
| Kit local | El contenido de DCF809C2 no se confirmó para Argentina | El contenido de DCF887D2 no se confirmó para Argentina |

**Análisis TallerLab.** El máximo publicado del DCF887 supera al DCF809 en 15 Nm, alrededor de 7,9 % respecto de 190 Nm. Esa diferencia es aritmética entre las cifras del fabricante; no predice el torque final de una unión. El dato más útil para control es que el manual DCF887 publica tres escalones de velocidad/torque, mientras el DCF809 citado no ofrece una tabla equivalente por modo. No atribuimos un resultado de apriete más preciso sin prueba.

**Declaración del fabricante.** DeWalt indica que el modo 1 del DCF887 (Precision Drive) se orienta a aplicaciones ligeras de atornillado y que, si no alcanza para la fijación, se debe seleccionar el modo 2. El manual advierte que el torque de fijación depende, entre otros factores, del voltaje y del material. Para una unión crítica, recomienda comprobar torque con una llave dinamométrica.

**Desconocido.** Los sufijos de kit cambian por mercado. No confirmamos baterías, cargador, garantía ni disponibilidad argentina para cada oferta; tampoco se ensayó el torque real.

## Fuentes consultadas

- **Documentación primaria:** [manual DeWalt DCF809](https://www.dewalt.com/GLOBALBOM/QU/DCF809C2/12/Instruction_Manual/EN/NA156061_DCF809_NA.pdf); [manual DeWalt DCF887, tabla de modos y torque](https://www.dewalt.com/GLOBALBOM/QU/DCF887D2/3/Instruction_Manual/EN/NA454905_DCF887_T2_T3_NA.pdf).
- **Opiniones:** no se revisó una muestra verificable.""",
        "Comparación documental DCF809/DCF887: torque máximo, modos de velocidad, portapuntas y diferencias entre torque declarado y apriete medido.",
        "/taladros/",
    ),
    "paginas/taladros/05-atornillador-de-impacto.md": (
        "Atornillador de impacto: hexagonal de 1/4 in frente a cuadrado de 1/2 in",
        "**Dato verificado:** comparamos dos herramientas de impacto Bosch con interfaz distinta y el DeWalt DCF887 con modos documentados. El nombre comercial “de impacto” no alcanza para determinar qué accesorio admite cada modelo.",
        """| Modelo documentado | Interfaz | Dato de torque publicado | Control publicado | Qué indica la interfaz |
| :--- | :--- | ---: | :--- | :--- |
| Bosch GDR 18V-200 | Hexagonal 1/4 in | 200 Nm máximo | Gatillo variable; 0–3.400 rpm | Puntas y accesorios con vástago hexagonal compatible |
| Bosch GDX 18V-200 | Hexagonal 1/4 in y cuadrado 1/2 in | 200 Nm máximo de apriete; 350 Nm de arranque | Gatillo variable | Admite puntas hexagonales y dados con encastre cuadrado compatible |
| DeWalt DCF887 | Hexagonal 1/4 in | 27 / 170 / 205 Nm por modo | 3 modos, hasta 3.250 rpm | Atornillado con punta; no es una llave de impacto de cuadradillo |

**Análisis TallerLab.** La comparación propia es funcional: el GDX combina dos encastres; GDR y DCF887 citados tienen portapuntas hexagonal. Una llave de impacto con cuadrado de 1/2 in se elige para dados, y no debe confundirse con un atornillador que solo sujeta puntas de 1/4 in. Aunque el GDX publica 350 Nm de arranque, ese número no se compara con los 200–205 Nm de apriete de los otros equipos: son magnitudes/condiciones diferentes.

**Dato verificado.** Bosch publica 200 Nm para GDR 18V-200, y para GDX 18V-200 diferencia torque máximo y torque de arranque. DeWalt ofrece tres modos de control en el DCF887. Estas fichas permiten identificar compatibilidad y ajuste, no el resultado en una fijación específica.

**Desconocido.** No medimos fuerza de apriete, precisión, vibración ni desempeño con un accesorio concreto. Confirmá retención, dimensiones del vástago, clasificación de impacto de la punta/dado y el manual antes de usar.

## Fuentes consultadas

- **Documentación primaria:** [Bosch GDR 18V-200](https://www.bosch-professional.com/es/es/products/gdr-18v-200-06019J2105); [Bosch Argentina GDX 18V-200](https://www.bosch-professional.com/ar/es/products/gdx-18v-200-06019J22E0); [manual DeWalt DCF887](https://www.dewalt.com/GLOBALBOM/QU/DCF887D2/3/Instruction_Manual/EN/NA454905_DCF887_T2_T3_NA.pdf).
- **Opiniones:** no se revisó una muestra verificable.""",
        "Comparación de encastres y modos entre Bosch GDR 18V-200, GDX 18V-200 y DeWalt DCF887; distingue torque de apriete y arranque.",
        "/taladros/",
    ),
    "paginas/taladros/07-taladro-percutor-inalambrico.md": (
        "Percutores inalámbricos: la comparación empieza por datos comunes",
        "**Dato verificado:** esta matriz reúne cuatro taladros percutores identificados. Solo comparamos campos publicados; los datos de torque, percusión y peso no siguen necesariamente un protocolo común entre marcas.",
        """| Modelo | Plataforma | Torque máximo publicado | Percusión publicada | Mandril | Batería en código citado |
| :--- | ---: | ---: | ---: | ---: | :--- |
| Bosch GSB 18V-50 (0 601 9H5 1E2) | 18 V | 50 Nm | Hasta 27.000 impactos/min | Metálico, 1,5–13 mm | No incluida en variante de caja |
| DeWalt DCD805B | 20 V MAX (18 V nominales) | No publicado en la ficha consultada | Modo percutor; cifra no cotejada aquí | Metálico, 1/2 in | No incluida; herramienta sola |
| Einhell TP-CD 18/50 Li-i BL Solo (4513942) | 18 V | 50 Nm duro | 8.000 / 28.800 impactos/min | Metálico, hasta 13 mm | No; Solo |
| Milwaukee M18 FUEL 2904-20 | 18 V | 1.400 in-lb (≈158 Nm) | Hasta 33.000 impactos/min | Metálico, 1/2 in | No; herramienta sola |

**Análisis TallerLab.** Esta tabla prioriza una decisión verificable: presencia de modo percutor, tipo/tamaño de mandril y kit. No ordenamos los modelos por torque ni por impactos/min: DeWalt no publica el mismo campo en la fuente consultada, y las cifras de fabricante no prueban el mismo rendimiento sobre una pared. El peso también se excluye porque las fichas no usan una condición de batería común.

Un taladro percutor inalámbrico combina giro con percusión para ciertas perforaciones en mampostería; no equivale a un rotomartillo SDS. Si el trabajo requiere perforación repetida en hormigón o brocas SDS, compará [rotomartillos](/taladros/rotomartillos/) por encastre y energía de impacto. Para madera y metal, desactivá la percusión cuando el manual así lo indique.

**Declaración del fabricante.** Los códigos Bosch y Einhell citados especifican mandril metálico; Milwaukee ofrece también mandril completamente metálico. Esta descripción de construcción no constituye una evaluación propia de retención ni durabilidad.

**Desconocido.** No se realizó ensayo físico ni se verificaron kits, precios, garantía o servicio argentinos de estos códigos. Confirmá variantes y manuales de la unidad concreta.

## Fuentes consultadas

- **Documentación primaria:** [Bosch GSB 18V-50 Argentina](https://www.bosch-professional.com/ar/es/products/gsb-18v-50-06019H51E2); [DeWalt DCD805B](https://www.dewalt.com/en-us/product/dcd805b/20v-max-xr-brushless-cordless-12-hammer-drilldriver-tool-only); [Einhell TP-CD 18/50 Li-i BL Solo](https://www.einhell.de/p/4513942); [Milwaukee M18 FUEL 2904-20](https://www.milwaukeetool.com/products/details/m18-fuel-1-2-hammer-drill-driver-cordless-power-tool/2904-20).
- **Opiniones:** no se revisó una muestra verificable.""",
        "Matriz documental de cuatro taladros percutores inalámbricos por modelo, torque/impactos publicados, mandril y contenido de kit.",
        "/taladros/",
    ),
}

FIELDS = {
    "research_type": "documental",
    "physical_test": "no",
    "specifications_contrasted": "sí",
    "buyer_opinions": "no",
    "primary_sources": "sí",
    "asset_status": "verificado",
    "reviewed": "27/09/2026",
    "published": "true",
}

RELATED = {
    "paginas/taladros/20-taladro-inalambrico-bosch.md": "Para ampliar la comparación entre plataformas, consultá la guía de [taladros inalámbricos](/taladros/inalambricos/).",
    "paginas/taladros/13-taladro-inalambrico-dewalt.md": "También podés ver la matriz de [percutores inalámbricos](/taladros/taladro-percutor-inalambrico/).",
    "paginas/taladros/12-taladro-inalambrico-einhell.md": "Para comparar con otras plataformas y modelos, seguí por la guía de [taladros inalámbricos](/taladros/inalambricos/).",
    "paginas/taladros/18-taladro-stanley.md": "Si necesitás percusión, compará estas categorías en la guía de [taladros percutores](/taladros/percutores/).",
    "paginas/taladros/09-taladro-black-decker.md": "Para comparar mandriles, torque y baterías entre marcas, consultá [taladros inalámbricos](/taladros/inalambricos/).",
    "paginas/taladros/15-taladro-milwaukee.md": "La guía de [percutores inalámbricos](/taladros/taladro-percutor-inalambrico/) reúne otros modelos con esa función.",
    "paginas/taladros/01-taladro-inalambrico.md": "Las guías de [Bosch](/taladros/bosch-inalambrico/) y [DeWalt](/taladros/dewalt-inalambrico/) profundizan en modelos concretos.",
    "paginas/taladros/19-atornillador-de-impacto-dewalt.md": "Para conocer las diferencias entre herramienta de impacto y taladro, seguí por [atornilladores de impacto](/taladros/atornilladores-de-impacto/).",
    "paginas/taladros/05-atornillador-de-impacto.md": "La comparativa de [atornilladores DeWalt](/taladros/atornillador-impacto-dewalt/) detalla dos modelos de esa familia.",
    "paginas/taladros/07-taladro-percutor-inalambrico.md": "Para contrastar el uso con cable y la función de percusión, visitá [taladros percutores](/taladros/percutores/).",
}

for filename, (asset, lead, content, description, hub) in PAGES.items():
    path = ROOT / filename
    original = path.read_text(encoding="utf-8")
    match = re.match(r"---\n(.*?)\n---\n", original, flags=re.S)
    if not match:
        raise RuntimeError(f"Missing front matter: {path}")
    front = match.group(1)
    h1_match = re.search(r'^h1: "(.+)"$', front, re.M)
    if not h1_match:
        raise RuntimeError(f"Missing H1: {path}")
    h1 = h1_match.group(1)
    front = re.sub(r"^description:.*$", lambda _: f'description: "{description}"', front, flags=re.M)
    fields = dict(FIELDS, information_asset=asset)
    for key, value in fields.items():
        line = f'{key}: "{value}"' if key != "published" else "published: true"
        if re.search(rf"^{key}:.*$", front, re.M):
            front = re.sub(rf"^{key}:.*$", lambda _: line, front, flags=re.M)
        else:
            front += "\n" + line
    content = content.replace("\n## Fuentes consultadas", f"\n{RELATED[filename]}\n\n## Fuentes consultadas", 1)
    body = f"# {h1}\n\n{lead}\n\n## {asset}\n\n{content.strip()}\n\n[Ver todas las guías de taladros]({hub}).\n"
    path.write_text(f"---\n{front}\n---\n\n{body}", encoding="utf-8")

print(f"Revisadas {len(PAGES)} páginas")
