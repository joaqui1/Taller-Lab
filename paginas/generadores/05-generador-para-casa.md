---
title: "Generador eléctrico para casa: qué potencia necesitás"
h1: "Cómo elegir un generador eléctrico para tu casa"
url: "/generadores/para-casa/"
description: "Calculá las cargas simultáneas y sus arranques, compará generadores por escala de potencia y revisá las medidas de seguridad para una vivienda."
author: "Joaquín Vallasciani"
category: "Generadores y Grupos Electrógenos"
keywords: ["generador electrico para casa", "que generador necesito para una casa", "grupo electrogeno para casa", "generador aire acondicionado y heladera"]
research_type: "documental"
physical_test: "no"
specifications_contrasted: "sí"
buyer_opinions: "no"
primary_sources: "sí"
information_asset: "Calculadora de cargas simultáneas con escenarios basados en manuales y fichas, referencias de equipos por escala y seguridad de instalación."
asset_status: "verificado"
reviewed: "28/09/2026"
published: true
---

# Cómo elegir un generador eléctrico para tu casa

<!-- AUDITORIA_EDITORIAL_178 -->

Para dimensionar un generador para una vivienda, definí primero qué cargas querés mantener encendidas al mismo tiempo. Después sumá su consumo de marcha y comprobá qué pasa cuando arranca el motor más exigente. Los ejemplos de abajo muestran cómo usar valores publicados y reemplazarlos por los de tus equipos.

Para comparar otros tamaños y configuraciones, consultá la [guía general para elegir un grupo electrógeno](/generadores/comparativa-general/).

La potencia por sí sola no decide la compra: también hay que revisar tensión, fase, tipo de regulación y cómo se va a conectar el equipo. Si querés alimentar circuitos de la casa, necesitás una transferencia instalada por un profesional; las medidas de seguridad aparecen antes de las referencias de modelos.


**Dato documentado:** las especificaciones se atribuyen a las fuentes enlazadas; los datos comerciales y las variantes se identifican por separado.

**Análisis TallerLab:** los criterios de selección interpretan la documentación según la carga prevista; esta guía no incluye prueba física de los equipos.

## Cómo calcular la potencia

Anotá solo los artefactos que querés usar durante un corte. De sus placas o manuales, copiá potencia o corriente de marcha, tensión, fase y dato de arranque. Si la carga informa amperios, calculá potencia aparente como **VA = voltios × amperios**. Si informa watts y factor de potencia (PF), estimá **VA = W ÷ PF**. Para una carga resistiva con PF 1, W y VA coinciden aproximadamente.

La suma de marcha muestra la carga simultánea sostenida. Para el pico, mantené las otras cargas que estarán encendidas y reemplazá la marcha del motor por su valor de arranque. Elegí usando la potencia nominal del generador para marcha y verificá también que el pico calculado quede dentro de lo que el manual permite; la potencia máxima no es una capacidad continua.

| Carga que vas a conectar | Marcha: dato de placa/manual | Arranque: dato de placa/manual | Tensión y fase | Fuente consultada |
| :--- | :--- | :--- | :--- | :--- |
| Heladera / motor | ______ VA o W | ______ VA o A | ______ | ______ |
| Iluminación | ______ VA o W | ______ VA o A | ______ | ______ |
| Aire acondicionado | ______ VA o W | ______ VA o A | ______ | ______ |
| Bomba u otra carga | ______ VA o W | ______ VA o A | ______ | ______ |
| **Total de marcha simultánea** | **______ VA** |  |  |  |
| **Pico con el motor más exigente arrancando** |  | **______ VA** |  |  |

## Heladera, luces y aire acondicionado

### Ejemplo completado: heladera y luces

El manual del generador Lüsqtoff LG2500 usa un ejemplo estimado de heladera de 150 W: indica 300 VA en trabajo y 450–750 VA al arrancar. En la misma tabla, una lámpara incandescente de 100 W aparece con 100 VA tanto en arranque como en trabajo. No son valores universales; sirven para mostrar la operación.

Supongamos tres lámparas de ese tipo encendidas junto con la heladera:

- **Marcha:** 300 VA de heladera + (3 × 100 VA de lámparas) = **600 VA**.
- **Pico al arrancar la heladera:** 450–750 VA + 300 VA de luces = **750–1.050 VA**.
- La hoja queda completa para esas cargas: la marcha suma 0,6 kVA y el pico estimado, 0,75–1,05 kVA.

