"""Séptimo lote editorial: diez guías documentales de discos y amoladoras."""
from pathlib import Path
import re

ROOT = Path(__file__).parent

PAGES = {
    "paginas/14-disco-diamantado-segmentado.md": (
        "Bosch PRO Concrete y EXPERT Multi Material: segmento, material y medida",
        """| Disco Bosch | Materiales listados por el fabricante | Diámetro / agujero | Ancho de corte | Altura del segmento |
| :--- | :--- | :--- | ---: | ---: |
| PRO Concrete, 2 608 602 651 | Hormigón | 115 / 22,23 mm | 2,2 mm | 12 mm |
| EXPERT Multi Material, 2 608 900 659 | Hormigón, ladrillo, teja y hormigón armado | 115 / 22,23 mm | 2,2 mm | 12 mm |

**Dato verificado:** la tabla transcribe medidas y aplicaciones de dos discos Bosch de 115 mm. Ambos aparecen con segmento de 12 mm; el segundo amplía en su ficha la lista de materiales. Esto no convierte a los discos en aptos para cualquier piedra o material de construcción.

**Declaración del fabricante:** Bosch describe los segmentos del EXPERT Multi Material como soldados con láser y sus laterales estriados para evacuar polvo. Para PRO Concrete la ficha identifica su uso en hormigón. Las páginas no atribuyen a TallerLab pruebas de velocidad, temperatura o vida útil.

**Análisis TallerLab:** “segmentado” describe la geometría del borde, pero no alcanza para elegir el disco. En esta comparación el código y la lista de materiales diferencian dos productos que comparten diámetro, orificio, ancho y altura de segmento. Si la pieza es azulejo, la ficha de un disco cerámico continuo corresponde a otra aplicación ([comparación para cerámica](/amoladoras/discos-ceramica/)).

**Desconocido:** no se deduce de estas fichas si una operación debe ser seca o húmeda ni la profundidad efectiva en una pieza. Confirmá esa instrucción, el sentido de giro, las rpm máximas y la guarda en el producto y manual exactos.

## Comprobación de compatibilidad

| Antes de montar | Dato de estas referencias |
| :--- | :--- |
| Diámetro de disco de la amoladora | 115 mm en ambos ejemplos |
| Agujero y fijación | 22,23 mm, tuerca convencional según ficha |
| Material de la pieza | Hormigón para PRO Concrete; materiales enumerados para EXPERT Multi Material |
| Perfil del borde | Segmentado, 12 mm de altura de segmento en estas referencias |

## Fuentes consultadas

- **Documentación primaria:** [Bosch PRO Concrete, disco de 115 mm](https://www.bosch-professional.com/es/es/disco-de-corte-con-diamante-pro-concrete-para-amoladoras-pequenas-diametro-interior-de-22-23-mm-3089216-ocs-ac/); [Bosch EXPERT Multi Material](https://www.bosch-professional.com/ar/es/disco-de-corte-con-diamante-expert-hard-ceramic-de-larga-vida-util-para-amoladoras-pequenas-diametro-interior-de-22-23-mm-2867632-ocs-ac/).
- **Seguridad:** verificar diámetro, montaje, velocidad y aplicación en etiqueta y manual.
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "Comparación por código de dos discos diamantados segmentados Bosch con igual geometría y distinto alcance declarado de materiales.",
        "/amoladoras/",
        "/amoladoras/discos-ceramica/",
        "disco diamantado para cerámica",
    ),
    "paginas/01-disco-flap.md": (
        "Bosch PRO X571: grano, forma y rpm de discos flap de 115 mm",
        """| Referencia Bosch PRO X571 | Forma | Grano | Diámetro / agujero | Velocidad máxima publicada |
| :--- | :--- | ---: | :--- | ---: |
| 2 608 607 322 | Recta | 40 | 115 / 22,23 mm | 13.300 rpm |
| 2 608 607 324 | Recta | 80 | 115 / 22,23 mm | 13.300 rpm |
| 2 608 619 008 | Angular T29 | 40 | 115 / 22,23 mm | La ficha de esta variante no mostró el dato en el recorte consultado |
| 2 608 619 010 | Angular T29 | 80 | 115 / 22,23 mm | 13.300 rpm |

**Dato verificado:** las fichas Bosch identifican X571 con grano de circonio y uso de desbaste de metal. Los modelos rectos y angulares se ofrecen con varios granos; las tablas distinguen el código consultado para que no se atribuyan todos los datos a la familia completa.

**Análisis TallerLab:** entre los códigos rectos 322 y 324 cambia el grano de 40 a 80, pero el diámetro, orificio y límite de rpm publicado coinciden. Esto permite filtrar accesorios por acabado buscado, pero no predice por sí solo cuánto material quitará por minuto ni la terminación real. La forma recta o angular también debe corresponder al apoyo y la aplicación indicados por el fabricante.

**Declaración del fabricante:** Bosch atribuye al PRO X571 desbaste de metal, granos de circonio y refuerzo X-cloth; la página anuncia hasta 1,5 veces más velocidad frente al X431 bajo su comparación. Es una afirmación de Bosch, no una medición de TallerLab.

**Desconocido:** no recomendamos un grano universal para cada tipo de acero ni extrapolamos las rpm máximas entre variantes. Revisá el código, material admitido y velocidad marcada en cada accesorio.

## Ruta de selección documental

| Necesidad declarada | Opción en la matriz | Dato que debe verificarse |
| :--- | :--- | :--- |
| Desbaste de metal con grano 40 | X571 recto 2 608 607 322 | Forma, rpm y apoyo compatibles |
| Grano 80 en la misma familia | X571 recto 2 608 607 324 | Acabado buscado; no hay ensayo independiente |
| Forma angular T29 | X571 2 608 619 008 / 010 | Que el ángulo y guarda del equipo admitan el uso |

## Fuentes consultadas

- **Documentación primaria:** [Bosch PRO X571 recto](https://www.bosch-professional.com/ar/es/disco-flap-pro-x571-para-amoladoras-angulares-pequenas-version-recta-fibra-3065170-ocs-ac/); [Bosch PRO X571 angular](https://www.bosch-professional.com/ar/es/disco-flap-pro-metal-x571-para-amoladoras-angulares-pequenas-version-en-angulo-fibra-3065169-ocs-ac/).
- **Seguridad:** la velocidad máxima del accesorio debe ser igual o superior a la de la amoladora, según manual y etiqueta.
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "Tabla de códigos Bosch X571 que cruza forma, grano y rpm máxima documentada.",
        "/amoladoras/",
        "/amoladoras/discos/",
        "guía general de discos para amoladora",
    ),
    "paginas/09-disco-para-cortar-ceramica.md": (
        "Bosch PRO Ceramic y EXPERT HardCeramic: borde turbo o continuo",
        """| Disco Bosch | Diseño descrito | Diámetro / agujero | Ancho de corte | Altura de segmento |
| :--- | :--- | :--- | ---: | ---: |
| PRO Ceramic, 2 608 602 478 | Segmento turbo | 115 / 22,23 mm | 1,4 mm | 7 mm |
| EXPERT HardCeramic, 2 608 900 654 | Borde continuo | 115 / 22,23 mm | 1,4 mm | 10 mm |

**Dato verificado:** Bosch describe ambos productos para corte de azulejos/cerámica. Las fichas publican la misma medida nominal de 115 mm, agujero de 22,23 mm y ancho de corte de 1,4 mm; difieren en el diseño declarado del borde y la altura publicada.

**Declaración del fabricante:** Bosch atribuye al disco PRO Ceramic un segmento turbo y al EXPERT HardCeramic un borde continuo diseñado para cortes de precisión en baldosas duras. Las promesas de precisión y menor desconchado son afirmaciones del fabricante, no resultados propios de TallerLab.

**Análisis TallerLab:** en esta comparación, el grosor nominal de 1,4 mm no basta para elegir: el PRO Ceramic se describe con segmento turbo y el EXPERT HardCeramic con borde continuo. La ficha del EXPERT menciona cerámica dura; no trasladamos ese alcance a cualquier revestimiento ni suponemos que las técnicas de uso sean idénticas. Para porcelanato, revisá también la [guía de accesorios para porcelanato](/taladros/mecha-porcelanato/).

**Desconocido:** las páginas consultadas no validan una velocidad de corte, una técnica de refrigeración universal ni un resultado en cada cerámica. La compatibilidad con amoladora depende del diámetro, agujero, sistema de montaje y velocidad de la variante.

## Antes de elegir

| Comprobación | Dato que aparece en estas fichas |
| :--- | :--- |
| Material indicado | Azulejos/baldosas; el EXPERT especifica cerámica dura |
| Montaje | Agujero 22,23 mm; Bosch indica uso en amoladoras con tuerca o X-Lock según variante |
| Perfil | Turbo en PRO Ceramic; continuo en EXPERT HardCeramic |
| Espesor de corte | 1,4 mm en ambos modelos comparados |

## Fuentes consultadas

- **Documentación primaria:** [Bosch PRO Ceramic](https://www.bosch-professional.com/ar/es/disco-de-corte-con-diamantes-pro-ceramic-para-amoladoras-angulares-pequenas-orificio-de-22-23-mm-3088608-ocs-ac/); [Bosch EXPERT HardCeramic](https://www.bosch-professional.com/ar/es/discos-de-corte-de-diamante-expert-hardceramic-2868235-ocs-ac/).
- **Seguridad:** revisar variante de fijación, velocidad y uso del accesorio en el manual.
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "Comparación dimensional Bosch de discos para azulejo con segmentos turbo y borde continuo.",
        "/amoladoras/",
        "/amoladoras/disco-diamantado-segmentado/",
        "disco diamantado segmentado",
    ),
    "paginas/24-disco-para-cortar-vidrio.md": (
        "Vidrio y discos de amoladora: qué aplicación no queda confirmada",
        """| Pregunta previa | Resultado de la fuente primaria consultada |
| :--- | :--- |
| ¿Bosch ofrece una hoja diamantada de amoladora diseñada para vidrio? | La página de preguntas frecuentes de Bosch dice que no dispone de una hoja diamantada para vidrio en su gama actual consultada |
| ¿Un disco para cerámica queda aprobado para vidrio por esa razón? | No; la fuente no declara esa compatibilidad |
| ¿Se puede trasladar una recomendación de cortavidrios manual a una amoladora? | No; son herramientas y procesos diferentes |
| ¿Qué debe confirmar una ficha antes de usar disco rotativo? | Tipo de vidrio, máquina, diámetro, agujero, rpm, montaje y resguardo |

**Dato verificado:** Bosch indica en su FAQ de accesorios que no ofrece actualmente una hoja diamantada para vidrio en su gama consultada. Esto describe el catálogo de Bosch, no prueba que ningún fabricante venda un accesorio específico para vidrio.

**Análisis TallerLab:** una oferta que diga “diamantado”, “cerámica” o “multiuso” no acredita por sí sola que el accesorio sea apto para cortar vidrio. En las fuentes consultadas no encontramos un disco Bosch para esa aplicación; por eso no publicamos una combinación de disco, vidrio y amoladora como recomendación verificada. La matriz anterior identifica qué dato debe aparecer en una fuente del fabricante antes de seguir.

**Declaración del fabricante:** Bosch recomienda utilizar hojas de diamante únicamente en máquinas y diámetros indicados en los manuales de la herramienta, montar con brida y no usar la amoladora sin protector. Estas instrucciones son generales de Bosch para sus accesorios y no autorizan el corte de vidrio.

**Desconocido:** no se verificó una ficha primaria de disco rotativo para vidrio que incluya forma de montaje, rpm y tipos de vidrio admitidos. Tampoco se evaluó un cortavidrios, un sistema de refrigeración o una técnica de corte. La composición del vidrio y la sujeción cambian los riesgos; consultá documentación del accesorio y equipo exactos.

## Alternativa para corte recto

**Análisis TallerLab:** si la tarea es una línea recta en una plancha, compará el proceso con un cortavidrios manual y una regla guía; la elección debe depender del tipo de vidrio y el acabado requerido. Esta página no declara que una técnica sirva para vidrio templado, laminado u otro tipo sin una fuente específica.

## Fuentes consultadas

- **Documentación primaria:** [FAQ Bosch sobre discos de diamante y vidrio](https://www.bosch-professional.com/es/es/disco-de-corte-con-diamante-expert-hard-ceramic-de-larga-vida-util-para-amoladoras-pequenas-x-lock-2867633-ocs-ac/); [guía Bosch de compatibilidad y montaje de discos](https://www.bosch-professional.com/es/es/disco-de-corte-con-diamante-expert-hard-ceramic-de-larga-vida-util-para-amoladoras-pequenas-x-lock-2867633-ocs-ac/).
- **Desconocido:** no se enlaza una oferta como recomendación técnica sin documentación del uso en vidrio.
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "Matriz de comprobación para no dar por aprobados en vidrio discos anunciados para otros materiales.",
        "/amoladoras/",
        "/amoladoras/discos-ceramica/",
        "disco para cerámica",
    ),
    "paginas/02-discos-para-amoladora.md": (
        "Matriz de compatibilidad Bosch: disco según operación y material declarado",
        """| Operación | Accesorio Bosch documentado | Material declarado | Dimensiones identificadas |
| :--- | :--- | :--- | :--- |
| Cortar metal | PRO Metal 2 608 619 252 | Metal | 115 × 1,6 × 22,23 mm |
| Desbastar metal | PRO Metal 2 608 600 218 | Metal | 115 × 6 × 22,23 mm |
| Lijar/desbastar metal | Flap PRO X571, 2 608 607 322 | Acero y acero inoxidable en la familia | 115 mm, grano 40, agujero 22,23 mm |
| Cortar hormigón | PRO Concrete 2 608 602 651 | Hormigón | 115 mm, agujero 22,23 mm, segmento 12 mm |
| Cortar azulejo | PRO Ceramic 2 608 602 478 | Azulejos/cerámica | 115 × 1,4 × 22,23 mm |

**Dato verificado:** la matriz utiliza cinco códigos Bosch distintos. La categoría de material está tomada de la ficha de cada accesorio; la tabla no pretende cubrir todas las marcas, aleaciones ni modelos de disco.

**Análisis TallerLab:** para evitar confusiones, identificá primero la operación (cortar, desbastar o lijar), luego el material y finalmente las dimensiones. En los ejemplos, el disco rígido de desbaste mide 6 mm de espesor, frente a 1,6 mm del disco de corte; el flap es un accesorio de láminas abrasivas. El diámetro común de 115 mm no hace que estos usos sean intercambiables.

**Declaración del fabricante:** Bosch publica la velocidad máxima admisible y materiales por código de accesorio. El manual de la amoladora exige que rpm del accesorio sean compatibles con las de la herramienta y que se utilicen la guarda y bridas indicadas.

**Desconocido:** no se deduce por el nombre de una categoría que el disco sirva para vidrio, aluminio u otro material no mostrado en la fila. La tabla tampoco fija una técnica o velocidad para la pieza. Comprobá la etiqueta del accesorio exacto y las indicaciones del manual.

## Regla de lectura para la etiqueta

| Campo de la etiqueta | Comprobación |
| :--- | :--- |
| Diámetro exterior | No debe superar el máximo de la amoladora |
| Agujero y fijación | Debe coincidir con brida, tuerca o sistema X-Lock admitido |
| Velocidad máxima | Debe ser igual o mayor que las rpm máximas de la herramienta |
| Material y operación | Debe incluir expresamente el trabajo que vas a hacer |

## Fuentes consultadas

- **Documentación primaria:** [Bosch disco PRO Metal de corte](https://www.bosch-professional.com/ar/es/disco-de-corte-abrasivo-pro-metal-para-amoladoras-angulares-pequenas-x-lock-3090752-ocs-ac/); [Bosch disco PRO Metal de desbaste](https://www.bosch-professional.com/ar/es/disco-de-desbaste-abrasivo-pro-metal-para-amoladoras-angulares-pequenas-orificio-de-22-23-mm-osa-3090771-ocs-ac/); [Bosch flap PRO X571](https://www.bosch-professional.com/ar/es/disco-flap-pro-x571-para-amoladoras-angulares-pequenas-version-recta-fibra-3065170-ocs-ac/); [Bosch PRO Concrete](https://www.bosch-professional.com/es/es/disco-de-corte-con-diamante-pro-concrete-para-amoladoras-pequenas-diametro-interior-de-22-23-mm-3089216-ocs-ac/); [Bosch PRO Ceramic](https://www.bosch-professional.com/ar/es/disco-de-corte-con-diamantes-pro-ceramic-para-amoladoras-angulares-pequenas-orificio-de-22-23-mm-3088608-ocs-ac/).
- **Seguridad:** [manual Bosch para amoladoras](https://www.bosch-professional.com/binary/manualsmedia/o606197v21_160992AD3S_202509.pdf).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "Matriz propia de cinco accesorios que separa corte, desbaste, flap y diamante por uso y material.",
        "/amoladoras/",
        "/amoladoras/disco-de-corte/",
        "disco de corte para amoladora",
    ),
    "paginas/23-amoladoras-dowen-pagio.md": (
        "Dowen Pagio 9993220.7, 9993220.9 y 9993224.2: potencia no es la única diferencia",
        """| Código Dowen Pagio | Potencia declarada | Disco máximo | Velocidad sin carga | Control de velocidad | Eje |
| :--- | ---: | ---: | ---: | :--- | :--- |
| 9993220.7 / AA115H4 | 900 W | 115 mm | 12.000 rpm | No indicado como variable | M14 (5/8–11) |
| 9993220.9 / AA115SP2 | 1.050 W | 115 mm | 12.000 rpm | No indicado como variable | M14 (5/8–11) |
| 9993224.2 / AA125SPL | 1.250 W | 115/125 mm | 4.000–12.000 rpm | Variable | M14 (5/8–11) |

**Dato verificado:** el catálogo Dowen Pagio 2025 publica esos códigos y valores. También indica 220 V~50 Hz para los modelos. El título AA115SP2 presenta 1050 W con disco de 115 mm, aunque la tabla del fabricante nombra 115 mm; se usa esa medida documentada y no se infiere un disco de 125 mm.

**Análisis TallerLab:** el 9993220.9 declara 150 W más que el 9993220.7 y ambos publican 12.000 rpm sin carga y 115 mm. El 9993224.2 suma control variable y acepta 115/125 mm según el catálogo. Estas diferencias ayudan a identificar funciones y consumibles, pero no prueban más rapidez o calidad en uso.

**Declaración del fabricante:** el catálogo informa que los modelos 9993220.7 y 9993220.9 no incluyen disco de corte; no asumas que un kit comercial trae el mismo contenido. Verificá guardas, brida, interruptor y código completo al recibir el producto.

**Desconocido:** no se verificó disponibilidad, precio ni garantía de cada variante en el mercado actual. El catálogo no publica en la tabla una medida de peso común que permita comparar masa.

## Qué cambia entre estos códigos

| Si necesitás… | Referencia documentada | Límite de esta comparación |
| :--- | :--- | :--- |
| Disco fijo de 115 mm | 9993220.7 o 9993220.9 | Potencia diferente, rpm iguales en catálogo |
| Ajustar las rpm | 9993224.2 | Revisar rango y manual según accesorio |
| Usar disco de 125 mm | 9993224.2 | Confirmar que la guarda y variante ofertada correspondan |

## Fuentes consultadas

- **Documentación primaria:** [catálogo oficial Dowen Pagio 2025](https://www.dowenpagioweb.com.ar/inventario/Catalogo-Dowen-Pagio-2025.pdf).
- **Seguridad:** usar discos compatibles con diámetro, agujero, velocidad y guarda del modelo.
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "Comparación de tres códigos Dowen Pagio según potencia, disco, rpm y control variable, usando catálogo de fabricante.",
        "/amoladoras/",
        "/amoladoras/gamma/",
        "amoladoras Gamma",
    ),
    "paginas/21-amoladoras-gamma.md": (
        "Gamma G1910KAR en kit y G1917AR: potencia, disco y contenido publicado",
        """| Dato de ficha oficial | Gamma G1910KAR, kit | Gamma G1917AR |
| :--- | ---: | ---: |
| Potencia | 750 W | 850 W |
| Velocidad sin carga | 11.000 rpm | 11.000 rpm |
| Diámetro de disco | 115 mm | 115 mm |
| Rosca de eje | M14 × 2 | M14 × 2 |
| Accesorios publicados | 5 discos de corte, 5 discos de desbaste y maletín | Mango, guarda y llave según página de producto |
| Alimentación | 220 VCA / 50 Hz | 220 VCA / 50 Hz |

**Dato verificado:** los datos proceden de las páginas oficiales Gamma para estos dos SKU. Gamma denomina el primero G1910KAR y al segundo G1917AR; no usar el sufijo “KAR” para asumir que otro modelo incluye accesorios.

**Análisis TallerLab:** ambos modelos publican 11.000 rpm y disco de 115 mm. El G1917AR declara 100 W más; la diferencia útil del kit G1910KAR está en el contenido de caja publicado. No verificamos si el conjunto de discos cubre la tarea del comprador ni comparamos el precio del paquete con compras por separado.

**Declaración del fabricante:** Gamma describe el G1910KAR para corte, desbaste y esmerilado de metal, piedra y hormigón; la página del G1917AR enumera metal, madera y otros materiales. Esta diferencia de redacción no amplía la aplicación permitida por la ficha de discos: el accesorio exacto debe estar indicado para el material.

**Desconocido:** no se revisó una muestra de compradores ni disponibilidad/garantía vigente por tienda. Confirmá que el aviso corresponda al código exacto y que los consumibles y el maletín estén incluidos.

## Comprobación del kit

| Confirmar en la publicación | G1910KAR según Gamma |
| :--- | :--- |
| Máquina | Amoladora de 750 W, disco 115 mm |
| Discos | Gamma enumera cinco discos de corte y cinco de desbaste |
| Guardado | Maletín transportador incluido en ficha |
| Compatibilidad | Eje M14 × 2 y 220 VCA / 50 Hz |

## Fuentes consultadas

- **Documentación primaria:** [Gamma G1910KAR, amoladora en kit](https://www.gammaherramientas.com.ar/producto/amoladora-angular-750-w/); [Gamma G1917AR, 850 W](https://www.gammaherramientas.com.ar/producto/amoladora-angular-850w/).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "Ficha comparativa de Gamma G1910KAR y G1917AR, con contenido de kit atribuido al fabricante.",
        "/amoladoras/",
        "/amoladoras/dowen-pagio/",
        "amoladoras Dowen Pagio",
    ),
    "paginas/08-amoladoras-inalambricas.md": (
        "Bosch GWS 18V-10 PC e INGCO CAGLI1151: discos y plataformas distintos",
        """| Dato publicado | Bosch GWS 18V-10 PC | INGCO CAGLI1151 |
| :--- | ---: | ---: |
| Plataforma indicada | 18 V Bosch Professional | 20 V INGCO |
| Diámetro de disco | 125 mm | 115 mm |
| Velocidad sin carga | 9.000 rpm | 8.500 rpm |
| Rosca de eje | M14 | M14 |
| Peso | 2,0 kg sin batería; 2,8 kg con batería | No publicado en ficha consultada |
| Batería y cargador | Bosch 18 V compatibles; la ficha depende de variante/kit | Se venden por separado |

**Dato verificado:** las especificaciones se refieren a Bosch 0 601 9G3 E0B y al INGCO CAGLI1151 de la ficha oficial. La página INGCO no confirma disponibilidad en Argentina; la ficha Bosch sí pertenece al sitio regional argentino.

**Análisis TallerLab:** en estos dos códigos la herramienta Bosch admite un disco de 10 mm mayor y publica 500 rpm más sin carga. Es una diferencia de catálogo, no un ensayo de corte. Las etiquetas de 18 V y 20 V pertenecen a plataformas distintas y no permiten deducir autonomía, potencia bajo carga o compatibilidad cruzada.

**Declaración del fabricante:** Bosch describe motor brushless y declara potencia equivalente a una herramienta con cable de 1.000 W; es una equivalencia publicitaria del fabricante. INGCO indica que CAGLI1151 se vende sin batería ni cargador. Ninguna declaración reemplaza una prueba común de corte.

**Desconocido:** no se compararon minutos de trabajo, cortes por carga, batería equivalente, peso completo del INGCO ni condiciones de uso. Para decidir, comprobá batería/cargador incluidos, diámetro de disco, guarda, código de mercado y disponibilidad de repuestos.

## Costo de entrada: una lista de verificación

| Partida | Bosch GWS 18V-10 PC | INGCO CAGLI1151 |
| :--- | :--- | :--- |
| Cuerpo de herramienta | Código 0 601 9G3 E0B | Código CAGLI1151 |
| Batería/cargador | Compatibles con sistema Bosch Professional 18 V | No incluidos según ficha |
| Disco | 125 mm máximo | 115 mm máximo |
| Peso del cuerpo | 2,0 kg | No publicado |

## Fuentes consultadas

- **Documentación primaria:** [Bosch GWS 18V-10 PC Argentina](https://www.bosch-professional.com/ar/es/products/gws-18v-10-pc-06019G3E0B); [INGCO CAGLI1151](https://www.ingco.com/product/cordless-angle-grinder/CAGLI1151); [INGCO, baterías y plataforma 20 V](https://www.ingco.com/cl-en/products/cordless-tools).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "Comparación de dos amoladoras inalámbricas que separa plataforma, diámetro, velocidad y kit de batería.",
        "/amoladoras/",
        "/amoladoras/ingco/",
        "amoladoras INGCO",
    ),
    "paginas/17-amoladoras-ingco.md": (
        "INGCO AG750282, AG8508 y AG200018: modelos y mercados identificados",
        """| Código INGCO | Mercado de página consultada | Potencia | Diámetro de disco | Velocidad en vacío | Eje |
| :--- | :--- | ---: | ---: | ---: | :--- |
| AG750282 | India | 750 W | 100 mm | 12.000 rpm | M10 |
| AG8508 | Egipto | 950 W | 115 mm | 11.000 rpm | M14 |
| AG200018 | India | 2.000 W | 180 mm | 8.450 rpm | M14 |
| CAGLI1151 | Ficha global | 20 V | 115 mm | 8.500 rpm | M14 |

**Dato verificado:** cada fila corresponde a un código de la documentación oficial INGCO. Las páginas corresponden a mercados distintos y no prueban la disponibilidad, tensión de red o garantía de esos modelos en Argentina. AG750282 admite 100 mm, no 115 mm; no confundas variantes por la potencia publicada.

**Análisis TallerLab:** las fichas muestran que “amoladora INGCO” no identifica un único tamaño: esta selección cubre 100, 115 y 180 mm. El AG200018 declara 1.250 W más que el AG8508 y un diámetro 65 mm mayor, pero publica una velocidad en vacío menor; no se deduce de esos números el ritmo o la calidad de corte. CAGLI1151 usa una plataforma de batería y no se compara por vatios con los modelos con cable.

**Declaración del fabricante:** INGCO identifica códigos de batería y características de cada versión por página regional. En CAGLI1151 indica que batería, cargador y disco no están incluidos. Esos contenidos no se trasladan a otros códigos ni a kits locales.

**Desconocido:** esta revisión no confirma distribuidores, servicio posventa, repuestos ni garantía en Argentina para AG750282, AG8508 o AG200018. Antes de comprar, cotejá etiqueta eléctrica, tamaño de disco, rosca, guarda y consumibles disponibles en el mercado local.

## Selección por diámetro y alimentación

| Requisito | Código en esta muestra | Límite documental |
| :--- | :--- | :--- |
| Disco de 100 mm | AG750282 | Ficha india, 220–240 V según fabricante local de esa página |
| Disco de 115 mm con cable | AG8508 | Ficha de Egipto, 220–240 V~50/60 Hz |
| Disco de 180 mm con cable | AG200018 | Ficha de India, confirmar tensión y variante ofrecida |
| Movilidad sin cable | CAGLI1151 | 20 V, batería/cargador aparte |

## Fuentes consultadas

- **Documentación primaria:** [INGCO AG750282](https://www.ingco.com/in/product/angle-grinder/AG750282); [INGCO AG8508](https://www.ingco.com/eg-en/product/angle-grinder/AG8508); [INGCO AG200018](https://www.ingco.com/in/product/angle-grinder/AG200018); [INGCO CAGLI1151](https://www.ingco.com/product/cordless-angle-grinder/CAGLI1151).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "Tabla por código de cuatro amoladoras INGCO con dimensiones y mercados de las fichas oficiales consultadas.",
        "/amoladoras/",
        "/amoladoras/inalambricas/",
        "amoladoras inalámbricas",
    ),
    "paginas/11-amoladoras-lusqtoff.md": (
        "Lusqtoff AML850-8, AML1010-8 y AML115-9B: con cable y a batería",
        """| Código | Alimentación | Potencia/tensión | Disco | Velocidad publicada | Peso publicado |
| :--- | :--- | :--- | ---: | ---: | ---: |
| AML850-8 | Cable | 850 W; 220 V~50 Hz | 115 mm | 11.000 rpm | 2,60 kg |
| AML1010-8 | Cable | 1.010 W; 220 V~50 Hz | Hasta 125 mm | Variable, 0–11.000 rpm; seis posiciones | 2,60 kg |
| AML115-9B | Batería Iron Volt | 18 V | 115 mm | 0–8.500 rpm | 2,1 kg |

**Dato verificado:** AML850-8 y AML1010-8 aparecen en el catálogo Lusqtoff 2024–2025; AML115-9B figura en el catálogo de herramientas inalámbricas Black Series. El peso y la configuración corresponden a esos códigos, no a toda la marca.

**Análisis TallerLab:** AML1010-8 declara 160 W más que AML850-8 y agrega velocidad variable y soporte de disco de hasta 125 mm en catálogo. AML115-9B es inalámbrica y la ficha actual indica que no incluye batería ni cargador. Las rpm máximas publicadas no permiten comparar corte bajo carga entre cable y batería.

**Declaración del fabricante:** Lusqtoff indica rosca M14 en los modelos con cable descritos, protección antipolvo en AML850-8 y tecnología brushless en AML115-9B. La página del AML115-9B también lista guarda de ajuste rápido y gatillo de hombre muerto. Son funciones atribuidas al código, no mediciones de TallerLab.

**Desconocido:** no se verificaron autonomía, capacidad de corte, vibración comparativa, disponibilidad actual del catálogo antiguo ni garantía de una publicación concreta. La página de la batería AML115-9B no incluye cargador ni batería; sumalos al costo total si no los tenés.

## Filtro por trabajo y paquete

| Prioridad | Código documentado | Dato a tener en cuenta |
| :--- | :--- | :--- |
| Alimentación con cable y disco de 115 mm | AML850-8 | 850 W, velocidad fija en catálogo |
| Velocidad variable y opción de 125 mm | AML1010-8 | Confirmar guarda y disco del código vendido |
| Movilidad en sistema Iron Volt | AML115-9B | Batería y cargador vendidos aparte según fabricante |

## Fuentes consultadas

- **Documentación primaria:** [catálogo Lusqtoff 2024–2025, AML850-8 y AML1010-8](https://www.lusqtoff.com.ar/2023/uploads/Catalogos/CAT%C3%81LOGO%20LQ%202024-2025%20-%20web%20%281%29.pdf); [Lusqtoff AML115-9B](https://lusqtoff.com.ar/ver-producto/AML115-9B); [catálogo oficial de herramientas Black Series](https://www.lusqtoff.com.ar/ver-productos/18-black-series).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "Comparación de fichas Lusqtoff con cable y batería: potencia, diámetro, rpm, peso y contenido de kit.",
        "/amoladoras/",
        "/amoladoras/inalambricas/",
        "amoladoras inalámbricas",
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
        f"# {h1_value}\n\n<!-- AUDITORIA_EDITORIAL_178 -->\n\n{body}\n\n"
        f"Para seguir comparando: [{sibling_title}]({sibling}).\n\n"
        f"Para explorar la categoría: [guías de amoladoras]({hub}).\n"
    )
    path.write_text(f"---\n{front}\n---\n\n{newbody}", encoding="utf-8")
    print(relpath)
