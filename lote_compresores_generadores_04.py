"""Décimo lote editorial: ocho guías de compresores y dos de generadores."""
from pathlib import Path
import re

ROOT = Path(__file__).parent

PAGES = {
    "paginas/compresores/09-compresor-lusqtoff-50-litros.md": (
        "Tabla de tres modelos Lüsqtoff de 50 L: separa datos completos de ficha, cifras de variantes y campos aún sin documentación primaria.",
        """| Modelo | Configuración documentada | Potencia | Caudal publicado | Peso | Límite documental |
| :--- | :--- | ---: | ---: | ---: | :--- |
| LC2550B-8 | Lubricado, 50 L | 2,5 HP / 1.750 W | 206 L/min | 30 kg | La ficha no identifica método de medición del flujo |
| LC2550VS | Sin aceite, 50 L | 2,5 HP / 1.750 W | 230 L/min | No publicado en la ficha consultada | La presión acústica indicada es 72 dB; no se compara sin condiciones equivalentes |
| LCS50-8 | La gama actual lista el código como compresor sin aceite de 50 L | Desconocida | Desconocido | Desconocido | No se localizó ficha primaria completa del código |

**Dato verificado:** Lüsqtoff publica para el LC2550B-8 220 V–50 Hz, 115 psi, 206 L/min, tanque de 50 L y 30 kg. Para el LC2550VS publica el mismo tanque y potencia nominal, 115 psi y 230 L/min. Son datos de fichas distintas; la marca no explica en ellas una condición común para medir ambos caudales.

**Análisis TallerLab:** la resta entre los flujos impresos es 24 L/min (11,7 % sobre 206), pero no demuestra que el VS entregue más aire útil bajo carga: no hay FAD ni método de medición común indicado. El LC2550B-8 y LC2550VS comparten capacidad y potencia declaradas, aunque difieren en lubricación y en los caudales publicados. Para LCS50-8 no transferimos cifras de otros modelos de 50 L.

**Desconocido:** la documentación consultada no confirma caudal efectivo, peso del LC2550VS, ni especificaciones completas del LCS50-8. Tampoco permite deducir desempeño continuo o compatibilidad con una herramienta solo por potencia y capacidad del tanque.

## Fuentes consultadas

- **Documentación primaria:** [ficha Lüsqtoff LC2550B-8](https://www.lusqtoff.com.ar/productos/compresor-de-aire-o-25-hp-50-lts-lc2550b-8); [ficha Lüsqtoff LC2550VS](https://lusqtoff.com.ar/ver-producto/LC-2550VS); [gama actual de compresores Lüsqtoff](https://lusqtoff.com.ar/ver-productos/16-compresores-de-aire); [manual LC2550VS](https://www.lusqtoff.com.ar/2023/uploads/Productos/NUEVOS/COMPRESORES_DE_AIRE/LC-2550VS/MANUAL/LC-2550VS.pdf).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/compresores/", "/compresores/100-litros/", "compresor Lüsqtoff de 100 litros",
    ),
    "paginas/compresores/03-manguera-para-compresor-de-aire.md": (
        "Tabla de dimensionamiento Parker que cruza conexión, largo, diámetro interno mínimo, presión y caudal; distingue esa tabla técnica de una recomendación universal.",
        """| Conexión indicada por Parker | Largo de manguera | Diámetro interno mínimo | Presión mínima de la tabla | Caudal a 6 bar publicado |
| :--- | :--- | ---: | ---: | ---: |
| 1/4″ | 0–10 m | 7 mm | 4 bar | 480 L/min |
| 1/4″ | 10–20 m | 8 mm | 4 bar | 480 L/min |
| 3/8″ | 0–10 m | 10 mm | 4 bar | 1.100 L/min |
| 3/8″ | 10–20 m | 12 mm | 4 bar | 1.100 L/min |
| 1/2″ | 0–10 m | 12 mm | 4 bar | 2.000 L/min |
| 1/2″ | 10–20 m | 14 mm | 4 bar | 2.000 L/min |

**Dato verificado:** la tabla Parker «Dimensioning of Compressed Air Hoses and Equipment» publica esos mínimos y caudales bajo sus propias condiciones de dimensionamiento. En esa tabla el tamaño de conexión y el diámetro interior de la manguera son columnas distintas; no se deben tratar como la misma medida.

**Análisis TallerLab:** entre los tramos de hasta 10 m y los de 10–20 m, Parker aumenta 1 mm el diámetro mínimo indicado para las conexiones de 1/4″ y 3/8″, y 2 mm para 1/2″. Es una diferencia documental de dimensionamiento, no una medición de pérdida de presión de una manguera cualquiera. Para elegir también hay que cotejar el consumo y la presión exigidos por el equipo conectado, además de racores, longitud real y presión nominal de cada componente.

**Desconocido:** no hay un diámetro universal para toda herramienta neumática ni una conversión directa entre diámetro de conexión nominal y diámetro interior. Los caudales Parker de esta tabla no certifican el caudal de una manguera sin marca, largo y construcción identificados.

## Fuentes consultadas

- **Documentación técnica primaria:** [Parker, catálogo neumático 0726-E, tabla de dimensionamiento de mangueras y equipos](https://www.parker.com/content/dam/Parker-com/Literature/Literature-Files/pneumatic/UPD_2010/Catalog_0726-E.pdf); [Parker, catálogo de mangueras industriales 4401UK](https://www.parker.com/static_content/parkerimages/euro_hpd/CAT_4401UK.pdf).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/compresores/", "/compresores/kits-accesorios/", "kits y accesorios para compresor",
    ),
    "paginas/compresores/07-compresor-para-aerografo.md": (
        "Contraste entre un kit BTA de aerógrafo que no incluye compresor y el Fengda AS-186, con tanque y valores publicados de presión y caudal.",
        """| Producto | Qué documenta la fuente | Tanque | Presión/caudal publicados | Qué falta para confirmar una pareja |
| :--- | :--- | ---: | :--- | :--- |
| BTA AP8, código 279004.1 | Aerógrafo, manguera, soporte y accesorios; sugiere compresor de 2 HP | No incluye | Presión máxima 10 bar; consumo de aire no indicado | Caudal requerido por el aerógrafo y contenido final del paquete |
| Fengda AS-186 / FD-186 | Compresor para aerografía, sin aceite, un pistón | 3 L | Aire libre sin carga 20–23 L/min; arranque 3 bar y corte 4 bar | Compatibilidad concreta con AP8 no declarada por los fabricantes |

**Dato verificado:** la lista de BTA para el AP8 incluye componentes de aerografía, pero no el compresor; «sugerido 2 HP» es la recomendación publicada, no una medición del consumo. Fengda publica para el AS-186 un tanque de 3 L, 20–23 L/min sin carga y control automático entre 3 y 4 bar.

**Análisis TallerLab:** las cifras no permiten declarar compatible al Fengda con el AP8: uno de los datos esenciales, el consumo de aire del aerógrafo, no está publicado en la ficha BTA consultada. Además, los 20–23 L/min de Fengda están identificados como flujo sin carga y no se comparan directamente con caudal requerido bajo pulverización. Antes de comprar un conjunto, pedí consumo a la presión de trabajo y compatibilidad de roscas/adaptadores para los códigos exactos.

**Desconocido:** no se documentaron patrón de pulverización, acabado, nivel sonoro comparativo ni una prueba con ambos modelos. No inferimos que todo compresor con tanque pequeño sirva para cualquier aerógrafo.

## Fuentes consultadas

- **Documentación primaria/comercial del producto:** [BTA, aerógrafo AP8](https://btatools.com.ar/producto/aerografo-profesional); [Fengda Europe, AS-186 / FD-186](http://www.fengda-europe.com/Airbrush-mini-compressor-with-air-tank-Fengda-AS-186%28FD-186%29?Lng=en).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/compresores/", "/compresores/", "guías de compresores",
    ),
    "paginas/compresores/01-compresor-de-aire-para-auto.md": (
        "Comparación documental de dos infladores 12 V y un criterio de selección basado en presión del vehículo; no equipara presión máxima con presión objetivo.",
        """| Modelo | Alimentación | Presión máxima publicada | Caudal publicado | Datos adicionales de ficha |
| :--- | :--- | ---: | ---: | :--- |
| Lüsqtoff MCL150-8 | 12 V; 275 W | 150 psi | 60 L/min | Doble pistón; 2,63 kg; parada automática, luz LED y manómetro digital |
| Gadnic AV000009 | 12 V | 150 psi | 85 L/min | La página comercial indica 23 A y peso de 2,54 kg; no informa condición de medición del caudal |

**Dato verificado:** Lüsqtoff declara para MCL150-8 12 V, 275 W, máximo de 150 psi y flujo de 60 L/min. Gadnic publica 150 psi y 85 L/min para AV000009, pero no indica una condición de presión para ese caudal. Las fichas no usan un método de medición compartido que permita concluir que un modelo infla más rápido.

**Análisis TallerLab:** el número 150 psi describe la presión máxima del inflador, no la presión objetivo de un neumático. Michelin indica tomar la presión recomendada por el fabricante del vehículo, que suele estar en la etiqueta del vehículo o su manual, y comprobarla con los neumáticos fríos. Por eso, la comparación útil es primero de alimentación, manómetro, parada automática, accesorios y datos de caudal comparables; no basta con elegir el mayor máximo impreso.

| Decisión | Verificación documental |
| :--- | :--- |
| Presión objetivo | Etiqueta/manual del vehículo; no usar como objetivo el máximo del inflador |
| Conexión eléctrica | Confirmar toma, consumo y protección del vehículo |
| Caudal | Pedir flujo a una presión declarada y método común antes de comparar tiempos |
| Accesorios | Revisar manguera, válvula, cable, fusible y adaptadores del código exacto |

**Desconocido:** no comparamos tiempos de inflado ni exactitud de manómetros; no hay ensayo de TallerLab ni caudal de ambos equipos medido a una misma presión. La recomendación de presión depende del vehículo y de su condición de carga.

## Fuentes consultadas

- **Documentación primaria:** [Lüsqtoff, ficha MCL150-8](https://lusqtoff.com.ar/ver-producto/MCL150-8).
- **Información comercial:** [Gadnic, inflador 12 V AV000009](https://www.gadnic.com.ar/infladores-y-compresores/compresor-de-aire-12v-85l-min).
- **Seguridad/información del fabricante del neumático:** [Michelin, cómo comprobar e inflar neumáticos](https://middle-east.michelin.com/en/auto/advice/tyre-pressure/inflate-tyres).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/compresores/", "/compresores/12v/", "compresores de 12 V",
    ),
    "paginas/compresores/21-compresor-para-pintar.md": (
        "Cruce documental entre consumo publicado por dos pistolas BTA y admisión publicada por compresores concretos; explicita que la admisión no equivale al aire entregado.",
        """| Equipo / código | Requisito o dato publicado | Comparación permitida |
| :--- | :--- | :--- |
| Pistola BTA AS-1021, 279064.1 | 85 L/min aprox.; 10–40 psi; copa 1 L | El fabricante publica consumo aproximado y rango de presión |
| Pistola BTA ASP1070, 279063 | 119–201 L/min; presión recomendada 29–51 psi; copa 1.000 cm³ | Rango publicado; el catálogo sugiere compresor de 2 HP |
| Compresor BTA 25 L, D-CA1-25-6 | Admisión 206 L/min; 2 HP; 8 bar | Admisión de la bomba, no caudal efectivo de salida |
| Compresor BTA 24 L sin aceite, 272005 | Admisión 170 L/min; 2 HP; 8 bar | Admisión publicada; no usar como FAD |

**Dato verificado:** BTA especifica consumos distintos para las pistolas AS-1021 y ASP1070. En fichas separadas publica 206 L/min de admisión para el compresor de 25 L y 170 L/min para el de 24 L sin aceite. Los valores de pistola y compresor provienen de fichas/catálogo del mismo fabricante, pero el catálogo no presenta caudal de salida de ambos compresores medido bajo la presión de pulverización.

**Análisis TallerLab:** el caudal de admisión del compresor de 25 L supera en 2 L/min el extremo alto publicado para ASP1070 y en 87 L/min su extremo bajo; esas restas no prueban suministro suficiente porque comparan admisión con consumo de herramienta y no incluyen pérdida ni condición de presión. Para AS-1021, la resta frente a 206 L/min también es solo una comparación nominal. Confirmá caudal efectivo (FAD) a la presión de trabajo y régimen de uso con el fabricante antes de afirmar continuidad de pulverización.

**Desconocido:** las fuentes no documentan el resultado de pintar con estas combinaciones, recuperación entre pasadas ni el tiempo que cada compresor sostiene ese caudal. Los HP sugeridos o la capacidad del tanque, por sí solos, no contestan esas preguntas.

## Fuentes consultadas

- **Documentación primaria:** [BTA, pistola AS-1021](https://btatools.com.ar/producto/pistola-para-pintar-baja-presion); [catálogo BTA 2026/27, pistola ASP1070](https://btatools.com.ar/catalogo/catalogo-bta-2026-27-1.pdf); [BTA, compresor 25 L](https://btatools.com.ar/producto/compresor-de-aire-25-litros-2-0-hp); [BTA, compresor 24 L sin aceite](https://btatools.com.ar/producto/compresor-de-aire-24-litros-2-0-hp-portatil-sin-aceite).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/compresores/", "/compresores/pistola-para-pintar/", "pistolas para pintar con compresor",
    ),
    "paginas/compresores/05-pistola-para-pintar-con-compresor.md": (
        "Tabla por código de tres pistolas BTA: contrasta consumo, presión, alimentación y tamaño de copa, sin inferir eficiencia ni continuidad.",
        """| Código / modelo BTA | Alimentación / sistema | Consumo de aire publicado | Presión publicada | Copa |
| :--- | :--- | ---: | :--- | ---: |
| 279064.1 / AS-1021 | Baja presión; ficha de producto | Aprox. 85 L/min | 10–40 psi | 1 L |
| 279063 / ASP1070 | Succión, HVLP | 119–201 L/min | Recomendada 29–51 psi; máxima 120 psi | 1.000 cm³ |
| 279068 / ASPM1070 | Gravedad, alta presión; retoques | 68 L/min | Recomendada 43,5–58 psi; máxima 120 psi | 200 cm³ |

**Dato verificado:** el catálogo BTA 2026/27 identifica ASP1070 y ASPM1070 por códigos distintos y especifica sistemas de alimentación, presión, copa y consumo. La ficha de AS-1021 publica cerca de 85 L/min. En el catálogo, BTA sugiere compresor de 2 HP para ASP1070 y ASPM1070; esa recomendación aparece como campo del fabricante.

**Análisis TallerLab:** la diferencia numérica entre los consumos publicados de ASP1070 (119–201 L/min) y ASPM1070 (68 L/min) es de 51–133 L/min, según el extremo del rango ASP1070 que se tome. No permite declarar mayor eficiencia: los documentos no explican una condición de medición común ni miden cobertura o transferencia de pintura. También cambia la aplicación declarada y el volumen de copa, así que primero corresponde emparejar proceso, presión y consumo, luego cotejar el FAD del compresor a esa presión.

**Desconocido:** el catálogo no prueba qué compresor sostiene cada pistola en uso continuo, ni el acabado, desperdicio o superficie por hora. La sugerencia de 2 HP no sustituye el caudal de salida medido.

## Fuentes consultadas

- **Documentación primaria:** [catálogo BTA 2026/27](https://btatools.com.ar/catalogo/catalogo-bta-2026-27-1.pdf); [ficha BTA AS-1021](https://btatools.com.ar/producto/pistola-para-pintar-baja-presion).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/compresores/", "/compresores/para-pintar/", "compresores para pintar",
    ),
    "paginas/compresores/15-compresor-sin-aceite.md": (
        "Comparación de tres compresores sin aceite por código y admisión publicada; distingue mantenimiento sin aceite de usos que exigen aire certificado.",
        """| Modelo | Tanque | Potencia publicada | Admisión publicada | Presión publicada |
| :--- | ---: | ---: | ---: | ---: |
| BTA CSA-24, código 272005 | 24 L | 2 HP / 1.500 W | 170 L/min | 8 bar |
| BTA CSA-50-2, código 272009.2 | 50 L | 1,5 HP / 1.100 W | 260 L/min | 8 bar |
| Lüsqtoff LC-0122 | 24 L | 1 HP / 750 W | 180 L/min | 115 psi |

**Dato verificado:** las fichas identifican los tres como modelos sin aceite y publican los valores resumidos en la tabla. BTA declara 2.850 rpm para CSA-50-2 y 3.750 rpm para CSA-24; Lüsqtoff indica 24 kg para LC-0122. Las cifras de litros por minuto son de admisión publicadas por cada marca, no caudal efectivo de salida bajo presión.

**Análisis TallerLab:** el CSA-50-2 declara 90 L/min más de admisión que el CSA-24, equivalente a 52,9 % respecto de 170 L/min, mientras su tanque duplica la capacidad nominal menos 2 L (50 frente a 24 L). Esa comparación describe fichas y no acredita mayor caudal entregado por minuto durante un uso real. Frente a LC-0122, las dos fichas de 24 L declaran admisiones de 170 y 180 L/min, pero sus potencias son distintas y no hay método común de medición publicado.

«Sin aceite» describe la lubricación de la bomba en estos modelos. **Desconocido:** no constituye por sí solo certificación de aire respirable, médico, alimentario o libre de contaminantes; tampoco confirma ruido, vida útil o servicio continuo. Para esos usos se requiere especificación y certificación apropiada del sistema completo.

## Fuentes consultadas

- **Documentación primaria:** [BTA CSA-24, 24 L sin aceite](https://btatools.com.ar/producto/compresor-de-aire-24-litros-2-0-hp-portatil-sin-aceite); [BTA CSA-50-2, 50 L sin aceite](https://btatools.com.ar/producto/compresor-de-aire-50-litros-1-5-hp-silenciado-sin-aceite); [Lüsqtoff LC-0122](https://lusqtoff.com.ar/ver-producto/LC-0122).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/compresores/", "/compresores/lusqtoff-50-litros/", "compresor Lüsqtoff de 50 litros",
    ),
    "paginas/compresores/20-compresor-stanley.md": (
        "Comparación de dos Stanley D210/8 del mismo catálogo: cuantifica qué cambia al pasar de tanque de 24 a 50 L y qué campos permanecen iguales.",
        """| Dato de catálogo Stanley | D210/8/24 | D210/8/50 |
| :--- | ---: | ---: |
| Tanque | 24 L | 50 L |
| Motor declarado | 2 HP / 1,5 kW | 2 HP / 1,5 kW |
| Presión máxima | 8 bar / 116 psi | 8 bar / 116 psi |
| Desplazamiento de aire declarado | 222 L/min | 222 L/min |
| Velocidad | 2.850 rpm | 2.850 rpm |
| Peso bruto de catálogo | 24 kg | 36 kg |
| Lubricación | Aceitado | Aceitado |

**Dato verificado:** el catálogo Stanley para la serie D210/8 publica la misma potencia, presión, velocidad y desplazamiento para las variantes de 24 y 50 L. Cambia el tanque y el peso bruto de catálogo. El documento es un catálogo regional europeo alojado por un distribuidor; no prueba la disponibilidad, revisión ni garantía argentina de una unidad ofrecida hoy.

**Análisis TallerLab:** el tanque aumenta 26 L (108,3 % sobre 24 L), mientras el peso bruto informado aumenta 12 kg (50 % sobre 24 kg). El desplazamiento publicado no aumenta junto con el tanque; ese dato no equivale a FAD ni permite comparar tiempo de recuperación sin curva y presión común. La tabla sirve para diferenciar capacidad de reserva de aire y tamaño del conjunto, no para afirmar rendimiento de taller.

**Desconocido:** no se confirmó caudal efectivo, estado actual de la línea D210/8 ni servicio/repuestos en Argentina. Antes de comprar, cotejar código de placa, manual correspondiente y condiciones escritas de garantía del vendedor local.

## Fuentes consultadas

- **Documentación del fabricante/catálogo de línea:** [catálogo Stanley de compresores D210/8](https://www.nuair.pt/images/katalogi/Catalogo-STANLEY-2017.pdf); [Stanley Black & Decker, centro de soporte](https://support.stanleytools.com/hc/en-us/article_attachments/360012470297) (manual de compresores; confirmar que la revisión corresponda al código de placa).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/compresores/", "/compresores/lusqtoff-50-litros/", "compresor Lüsqtoff de 50 litros",
    ),
    "paginas/generadores/19-generadores-a-gas.md": (
        "Matriz que separa grupos diseñados de fábrica para gas natural/GLP de kits de conversión para motores pequeños; agrega el límite de instalación regulada.",
        """| Caso documentado | Combustible/configuración | Potencia publicada | Qué muestra la fuente |
| :--- | :--- | ---: | :--- |
| Generac Guardian residencial, 8 kVA | Configuración para LP y gas natural | 8.000 VA máximo continuo en LP; 7.000 VA en gas natural | Ficha técnica de una familia diseñada para ambos combustibles |
| Kit Lüsqtoff K1 | Conversión a gas envasado para motores compatibles | La ficha indica aplicación en motores de 5,5; 6,5 y 7 HP | Es un accesorio de conversión y no una autorización universal |

**Dato verificado:** para el Guardian 8 kVA, la ficha Generac publica distinta potencia continua máxima según combustible: 8 kVA con LP y 7 kVA con gas natural. También especifica consumos y presiones de entrada por gas y carga. Lüsqtoff describe el kit K1 para ciertas potencias de motor; esos motores y el generador Guardian son categorías distintas y no se deben mezclar como si compartieran kit.

**Análisis TallerLab:** “generador a gas” puede referirse a un equipo configurado de fábrica para gas o a un motor adaptado con un kit concreto. La ficha Guardian compara dos combustibles en una familia determinada; el K1 se limita a los motores que Lüsqtoff enumera. No deducimos que un generador cualquiera acepte gas ni extrapolamos la potencia nominal de nafta a gas.

**Seguridad:** las conexiones, dimensionamiento y puesta en marcha de una instalación de gas requieren intervención de personal matriculado y aprobación según normativa y fabricante. Generac Argentina indica instalación profesional para sus equipos; ENARGAS señala la intervención de instalador matriculado para modificaciones de la instalación. Esta guía no es una instrucción de conversión.

**Desconocido:** la ficha de K1 no valida todos los códigos de generadores, la potencia final en cada aplicación ni los requisitos de instalación de cada localidad. Antes de comprar, exigir compatibilidad escrita del fabricante para código y combustible exactos.

## Fuentes consultadas

- **Documentación primaria:** [Generac Argentina, ficha Guardian 8/10/13 kVA](https://www.generac.com.ar/_files/ugd/31f31b_3460fa12940846e3b3cb0df69786d423.pdf); [Lüsqtoff, kit de conversión K1](https://www.lusqtoff.com.ar/productos/K1); [Generac Argentina, instaladores](https://www.generac.com.ar/instaladores).
- **Seguridad/normativa:** [ENARGAS, preguntas frecuentes sobre instalaciones de gas](https://www.enargas.gob.ar/secciones/seguridad-en-el-hogar/preguntas-frecuentes.php).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/generadores/", "/generadores/a-nafta/", "generadores a nafta",
    ),
    "paginas/generadores/08-generadores-a-nafta.md": (
        "Tabla de tres modelos Lüsqtoff a nafta que expone diferencias y contradicciones entre fichas y manual del LGI3.8-8 y la potencia del LG3000.",
        """| Modelo | Potencia continua/nominal publicada | Máxima publicada | Tanque / autonomía | Observación documental |
| :--- | ---: | ---: | :--- | :--- |
| LG3500EX | 2.450 W nominales | 3.500 W | 15 L; aprox. 6–8 h según ficha | Motor 4 tiempos; 45 kg |
| LG3500EXI | No especificada en la ficha consultada | 3.500 W | 15 L; 11 h declaradas | Inverter; autonomía sin condición de carga detallada en la ficha |
| LGI3.8-8 | 3,5 kW | 3,8 kW | 8 L | Página: 223 cm³ y 28 kg; manual: 233 cm³ y 27 kg |
| LG3000 | 2,5 kVA | 2,8 kVA | 15 L; 12 h declaradas | La misma página también imprime 4,8 kW como “potencia máxima de salida” |

**Dato verificado:** las fichas oficiales Lüsqtoff publican los valores resumidos. En LGI3.8-8, página de producto y manual discrepan en cilindrada (223/233 cm³) y peso (28/27 kg). En LG3000, los campos de 2,5 kVA nominal y 2,8 kVA máximo coexisten en la ficha con otro campo que dice 4,8 kW máximo. No resolvemos esas diferencias sin aclaración de la marca.

**Análisis TallerLab:** estos casos muestran por qué hay que comparar potencia nominal con nominal y máxima con máxima, además de distinguir W de VA. Para LG3000, 4,8 kW no concuerda con el campo máximo de 2,8 kVA tal como está publicado; se deja registrada la inconsistencia sin elegir arbitrariamente una cifra. Las autonomías de 6–8, 11 y 12 horas tampoco son comparables sin carga y procedimiento equivalentes.

**Desconocido:** no se convierte el consumo LG3000 de 360 g/kWh a litros por hora sin conocer potencia entregada y densidad del combustible en la condición de ensayo. La evidencia consultada tampoco confirma autonomía con una carga específica, contenido de kit, garantía vigente o potencia recomendada para cada artefacto.

## Fuentes consultadas

- **Documentación primaria:** [Lüsqtoff LG3500EX](https://lusqtoff.com.ar/ver-producto/LG3500EX); [Lüsqtoff LG3500EXI](https://www.lusqtoff.com.ar/ver-producto/LG3500EXI); [Lüsqtoff LGI3.8-8](https://www.lusqtoff.com.ar/ver-producto/LGI3.8-8); [manual Lüsqtoff LGI3.8-8](https://www.lusqtoff.com.ar/2023/uploads/Productos/NUEVOS/GRUPOS_ELECTROGENES/LGI38-8/LGI3-8-8.pdf); [Lüsqtoff LG3000](https://lusqtoff.com.ar/ver-producto/LG3000).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/generadores/", "/generadores/a-gas/", "generadores a gas",
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
    front = re.sub(r"(?m)^description:.*$", f'description: "{asset.replace(chr(34), chr(92)+chr(34))}"', front)
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
