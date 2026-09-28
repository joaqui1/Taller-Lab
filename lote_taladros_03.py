"""Sexto lote editorial: tres guías de taladros y siete de amoladoras."""
from pathlib import Path
import re

ROOT = Path(__file__).parent

PAGES = {
    "paginas/taladros/23-combo-taladro-amoladora.md": (
        "Comparación documental de un combo Lusqtoff: herramientas, baterías y garantía",
        """| Componente del kit Lusqtoff KATL-9BK | Dato de la ficha oficial |
| :--- | :--- |
| Amoladora | 18 V, disco de 115 mm, rosca M14, 6.500 / 7.000 / 8.500 rpm |
| Taladro atornillador | 18 V, mandril de 10 mm, dos velocidades, 0–500 / 0–2.000 rpm |
| Torque máximo publicado del taladro | 60 Nm |
| Baterías incluidas | Una de 4 Ah y una de 2 Ah |
| Cargador | Incluido |
| Garantía informada por el fabricante | Herramientas: 3 años; baterías: 6 meses |

**Dato documentado:** la tabla corresponde al código KATL-9BK que Lusqtoff publica como kit de amoladora angular y taladro inalámbrico. No trasladamos esos datos a otros combos de nombre o aspecto parecido.

**Análisis TallerLab:** el kit contiene dos baterías de capacidades distintas, 4 Ah y 2 Ah; la ficha no indica cuál se destina a cada herramienta. La amoladora tiene tres velocidades listadas, mientras el taladro ofrece dos velocidades mecánicas. La diferencia entre las baterías es de 2 Ah, pero ese valor no predice por sí solo cuántos cortes o agujeros permite cada una.

**Declaración del fabricante:** el taladro se identifica como herramienta de 18 V con torque máximo de 60 Nm. La página del kit no detalla una función de percusión; queda **desconocida** para este código mientras no aparezca en la ficha o el manual.

**Desconocido:** no comparamos el precio del kit con las dos herramientas compradas por separado; los precios y las ofertas cambian. Tampoco verificamos resultados bajo carga, autonomía, disponibilidad actual o garantía de una publicación particular. Para otro combo, contrastá por separado cada código, sus baterías, el cargador y los discos incluidos.

## Comprobación de otros combos anunciados

| Combo que aparece en ofertas comerciales | Qué puede tomarse del anuncio | Qué sigue sin documentación primaria en esta revisión |
| :--- | :--- | :--- |
| Kommberg con cable | El anuncio identifica una amoladora de 820 W y un taladro de 650 W | Códigos de modelo, diámetros, rpm, percusión y contenido de accesorios |
| Daewoo con cable | El anuncio describe amoladora de 750 W / 115 mm y taladro percutor | Modelo exacto, capacidades, manual y garantía |
| Kommberg inalámbrico | El anuncio presenta ambas máquinas como inalámbricas | Plataforma, Ah, cantidad de baterías y cargador |
| KLD 18 V | El anuncio menciona taladro percutor, amoladora 115 mm y dos baterías | Códigos, Ah, rendimiento y cobertura de garantía |

Los datos de esta tabla describen el texto de cada aviso, no quedan verificados como especificaciones del fabricante. Para una comparación de compra válida, el vendedor debe identificar cada modelo y el contenido exacto del paquete.

## Fuentes consultadas

- **Documentación primaria:** [Lusqtoff KATL-9BK](https://www.lusqtoff.com.ar/productos/KATL-9BK); [Lusqtoff TAL60-9B](https://www.lusqtoff.com.ar/ver-producto/TAL60-9B), referencia del taladro incluido.
- **Información comercial:** avisos enlazados en la tabla de combos, tratados únicamente como descripción de oferta.
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "Ficha comprobable del combo Lusqtoff KATL-9BK y matriz de datos faltantes en otros kits anunciados.",
        "/taladros/",
        "/taladros/lusqtoff-inalambrico/",
        "taladro inalámbrico Lusqtoff",
    ),
    "paginas/taladros/16-taladro-inalambrico-lusqtoff.md": (
        "TIL23-8B y TAL60-9B: dos taladros Lusqtoff con kits distintos",
        """| Dato publicado por Lusqtoff | TIL23-8B | TAL60-9B |
| :--- | ---: | ---: |
| Plataforma | 12 V | 18 V, línea Iron Volt |
| Torque máximo | 23 Nm | 60 Nm |
| Mandril | 10 mm | Metálico, 10 mm |
| Velocidad sin carga | Hasta 710 rpm | 0–500 / 0–2.000 rpm |
| Peso declarado | 2,2 kg | 0,9 kg |
| Batería/cargador | 2 baterías y cargador incluidos | No incluidos |
| Garantía publicada | 2 años | 3 años |

**Dato documentado:** la tabla reproduce fichas oficiales de los códigos TIL23-8B y TAL60-9B. La página de TIL23-8B no explica si el peso incluye baterías; el fabricante tampoco describe en esas fichas una condición de pesaje común. La comparación de masa queda limitada por esa diferencia documental.

**Análisis TallerLab:** el TAL60-9B declara 37 Nm más de torque máximo y una velocidad máxima 1.290 rpm superior; se vende sin batería ni cargador. El TIL23-8B incluye dos baterías y cargador en la ficha consultada. No calculamos autonomía ni rapidez real con esos datos, y no presentamos el mayor torque como prueba de que un modelo sea mejor para toda tarea.

**Declaración del fabricante:** el TAL60-9B usa motor brushless y es compatible con Iron Volt, según Lusqtoff. Ninguna de las dos fichas citadas declara percusión; por lo tanto, la función no queda confirmada para estos dos códigos. Si necesitás perforar mampostería, verificá expresamente esa función en otro modelo.

**Desconocido:** los contenidos de caja y precios pueden variar por publicación. La ficha del TIL23-8B declara 1,5 Ah y la página TAL60-9B no incluye batería; no hay una prueba de autonomía bajo la misma tarea ni una comparación de vida útil de los motores.

## Decisión por paquete y plataforma

| Si priorizás… | Referencia en esta comparación | Revisá antes de comprar |
| :--- | :--- | :--- |
| Recibir un kit listo para usar | TIL23-8B | Que el aviso conserve las dos baterías y el cargador anunciados |
| Usar plataforma 18 V brushless | TAL60-9B | Costo de batería y cargador compatibles, vendidos aparte |
| Percusión para mampostería | Ninguno queda confirmado en estas dos fichas | Elegir un modelo cuya documentación indique percusión |

## Fuentes consultadas

- **Documentación primaria:** [Lusqtoff TIL23-8B](https://www.lusqtoff.com.ar/productos/taladro-atornillador-a-bateria-o-12-v-til23-8b); [Lusqtoff TAL60-9B](https://www.lusqtoff.com.ar/ver-producto/TAL60-9B); [catálogo oficial Lusqtoff 2024–2025](https://www.lusqtoff.com.ar/2023/uploads/Catalogos/CAT%C3%81LOGO%20LQ%202024-2025%20-%20web%20%281%29.pdf).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "Comparación de dos modelos Lusqtoff con códigos, torque, velocidad, contenido de kit y plataforma identificados.",
        "/taladros/",
        "/taladros/combo-taladro-amoladora/",
        "combo de taladro y amoladora",
    ),
    "paginas/taladros/04-taladro-de-banco.md": (
        "TB-16 y TBL710-9D: mandril, recorrido y ciclos declarados por Lusqtoff",
        """| Dato publicado | Lusqtoff TB-16 | Lusqtoff TBL710-9D |
| :--- | ---: | ---: |
| Potencia nominal | 450 W | 710 W; 900 W indicado para S2 de 5 min |
| Mandril | 16 mm | 1,5–13 mm |
| Recorrido del husillo | 65 mm en la ficha actual | 0–100 mm |
| Velocidades | 12; 300–2.550 rpm | Dos rangos: 170–880 y 490–2.600 rpm |
| Mesa | No declarada en la ficha consultada | 330 × 300 mm |
| Peso | 33 kg | No publicado en la ficha consultada |

**Dato documentado:** las cifras provienen de las páginas oficiales de Lusqtoff para TB-16 y TBL710-9D. En la ficha del TBL710-9D, 900 W aparece junto con la condición S2 de 5 minutos; no se debe presentar como potencia nominal para uso continuo. Una ficha anterior de TB-16 indica un recorrido de 50 mm y un peso de 31 kg, mientras la página actual publica 65 mm y 33 kg. Conservamos esa discrepancia en vez de mezclar versiones.

**Análisis TallerLab:** el TB-16 declara un mandril 3 mm mayor que el TBL710-9D; el TBL710-9D publica hasta 35 mm más de recorrido frente a los 65 mm de la ficha actual del TB-16. El diámetro de mandril describe el vástago que puede sujetar: no demuestra por sí solo qué diámetro de agujero logra el motor en un material concreto.

**Declaración del fabricante:** el manual del TB-16 indica sujetar la pieza, detener la máquina antes de hacer ajustes y no exceder la capacidad del mandril. Esas indicaciones se atribuyen a Lusqtoff y no sustituyen el manual específico del taladro que se compre.

**Desconocido:** la ficha del TBL710-9D no publica peso en la página consultada ni la del TB-16 publica dimensión de mesa. Tampoco hay resultados de precisión, vibración o capacidad de perforación comparados bajo el mismo material y broca.

## Qué comparar en un taladro de banco

| Necesidad | Campo de la ficha | Límite de interpretación |
| :--- | :--- | :--- |
| Sujetar una broca | Apertura de mandril | No equivale a capacidad de agujero |
| Perforar una pieza gruesa en un avance | Recorrido del husillo | No indica precisión ni rigidez de columna |
| Elegir velocidad para material | Rango y cantidad de velocidades | Confirmar tablas del manual por material y diámetro |
| Operar en una tanda larga | Régimen nominal y ciclo S2 | 900 W S2 de 5 minutos no es potencia continua |

## Fuentes consultadas

- **Documentación primaria:** [Lusqtoff TB-16, ficha actual](https://www.lusqtoff.com.ar/ver-producto/TB-16); [Lusqtoff TBL710-9D](https://www.lusqtoff.com.ar/ver-producto/TBL710-9D); [manual oficial TB-16](https://www.lusqtoff.com.ar/2023/uploads/Productos/12.%20HERRAMIENTAS%20DE%20PIE%20Y%20BANCO/TB-16/MANUAL/TB-16.pdf); [catálogo Lusqtoff 2020–2021, dato anterior de TB-16](https://lusqtoff.com.ar/files/Catalogo_Lusqtoff_2020.pdf).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "Comparación de fichas oficiales de dos taladros de banco: recorrido, mandril, velocidades y régimen S2.",
        "/taladros/",
        "/taladros/mecha-forstner-35-mm/",
        "mecha Forstner de 35 mm",
    ),
    "paginas/00-amoladoras.md": (
        "Matriz Bosch por diámetro de disco: 115, 180 y 230 mm",
        """| Modelo Bosch consultado | Diámetro máximo de disco | Potencia absorbida | Velocidad en vacío | Peso publicado |
| :--- | ---: | ---: | ---: | ---: |
| GWS 9-115 S | 115 mm | 900 W | 2.800–11.000 rpm | 1,9 kg |
| GWS 25-180 LVI R | 180 mm | 2.500 W | 8.500 rpm | No consta en el recorte consultado |
| GWS 25-230 | 230 mm | 2.500 W | 6.500 rpm | 5,9 kg |

**Dato documentado:** cada fila corresponde al modelo indicado en las fichas Bosch. La página del GWS 25-180 LVI R confirma 2.500 W, 8.500 rpm y disco de 180 mm; el peso no aparece en los datos citados aquí, por eso no completamos la celda por analogía. Las herramientas de otros países pueden diferir en tensión, variantes e interruptores.

**Análisis TallerLab:** los tres diámetros muestran por qué la medida del accesorio es el primer filtro de compatibilidad: los discos de 115, 180 y 230 mm no son intercambiables en una máquina diseñada para otra medida. En la ficha del GWS 25-180 y GWS 25-230 la potencia declarada coincide, mientras que la velocidad en vacío y el diámetro difieren. Eso no determina la profundidad real de corte: depende del disco, guarda, geometría y material.

**Declaración del fabricante:** Bosch clasifica las herramientas angulares grandes para corte y desbaste de mayor exigencia. En sus páginas se describen funciones de seguridad concretas para ciertos modelos, como KickBack Control, Soft Start o protección contra rearranque; no todas las amoladoras incorporan las mismas funciones.

**Desconocido:** esta selección no compara todas las marcas, discos, rectificadoras ni equipos de banco. No hay medición propia de profundidad, ritmo de corte, temperatura o vibración. Verificá el código del equipo y los límites de rpm y diámetro indicados en cada accesorio.

## Matriz rápida por diámetro

| Diámetro nominal | Ejemplo documentado | Qué permite concluir esta guía |
| :--- | :--- | :--- |
| 115 mm | Bosch GWS 9-115 S | Referencia de amoladora angular pequeña, 900 W |
| 180 mm | Bosch GWS 25-180 LVI R | Máquina para discos de 180 mm y 8.500 rpm en vacío |
| 230 mm | Bosch GWS 25-230 | Máquina para discos de 230 mm y 6.500 rpm en vacío |

Elegí por tarea, pieza, disco compatible y forma de sujeción. Para una amoladora de banco o una recta, consultá la ficha de esa familia: su montaje y uso no se deducen de una angular.

## Fuentes consultadas

- **Documentación primaria:** [Bosch GWS 9-115 S](https://www.bosch-professional.com/es/es/products/gws-9-115-s-0601396103); [Bosch GWS 25-180 LVI R](https://www.bosch-professional.com/ar/es/products/gws-25-180-lvi-r-06018F71H1); [Bosch GWS 25-230](https://www.bosch-professional.com/ar/es/products/gws-25-180-06018F41H0).
- **Seguridad:** manual Bosch para herramientas angulares grandes, [GWS 25-180/230 LVI R](https://www.bosch-professional.com/binary/manualsmedia/o424644v21_160992A8T6_202306.pdf).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "Tabla de tres amoladoras angulares Bosch para distinguir diámetros, potencia, rpm y peso documentado.",
        "/amoladoras/",
        "/amoladoras/115-o-125/",
        "comparación entre amoladoras de 115 y 125 mm",
    ),
    "paginas/19-amoladora-7-pulgadas.md": (
        "Bosch GWS 25-180 LVI R: qué confirma su ficha de 180 mm",
        """| Dato publicado | Bosch GWS 25-180 LVI R |
| :--- | ---: |
| Código de pedido | 0 601 8F7 1H1 |
| Potencia absorbida | 2.500 W |
| Diámetro de disco | 180 mm |
| Velocidad en vacío | 8.500 rpm |
| Rosca del eje | M14 |
| Tensión indicada | 220 V |
| Funciones listadas | Vibration Control, KickBack Control, Soft Start y Restart Protection |

**Dato documentado:** Bosch publica estas especificaciones para el código GWS 25-180 LVI R. La página identifica una variante con tuerca y menciona accesorios incluidos; el contenido puede variar según el número de pedido completo.

**Análisis TallerLab:** 7 pulgadas equivalen a 177,8 mm, mientras que el diámetro métrico publicado por el fabricante es 180 mm (aproximadamente 7,09 pulgadas). La diferencia es de 2,2 mm en el diámetro nominal. La etiqueta “7 pulgadas” es una denominación comercial redondeada; para comprar discos, manda la medida indicada en la herramienta y el accesorio. El diámetro mayor tampoco permite calcular por sí solo el corte útil.

**Declaración del fabricante:** Bosch describe las protecciones Vibration Control, KickBack Control, Soft Start y Restart Protection en la ficha de este código. Esas funciones son del modelo nombrado; no se atribuyen a todas las amoladoras de 180 mm ni se convierten en una afirmación de ausencia de riesgo.

**Desconocido:** la ficha consultada no permite confirmar profundidad real de corte en una pieza específica, masa del conjunto de trabajo ni disponibilidad/garantía de una oferta argentina. La potencia y las rpm en vacío tampoco representan rendimiento bajo carga.

## Filtro de compatibilidad

| Antes de comprar | Confirmación para este código |
| :--- | :--- |
| Disco | 180 mm máximo publicado |
| Orificio/eje | Rosca M14; el disco debe admitir brida y montaje del modelo |
| Alimentación | Bosch indica 220 V |
| Accesorio de corte o desbaste | Revisar uso previsto y velocidad máxima en su etiqueta |

## Fuentes consultadas

- **Documentación primaria:** [Bosch GWS 25-180 LVI R](https://www.bosch-professional.com/ar/es/products/gws-25-180-lvi-r-06018F71H1); [manual Bosch GWS 25-180/230 LVI R](https://www.bosch-professional.com/binary/manualsmedia/o424644v21_160992A8T6_202306.pdf).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "Ficha con medidas y funciones de un modelo Bosch de 180 mm y cálculo transparente de la equivalencia comercial con 7 pulgadas.",
        "/amoladoras/",
        "/amoladoras/9-pulgadas/",
        "amoladoras de 9 pulgadas",
    ),
    "paginas/12-amoladora-de-9-pulgadas.md": (
        "GWS 25-230: 230 mm, 2.500 W y 6.500 rpm en vacío",
        """| Dato publicado | Bosch GWS 25-230 |
| :--- | ---: |
| Código de pedido | 0 601 8F4 1H0 |
| Potencia absorbida | 2.500 W |
| Diámetro de disco | 230 mm |
| Velocidad en vacío | 6.500 rpm |
| Peso | 5,9 kg |
| Rosca del eje | M14 |

**Dato documentado:** la fuente Bosch identifica el GWS 25-230 con estas especificaciones. El manual consultado es compartido con la variante GWS 25-180 LVI R, cuyas prestaciones deben leerse en su propia columna y no trasladarse al modelo de 230 mm.

**Análisis TallerLab:** frente al GWS 25-180 LVI R, este modelo admite un disco de 50 mm más de diámetro y declara 2.000 rpm menos en vacío; ambos publican 2.500 W. El cambio de diámetro no se traduce directamente en 25 mm más de profundidad de corte, porque intervienen el radio efectivo, la guarda y el disco. El dato de masa publicado, 5,9 kg, también debe considerarse al planificar el manejo de la herramienta.

**Declaración del fabricante:** Bosch lista funciones como arranque suave y control de retroceso para las variantes indicadas de la gama GWS 25 LVI R. La lista de funciones del modelo exacto y de su sufijo es la referencia; un código distinto puede cambiar interruptor o protecciones.

**Desconocido:** no se midió la profundidad útil de corte, la fatiga ni el rendimiento sobre metal o concreto. La ficha no constituye una recomendación para operar con una mano, sin guarda o con un disco de otra medida.

## Decisión por tamaño

| Si comparás… | GWS 25-180 LVI R | GWS 25-230 |
| :--- | ---: | ---: |
| Diámetro máximo de disco | 180 mm | 230 mm |
| Potencia absorbida | 2.500 W | 2.500 W |
| Velocidad en vacío | 8.500 rpm | 6.500 rpm |
| Peso publicado en las fichas revisadas | No indicado en el recorte usado | 5,9 kg |

Esta tabla ayuda a reconocer la variante por medida. La elección final depende del acceso, material, profundidad necesaria, disco compatible y manejo previsto.

## Fuentes consultadas

- **Documentación primaria:** [Bosch GWS 25-230](https://www.bosch-professional.com/ar/es/products/gws-25-180-06018F41H0); [Bosch GWS 25-180 LVI R](https://www.bosch-professional.com/ar/es/products/gws-25-180-lvi-r-06018F71H1); [manual compartido de la serie](https://www.bosch-professional.com/binary/manualsmedia/o424644v21_160992A8T6_202306.pdf).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "Comparación documental de Bosch 180 y 230 mm que contrasta potencia, velocidad y dato de peso disponible.",
        "/amoladoras/",
        "/amoladoras/7-pulgadas/",
        "amoladora de 7 pulgadas y 180 mm",
    ),
    "paginas/06-amoladora-de-banco.md": (
        "Amoladoras de banco Bosch y Lusqtoff: muelas, régimen y ciclo de trabajo",
        """| Dato publicado | Bosch GBG 35-15 | Lusqtoff AB-375 |
| :--- | ---: | ---: |
| Potencia absorbida | 350 W | 375 W |
| Diámetro de muela | 150 mm | 150 mm |
| Ancho / espesor de muela | 20 mm | 16 mm |
| Velocidad en vacío | 3.000 rpm a 50 Hz | 2.950 rpm |
| Peso | 10 kg | 6 kg |
| Muelas declaradas | Granos 24 y 60 | Granos 36 y 60 |
| Régimen de trabajo | S2 (60 min), según manual | No indicado en ficha citada |

**Dato documentado:** los valores corresponden a las fichas oficiales y manual de cada código. Bosch informa orificios de muela de 12,7/20 mm en manual; la página del producto describe discos de 20 mm. Lusqtoff publica piedra de 150 × 16 × 12,7 mm. Verificá el diámetro de eje y los bujes antes de montar un repuesto.

**Análisis TallerLab:** ambos ejemplos usan muelas de 150 mm, pero difieren en ancho publicado en 4 mm y en régimen en 50 rpm. Bosch publica un peso 4 kg mayor. Es una diferencia aritmética entre fichas, no evidencia de estabilidad o precisión. El dato S2 (60 min) de Bosch delimita el régimen de operación indicado por fabricante; no equivale a un permiso de funcionamiento indefinido.

**Declaración del fabricante:** Bosch incluye apoyos de pieza ajustables y protecciones contra chispas en la GBG 35-15. Lusqtoff indica protectores y perforaciones de base para anclaje en la AB-375. La presencia, forma y ajuste de los apoyos deben verificarse en la unidad exacta.

**Desconocido:** no se compararon vibración, temperatura, estabilidad instalada, facilidad de afilado o duración de muelas. Tampoco se confirma compatibilidad universal por compartir diámetro: ancho, orificio, velocidad y aplicación deben coincidir.

## Qué revisar al cambiar una muela

| Campo | Bosch GBG 35-15 | Lusqtoff AB-375 |
| :--- | :--- | :--- |
| Diámetro exterior | 150 mm | 150 mm |
| Ancho | 20 mm | 16 mm |
| Orificio | 12,7 o 20 mm según manual/variante | 12,7 mm |
| Velocidad indicada | 3.000 rpm a 50 Hz | 2.950 rpm |

No montes una muela basándote solo en el diámetro. Consultá su etiqueta y el manual del esmeril para revisar diámetro, espesor, orificio, tipo de trabajo y rpm máximas.

## Fuentes consultadas

- **Documentación primaria:** [Bosch GBG 35-15](https://www.bosch-professional.com/es/es/products/gbg-35-15-060127A300); [manual Bosch GBG 35-15](https://www.bosch-professional.com/binary/manualsmedia/o518745v21_160992AA24_202411.pdf); [Lusqtoff AB-375](https://www.lusqtoff.com.ar/productos/amoladora-de-banco-o-375-w-ab-375).
- **Seguridad:** revisar compatibilidad de muela, régimen, apoyos y protección en los manuales.
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "Comparación dimensional y de ciclo de trabajo entre dos esmeriles de banco de 150 mm.",
        "/amoladoras/",
        "/amoladoras/recta/",
        "amoladora recta",
    ),
    "paginas/03-amoladoras-dewalt.md": (
        "DWE402 y DWE4120: dos amoladoras DeWalt de 115 mm",
        """| Dato publicado en ficha estadounidense | DWE402 | DWE4120 |
| :--- | ---: | ---: |
| Diámetro de disco | 115 mm (4½ in) | 115 mm (4½ in) |
| Corriente nominal | 11 A | 9 A |
| Velocidad en vacío | 11.000 rpm | 12.000 rpm |
| Interruptor | Paleta con bloqueo de seguridad | Paleta |
| Guarda | One-Touch T27 según ficha | One-Touch con giro de 360° |
| Husillo | No transcrito en la fuente consultada | 5/8 in–11 |
| Tensión de variante | 120 V, página de Estados Unidos | Mercado Estados Unidos; consultar placa |

**Dato documentado:** las fuentes DeWalt identifican ambos productos como amoladoras con cable de 115 mm. La ficha DWE402 especifica 120 V y 11 A; DWE4120 declara 9 A, 12.000 rpm y rosca 5/8 in–11. Las páginas son estadounidenses y no confirman disponibilidad o especificaciones regionales de Argentina.

**Análisis TallerLab:** ambas herramientas admiten el diámetro nominal de 115 mm; la DWE4120 publica 1.000 rpm más en vacío, mientras la DWE402 publica 2 A más. Los amperes y rpm no permiten deducir por sí solos velocidad de remoción, torque o rendimiento bajo carga. Tampoco usamos esas cifras para elegir una herramienta con tensión distinta.

**Declaración del fabricante:** DeWalt describe el sistema de guarda One-Touch y bloqueo de seguridad en las fichas correspondientes. No inferimos que todos los sufijos DWE402/DWE4120 incluyan idénticos interruptores, accesorios o funciones.

**Desconocido:** no confirmamos la tensión argentina, certificación local, sufijo regional, contenido de kit, garantía local ni servicio posventa para los modelos consultados. Antes de comprar, verificá la placa del equipo y manual que acompañan la publicación.

## Diferencia que sí puede verificarse

| Pregunta de compra | Resultado limitado a estas fichas |
| :--- | :--- |
| ¿Comparten diámetro de disco? | Sí, 115 mm |
| ¿Publican la misma velocidad en vacío? | No; DWE4120 indica 1.000 rpm más |
| ¿Publican la misma corriente? | No; DWE402 indica 2 A más |
| ¿Estos datos prueban mayor rendimiento? | No; no hay una prueba común bajo carga |

## Fuentes consultadas

- **Documentación primaria:** [DeWalt DWE402](https://www.dewalt.com/en-us/product/dwe402/4-12-115mm-small-angle-grinder); [DeWalt DWE4120](https://www.dewalt.com/en-us/product/dwe4120/angle-grinder-tool-4-12-paddle-switch); [manual DWE4120](https://www.dewalt.com/GLOBALBOM/QU/DWE4120/1/Instruction_Manual/EN/N457586_DWE4120.pdf).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "Comparación de fichas DeWalt estadounidenses DWE402/DWE4120 con advertencia de tensión y mercado.",
        "/amoladoras/",
        "/amoladoras/inalambricas/",
        "amoladoras inalámbricas",
    ),
    "paginas/16-disco-de-corte.md": (
        "Disco de corte Bosch de 115 mm: material, espesor, agujero y montaje",
        """| Variante Bosch documentada | Aplicación declarada | Diámetro × espesor × orificio | Código de parte |
| :--- | :--- | :--- | :--- |
| PRO Metal | Corte de metal | 115 × 1,6 × 22,23 mm | 2 608 619 252 |
| PRO Stainless Steel and Metal | Corte de acero inoxidable y metal | 115 × 1,0 × 22,23 mm | 2 608 619 261 |
| PRO Metal de desbaste | Desbaste de metal | 115 × 6 × 22,23 mm | 2 608 600 218 |

**Dato documentado:** dimensiones y usos declarados por Bosch para los códigos listados. X-Lock y el montaje con tuerca son sistemas que dependen del disco exacto; comprobar el tipo de centro y la herramienta antes de instalar. La ficha del disco PRO Metal consultada describe una opción X-Lock, mientras la tabla dimensional corresponde al código 2 608 619 252.

**Análisis TallerLab:** el disco de desbaste de 6 mm es seis veces más grueso que la variante de corte de 1 mm y 3,75 veces más grueso que la de corte de 1,6 mm. Esas medidas describen geometría, no calidad del corte. La diferencia práctica decisiva es el uso que el fabricante declara: corte o desbaste; no elijas solo por grosor o por el diámetro exterior.

**Declaración del fabricante:** Bosch especifica cada disco para el material indicado y exige que la velocidad admisible del accesorio corresponda a la de la amoladora. La rpm máxima debe leerse en la etiqueta del accesorio exacto; no se completa por analogía con otro disco de 115 mm.

**Desconocido:** las fichas consultadas no cubren todas las aleaciones, espesores de pieza o condiciones de corte. Esta página no prescribe presión, ángulo ni rendimiento real. Para acero inoxidable, elegí una variante cuya documentación incluya explícitamente ese material.

## Filtro de compatibilidad antes del montaje

| Revisar | Ejemplo en esta tabla |
| :--- | :--- |
| Aplicación | Corte o desbaste según ficha |
| Diámetro exterior | 115 mm en los tres códigos |
| Agujero central | 22,23 mm en los tres códigos citados |
| Espesor | 1,0 mm / 1,6 mm para corte; 6 mm para desbaste |
| Velocidad y sistema de fijación | Comparar con etiqueta y manual de disco y amoladora |

## Fuentes consultadas

- **Documentación primaria:** [Bosch PRO Metal para corte](https://www.bosch-professional.com/ar/es/disco-de-corte-abrasivo-pro-metal-para-amoladoras-angulares-pequenas-x-lock-3090752-ocs-ac/); [Bosch PRO Stainless Steel and Metal](https://www.bosch-professional.com/ar/es/disco-de-corte-abrasivo-pro-stainless-steel-and-metal-de-larga-duracion-para-amoladoras-angulares-pequenas-x-lock-3090747-ocs-ac/); [Bosch PRO Metal para desbaste](https://www.bosch-professional.com/ar/es/disco-de-desbaste-abrasivo-pro-metal-para-amoladoras-angulares-pequenas-orificio-de-22-23-mm-osa-3090771-ocs-ac/); [manual Bosch de amoladoras](https://www.bosch-professional.com/binary/manualsmedia/o606197v21_160992AD3S_202509.pdf).
- **Seguridad:** respetar material, rpm, guarda y montaje especificados en manual y etiqueta.
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "Matriz técnica de discos Bosch para separar corte, desbaste, dimensiones y códigos concretos.",
        "/amoladoras/",
        "/amoladoras/disco-de-desbaste/",
        "disco de desbaste",
    ),
    "paginas/04-disco-de-desbaste.md": (
        "Bosch PRO Metal 115 × 6 mm: dimensiones y uso documentado de desbaste",
        """| Dato de producto | Bosch PRO Metal, código 2 608 600 218 |
| :--- | :--- |
| Aplicación declarada | Desbaste de metal |
| Diámetro exterior | 115 mm |
| Espesor | 6 mm |
| Orificio | 22,23 mm |
| Especificación abrasiva | A 30 T BF |
| Certificación indicada | oSa en la ficha |

**Dato documentado:** Bosch publica estas medidas y especificación para el disco de desbaste PRO Metal citado. La misma página lista una variante de 125 × 6 × 22,23 mm y otra de 125 mm con especificación distinta; no combinar sus códigos ni granulometrías.

**Análisis TallerLab:** la tabla permite comprobar tres condiciones geométricas antes de comprar: disco máximo admitido por la amoladora, orificio compatible con brida y tuerca, y espesor. Frente a un disco de corte de 115 × 1,6 × 22,23 mm, el disco de desbaste de 6 mm es 3,75 veces más grueso. No deben intercambiarse sus aplicaciones: Bosch identifica uno para desbaste y el otro para corte.

**Declaración del fabricante:** Bosch describe el disco como destinado a desbastar metal, con granos de óxido de aluminio, matriz de resina y refuerzo de fibra de vidrio. Son características declaradas por el fabricante; no reportamos ensayos propios de duración o productividad.

**Desconocido:** el código consultado no autoriza una conclusión común para todos los metales, fundiciones o aceros inoxidables. Tampoco define por sí solo el ángulo de trabajo, presión o vida útil. Confirmá que el material esté indicado en la ficha del abrasivo exacto.

## Diferenciar desbaste de corte

| Accesorio de referencia | Dimensiones | Uso publicado | Lectura documental |
| :--- | :--- | :--- | :--- |
| Bosch PRO Metal 2 608 600 218 | 115 × 6 × 22,23 mm | Desbaste de metal | Disco más grueso en esta comparación |
| Bosch PRO Metal 2 608 619 252 | 115 × 1,6 × 22,23 mm | Corte de metal | Código de disco de corte; no sustituye al de desbaste |

Para remover material de una cara o borde, consultá la categoría “desbaste” y las indicaciones del fabricante. Para separar una pieza, usá un disco de corte admitido para el material y la amoladora.

## Fuentes consultadas

- **Documentación primaria:** [Bosch PRO Metal para desbaste](https://www.bosch-professional.com/ar/es/disco-de-desbaste-abrasivo-pro-metal-para-amoladoras-angulares-pequenas-orificio-de-22-23-mm-osa-3090771-ocs-ac/); [Bosch PRO Metal para corte](https://www.bosch-professional.com/ar/es/disco-de-corte-abrasivo-pro-metal-para-amoladoras-angulares-pequenas-x-lock-3090752-ocs-ac/); [manual Bosch de amoladoras angulares](https://www.bosch-professional.com/binary/manualsmedia/o606197v21_160992AD3S_202509.pdf).
- **Seguridad:** nunca exceder las rpm indicadas en la etiqueta del disco ni retirar la guarda.
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "Ficha documentada de un disco de desbaste de 115 mm y comparación funcional con un disco de corte.",
        "/amoladoras/",
        "/amoladoras/disco-de-corte/",
        "disco de corte para amoladora",
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
