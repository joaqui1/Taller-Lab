"""Undécimo lote editorial: diez guías de generadores."""
from pathlib import Path
import re

ROOT = Path(__file__).parent

PAGES = {
    "paginas/generadores/21-grupos-electrogenos-chicos.md": (
        "Contraste entre los datos de publicación de Pektra GPK980 y la ficha de fabricante del Konan KGE/800; separa potencia nominal y máxima.",
        """| Modelo | Potencia nominal publicada | Potencia máxima publicada | Motor / datos disponibles | Estado de la evidencia |
| :--- | ---: | ---: | :--- | :--- |
| Pektra GPK980 | 650 W | 720 W | La publicación comercial lo identifica como 2 tiempos, mezcla, 220 V y arranque manual | Publicación de vendedor; no se halló manual o ficha del fabricante que confirme esos campos |
| Konan KGE/800 | 650 W | 800 W | 2 tiempos, 63 cm³, 220 V–50 Hz, tanque 4 L y 4,5 h declaradas | Sitio del representante exclusivo publica ficha y manual |
| Gamma GE3441AR / 950 | El fabricante llama al campo «energía generada contenida»: 0,57 kW | 0,87 kW | 2 tiempos, 63 cm³, producto discontinuado | Ficha oficial; el nombre del campo no se sustituye por «potencia nominal» |

**Dato documentado:** Konan informa 650 W nominales y 800 W máximos para KGE/800. Para Pektra GPK980, la fuente consultada es una publicación comercial cuyo título dice 720 W; una página de comercio que reproduce datos del vendedor enumera 650 W nominales y 720 W máximos. No localizamos documentación primaria del fabricante Pektra que confirme esos valores. Gamma publica para el GE3441AR máximo de 0,87 kW y «energía generada contenida» de 0,57 kW.

**Análisis TallerLab:** en KGE/800, el valor máximo supera el nominal en 150 W (23,1 % sobre 650 W). En Pektra GPK980 la diferencia sería 70 W (10,8 %) si la cifra nominal de 650 W de la publicación comercial se confirma. Estas restas no son una prueba de arranque de motores ni de compatibilidad con una carga concreta; para seleccionar hay que cotejar potencia de funcionamiento y pico de arranque en las placas/manuales de los equipos conectados.

**Desconocido:** no se verificaron de forma primaria para Pektra el consumo, el peso, la autonomía ni la potencia nominal. En Gamma, la página consultada no rotula 0,57 kW como potencia nominal continua, así que conservamos su nombre original.

## Fuentes consultadas

- **Documentación primaria:** [Konan, KGE/800 y especificaciones](https://www.konan.com.ar/productos/generador-electrico-kge-800); [catálogo oficial Konan 2025](https://konan.com.ar/media/descargas/KONAN-Catalogo-2025.pdf); [Gamma, GE3441AR/950 discontinuado](https://www.gammaherramientas.com.ar/producto/grupo-electrogeno-950/).
- **Información comercial:** [publicación de Pektra GPK980 en Mercado Libre](https://listado.mercadolibre.com.ar/construccion/electricidad/grupos-electrogenos/nuevo/pektra/); sus cifras no se atribuyen al fabricante.
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/generadores/", "/generadores/gamma-950/", "Gamma 950 y sus límites documentales",
    ),
    "paginas/generadores/01-grupos-electrogenos.md": (
        "Tabla de potencia nominal y máxima en tres modelos documentados más una cuenta de carga reproducible a partir de voltios y amperes.",
        """| Modelo / fuente | Potencia nominal | Potencia máxima | Tensión y fase publicados | Dato que no debe confundirse |
| :--- | ---: | ---: | :--- | :--- |
| Honda EG6500CXS | 5,0 kVA | 5,5 kVA | 220 V, monofásico | El documento expresa potencia aparente en kVA |
| Honda EZ6500CXS | 5,5 kVA | 6,5 kVA | 220 V, monofásico | El pico no es la potencia nominal de servicio |
| Gamma GE3481AR 6000V | 5,5 kW | 6,0 kW | 220 VCA, salida auxiliar 12 VCC | La ficha identifica los valores en kW |

**Dato documentado:** las fichas de Honda separan nominal y máximo en kVA; Gamma publica para GE3481AR 5,5 kW de potencia y 6 kW máxima. No convertimos kVA a kW sin el factor de potencia aplicable a la carga.

### Una cuenta de carga que sí puede repetirse

El manual Hyundai indica calcular watts como voltios × amperes cuando no está impresa la potencia en watts. Por ejemplo, un equipo rotulado 220 V y 4 A representa 880 W de potencia aparente calculada en corriente alterna monofásica; si el fabricante informa W directamente, usar ese dato y considerar el factor de potencia de la carga cuando corresponda. La suma de las cargas de marcha no debe compararse con el valor máximo breve como si ambos fueran el mismo régimen.

**Análisis TallerLab:** en el Gamma citado, la diferencia entre 6,0 kW máximos y 5,5 kW publicados como potencia es 0,5 kW (9,1 % sobre 5,5). En Honda EG6500CXS, la diferencia indicada entre nominal y máxima es 0,5 kVA. Las unidades y fuentes difieren, así que los dos resultados no permiten ordenar equipos entre marcas.

**Desconocido:** el consumo de arranque depende del aparato y no se deduce de su potencia de marcha sin datos del fabricante. Esta guía no afirma que un modelo alimente una heladera, bomba, soldadora o vivienda sin calcular las cargas exactas y revisar tensión, fase, frecuencia y picos.

## Fuentes consultadas

- **Documentación primaria:** [Honda EG6500CXS](https://pf.honda.com.ar/producto/EG6500CXS); [Honda EZ6500CXS](https://pf.honda.com.ar/producto/EZ6500CXS); [Gamma GE3481AR, 6000V](https://www.gammaherramientas.com.ar/producto/grupo-electrogeno-6000v/); [manual Hyundai HHY2200F: cálculo de watts y cargas](https://hyundaiherramientas.com.ar/wp-content/uploads/Manuales_Fichas/019-0010.pdf).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/generadores/", "/generadores/diesel/", "generadores diésel: datos y límites",
    ),
    "paginas/generadores/14-generadores-diesel.md": (
        "Matriz de tres códigos diésel comercializados localmente que evidencia qué modelos tienen potencia continua publicada y cuáles solo informan máximo.",
        """| Código publicado | Potencia máxima | Potencia continua publicada | Cilindrada / fase o presentación | Límite de la ficha consultada |
| :--- | ---: | ---: | :--- | :--- |
| Hyundai 070G | 8.000 W | Desconocida | 465 cm³; listado como monofásico | No informa tanque ni consumo en la ficha abierta |
| Hyundai 071G | 8.000 W | Desconocida | 465 cm³; insonorizado según título comercial | El campo de uso continuo dice 6,5 h, sin detallar carga |
| Hyundai 073G | 6.400 W | 5.800 W | 456 cm³; insonorizado según título comercial | El vendedor publica 6,5 h, pero no indica carga de ensayo |
| Hyundai 080G | 8 kVA máximo | Desconocida | Trifásico; 456 cm³ | La página alterna rótulos kVA y kW en sus datos; confirmar placa |

**Dato documentado:** el sitio local de Hyundai Herramientas lista los códigos 070G, 071G y 073G en su familia de generadores diésel. Sus fichas comerciales publican 8.000 W máximos para 070G y 071G; para 073G publican 5.800 W continuos y 6.400 W máximos. La ficha del 080G lo titula 8 kVA, mientras otros campos usan W; señalamos esa inconsistencia para cotejo con la placa y manual.

**Análisis TallerLab:** solo para 073G pueden calcularse ambas potencias desde los datos publicados: 6.400 − 5.800 = 600 W (10,3 % sobre la continua). No asignamos 5.800 W continuos a los códigos 070G o 071G por similitud de cilindrada o presentación. “Uso continuo 6,5 h” es duración declarada sin una carga identificada y no equivale a ciclo de trabajo ilimitado.

**Desconocido:** no se encontraron en las páginas abiertas consumos en L/h por porcentaje de carga, capacidad de tanque y peso para todos los códigos. La página de 070G/071G/073G advierte consultar el manual para requisitos de energía; estos datos no bastan para calcular costo horario ni dimensionar una instalación.

## Fuentes consultadas

- **Información del representante local Hyundai:** [070G diésel monofásico](https://hyundaiherramientas.com.ar/producto/generador-diesel-monofasico-8kva-070g/); [071G diésel insonorizado](https://hyundaiherramientas.com.ar/producto/generador-insonorizado-8-kva-071g/); [073G diésel insonorizado](https://hyundaiherramientas.com.ar/producto/generador-insonorizado-8-kva-073g); [080G diésel trifásico](https://hyundaiherramientas.com.ar/producto/generador-diesel-trifasico-con-arranque-electrico-8-kva-080g/).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/generadores/", "/generadores/hyundai/", "generadores Hyundai: modelos y diferencias",
    ),
    "paginas/generadores/20-estaciones-de-energia-portatiles.md": (
        "Comparación de EcoFlow DELTA 2 y BLUETTI AC70 que separa capacidad almacenada en Wh de límite instantáneo de salida en W y calcula autonomías ideales de referencia.",
        """| Modelo | Energía nominal almacenada | Salida CA nominal | Pico indicado | Región/documento |
| :--- | ---: | ---: | ---: | :--- |
| EcoFlow DELTA 2 | 1.024 Wh | 1.800 W | 2.700 W | Manual regional UE, 230 V |
| BLUETTI AC70 | 768 Wh | 1.000 W | No se usa aquí un dato de pico | Catálogo del fabricante; variantes de tomacorriente por región |

**Dato documentado:** el manual EcoFlow separa 1.024 Wh de capacidad de batería y 1.800 W de salida CA (2.700 W de pico). El catálogo BLUETTI declara para AC70 768 Wh y 1.000 W. Wh describe energía almacenada; W de salida describe el límite de potencia instantánea declarado.

### Una estimación matemática, no una prueba de autonomía

| Carga constante supuesta | DELTA 2: 1.024 Wh ÷ carga | AC70: 768 Wh ÷ carga |
| :--- | ---: | ---: |
| 100 W | 10,24 h teóricas | 7,68 h teóricas |
| 500 W | 2,05 h teóricas | 1,54 h teóricas |

**Análisis TallerLab:** las divisiones usan toda la capacidad nominal como si no hubiera pérdidas. Son techos matemáticos, no autonomías medidas ni garantías: salida CA, conversión, temperatura, corte de descarga y comportamiento de la carga modifican el tiempo real. A igual carga de 100 W, la diferencia aritmética de capacidad es 2,56 h ideales; no es una promesa de duración.

**Desconocido:** no se midieron Wh realmente utilizables en salida CA, consumo propio del inversor ni rendimiento de las unidades. Antes de conectar un equipo, verificar potencia de marcha, pico de arranque, tensión y compatibilidad de enchufe para la región exacta; X-Boost y funciones equivalentes no sustituyen el límite nominal para todos los aparatos.

## Fuentes consultadas

- **Documentación primaria:** [manual oficial EcoFlow DELTA 2 en español](https://manuals.ecoflow.com/eu/product/delta-2-portable-power-station?lang=es_ES); [catálogo oficial BLUETTI, AC70](https://bluetti.com/wp-content/uploads/2024/09/%EF%BC%88%E7%94%B5%E5%AD%90%E7%89%88%EF%BC%89Product-Catalog-EN-V4.2-1.pdf); [página BLUETTI AC70](https://www.bluettipower.com/products/ac70).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/generadores/", "/generadores/", "guías de grupos electrógenos",
    ),
    "paginas/generadores/10-gamma-6500.md": (
        "Ficha comparativa del Gamma GE3466AR/6500V discontinuado: registra código, potencia, autonomía declarada y batería no incluida, y evita presentarlo como línea actual.",
        """| Campo publicado para Gamma 6500V | Dato del código GE3466AR | Lectura editorial |
| :--- | :--- | :--- |
| Estado en sitio de Gamma | Discontinuado | No demuestra disponibilidad actual ni soporte de una unidad usada |
| Potencia continua publicada | 5,5 kW | Atribuida a la página del fabricante |
| Potencia máxima publicada | 6 kW | Diferencia de 0,5 kW frente al campo continuo |
| Motor / tanque | 389 cm³ / 25 L | La ficha lo identifica como naftero de 4 tiempos |
| Arranque y batería | Eléctrico; batería no incluida | Confirmar batería compatible y estado en la unidad concreta |
| Autonomía | La página de producto y manuales consultados no ofrecen una condición uniforme | No se publica como duración garantizada a una carga especificada |

**Dato documentado:** Gamma marca el 6500V como discontinuado y lo identifica como GE3466AR. La ficha del fabricante publica 5,5 kW continuos y 6 kW máximos; informa 389 cm³, tanque de 25 L, arranque eléctrico y aclara que la batería no viene incluida.

**Análisis TallerLab:** la potencia máxima publicada supera la continua en 500 W, equivalente a 9,1 % de la cifra continua. Para dimensionar una carga, la referencia debe ser la potencia continua y las instrucciones del manual del ejemplar; el margen máximo no se trata como régimen prolongado. Como el producto está discontinuado, una publicación comercial actual no prueba disponibilidad de repuestos, garantía o condición de una unidad usada.

**Desconocido:** la evidencia revisada no permite fijar autonomía por carga, consumo horario representativo ni compatibilidad de artefactos sin datos de placa y de arranque. Tampoco se verificó soporte de servicio actual para cada región.

## Fuentes consultadas

- **Documentación primaria:** [Gamma, Grupo Electrógeno 6500V GE3466AR](https://www.gammaherramientas.com.ar/producto/grupo-electrogeno-6500-v-2/); [manual Gamma de grupos serie V](https://www.gammaherramientas.com.ar/web/wp-content/uploads/2023/11/MANUAL-GE-OK_compressed.pdf); [archivo Gamma de productos discontinuados](https://www.gammaherramientas.com.ar/categoria-producto/discontinuos/).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/generadores/", "/generadores/gamma/", "generadores Gamma por modelo",
    ),
    "paginas/generadores/17-gamma-950.md": (
        "Calcula la diferencia entre las dos salidas que Gamma publica para GE3441AR y preserva el rótulo ambiguo del fabricante en vez de llamarlo potencia nominal.",
        """| Campo Gamma para GE3441AR | Valor publicado | Interpretación permitida |
| :--- | ---: | :--- |
| Potencia máxima | 0,87 kW | El fabricante lo denomina máximo |
| «Energía generada contenida» | 0,57 kW | Se conserva el rótulo; la página no lo define como nominal/continua |
| Tensión / frecuencia | 220 V / 50 Hz | Dato publicado por Gamma |
| Motor y combustible | 2 tiempos, 63 cm³ | Gamma indica motor naftero 2T; no inferimos mezcla exacta sin seguir el manual |
| Estado | Discontinuado | Confirmado en la página oficial Gamma |

**Dato documentado:** Gamma publica para el modelo 950 GE3441AR 0,87 kW de potencia máxima y 0,57 kW bajo el campo «energía generada contenida», además de 220 V–50 Hz, motor naftero de 2 tiempos, tanque de 4,2 L y 22 kg. La marca indica que el producto está discontinuado.

**Análisis TallerLab:** 0,87 − 0,57 = 0,30 kW (300 W); el máximo publicado es 52,6 % mayor que el valor de «energía generada contenida». Ese cálculo deja ver dos cifras distintas en la ficha, pero no determina por sí mismo cuántos watts puede sostener el equipo en uso prolongado: Gamma no define el segundo rótulo en la página consultada. No transformamos esas cifras en recomendación para cargas concretas.

**Desconocido:** no afirmamos una lista de artefactos compatibles, consumo horario ni autonomía a carga determinada a partir del tanque y las horas que aparecen en la ficha. Para una unidad usada, comprobar etiqueta y manual correspondiente.

## Fuentes consultadas

- **Documentación primaria:** [Gamma, ficha GE3441AR / Grupo Electrógeno 950](https://www.gammaherramientas.com.ar/producto/grupo-electrogeno-950/); [manual Gamma grupos electrógenos](https://www.gammaherramientas.com.ar/web/wp-content/uploads/2023/11/MANUAL-GE-OK_compressed.pdf); [despiece Gamma GE3441AR](https://www.gammaherramientas.com.ar/web/wp-content/uploads/grupos-electrogenos_grupo-electrogeno-950_GE3441AR-103-despiece.pdf).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/generadores/", "/generadores/chicos/", "generadores chicos: potencias documentadas",
    ),
    "paginas/generadores/12-generadores-gamma.md": (
        "Mapa de modelos Gamma que distingue equipos actuales de discontinuados y compara cifras de potencia, tanque y autonomía solo donde la ficha las publica.",
        """| Modelo / artículo | Estado en el sitio Gamma | Potencia continua / máxima publicada | Tanque | Autonomía declarada |
| :--- | :--- | :--- | ---: | :--- |
| GE3480AR / 3000V | En catálogo actual consultado | 2,7 / 3,0 kW | 15 L | 13 h a 50 %; 8 h a 100 % |
| GE3481AR / 6000V | En catálogo actual consultado | 5,5 / 6,0 kW | 25 L | 10 h a 50 %; 6 h a 100 % |
| GE3464AR / 3500V | Discontinuado | 2,8 / 3,1 kW en manual de serie V | 12 L | No confirmado en la ficha del fabricante abierta |
| GE3466AR / 6500V | Discontinuado | 5,5 / 6,0 kW | 25 L | La página y los documentos consultados no dan una condición homogénea |
| GE3441AR / 950 | Discontinuado | Máx. 0,87 kW; otro campo dice 0,57 kW «energía generada contenida» | 4,2 L | La página indica 2,8 h, sin carga de ensayo explícita |

**Dato documentado:** Gamma publica para GE3480AR y GE3481AR potencias, autonomías por carga y tanques distintos. Para los códigos antiguos GE3464AR y GE3466AR, el archivo oficial de discontinuados los identifica como tales y su manual de serie V conserva especificaciones. El manual de GE3464AR expresa dos cifras de potencia, pero la transcripción consultada no conserva de forma clara los rótulos de columna; se muestran como par del documento y no se equiparan con la misma nomenclatura de las fichas actuales.

**Análisis TallerLab:** al pasar de GE3480AR a GE3481AR, el tanque aumenta 10 L (66,7 % respecto de 15 L) y la autonomía publicada a media carga baja de 13 a 10 h. No se debe interpretar como comparación de eficiencia sin mismo procedimiento y salida comparable. En el GE3441AR tampoco convertimos 0,57 kW en potencia nominal, porque Gamma usa otro rótulo.

**Desconocido:** no hay base en estas páginas para comparar precios actuales, repuestos, garantía, consumo horario entre toda la gama o compatibilidad con una carga concreta. La disponibilidad debe confirmarse por código y vendedor.

## Fuentes consultadas

- **Documentación primaria:** [Gamma GE3480AR / 3000V](https://www.gammaherramientas.com.ar/producto/grupo-electrogeno-3000v-ge3480ar/); [Gamma GE3481AR / 6000V](https://www.gammaherramientas.com.ar/producto/grupo-electrogeno-6000v/); [Gamma GE3441AR / 950](https://www.gammaherramientas.com.ar/producto/grupo-electrogeno-950/); [manual Gamma de serie V](https://www.gammaherramientas.com.ar/web/wp-content/uploads/2023/11/MANUAL-GE-OK_compressed.pdf); [Gamma, discontinuados](https://www.gammaherramientas.com.ar/categoria-producto/discontinuos/).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/generadores/", "/generadores/gamma-6500/", "Gamma 6500: ficha y estado de línea",
    ),
    "paginas/generadores/04-honda-6500.md": (
        "Comparación de las fichas Honda EG6500CXS y EZ6500CXS: diferencias en potencia, combustible, peso y autonomía documentada pese al número comercial parecido.",
        """| Campo de ficha | EG6500CXS | EZ6500CXS |
| :--- | ---: | ---: |
| Potencia nominal CA | 5,0 kVA | 5,5 kVA |
| Potencia máxima CA | 5,5 kVA | 6,5 kVA |
| Motor | GX390, 389 cm³, 4 tiempos | GX390, 389 cm³, 4 tiempos |
| Combustible / tanque | 24 L | 15,5 L |
| Uso continuo publicado | 8,1 h | 5,8 h |
| Peso en seco | 87 kg | 80 kg |
| Regulación | D-AVR | AVR |

**Dato documentado:** Honda lista para EG6500CXS 5,0 kVA nominales y 5,5 kVA máximos, con tanque de 24 L y 8,1 h declaradas. Para EZ6500CXS publica 5,5 kVA nominales y 6,5 kVA máximos, tanque de 15,5 L y 5,8 h. Ambas fichas informan motor GX390 de 389 cm³ y 220 V–50 Hz.

**Análisis TallerLab:** el EZ6500CXS declara 1,0 kVA más de máximo que el EG6500CXS (18,2 % sobre 5,5 kVA), mientras el EG informa 8 kg más de peso en seco y 8,5 L más de capacidad de combustible. Las autonomías declaradas no permiten comparar rendimiento porque no se especifica una condición de carga equivalente. El número «6500» del EZ no debe sustituir la potencia nominal impresa en la ficha.

**Desconocido:** ninguna ficha citada prueba qué aparatos específicos puede arrancar ni el consumo en todas las cargas. Comprobar factor de potencia, corriente de arranque, tensión/fase y placa del equipo antes de dimensionar.

## Fuentes consultadas

- **Documentación primaria:** [Honda EG6500CXS](https://pf.honda.com.ar/producto/EG6500CXS); [ficha técnica Honda EG6500CXS](https://pf.honda.com.ar/descargar/ficha_tecnica/EG6500.pdf); [Honda EZ6500CXS](https://pf.honda.com.ar/producto/EZ6500CXS); [ficha técnica Honda EZ6500CXS](https://pf.honda.com.ar/descargar/ficha_tecnica/EZ6500CXS.pdf).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/generadores/", "/generadores/honda/", "generadores Honda por modelo",
    ),
    "paginas/generadores/03-grupos-electrogenos-honda.md": (
        "Tabla de la gama Honda publicada en Argentina que separa equipos inverter compactos, convencionales y un modelo de mayor tensión/fase.",
        """| Modelo Honda | Potencia nominal CA | Potencia máxima CA | Salida CA / regulación | Masa en seco |
| :--- | ---: | ---: | :--- | ---: |
| EU22i | 1,8 kVA | 2,2 kVA | 220 V monofásica; inverter | 21 kg |
| EU30is | 2,8 kVA | 3,0 kVA | 220 V monofásica; inverter | 59 kg |
| EG6500CXS | 5,0 kVA | 5,5 kVA | 220 V monofásica; D-AVR | 87 kg |
| EZ6500CXS | 5,5 kVA | 6,5 kVA | 220 V monofásica; AVR | 80 kg |
| ET12000 | 11 kVA máxima publicada | 12 kVA nominal: desconocido en el fragmento consultado | 220/380 V, monofásico y trifásico; AVR | 162 kg |

**Dato documentado:** las fichas oficiales de Honda permiten separar EU22i y EU30is, que identifican regulación inverter y potencias distintas, de EG/EZ6500CXS con AVR o D-AVR. La ficha de ET12000 lo describe como salida mono/trifásica 220/380 V y publica 11 kVA máximos. No inventamos una potencia nominal ausente en el fragmento usado.

**Análisis TallerLab:** EU30is declara 1,2 kVA más de potencia máxima que EU22i (54,5 % respecto de 2,2 kVA), y pesa 38 kg más. Esta comparación de ficha no determina autonomía, nivel sonoro en una misma condición ni adecuación a una herramienta. En los modelos rotulados 6500, la potencia nominal tampoco coincide; conviene comparar el código completo, no el número comercial.

**Desconocido:** la categoría de marca no confirma stock, precio, garantía o revisión de cada unidad en Argentina. Para conectar cargas, cotejar potencia nominal, arranque, tensión, frecuencia, fase y factor de potencia; el rótulo inverter por sí solo no valida compatibilidad con todo dispositivo.

## Fuentes consultadas

- **Documentación primaria:** [catálogo de generadores Honda Argentina](https://pf.honda.com.ar/categoria-producto/generadores); [Honda EU22i](https://pf.honda.com.ar/producto/EU22i); [Honda EU30is](https://pf.honda.com.ar/producto/EU30is); [Honda EG6500CXS](https://pf.honda.com.ar/producto/EG6500CXS); [Honda ET12000](https://pf.honda.com.ar/producto/ET12000).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/generadores/", "/generadores/honda-6500/", "Honda 6500: diferencias entre EG y EZ",
    ),
    "paginas/generadores/09-generadores-hyundai.md": (
        "Comparativa de modelos Hyundai publicados por el representante local: potencia de marcha y máxima en códigos pequeños, con una brecha aritmética por modelo.",
        """| Modelo | Potencia continua publicada | Potencia máxima publicada | Cilindrada | Uso continuo publicado |
| :--- | ---: | ---: | ---: | ---: |
| HYH960A | 720 W | 800 W | 63 cm³ | 6,3 h |
| HHY2200F | 2.000 W | 2.200 W | 210 cm³ | 8 h |
| HHY3000FE | 2.500 W | 2.800 W | 210 cm³ | 8 h |

**Dato documentado:** la tienda Hyundai Herramientas para Argentina publica para HYH960A 720 W continuos y 800 W máximos; para HHY2200F 2.000/2.200 W; y para HHY3000FE 2.500/2.800 W. Son datos de sus fichas comerciales y deben cotejarse con manual/placa de la unidad; las páginas consultadas también señalan falta de stock en varios productos.

**Análisis TallerLab:** las diferencias máxima menos continua son 80 W en HYH960A, 200 W en HHY2200F y 300 W en HHY3000FE. Respecto de su potencia continua, equivalen a 11,1 %, 10 % y 12 %. El porcentaje compara únicamente cada ficha consigo misma; no representa potencia de arranque comprobada ni rendimiento.

**Desconocido:** las tres autonomías no tienen porcentaje de carga común documentado en estas páginas, así que no se deben ordenar por duración. No se verificaron con esas fuentes el caudal o pico de motores conectados, la garantía regional de cada código ni el stock actual.

## Fuentes consultadas

- **Información del representante local Hyundai:** [HYH960A, ficha publicada](https://hyundaiherramientas.com.ar/producto/generador-800-w-hyh960a/); [HHY2200F, ficha publicada](https://hyundaiherramientas.com.ar/producto/generador-2200-w-hhy2200f/); [catálogo/listado de generadores Hyundai](https://hyundaiherramientas.com.ar/categoria-producto/generadores/).
- **Documentación técnica:** [manual de la serie HHY](https://hyundaiherramientas.com.ar/wp-content/uploads/Manuales_Fichas/019-0010.pdf), para instrucciones de suma de cargas; no reemplaza el manual del código específico.
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/generadores/", "/generadores/chicos/", "generadores chicos: potencia continua y máxima",
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
        f"Para explorar la categoría: [guías de generadores]({hub}).\n"
    )
    path.write_text(f"---\n{front}\n---\n\n{newbody}", encoding="utf-8")
    print(relpath)
