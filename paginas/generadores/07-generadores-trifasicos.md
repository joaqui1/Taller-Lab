---
title: "Generador trifásico: cómo dimensionarlo y elegir"
h1: "Cómo elegir un generador trifásico"
url: "/generadores/trifasicos/"
description: "Aprendé a calcular kVA y kW, dimensionar el arranque de un motor trifásico y distribuir cargas por fase antes de comparar generadores."
author: "Joaquín Vallasciani"
category: "Generadores y Grupos Electrógenos"
keywords: ["generador trifasico", "grupo electrogeno trifasico", "generador 380v", "diferencia kva y kw", "balanceo de fases generador"]
research_type: "documental"
physical_test: "no"
specifications_contrasted: "sí"
buyer_opinions: "no"
primary_sources: "sí"
information_asset: "Guía de dimensionamiento trifásico con fórmulas de potencia, ejemplo de motor, límites por fase y referencias de equipo según aplicación."
asset_status: "verificado"
reviewed: "28/09/2026"
published_on: "30/09/2026"
published: true
---

# Cómo elegir un generador trifásico

<!-- AUDITORIA_EDITORIAL_178 -->

Un generador trifásico se justifica cuando una máquina necesita tres fases según su placa —por ejemplo, un motor industrial 3~380 V, un compresor de taller trifásico o una soldadora con entrada trifásica— o cuando la instalación que se debe respaldar está diseñada para esa alimentación. El nombre del aparato no alcanza: existen compresores, bombas y soldadoras monofásicos y trifásicos; revisá tensión, símbolo de fases y corriente en la placa.

Para dimensionarlo, calculá la potencia de marcha y el pico de arranque del equipo más exigente, luego revisá la corriente admisible en cada fase. La potencia total en la tapa del generador no garantiza que alcance en una fase concreta ni que soporte un arranque de motor.


**Dato documentado:** las especificaciones se atribuyen a las fuentes enlazadas; los datos comerciales y las variantes se identifican por separado.

**Análisis TallerLab:** los criterios de selección interpretan la documentación según la carga prevista; esta guía no incluye prueba física de los equipos.

## Cuándo necesitás alimentación trifásica

Buscá una salida trifásica si la placa de la carga indica `3~`, tres fases o tensión entre fases de 380/400 V, y el manual del equipo pide esa alimentación. Es habitual en motores de máquinas de taller, compresores industriales, bombas de mayor tamaño, equipos de elevación y algunas soldadoras. Confirmá el modelo exacto y su diagrama: una máquina de la misma clase puede venir en versión monofásica.

> **Si todas tus cargas son monofásicas de 220 V, no elijas un trifásico solo porque muestra más kVA.** Necesitás que entregue esa tensión y que sus salidas monofásicas soporten la corriente y distribución de tus cargas, además de cumplir el límite de desbalance indicado por su fabricante.

## Diferencias entre kVA y kW

- **kVA** expresa potencia aparente: voltios por amperios, incluyendo el efecto del factor de potencia.
- **kW** expresa potencia activa, la que realiza trabajo. Para una carga trifásica equilibrada: **kW = kVA × PF**.
- Si la placa informa tensión entre fases y corriente de línea: **kVA = √3 × V línea × A línea ÷ 1.000**; **kW = √3 × V línea × A línea × PF ÷ 1.000**.
- Para una carga monofásica entre fase y neutro: **kVA = V × A ÷ 1.000**; si solo tenés watts, **kVA ≈ kW ÷ PF**.

**Ejemplo:** Honda publica para el ET12000 una potencia nominal trifásica de 10 kVA y un factor de potencia de 0,8. La potencia activa correspondiente es **10 kVA × 0,8 = 8 kW**. No se debe comparar directamente esos 10 kVA con los 17 kW que Gamma publica para GE3494AR: las unidades y el factor de potencia documentado son distintos.

## Cómo dimensionar un motor trifásico

Usá la corriente nominal y la corriente de arranque que figuran en la placa o documentación del motor. Como ejemplo reproducible, la tabla técnica de motores WEG W22 IE3 a 50 Hz informa para un motor de referencia de **0,75 kW, cuatro polos y 380 V**: corriente nominal **1,77 A**, factor de potencia **0,78** y relación de corriente de arranque `Ip/In = 7`.

1. **Marcha aparente:** √3 × 380 V × 1,77 A ÷ 1.000 = **1,17 kVA**.
2. **Marcha activa aproximada:** 1,17 kVA × 0,78 = **0,91 kW** eléctricos para entregar 0,75 kW mecánicos.
3. **Corriente de arranque de referencia:** 1,77 A × 7 = **12,39 A por línea**.
4. **Pico aparente de arranque:** √3 × 380 V × 12,39 A ÷ 1.000 = **8,15 kVA** para el motor solo.

El cálculo sirve para cotejar la carga con la potencia nominal y la capacidad transitoria del generador. No confirma por sí mismo que un modelo arranque el motor: influyen el tipo de arranque (directo, estrella-triángulo o variador), las otras cargas conectadas y la caída de tensión permitida. Pedí al fabricante del generador una confirmación de arranque para ese motor si la ficha no publica respuesta transitoria. No agregues una regla de “tres veces” si ya tenés `Ip/In` de la placa.

## Cómo distribuir las cargas por fase

En un sistema 380/220 V, los 380 V suelen medirse entre dos fases y los 220 V entre una fase y neutro. Una máquina trifásica utiliza las tres fases; una carga monofásica de 220 V normalmente queda entre una fase y neutro. El esquema exacto debe coincidir con la placa, las tomas y el diagrama del generador.