Al hacer tu cuenta, sustituí la heladera y las lámparas de este ejemplo por los datos de placa reales. Si el fabricante no da el arranque de la heladera, buscá la corriente LRA/pico en su etiqueta o manual; no la deduzcas aplicando un multiplicador universal.

### Escenario con aire acondicionado: una cuenta de placa

LG publica para el modelo inverter US-W096WSG3 una potencia de entrada de 815 W y una corriente de refrigeración de 5 A. A 220 V, la corriente corresponde a **1.100 VA** (220 × 5). Para combinarlo con la heladera estimada y las tres lámparas anteriores:

- **Marcha simultánea:** 1.100 VA del aire + 300 VA de heladera + 300 VA de luces = **1.700 VA (1,7 kVA)**.
- **Pico si arranca la heladera mientras el aire ya funciona:** 1.100 + 300 + 450–750 = **1.850–2.150 VA (1,85–2,15 kVA)**.

La página de LG consultada no informa el pico de arranque del aire acondicionado. Por eso esta segunda cuenta **no valida el arranque simultáneo del compresor del aire**. Revisá el manual/placa del código exacto o pedí ese dato al fabricante antes de dimensionar para esa combinación. Un equipo inverter puede variar su consumo mientras regula; usá el máximo eléctrico publicado, si está disponible, y no las frigorías como si fueran watts eléctricos.

## Inverter o convencional

| Qué necesitás priorizar | Qué revisar en un inverter | Qué revisar en un convencional |
| :--- | :--- | :--- |
| Electrónica y cargas sensibles | Tipo de onda declarado, tensión/frecuencia y límites de potencia; la tecnología inverter no reemplaza la compatibilidad indicada por el fabricante del aparato | Tipo de regulación (por ejemplo AVR) y especificación de tensión/frecuencia bajo carga; no asumir que toda electrónica es compatible |
| Cargas con motor y arranques | Potencia nominal, máxima y respuesta/pico admitido; una salida estable no significa capacidad de arranque suficiente | Potencia nominal y máxima, corriente de arranque admitida y regulación de tensión |
| Uso con carga variable o baja | Si tiene modo económico y cómo afecta autonomía y potencia disponible | Consumo y autonomía publicados para distintas cargas, si el fabricante los informa |
| Portabilidad y uso cerca de personas | Peso y ruido medido con condición comparable | Peso, ruido y ubicación necesaria; no inferir nivel sonoro por ser convencional |

Compará las cifras del manual del modelo concreto. “Inverter” describe una tecnología de generación/regulación; no es sinónimo de más potencia, arranque más fácil ni silencio garantizado.

Para comparar modelos, consultá [generadores inverter](/generadores/inverter/) y revisá la salida nominal y la capacidad de arranque de cada uno.

## Seguridad antes de conectar cargas

- **Monóxido de carbono:** usá el generador portátil solo al aire libre, lejos de puertas, ventanas y ventilaciones, con el escape orientado en sentido contrario a la vivienda. Nunca lo uses dentro de la casa, garaje, galpón o espacio semicerrado, aunque abras ventanas. Mantené alarmas de monóxido operativas en la vivienda. La CPSC recomienda separarlo al menos 20 pies (unos 6 m) de la casa; seguí además la distancia y ubicación que indique el manual del equipo y las condiciones del lugar.
- **Conexión a la vivienda:** no conectes un generador a un tomacorriente de la casa para energizar la instalación. Para alimentar circuitos fijos, un electricista habilitado debe instalar el sistema de transferencia y las protecciones adecuadas para impedir el retorno hacia la red.
- **Tierra y protecciones:** no agregues una jabalina ni unas el neutro a tierra por una regla genérica. El esquema depende del equipo, su manual, la transferencia y la instalación. Que un profesional verifique puesta a tierra, disyuntor, interruptores y protecciones conforme al generador y normativa aplicable.
- **Intemperie y extensiones:** mantené el equipo seco y ventilado; usá cables aptos para exterior, con sección y corriente adecuadas a la carga, sin fichas dañadas ni conexiones improvisadas. Seguí las instrucciones del fabricante sobre lluvia, combustible, ventilación y distancia.

## Modelos según el consumo del hogar

Estos modelos sirven como **escalones de potencia documentados**, no como un ranking ni como garantía para una lista de aparatos. Compará la carga nominal calculada con la potencia nominal del generador y el pico con la capacidad máxima y el manual de arranque. Si las cargas superan esos valores o hay varios motores, pasá al escalón siguiente y verificá cada pico.

