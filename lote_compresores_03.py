"""Noveno lote editorial: diez guías de compresores."""
from pathlib import Path
import re

ROOT = Path(__file__).parent

PAGES = {
    "paginas/compresores/08-aceite-para-compresor-de-aire.md": (
        "Contraste de grados e intervalos de aceite en manuales de tres compresores concretos; muestra por qué no hay una viscosidad universal.",
        """| Modelo y documento | Lubricante indicado | Intervalo o control que sí aparece |
| :--- | :--- | :--- |
| Gamma G2802AR, 50 L | SAE 30 o L-DAB 100 sobre 10 °C; SAE 10 o L-DAB 68 bajo 10 °C | Primer cambio a las 10 h; luego cada 500 h |
| Lüsqtoff LC-40100 | Aceite normal 40W, según manual | Cambio después de 50 h de uso |
| Lüsqtoff LC-30100 | El manual consultado indica llenar hasta el punto rojo del visor, pero no fija un grado en el fragmento de mantenimiento revisado | Uso ocasional: cada 6 meses; uso diario: cada 1.000 h, según el manual |

**Dato documentado:** estas son instrucciones de los manuales de los modelos citados, no equivalencias creadas por TallerLab. Gamma establece grados distintos según temperatura; Lüsqtoff también presenta pautas que dependen del modelo. Un SAE no se debe convertir automáticamente a ISO VG con una tabla genérica para decidir qué poner en un equipo.

**Análisis TallerLab:** la diferencia entre manuales basta para descartar «ISO VG 100» o «SAE 30» como respuesta universal. Para comprar, prevalece el manual del código y revisión exactos. Si la etiqueta, el manual disponible y el aceite recomendado por el servicio técnico difieren, registrá el código de serie y pedí confirmación al fabricante antes de rellenar.

## Control documental antes de cargar aceite

| Paso | Qué cotejar | Límite |
| :--- | :--- | :--- |
| Identificar el equipo | Marca, código y si la bomba requiere lubricación | “Compresor de 50 litros” no identifica por sí solo el lubricante |
| Consultar el manual | Grado, temperatura ambiente, nivel y primer cambio | No extrapolar intervalos de otro modelo |
| Revisar el visor | Posición de nivel que especifica el manual | No llenar por volumen supuesto |
| Desechar y mantener | Procedimiento de cambio y drenaje indicado para ese equipo | Esta guía no sustituye el procedimiento seguro del fabricante |

**Desconocido:** no confirmamos una regla general sobre aceites detergentes, volúmenes en mililitros ni equivalencias SAE/ISO para todos los compresores. El manual LC-30100 consultado explica el nivel y los intervalos, pero no respalda por sí solo un grado que no aparece en esa instrucción.

## Fuentes consultadas

- **Documentación primaria:** [manual Gamma G2802AR](https://www.gammaherramientas.com.ar/web/wp-content/uploads/compresores_compresor-de-50-litros_G2802AR-102-manual.pdf); [manual Lüsqtoff LC-40100](https://lusqtoff.com.ar/2023/uploads/Productos/16.%20COMPRESORES/LC-40100/MANUAL/LC-40100.pdf); [manual Lüsqtoff LC-30100](https://lusqtoff.com.ar/2023/uploads/Productos/16.%20COMPRESORES/LC-30100/MANUAL/LC-30100.pdf).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/compresores/", "/compresores/gamma-50-litros/", "compresor Gamma de 50 litros",
    ),
    "paginas/compresores/06-acople-rapido-para-compresor.md": (
        "Matriz que separa el perfil del enchufe rápido de la rosca de conexión; contrasta perfiles normalizados y un acople BTA identificado por código.",
        """| Elemento que debe coincidir | Ejemplo documentado | Qué no se deduce |
| :--- | :--- | :--- |
| Perfil del enchufe y del acople | Parker publica tablas de intercambio de perfiles neumáticos; CEJN identifica perfiles y series específicas | La palabra “europeo” o el aspecto exterior no confirma compatibilidad |
| Diámetro nominal de la conexión | BTA ofrece el conector tipo italiano hembra 279106 de Ø 1/4″ | Ø 1/4″ no identifica por sí solo el perfil de enchufe ni la rosca |
| Rosca de montaje | Debe cotejarse en la ficha de cada pieza (por ejemplo, BSPP, BSPT o NPT) | No inferir NPT/BSP por el diámetro exterior aproximado |
| Válvula y desconexión | CEJN eSafe Series 300 describe un acople con descarga de presión antes de separar | No todas las hembras tienen función de descarga de seguridad |

**Dato documentado:** Parker y CEJN documentan varios perfiles de acople neumático. La ficha BTA del código 279106 identifica un conector hembra tipo italiano Ø 1/4″, lo que ofrece una referencia de producto local concreta; no certifica compatibilidad con cualquier macho comercializado como “universal”.

**Análisis TallerLab:** para comprobar una pareja hacen falta al menos dos identificadores independientes: perfil de acople y tipo/medida de rosca. Una rosca compatible no hace coincidir perfiles distintos, y un perfil compatible no resuelve una rosca incorrecta. La tabla de intercambio del fabricante del acople es la referencia; una prueba de ajuste sin presión no demuestra estanqueidad bajo servicio.

## Secuencia de identificación

| Orden | Comprobación | Evidencia que conviene guardar |
| ---: | :--- | :--- |
| 1 | Leer marca, código y perfil marcado en ambas piezas | Ficha o catálogo del fabricante |
| 2 | Confirmar rosca y género en cada extremo | Especificación del racor y del acople |
| 3 | Revisar presión nominal y mecanismo de cierre | Marcado/manual de los dos componentes |
| 4 | Despresurizar antes de desconectar | Procedimiento del equipo y del fabricante del acople |

**Desconocido:** no se declara qué perfil domina en todas las herramientas vendidas en Argentina ni qué combinación concreta encaja con una pieza sin código. Tampoco se asigna una rosca a partir de fotos o nombres comerciales.

## Fuentes consultadas

- **Documentación primaria:** [Parker, tabla de intercambio de acoples neumáticos](https://www.parker.com/content/dam/Parker-com/Divisions-2011/Quick-Coupling-Division/SupportAssets/PneuInterchgChart.pdf); [CEJN, guía de identificación de niples](https://prod.cejn.com/en-us/guides-support/toolbox/compressed-air-nipple-guide/); [catálogo BTA 2026/27, conector tipo italiano 279106](https://btatools.com.ar/catalogo/catalogo-bta-2026-27-1.pdf); [CEJN, eSafe Series 300](https://www.cejn.com/globalassets/documents/brochures/esafe-with-series-430-and-550/esafe-en.pdf).
- **Seguridad:** despresurizar y seguir instrucciones de acople y herramienta antes de separar una conexión.
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/compresores/", "/compresores/kits-accesorios/", "kits de accesorios para compresor",
    ),
    "paginas/compresores/17-compresor-bta-25-litros.md": (
        "Comparación del BTA de 25 L lubricado con el BTA de 24 L sin aceite; deja explícito que admisión y entrega útil son magnitudes distintas.",
        """| Modelo BTA | Código/modelo | Potencia | Tanque | Presión máx. | Caudal que declara BTA |
| :--- | :--- | ---: | ---: | ---: | :--- |
| Compresor 25 L | 272057.1 / D-CA1-25-6 | 1,5 kW (2 HP) | 25 L | 8 bar | Admisión: 206 L/min |
| Compresor portátil sin aceite 24 L | 272005 | 1,5 kW (2 HP) | 24 L | 8 bar | Admisión: 170 L/min en ficha consultada |

**Dato documentado:** la ficha BTA del 25 L especifica 220 V~50 Hz, 2.850 rpm, admisión de 206 L/min y tanque de 25 L. BTA presenta el 24 L como una variante portátil sin aceite; sus cifras describen esa ficha y no se transfieren al equipo de 25 L.

**Análisis TallerLab:** el modelo de 25 L declara 36 L/min más de admisión que el 24 L (21,2 % respecto de 170 L/min), pero no se publica una condición común de medición ni un caudal efectivo de salida a presión de trabajo. La resta sirve para comparar lo impreso en las fichas; no permite asegurar tiempos de inflado o aptitud para una herramienta neumática continua.

## Qué puede concluirse para una compra

| Pregunta | Respuesta con la evidencia disponible |
| :--- | :--- |
| ¿Es un tanque de 25 L? | Sí, la ficha del código 272057.1 declara 25 L |
| ¿Qué motor declara? | 1,5 kW / 2 HP, 220 V~50 Hz |
| ¿Cuánto aire entrega bajo carga? | No se localizó un valor de FAD comparable; 206 L/min es admisión declarada |
| ¿Se verificó el paquete y su garantía? | El catálogo vigente muestra el modelo; confirmar contenido y términos en el vendedor y documentación entregada |
| ¿Hay experiencia propia u opiniones resumidas? | No; no se probó la unidad ni se analizó una muestra de reseñas |

**Desconocido:** las fichas consultadas no bastan para recomendarlo para pintura continua, ni para declarar ciclos, ruido, tiempo de recuperación o repuestos disponibles. Compará el caudal de salida bajo una presión común con el consumo de la herramienta y usá la especificación del modelo exacto.

## Fuentes consultadas

- **Documentación primaria:** [BTA, ficha del modelo D-CA1-25-6](https://btatools.com.ar/producto/compresor-de-aire-25-litros-2-0-hp); [catálogo BTA 2026/27](https://btatools.com.ar/catalogo/catalogo-bta-2026-27-1.pdf); [BTA, compresor portátil sin aceite 24 L](https://btatools.com.ar/producto/compresor-de-aire-24-litros-2-0-hp-portatil-sin-aceite).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/compresores/", "/compresores/24-litros/", "compresor de 24 litros",
    ),
    "paginas/compresores/10-filtro-de-aire-para-compresor.md": (
        "Distingue el filtro de admisión de la unidad de filtro/regulador/lubricador BTA y registra dos caudales distintos en la ficha del conjunto.",
        """| Componente | Dónde trabaja | Dato de fabricante | Límite de lectura |
| :--- | :--- | :--- | :--- |
| Filtro de admisión del compresor | Entrada de aire de la bomba | El manual Gamma G2802AR ordena revisar y mantener limpio el filtro de admisión | No es el conjunto de tratamiento de línea |
| Filtro-regulador-lubricador BTA AA-2040I, código 802834.1 | Línea neumática aguas abajo del tanque | Conexión 1/2″; elemento filtrante de 5–40 µm; drenaje automático/manual; presión máxima 145 psi | La ficha muestra 50 NI/min como “pulverizado (caudal)” y 4.000 NI/min como caudal mínimo de goteo |

**Dato documentado:** el AA-2040I no es un repuesto de admisión: BTA lo describe como conjunto de filtro, regulador y lubricador para la línea de aire. Su propia ficha publica dos valores de caudal con rótulos distintos (50 y 4.000 NI/min), así que los transcribimos sin interpretarlos como una única capacidad de servicio.

**Análisis TallerLab:** la selección empieza por la ubicación y función del componente. El filtro de admisión protege la entrada indicada por el fabricante del compresor; el conjunto de línea trata el aire y regula la presión después del tanque. Una rosca de 1/2″, una filtración en micrones y un caudal son campos diferentes y ninguno sustituye a los otros.

## Comprobaciones antes de elegir

| Necesidad | Dato a cotejar |
| :--- | :--- |
| Reemplazar el elemento de entrada | Código del compresor y referencia de filtro indicada en su manual |
| Instalar tratamiento de línea | Rosca, presión nominal, sentido de flujo y caudal requerido de la unidad FRL |
| Filtrar partículas | Micronaje especificado y contaminante objetivo; no inferir pureza respirable |
| Lubricar herramienta | Confirmar si la herramienta requiere lubricación y el lubricante indicado |

**Desconocido:** BTA no aclara en la ficha consultada cómo se relacionan sus dos cifras de caudal ni las condiciones de medición. No deducimos que el conjunto quite toda el agua o todo contaminante, ni lo recomendamos para aire respirable o aplicaciones sensibles.

## Fuentes consultadas

- **Documentación primaria:** [BTA, filtro-regulador-lubricador AA-2040I](https://btatools.com.ar/producto/filtro-regulador-y-lubricador-de-aire-1-2); [manual Gamma G2802AR, mantenimiento del filtro de admisión](https://www.gammaherramientas.com.ar/web/wp-content/uploads/compresores_compresor-de-50-litros_G2802AR-102-manual.pdf); [catálogo BTA 2026/27](https://btatools.com.ar/catalogo/catalogo-bta-2026-27-1.pdf).
- **Seguridad:** instalar y mantener cada componente según su manual y la presión permitida.
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/compresores/", "/compresores/acoples-rapidos/", "acoples rápidos para compresor",
    ),
    "paginas/compresores/12-compresor-gamma-50-litros.md": (
        "Contraste del Gamma G2802AR con su versión en kit y exposición de la contradicción de potencia entre título, manual y tabla de producto.",
        """| Documento/producto | Tanque | Potencia publicada | Otros datos identificados |
| :--- | ---: | ---: | :--- |
| Gamma G2802AR, página de producto | 50 L | Título: 2,5 HP; tabla técnica: 2 HP | 220 V–50 Hz; 2.850 rpm; 27 kg |
| Gamma G2802AR, manual | 50 L | 2,5 HP | Manual compartido para las variantes 25 L (2,2 HP) y 50 L (2,5 HP) |
| Gamma G2802KAR, versión en kit | 50 L | 2,5 HP | La página presenta accesorios incluidos; confirmar su lista en la oferta concreta |

**Dato documentado:** la página Gamma del G2802AR presenta ambas cifras de potencia: “2.5 HP” en su título y “2 HP” en la tabla. El manual del fabricante identifica 2,5 HP para la variante de 50 L. Esa diferencia queda visible; no se promedian ni se oculta. El G2802KAR es la presentación en kit identificada en otra página Gamma.

**Análisis TallerLab:** para describir la variante de 50 L, el manual respalda 2,5 HP, mientras la tabla online conserva un valor contradictorio de 2 HP. La ficha disponible registra 27 kg, 220 V–50 Hz y 2.850 rpm. Antes de aplicar estas especificaciones a una unidad, cotejá placa y código completos; el sufijo KAR afecta la presentación del paquete.

## Diferencias que afectan la comparación

| Campo | G2802AR | G2802KAR | Qué falta confirmar |
| :--- | :--- | :--- | :--- |
| Presentación | Compresor G2802AR | Compresor comercializado como kit | El contenido exacto del vendedor |
| Capacidad | 50 L | 50 L | Que placa y embalaje coincidan con el código |
| Potencia | Manual: 2,5 HP; tabla de web: 2 HP | Página de kit: 2,5 HP | La cifra de la página técnica general es contradictoria |
| Caudal útil/FAD | No establecido en la página citada | No se usa para declarar herramienta compatible | Requerir condición comparable y presión de trabajo |

**Desconocido:** no afirmamos caudal efectivo, ciclo continuo, nivel sonoro medido, compatibilidad universal con pintura ni disponibilidad de repuestos. Las expresiones comerciales sobre usos no sustituyen al cotejo de consumo, presión y ciclo del accesorio neumático.

## Fuentes consultadas

- **Documentación primaria:** [Gamma G2802AR, ficha y descargas](https://www.gammaherramientas.com.ar/producto/compresor-de-50-litros/); [manual Gamma G2802AR](https://www.gammaherramientas.com.ar/web/wp-content/uploads/compresores_compresor-de-50-litros_G2802AR-102-manual.pdf); [Gamma G2802KAR, versión en kit](https://www.gammaherramientas.com.ar/producto/compresor-de-50-litros-en-kit/).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/compresores/", "/compresores/bta-25-litros/", "compresor BTA de 25 litros",
    ),
    "paginas/compresores/19-compresor-inalambrico.md": (
        "Comparación de infladores a batería con sus caudales declarados a distintas presiones; separa estos equipos sin tanque de los compresores para herramientas neumáticas.",
        """| Modelo a batería | Presión máxima | Caudal declarado | Tanque | Peso publicado |
| :--- | ---: | :--- | ---: | ---: |
| Einhell PRESSITO 18/25 | 11 bar | Aspiración 25 L/min; entrega 17 / 11 / 9 L/min a 0 / 4 / 7 bar | 0 L | 2,28 kg |
| Einhell PRESSITO 18/21 | 10,5 bar | Aspiración 21 L/min; entrega 14 / 9 / 6 L/min a 0 / 4 / 7 bar | 0 L | 2,06 kg |
| Makita DMP180Z | 8,3 bar | 12 / 8 / 7 L/min a 200 / 700 / 830 kPa | 0 L | 1,7 kg |

**Dato documentado:** Einhell identifica ambos PRESSITO como equipos Power X-Change de 18 V sin batería ni cargador incluidos en las configuraciones citadas; sus fichas publican tanque de 0 L. Makita DMP180Z es también un inflador portátil de batería con valores de caudal publicados por presión. No se confunden con compresores con calderín.

**Análisis TallerLab:** los caudales bajan al aumentar la presión en cada ficha, por lo que la cifra de aspiración no describe el caudal a presión alta. PRESSITO 18/25 declara 3 L/min más que 18/21 a 7 bar (50 % respecto de 6 L/min), pero no se usa esa diferencia para afirmar un tiempo real de inflado: condiciones, batería y medición no son un ensayo común. Tanque cero significa que estas fichas no respaldan su uso como depósito para alimentar de forma continua herramientas neumáticas.

## ¿Qué tipo de trabajo cubre esta categoría?

| Si necesitás… | Evidencia que importa |
| :--- | :--- |
| Inflar un neumático o balón | Presión objetivo y caudal a esa presión |
| Llevar el equipo en el vehículo | Batería compatible, accesorios y método de carga/energía |
| Alimentar una herramienta neumática | Caudal continuo a presión de trabajo y reserva; los tres ejemplos de esta tabla no tienen tanque |
| Comprar un kit listo para usar | Verificar si el código incluye batería, cargador, adaptadores y manguera |

**Desconocido:** no se compararon autonomía, tiempo de inflado por rueda, ruido o rendimiento con una batería común. Tampoco se afirma que la etiqueta “inalámbrico” implique tanque o compatibilidad con herramientas de taller.

## Fuentes consultadas

- **Documentación primaria:** [Einhell Argentina PRESSITO 18/25](https://www.einhell.com.ar/p/4020420-pressito-18-25/); [Einhell Argentina PRESSITO 18/21](https://www.einhell.com.ar/p/4020467-pressito-18-21/); [Makita Argentina DMP180Z](https://makita.com.ar/producto/978-inflador-inalambrico/); [catálogo Makita Argentina 2025](https://makita.com.ar/wp-content/uploads/2025/09/CATALOGO-2025-v2.pdf).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/compresores/", "/compresores/inflador-neumaticos-portatil/", "inflador portátil para neumáticos",
    ),
    "paginas/compresores/22-inflador-de-neumaticos-portatil.md": (
        "Comparación de dos infladores portátiles con condiciones de caudal muy distintas; identifica por qué el número destacado de Gadnic no se puede rankear frente a caudales Makita medidos a presión especificada.",
        """| Modelo | Alimentación | Presión máxima | Caudal publicado | Peso |
| :--- | :--- | ---: | :--- | ---: |
| Gadnic AV000009 | 12 V, conexión a batería | 150 PSI | 85 L/min en página; condición de presión no detallada junto al valor | 2,54 kg |
| Makita DMP180Z | Batería 18 V | 8,3 bar | 12 L/min a 200 kPa; 8 a 700 kPa; 7 a 830 kPa | 1,7 kg |

**Dato documentado:** Gadnic lista también 23 A máximos, doble cilindro y ciclo recomendado de 30 minutos, con un máximo de 40 minutos en su página. Makita publica caudales por presión y recomienda cotejar la configuración comercial, porque el sufijo Z corresponde al cuerpo de herramienta sin batería/cargador en la nomenclatura de esa ficha.

**Análisis TallerLab:** no es válida una clasificación simple entre 85 L/min de Gadnic y 7 L/min de Makita: la ficha Gadnic no presenta la condición de presión junto a su caudal, mientras Makita separa valores por presión. La tabla muestra qué dato falta para una comparación de tiempo de inflado: mismo volumen inicial/final, misma presión objetivo, fuente de energía y método de medición.

## Antes de comprar un inflador

| Comprobación | Qué buscar en la ficha/manual |
| :--- | :--- |
| Alimentación | Tensión, batería o conexión directa; corriente requerida |
| Presión | Límite máximo y ajuste de corte, si está documentado |
| Caudal | Valor asociado a una presión concreta, no solo un máximo promocional |
| Ciclo | Tiempo de marcha y pausa definidos para el modelo |
| Accesorios | Longitud de manguera, adaptadores y compatibilidad con la válvula |

**Desconocido:** no se midieron los minutos que tarda cada modelo en inflar una cubierta concreta ni su temperatura en marcha. No extrapolamos el ciclo Gadnic a otros infladores y no se analizó una muestra de reseñas de compradores.

## Fuentes consultadas

- **Información de producto:** [Gadnic AV000009](https://www.gadnic.com.ar/infladores-y-compresores/compresor-de-aire-12v-85l-min).
- **Documentación primaria:** [Makita Argentina DMP180Z](https://makita.com.ar/producto/978-inflador-inalambrico/); [catálogo Makita Argentina 2025](https://makita.com.ar/wp-content/uploads/2025/09/CATALOGO-2025-v2.pdf).
- **Opiniones de compradores:** hay contenido comercial en la página Gadnic, pero no se extrajo ni evaluó una muestra; no se atribuye un patrón de opinión a TallerLab.""",
        "/compresores/", "/compresores/inalambricos/", "infladores inalámbricos",
    ),
    "paginas/compresores/13-kit-para-compresor-de-aire.md": (
        "Comparación entre kits BTA de alimentación por gravedad y por succión, con piezas compartidas y condición de alimentación publicada.",
        """| BTA, código | Alimentación de pistola | Datos publicados | Elementos del conjunto que lista el catálogo |
| :--- | :--- | :--- | :--- |
| 279010 | Gravedad | Entrada 1/4″; 90 PSI sugeridos; compresor sugerido 2 HP | Pistola 600 cc con pico 1,5 mm, inflador con manómetro, soplete, pistola de lavado, manguera espiral de 5 m |
| 279013 | Succión | Entrada 1/4″; 90 PSI sugeridos; compresor sugerido 2 HP | Pistola 750 cc con alimentación por succión y los accesorios de aire listados en el kit |

**Dato documentado:** BTA distingue sus kits multiuso por el mecanismo de alimentación de la pistola: gravedad para el código 279010 y succión para el 279013. El catálogo identifica accesorios compartidos y sugiere 2 HP/90 PSI; son valores publicados por BTA, no una medición de TallerLab.

**Análisis TallerLab:** elegir “kit para compresor” requiere revisar la herramienta concreta incluida, no solo contar piezas. Los depósitos de 600 y 750 cc pertenecen a pistolas con sistemas de alimentación diferentes; no implican que una tenga mayor caudal de aire ni que ambas sean intercambiables. La sugerencia de potencia/presión del catálogo tampoco demuestra que cualquier compresor de 2 HP mantenga el caudal que una pistola necesita.

## Qué revisar en el anuncio

| Variable | Confirmación necesaria |
| :--- | :--- |
| Código del kit | 279010 o 279013 y lista de componentes coincidente |
| Pistola incluida | Tipo de alimentación, capacidad y pico declarados |
| Compresor | Caudal disponible a presión de trabajo, además de potencia |
| Conexión | Rosca/perfil de acople de manguera y herramienta |
| Garantía | Plazo y cobertura en la unidad vendida por el distribuidor |

**Desconocido:** el catálogo no demuestra cobertura con todos los compresores ni define tiempo de trabajo continuo para cada accesorio. No afirmamos resultados de acabado ni ausencia de pérdidas sin una prueba o fuente específica.

## Fuentes consultadas

- **Documentación primaria:** [catálogo BTA 2026/27](https://btatools.com.ar/catalogo/catalogo-bta-2026-27-1.pdf); [BTA, catálogo de productos para pintura](https://btatools.com.ar/producto-segmento/pintura?85441e4f_page=1); [BTA, compresor D-CA1-25-6 de referencia 2 HP](https://btatools.com.ar/producto/compresor-de-aire-25-litros-2-0-hp).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/compresores/", "/compresores/filtros/", "filtros y tratamiento de aire",
    ),
    "paginas/compresores/04-aerografo-con-compresor.md": (
        "Comprueba si el producto denominado kit incluye realmente compresor: BTA AP8 incluye aerógrafo y accesorios de conexión, mientras el compresor se sugiere aparte.",
        """| Configuración | Qué incluye o declara el fabricante | Lo que queda fuera |
| :--- | :--- | :--- |
| BTA AP8, código 279004.1 | Aerógrafo, manguera, soporte, frasco de preparación, conector a línea y vaso pequeño; presión máxima publicada 10 bar; compresor sugerido 2 HP | La lista no incluye compresor ni especifica caudal de aire |
| Badger 180-15 | Compresor para aerografía sin aceite; 1/6 HP, 20–23 L/min, rango 0–4 bar; manguera/conexiones según manual | No es el BTA AP8 y no se presenta como un paquete combinado con ese aerógrafo |

**Dato documentado:** la ficha BTA del AP8 enumera los componentes del kit y sugiere un compresor de 2 HP; el compresor no aparece en el contenido incluido. El manual Badger describe un compresor distinto, con sus propios límites de caudal y presión. No se ha confirmado una pareja de estos dos productos.

**Análisis TallerLab:** antes de comparar precios de “aerógrafo con compresor”, separá el aerógrafo, la manguera y el suministro de aire. La potencia sugerida por BTA no basta para confirmar compatibilidad con un compresor sin conocer presión y consumo requeridos por el aerógrafo en uso. Una ficha de otro fabricante tampoco cubre el dato ausente del AP8.

## Lista de componentes a verificar

| Componente | ¿BTA AP8 lo lista? | Qué revisar si se compra separado |
| :--- | :---: | :--- |
| Aerógrafo | Sí | Boquilla, acción y repuestos del modelo exacto; no aparecen todos esos datos en la ficha consultada |
| Manguera y conector | Sí | Tipo de rosca y adaptadores necesarios |
| Compresor | No | Caudal y presión de trabajo compatibles, método de regulación y ciclo |
| Filtro/regulador | No identificado en la lista del AP8 | Compatibilidad de conexiones y mantenimiento |

**Desconocido:** no se encontró una especificación de consumo de aire para AP8 que permita validar el Badger 180-15 o cualquier otro compresor como combinación. Tampoco se presentan resultados de pulverización, ruido o acabado probados por TallerLab.

## Fuentes consultadas

- **Documentación primaria:** [BTA, aerógrafo AP8 279004.1](https://btatools.com.ar/producto/aerografo-profesional); [manual Badger 180-15](https://www.badgerairbrush.com/PDF/New%20180-15%20Instruction%20Book.pdf); [BTA, filtro-regulador-lubricador](https://btatools.com.ar/producto/filtro-regulador-y-lubricador-de-aire-1-2).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/compresores/", "/compresores/kits-accesorios/", "kits de accesorios para compresor",
    ),
    "paginas/compresores/14-compresor-lusqtoff-100-litros.md": (
        "Tabla de tres líneas Lüsqtoff de 100 L identificadas por código y tecnología; registra contradicciones de peso y evita completar un caudal actual no confirmado.",
        """| Modelo Lüsqtoff | Configuración | Potencia/capacidad | Caudal publicado | Peso y estado de evidencia |
| :--- | :--- | :--- | ---: | :--- |
| LC-30100 / LC30100-8 | Bicilíndrico a correa | 3 HP; tanque 100 L | 335 L/min | Manual: 115 kg; catálogos anteriores: 78–85 kg |
| LC-40100 / LC40100-8 | Mando directo, dos cilindros | 4 HP; tanque 100 L | 360 L/min en manual y catálogo 2020/21 | Manual: 58 kg; la revisión actual de catálogo no confirma si sigue idéntico |
| LCS100-8 | Sin aceite, 100 L | La gama actual lista el código, pero no se verificó una ficha técnica primaria completa | Desconocido | No asignamos valores de modelos discontinuados |

**Dato documentado:** el manual LC-30100 publica 3 HP, 2.200 W, 100 L, 115 PSI y 335 L/min. El mismo manual declara 115 kg, mientras catálogos previos de Lüsqtoff muestran 78–85 kg. Para LC-40100, el manual consultado informa 4 HP, 100 L, 360 L/min y 58 kg; su catálogo 2020/21 registra 56,8 kg. El catálogo actual de la marca lista LC30100-8, LC40100-8 y LCS100-8 como referencias de gama.

**Análisis TallerLab:** las diferencias de peso del LC-30100 (30–37 kg entre documentos) son demasiado grandes para colapsarlas en una cifra única; podrían reflejar documento/modelo distinto, y la evidencia consultada no lo resuelve. Los caudales de LC-30100 y LC-40100 son cifras nominales documentadas en generaciones distintas; no calculamos una ventaja de entrega efectiva ni presumimos que todas las revisiones actuales coincidan.

## Criterio para cotejar una unidad de 100 L

| Verificación | Por qué importa |
| :--- | :--- |
| Código completo en placa y catálogo | Distingue correa, mando directo y versiones sin aceite |
| Peso del documento de esa revisión | El LC-30100 presenta valores discordantes según manual/catálogo |
| Caudal y condición de medición | L/min nominal no equivale a FAD bajo una presión dada |
| Alimentación y fase | Confirmar con la placa y la instalación existente |
| Mantenimiento y aceite | Seguir el manual del código exacto; no transferir instrucciones de otro modelo |

**Desconocido:** no se encontraron datos suficientes para publicar especificaciones del LCS100-8 ni para resolver peso de placa actual de LC-30100-8. Se retiraron del borrador los valores FAD, ruido, RPM y compatibilidad con herramientas que no contaban con documentación primaria localizada.

## Fuentes consultadas

- **Documentación primaria:** [manual Lüsqtoff LC-30100](https://lusqtoff.com.ar/2023/uploads/Productos/16.%20COMPRESORES/LC-30100/MANUAL/LC-30100.pdf); [manual Lüsqtoff LC-40100](https://lusqtoff.com.ar/2023/uploads/Productos/16.%20COMPRESORES/LC-40100/MANUAL/LC-40100.pdf); [catálogo Lüsqtoff 2020/21](https://lusqtoff.com.ar/files/Catalogo_Lusqtoff_2020.pdf); [catálogo Lüsqtoff 2022/23](https://www.lusqtoff.com.ar/files/catalogo-lq-2022-2023.pdf); [gama actual de compresores Lüsqtoff](https://lusqtoff.com.ar/ver-productos/16-compresores-de-aire).
- **Seguridad:** seguir placa y manual del modelo en instalación, lubricación y mantenimiento.
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/compresores/", "/compresores/100-litros/", "compresores de 100 litros",
    ),
}

for relpath, (asset, body, _hub, sibling, sibling_title) in PAGES.items():
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
    title_before = re.search(r"(?m)^title:.*$", front).group(0)
    url_before = re.search(r"(?m)^url:.*$", front).group(0)
    description = asset.replace('"', '\\"')
    front = re.sub(r"(?m)^description:.*$", f'description: "{description}"', front)
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
    if title_before != re.search(r"(?m)^title:.*$", front).group(0) or url_before != re.search(r"(?m)^url:.*$", front).group(0):
        raise RuntimeError(f"Cambió title o URL al preparar {path}")
    newbody = (
        f"# {h1_value}\n\n<!-- AUDITORIA_EDITORIAL_178 -->\n\n"
        f"**Dato documentado:** las cifras se atribuyen al fabricante o documento indicado en cada tabla. Los cálculos se identifican como **Análisis TallerLab**; lo que no se pudo confirmar queda como **Desconocido**. Esta guía es documental y no incluye prueba física.\n\n"
        f"## Cómo investigamos esta guía\n\n"
        f"- Tipo de análisis: documental\n- Prueba física de TallerLab: no\n- Especificaciones contrastadas: sí\n- Opiniones de compradores: no\n- Fuentes primarias: sí\n- Última revisión: 27/09/2026\n\n"
        f"{body}\n\n"
        f"Para seguir comparando: [{sibling_title}]({sibling}).\n\n"
        f"Para conocer el criterio editorial: [Cómo trabajamos](/como-trabajamos/).\n\n"
        f"Para explorar la categoría: [guías de compresores](/compresores/).\n"
    )
    path.write_text(f"---\n{front}\n---\n\n{newbody}", encoding="utf-8")
    print(relpath)