Para distribuir cargas monofásicas, anotá los amperios de cada circuito y repartilos de manera pareja entre L1, L2 y L3. Compará **cada fase** con la corriente/potencia nominal y máxima por fase que publica el fabricante. Una fase puede sobrecargarse aunque la suma total de las tres siga debajo de la cifra global.

**Ejemplo de reparto:** tres cargas de 220 V consumen 5 A, 5 A y 2 A. En sus fases respectivas representan 1,10 kVA, 1,10 kVA y 0,44 kVA: la suma es **2,64 kVA**. Dividir 2,64 por tres da un promedio de 0,88 kVA por fase, pero la carga real sigue repartida como 1,10 / 1,10 / 0,44 kVA. El promedio no muestra la corriente de cada conductor ni demuestra que el desbalance esté permitido.

**Por qué no alcanza con dividir por tres:** ese cálculo supone un reparto exactamente equilibrado y no muestra el límite individual que el generador establece. Honda ET12000 publica **10 kVA trifásicos nominales / 11 kVA máximos**, y para su salida monofásica indica **3 × 2,7 kVA nominales / 3 × 3,0 kVA máximos**. En este modelo, los topes por salida monofásica son los datos a revisar para las cargas de 220 V; no se puede tratar 10 kVA como si estuvieran disponibles en una sola fase. La ficha no expresa una tolerancia porcentual universal de desbalance, así que para repartir cargas desiguales hay que seguir el manual y confirmar la configuración con Honda.

Los límites de desbalance son **propios de cada equipo**. Como ejemplo de esa variación, el manual Generac MGG100M establece que la diferencia de carga entre fases no debe superar el 25% de la carga nominal. Ese 25% corresponde al MGG100M; no se traslada a Honda, Gamma, Lüsqtoff ni a otro Generac. Si el manual del modelo que evaluás no expresa un límite de desbalance, pedí la especificación por escrito y distribuí las cargas con un electricista.

## Modelos según el uso

Estos equipos muestran aplicaciones y escalas distintas; no son un ranking. Antes de elegir, hacé coincidir salida, tensión, fase, potencia nominal, corriente por fase y método de arranque con las cargas reales.

| Aplicación para evaluar | Modelo documentado | Datos de salida que sirven para cotejar | Qué confirmar antes de decidir | Oferta |
| :--- | :--- | :--- | :--- | :--- |
| Obra móvil con una máquina que requiere 380 V trifásicos | Lüsqtoff LG7500EXT | 380 V, 50 Hz, trifásico; 6.500 W máximos; tanque 25 L. El fabricante no publica potencia nominal en la página consultada. | Corriente máxima por fase, potencia nominal y capacidad de arranque del motor de la máquina. No dimensionar usando solo 6.500 W máximos. | [Ver precio →](https://meli.la/1k8qxpL) |
| Servicio o taller con demanda trifásica intermedia y algunas salidas 220 V | Honda ET12000 | 380/220 V, 10/11 kVA trifásicos nominal/máximo; 3 × 2,7/3,0 kVA nominal/máximo en salida monofásica. | En qué configuración se usará, capacidad de cada salida, arranque de motores y distribución de cargas 220 V. | [Ver precio →](https://meli.la/2WRqiZR) |
| Taller fijo o instalación de mayor potencia, con suministro a gas | Gamma GE3494AR ([generadores a gas](/generadores/a-gas/)) | 380 V, 3 fases; 17/18,7 kW nominal/máxima con GLP y 16/17,6 kW con GN; arranque automático. | Corriente y kVA por fase, factor de potencia, cargas de arranque, ATS requerido, gas, baterías e instalación. Gamma indica que requiere tablero ATS GE3495AR. | — |

Para otras configuraciones de mayor uso horario, compará también [generadores diésel](/generadores/diesel/) y sus datos de consumo y fase publicados.

## Instalación y conexión

Una conexión a tablero o instalación fija debe proyectarla y ejecutarla un electricista habilitado. Tiene que verificar el esquema de transferencia, protecciones, conductor neutro, puesta a tierra, sección de cables y distribución de cargas de acuerdo con el manual del generador y la normativa local. No conectes un generador a un tomacorriente doméstico para energizar la instalación.

## Fuentes consultadas

- **Documentación primaria:** [Honda ET12000](https://pf.honda.com.ar/producto/ET12000) y [ficha técnica Honda ET12000](https://pf.honda.com.ar/descargar/ficha_tecnica/ET12000.pdf); [Lüsqtoff LG7500EXT](https://www.lusqtoff.com.ar/ver-producto/LG7500EXT); [Gamma GE3494AR](https://www.gammaherramientas.com.ar/producto/grupo-estacionario-17kw/) y [manual Gamma GE3493AR/GE3494AR](https://gammaherramientas.com.ar/web/wp-content/uploads/2025/12/GE3493AR_GE3494AR_MANUAL_web.pdf); [tabla técnica WEG W22 IE3, corrientes y factores de potencia](https://static.weg.net/medias/downloadcenter/h40/hc6/WEG-maniobra-y-proteccion-de-motores-y-circuitos-electricos-50112294-es.pdf); [manual Generac MGG100M](https://legacy.genconnect.generac.com/Media/vwDoc.axd?d=08d4c3d6-258a-4f62-98d1-218e72bdec3d). Consulta: 28/09/2026.
- **Opiniones de compradores:** no se revisó una muestra verificable.

Para seguir comparando: [grupos monofásicos](/generadores/monofasicos/), [generadores diésel](/generadores/diesel/) y la [guía general de grupos electrógenos](/generadores/comparativa-general/).

Para explorar la categoría: [guías de generadores y grupos electrógenos](/generadores/).