| Escala de carga calculada | Referencia documentada | Salida publicada | Cómo usarla en la comparación | Oferta |
| :--- | :--- | :--- | :--- | :--- |
| Cargas esenciales acotadas, como la cuenta ilustrativa de 0,6 kVA en marcha y hasta 1,05 kVA de pico | Honda EU22i, inverter | 1,8 kVA nominal / 2,2 kVA máxima; 220 V monofásica | La cuenta del ejemplo queda por debajo de las cifras publicadas. Confirmá tus cargas reales y el arranque en el manual. | [Ver precio →](https://meli.la/2AwxqaH) |
| Cargas simultáneas mayores o escenario que se acerca al pico del EU22i | Honda EU30is, inverter | 2,8 kVA nominal / 3,0 kVA máxima; 220 V monofásica | Compará su salida nominal y máxima con tu suma; el mayor tamaño no confirma un arranque que el fabricante no documente. | [Ver precio →](https://meli.la/2X86187) |
| Varias cargas simultáneas, si su suma medida justifica este rango | Honda EG6500CXS, convencional con D-AVR | 5,0 kVA nominal / 5,5 kVA máxima; 220 V monofásica | Referencia de mayor escala. Dimensioná con 5,0 kVA nominales para marcha; revisá los picos con el manual y el instalador. | [Ver precio →](https://meli.la/1sxNfJ5) |
| Cargas que, tras convertir correctamente a unidades comparables, requieren más que el escalón anterior | Gamma GE3481AR / 6000V | 5,5 kW nominal / 6 kW máxima; 220 V monofásica | Gamma expresa estos datos en kW. Para compararlos con kVA, necesitás el factor de potencia de la carga; no equipares kW y kVA sin ese dato. | [Ver precio →](https://meli.la/15vKtBp) |

El escenario con aire de 1,7 kVA de marcha y 1,85–2,15 kVA de pico estimado queda cerca del máximo publicado del EU22i. Además falta el dato de arranque del aire acondicionado. Para esa combinación, no decidas por la cifra máxima aislada: confirmá el arranque con el fabricante y cotejá una opción con más capacidad nominal si buscás margen para nuevas cargas.

<!-- GENERADORES-EXTRAS -->

### Gamma 3000V / GE3480AR

La [ficha y manual Gamma](https://www.gammaherramientas.com.ar/producto/grupo-electrogeno-3000v-ge3480ar/) documentan 2,7 kW nominales y 3 kW máximos, salida de 220 V, nafta y tanque de 15 L. Confirmá los picos de las cargas y la batería de arranque, que no está incluida.

[Ver precio del Gamma 3000V](https://meli.la/31SZbvv)

<!-- /GENERADORES-EXTRAS -->

## Fuentes consultadas

- **Documentación primaria:** [manual Lüsqtoff LG2500, tabla estimada de cargas](https://lusqtoff.com.ar/2023/uploads/Productos/9.%20GRUPOS%20ELECTR%C3%93GENOS/LG2500/LG2500.pdf); [LG US-W096WSG3, ficha de aire acondicionado](https://www.lg.com/ar/aire-acondicionado/lg-US-W096WSG3-inverter); [Honda EU22i](https://pf.honda.com.ar/producto/EU22i); [Honda EU30is](https://pf.honda.com.ar/producto/EU30is); [Honda EG6500CXS](https://pf.honda.com.ar/producto/EG6500CXS); [Gamma GE3481AR / 6000V](https://www.gammaherramientas.com.ar/producto/grupo-electrogeno-6000v/); [CPSC, seguridad de generadores y monóxido](https://www.cpsc.gov/Safety-Education/Safety-Guides/Carbon-Monoxide-Home/Generators-and-Engine-Driven-Tools); [CPSC, conexión segura a circuitos domésticos](https://www.cpsc.gov/s3fs-public/pdfs/foia_PortableGenerators.pdf). Consulta: 28/09/2026.
- **Opiniones de compradores:** no se revisó una muestra verificable.

Después de elegir potencia, compará [precios de grupos electrógenos](/generadores/precios/). Para seguir por configuración, consultá [grupos electrógenos monofásicos](/generadores/monofasicos/), [inverter](/generadores/inverter/), [silenciosos](/generadores/silenciosos/), [a gas](/generadores/a-gas/) y [a nafta](/generadores/a-nafta/); para más tamaños y criterios, volvé a la [guía general para elegir un grupo electrógeno](/generadores/comparativa-general/).

Para explorar la categoría: [guías de generadores y grupos electrógenos](/generadores/).
