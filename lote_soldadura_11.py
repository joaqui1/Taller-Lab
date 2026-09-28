"""Decimoséptimo lote editorial: procesos, máquinas y estación de retrabajo."""
from pathlib import Path
import re

ROOT = Path(__file__).parent

PAGES = {
    "paginas/soldadoras/07-soldadora-mig-sin-gas.md": (
        "Compara equipos que admiten alambre tubular autoprotegido por modos de proceso, rango, diámetro de alambre y límites documentales; separa FCAW-S de MIG con alambre macizo y gas.",
        """| Modelo documentado | Procesos / alambre | Salida y ciclo publicados | Límite que conviene notar |
| :--- | :--- | :--- | :--- |
| Lüsqtoff SML130-7 | FCAW con alambre tubular autoprotegido | 25–120 A; 120 A/10% y 50 A/60% a 40 °C | Discontinuada; página acepta rollos de 0,5 y 1 kg |
| Lüsqtoff SML120-8D | FLUX, MMA y Lift TIG | FLUX 20–120 A; ciclo declarado 25% a 25 °C | La hoja consultada no aclara todos los parámetros del alambre |
| ESAB HandyArc MIG 160i | MIG/MAG y tubular con o sin gas | GMAW 30–160 A; 160 A/15%, 80 A/60%, 62 A/100% | ESAB declara bobinas hasta 5 kg y alambre hasta 0,9 mm |

**Dato verificado:** las fuentes oficiales separan alambre tubular autoprotegido de alambre macizo para MIG/MAG. La SML130-7 se describe para FCAW y aparece como discontinuada; ESAB declara que MIG 160i acepta alambres tubulares con y sin gas y también ofrece proceso MIG/MAG.

**Análisis TallerLab:** para trabajar sin cilindro, el alambre debe ser autoprotegido y la fuente debe permitir su polaridad, diámetro y alimentación. La palabra “MIG” en el nombre no confirma por sí sola que la máquina admita alambre macizo sin gas. Comprobá manual de la máquina y ficha del consumible como un par compatible. Los puntos de ciclo de las dos máquinas no son comparables sin igualar proceso y temperatura de ensayo.

**Desconocido:** no se identificó un carrete concreto ni se verificó su ficha, stock argentino o condición estructural del trabajo. No se puede deducir espesor soldable universal a partir del amperaje máximo.

## Fuentes consultadas

- **Documentación primaria:** [Lüsqtoff SML130-7](https://lusqtoff.com.ar/ver-producto/SML130-7); [manual oficial SML130-7](https://lusqtoff.com.ar/2023/uploads/Productos/13.%20SOLDADORAS%20INVERTER/SML130-7/MANUAL%20FOR%20SML130-7.pdf); [Lüsqtoff SML120-8D](https://www.lusqtoff.com.ar/ver-producto/SML120-8D); [ESAB HandyArc MIG 160i, Argentina](https://esab.com/ar/sam_es/products-solutions/product/welding-equipment/mig-welders-gmaw/handyarc-mig-160i/).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/soldadoras/", "/soldadoras/mig-lusqtoff/", "modelos MIG Flux Lüsqtoff y sus ciclos publicados",
    ),
    "paginas/soldadoras/17-soldadora-para-aluminio.md": (
        "Compara dos fuentes TIG AC/DC que fabricantes documentan para aluminio: ESAB ET 200i AC/DC monofásica y Lüsqtoff TIG350ACDC-9 trifásica, con ciclo, corriente y alimentación.",
        """| Modelo | Proceso AC/DC que identifica la ficha | Alimentación | Salida TIG/ciclo publicado | Masa |
| :--- | :--- | :--- | :--- | ---: |
| ESAB ET 200i AC/DC (0738827) | TIG AC y DC; ESAB especifica AC para aluminio y DC para otros metales | 220 V ±10%, monofásica | 200 A/20%; 116 A/60%; 90 A/100% | 22 kg |
| Lüsqtoff TIG350ACDC-9 | TIG AC/DC, trifásica | 380 V, 50 Hz | 315 A/40%; rango 5–315 A según la página | 31,5 kg |

**Dato verificado:** las dos fichas identifican TIG AC/DC. ESAB explica que en ET 200i la salida AC se usa para aluminio y sus aleaciones; Lüsqtoff presenta TIG350ACDC-9 como equipo trifásico AC/DC y publica sus puntos de corriente/ciclo.

**Análisis TallerLab:** antes de comparar precio o amperaje, comprobá si la red disponible corresponde a una fuente monofásica de 220 V o trifásica de 380 V y leé ciclo, no solo corriente máxima. La tabla documenta especificaciones de fabricante; no determina espesor, aporte, gas, preparación, habilidad requerida ni calidad de cordón para una pieza concreta.

**Desconocido:** no se cotejaron alambres/varillas, aleación y estado del aluminio, espesor ni procedimiento aplicable. La ficha de ESAB enumera accesorios compatibles, pero la entrega de cada vendedor debe confirmarse en la oferta; para TIG350ACDC-9, el fabricante advierte que el cable de alimentación no está incluido.

## Fuentes consultadas

- **Documentación primaria:** [ESAB ET 200i AC/DC, Argentina](https://esab.com/ar/sam_es/products-solutions/product/welding-equipment/tig-welders-gtaw/et-200i-ac-dc/); [Lüsqtoff TIG350ACDC-9](https://lusqtoff.com.ar/ver-producto/TIG350ACDC-9); [catálogo de soldadoras Lüsqtoff](https://lusqtoff.com.ar/ver-productos/13-soldadoras-inverter).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/soldadoras/", "/soldadoras/soldadora-tig-ac-dc/", "comparativa de TIG AC/DC y sus condiciones eléctricas",
    ),
    "paginas/soldadoras/03-soldadora-de-punto.md": (
        "Compara dos equipos Telwin de resistencia documentados para reparación de chapa por espesor máximo, alimentación, corriente de punto y ciclo; muestra que spotters de carrocería requieren alimentación especializada.",
        """| Equipo Telwin | Aplicación/espesor máximo de dos chapas | Alimentación declarada | Corriente máxima de punto | Ciclo y peso |
| :--- | :--- | :--- | ---: | :--- |
| Digital Car Spotter 5500, 823232 | Equipo de reparación; hasta 1,5 + 1,5 mm | 400 V, 50/60 Hz, dos fases | 3.000 A (pico 4.200 A) | 3%; 25 kg |
| Digital Spotter 9000, 823195 | Soldadura por punto; hasta 3 + 3 mm | 400 V, 50/60 Hz, dos fases | 7.000 A | 3%; 78 kg |

**Dato verificado:** Telwin presenta el 5500 como spotter electrónico de reparación de carrocerías con accesorios para tracción y punteo; el Digital Spotter 9000 admite puntos en chapas de hasta 3+3 mm. Las magnitudes de la tabla son los máximos que el fabricante publica para cada modelo.

**Análisis TallerLab:** “soldadora de punto” puede referirse a una máquina de resistencia para unir chapas o a un spotter que también tracciona abolladuras. Estos ejemplos son equipos de carrocería que declaran alimentación de 400 V y ciclo del 3%; no representan una soldadora doméstica enchufable. El espesor máximo no valida cualquier material, geometría, recubrimiento, acceso o unión.

**Desconocido:** no se verificó suministro eléctrico del taller, herramientas opcionales, consumibles de electrodo ni disponibilidad local. Antes de adquirir o usar un equipo de estas características, cotejar manual, red, protecciones y procedimiento de reparación específico.

## Fuentes consultadas

- **Documentación primaria:** [Telwin Digital Car Spotter 5500 400V](https://www.telwin.com/intl/en/products/repair-systems/823232-digital-car-spotter-5500-400v); [Telwin Digital Spotter 9000](https://www.telwin.com/intl/en/products/spot-welding-machines/823195-digital-spotter-9000); [manual Telwin de soldadora por resistencia](https://www.telwin.com/ExternalAssets/risc6000/954534_L.PDF).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/soldadoras/", "/soldadoras/para-aluminio/", "soldadura de aluminio: comparación de fuentes TIG AC/DC",
    ),
    "paginas/soldadoras/14-soldadora-dogo-180.md": (
        "Registra las especificaciones de la Dogo Dogostar 180 Moderna código DOG50045, incluido factor de servicio por electrodo, masa y límite de uso TIG por raspado con torcha adicional.",
        """| Dato del modelo Dogo Dogostar 180 Moderna | Declaración publicada por Dogo |
| :--- | :--- |
| Código | DOG50045 |
| Tecnología/proceso base | Inverter IGBT; electrodo revestido MMA |
| Rango y tensión | 20–180 A; 220 V; tensión en vacío 60 V |
| Masa / accesorios listados | 3 kg; pinza de masa y portaelectrodos |
| Factor de servicio por diámetro informado | 2,5 mm: 100%; 3,2 mm: 80%; 4,0 mm: 60%; 5,0 mm: 30% |
| TIG | La descripción indica TIG por raspado con torcha adicional |

**Dato verificado:** la tabla corresponde al código DOG50045 de la ficha del fabricante. Dogo separa el máximo de 180 A del factor de servicio por diámetro; publica también que la función TIG requiere comprar una torcha adicional. Su campo de tipos de electrodos lista 1,5–4 mm, mientras el factor de servicio incluye un punto para 5 mm; conservamos ambas declaraciones sin inferir compatibilidad universal.

**Análisis TallerLab:** para comparar una oferta, verificá que código, tensión, accesorios y factores de servicio coincidan con DOG50045. Los porcentajes se atribuyen tal como Dogo los presenta; no prueban resultado de soldadura ni funcionamiento continuo fuera de esos valores.

**Desconocido:** la página oficial no detalla corriente/tensión de salida en cada punto de servicio, longitud/sección de cables ni condiciones de garantía en el extracto citado. Confirmar esos campos en manual y etiqueta antes de comprar; los precios y disponibilidad cambian.

## Fuentes consultadas

- **Documentación primaria:** [Dogo Dogostar 180 Moderna, código DOG50045](https://dogoherramientas.com.ar/tienda/soldadura/inverter/soldadora-inverter-dogostar-180-moderna-mma); [catálogo oficial Dogo](https://www.dogoherramientas.com.ar/Pubs/Public/Catalogo/DOGO-LABOR%20FINAL%2001-09%20B.pdf); [catálogo online de inverter Dogo](https://www.dogoherramientas.com.ar/tienda/soldadura/inverter).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/soldadoras/", "/soldadoras/soldadora-inverter-160-amp/", "comparativa de inverter alrededor de 160 A",
    ),
    "paginas/soldadoras/20-soldadora-inverter-160-amp.md": (
        "Compara fuentes con “160” en el código o salida máxima por proceso: ESAB HandyArc 162i MMA, ESAB MIG 160i GMAW/MMA y Dogo Dogostar 160 MMA, según ciclos y fichas propias.",
        """| Modelo/código | Proceso y rango máximo de ficha | Puntos de ciclo publicados | Masa |
| :--- | :--- | :--- | ---: |
| ESAB HandyArc 162i, 0409616 | MMA, 20–160 A | 160 A/20%; 92 A/60%; 72 A/100% | 3,7 kg |
| ESAB HandyArc MIG 160i, 0410060 | GMAW 30–160 A; MMA 10–140 A | GMAW: 160 A/15%, 80 A/60%, 62 A/100%; MMA: 140 A/15%, 70 A/60%, 54 A/100% | 10,2 kg |
| Dogo Dogostar 160 Moderna | MMA, 20–160 A | Dogo lista 2,5 mm/100%, 3,2 mm/80% y 4 mm/60% | Ficha de producto: verificar el peso de la versión ofertada |

**Dato verificado:** los dos modelos ESAB tienen fichas oficiales argentinas; la página Dogo identifica su Dogostar 160 y muestra el factor de servicio por consumible. El número “160” no establece que los procesos, puntos de ciclo, alimentación eléctrica o accesorios sean iguales.

**Análisis TallerLab:** HandyArc 162i y MIG 160i difieren en masa publicada en 6,5 kg (cálculo entre 10,2 y 3,7 kg), pero también en proceso y configuración. Ese dato no predice facilidad de uso ni el trabajo que puede completarse. Para una elección documental, compará el proceso necesario, ciclo a la corriente relevante, voltaje, tipo de consumible y disponibilidad de alimentación.

**Desconocido:** no se unifican los porcentajes por diámetro de Dogo con el ciclo IEC de ESAB, porque están expresados de forma distinta. Tampoco se confirmaron accesorios, existencias, garantías actuales ni resultados reales de soldadura.

## Fuentes consultadas

- **Documentación primaria:** [ESAB HandyArc 162i, Argentina](https://esab.com/ar/sam_es/products-solutions/product/welding-equipment/stick-welders-smaw/handyarc-132i-dv-142i-162i/); [ESAB HandyArc MIG 160i, Argentina](https://esab.com/ar/sam_es/products-solutions/product/welding-equipment/mig-welders-gmaw/handyarc-mig-160i/); [Dogo Dogostar 160 Moderna](https://www.dogoherramientas.com.ar/tienda/soldadura/inverter/soldadora-inverter-dogostar-160-moderna-mma); [catálogo de inverter Dogo](https://www.dogoherramientas.com.ar/tienda/soldadura/inverter).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/soldadoras/", "/soldadoras/soldadora-inverter-200-amp/", "equipos inverter cercanos a 200 A con ciclos publicados",
    ),
    "paginas/soldadoras/11-soldadora-inverter-200-amp.md": (
        "Compara dos equipos MMA locales con salida máxima declarada de 200 A: Lüsqtoff SLCEL200-9 y Dogo Dogostar 200 DOG50046; distingue rango de corriente, ciclo y datos que faltan.",
        """| Modelo/código | Entrada / proceso | Rango máximo de ficha | Punto de ciclo publicado | Masa |
| :--- | :--- | :--- | :--- | ---: |
| Lüsqtoff SLCEL200-9 | 230 V monofásica; MMA, selector para celulósico; también lift TIG | 10–200 A | Para electrodo de 2,5 mm: 100 A al 100% | 6,9 kg |
| Dogo Dogostar 200 Moderna, DOG50046 | 220 V; MMA; función TIG por raspado con torcha adicional | 20–200 A | Dogo lista 3,2 mm/100%, 4,0 mm/60% y 5,0 mm/50% | 3,3 kg |

**Dato verificado:** ambas fuentes publican un máximo de 200 A, pero describen servicio de maneras diferentes. Lüsqtoff ofrece un punto continuo de 100 A para electrodo de 2,5 mm; Dogo presenta porcentajes asociados a diámetros. No convertimos esos campos en un ciclo común ni suponemos salida continua a 200 A.

**Análisis TallerLab:** los 200 A del nombre son un máximo de rango. Para comparar uso sostenido, buscá condiciones de medición equivalentes, tensión de salida y temperatura; la documentación consultada no ofrece el mismo formato en ambos productos. La diferencia de entrada nominal (230 V frente a 220 V) merece comprobarse en la placa/manual y la instalación.

**Desconocido:** no se validó que el selector “celulósico” de Lüsqtoff equivalga a cualquier procedimiento o electrodo, ni que la cifra de Dogo para 5 mm aplique a todo producto de ese diámetro. Confirmar garantía, accesorios reales y manual correspondiente al código exacto.

## Fuentes consultadas

- **Documentación primaria:** [Lüsqtoff SLCEL200-9](https://lusqtoff.com.ar/ver-producto/SLCEL200-9); [catálogo de soldadoras Lüsqtoff](https://lusqtoff.com.ar/categorias/black-series/soldadoras); [Dogo Dogostar 200 Moderna, DOG50046](https://www.dogoherramientas.com.ar/tienda/soldadura/inverter/soldadora-inverter-dogostar-200-moderna-mma); [categoría inverter Dogo](https://www.dogoherramientas.com.ar/tienda/soldadura/inverter).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/soldadoras/", "/soldadoras/", "guía central de soldadoras y procesos",
    ),
    "paginas/soldadoras/04-soldadora-mig-con-gas.md": (
        "Compara una MIG/MAG ESAB HandyArc MIG 160i y una Lüsqtoff MIGDUAL200-9 por rango, alimentación de alambre, entrada y accesorios relacionados con conexión de gas que sus fichas enumeran.",
        """| Modelo | Proceso/capacidad publicada | Alimentación de alambre | Dato de gas documentado |
| :--- | :--- | :--- | :--- |
| ESAB HandyArc MIG 160i (0410060) | MIG/MAG, rango GMAW 30–160 A; ciclos 160 A/15%, 80 A/60%, 62 A/100% | Bobina hasta 5 kg; diámetro hasta 0,9 mm | Ficha admite alambres tubulares con gas y sin gas; verificar consumible y regulación para la aplicación |
| Lüsqtoff MIGDUAL200-9 | MIG, MMA y pulso MIG; rango MIG informado hasta 200 A | Porta rollo de 5–15 kg; incluye torcha MIG y manguera | La lista de accesorios incluye manguera; confirmar regulador, gas y consumible requeridos en manual |

**Dato verificado:** ESAB documenta los rangos, ciclos y capacidad del devanador para MIG 160i. Lüsqtoff publica los datos de MIGDUAL200-9 y enumera una manguera entre los elementos del kit. La presencia de manguera no identifica por sí sola el gas, regulador o configuración incluidos en una oferta comercial.

**Análisis TallerLab:** para soldar con protección gaseosa, verificá compatibilidad de alambre, rodillo, punta, polaridad y sistema de gas en el manual del equipo y ficha del consumible. Los rangos de corriente de dos equipos no sustituyen esas comprobaciones y no son directamente comparables si difieren condiciones de ciclo.

**Desconocido:** no se informa aquí qué regulador o cilindro incluye cada vendedor ni la mezcla de gas adecuada para una aleación y unión concretas. No se probó arco ni se recomendaron parámetros de procedimiento.

## Fuentes consultadas

- **Documentación primaria:** [ESAB HandyArc MIG 160i, Argentina](https://esab.com/ar/sam_es/products-solutions/product/welding-equipment/mig-welders-gmaw/handyarc-mig-160i/); [Lüsqtoff MIGDUAL200-9](https://lusqtoff.com.ar/ver-producto/MIGDUAL200-9); [catálogo oficial Lüsqtoff 2024/25](https://www.lusqtoff.com.ar/2023/uploads/Catalogos/CAT%C3%81LOGO%20LQ%202024-2025%20-%20web%20%281%29.pdf).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/soldadoras/", "/soldadoras/mig-sin-gas/", "qué especifica el fabricante para MIG con alambre tubular",
    ),
    "paginas/soldadoras/19-soldadora-tig-ac-dc.md": (
        "Compara equipos TIG AC/DC por corriente, ciclo, tensión de alimentación y fases: ESAB ET 200i 220 V, Lüsqtoff TIG350ACDC-9 380 V y SMART TIG-AC/DC200 de catálogo.",
        """| Modelo | Red / fases | Corriente TIG y ciclo publicado | Datos de selección que no hay que omitir |
| :--- | :--- | :--- | :--- |
| ESAB ET 200i AC/DC (0738827) | 220 V ±10%, monofásica | 200 A/20%; 116 A/60%; 90 A/100% | 22 kg; TIG AC HF y DC en ficha argentina |
| Lüsqtoff TIG350ACDC-9 | 380 V, trifásica | 315 A/40%; rango de 5–315 A | 31,5 kg; fabricante dice que cable de alimentación no está incluido |
| Lüsqtoff SMART TIG-AC/DC200, catálogo | 220 V monofásica ±10% | 200 A/25% en TIG AC y DC, según catálogo | Ficha de producto actual localizada no permite validar todas las cifras del catálogo |

**Dato verificado:** ESAB publica salidas distintas al 20%, 60% y 100% para ET 200i. Lüsqtoff identifica TIG350ACDC-9 como trifásica y publica 315 A/40%. El SMART TIG-AC/DC200 aparece en catálogo Lüsqtoff con dos modos AC/DC y puntos de ciclo; los tratamos como dato de esa edición, no como ficha actual confirmada.

**Análisis TallerLab:** las necesidades eléctricas y ciclos separan claramente estas opciones: no se comparan solo por el número máximo. Comprobá fases disponibles, protección de red, ciclo a corriente de trabajo, accesorios y manual del modelo. Las descripciones de producto no bastan para elegir corriente, frecuencia/pulso o preparación de una junta.

**Desconocido:** no se confirmó vigencia comercial local del modelo SMART TIG-AC/DC200, parámetros completos por modo de la versión corriente ni contenidos exactos de cada publicación. No se ensayaron materiales.

## Fuentes consultadas

- **Documentación primaria:** [ESAB ET 200i AC/DC, Argentina](https://esab.com/ar/sam_es/products-solutions/product/welding-equipment/tig-welders-gtaw/et-200i-ac-dc/); [Lüsqtoff TIG350ACDC-9](https://lusqtoff.com.ar/ver-producto/TIG350ACDC-9); [catálogo Lüsqtoff 2024/25, SMART TIG-AC/DC200](https://www.lusqtoff.com.ar/2023/uploads/Catalogos/CAT%C3%81LOGO%20LQ%202024-2025%20-%20web%20%281%29.pdf); [catálogo Lüsqtoff de soldadoras](https://lusqtoff.com.ar/ver-productos/13-soldadoras-inverter).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/soldadoras/", "/soldadoras/tig/", "soldadura TIG: procesos y fichas de equipos",
    ),
    "paginas/soldadoras/06-soldadora-tig.md": (
        "Matriz de equipos TIG por proceso, corriente, ciclo y alimentación: distingue AC/DC ESAB ET 200i, TIG DC de Lüsqtoff ST-200 discontinuada y PROTIG180-8 con parámetros de ciclo publicados.",
        """| Modelo | Proceso que declara el fabricante | Rango / puntos de ciclo TIG | Estado o restricción visible |
| :--- | :--- | :--- | :--- |
| ESAB ET 200i AC/DC | TIG AC/DC y MMA | 5–200 A; 200 A/20%, 116 A/60%, 90 A/100% | 220 V monofásica; 22 kg |
| Lüsqtoff ST-200 | TIG HF y MMA DC | TIG 10–200 A; 200 A/60%, 100 A/100% | Página la marca discontinuada; 220 V monofásica |
| Lüsqtoff PROTIG180-8 | Inverter TIG y MMA; la página citada no especifica corriente AC | TIG 180 A al 30%; MMA 160 A al 30% | 220 V/50 Hz; 5,2 kg; ficha declara garantía de 2 años |

**Dato verificado:** la ficha ESAB identifica explícitamente TIG AC/DC. Lüsqtoff ST-200 se describe como “TIG dual / DC-MMA” y está discontinuada. La página PROTIG180-8 informa corrientes y ciclo, pero no se usa para afirmar compatibilidad TIG AC.

**Análisis TallerLab:** un nombre “TIG” no confirma salida AC/DC, tipo de encendido ni proceso de electrodo. Si se necesita TIG AC para aluminio, confirmar esa función en la ficha/manual del código exacto; para cualquier compra, cotejar rango, ciclo, frecuencia de red y accesorios incluidos.

**Desconocido:** no se determinaron aleación, espesor, corriente necesaria, gas, electrodo de tungsteno ni aporte para una pieza específica. La disponibilidad actual de ST-200 no está confirmada y no extrapolamos su ficha a otro modelo.

## Fuentes consultadas

- **Documentación primaria:** [ESAB ET 200i AC/DC](https://esab.com/ar/sam_es/products-solutions/product/welding-equipment/tig-welders-gtaw/et-200i-ac-dc/); [Lüsqtoff ST-200, modelo discontinuado](https://lusqtoff.com.ar/ver-producto/ST-200); [Lüsqtoff PROTIG180-8](https://lusqtoff.com.ar/ver-producto/PROTIG180-8); [catálogo oficial de soldadoras](https://lusqtoff.com.ar/ver-productos/13-soldadoras-inverter).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/soldadoras/", "/soldadoras/soldadora-tig-ac-dc/", "fichas de fuentes TIG AC/DC y alimentación",
    ),
    "paginas/soldadura-electronica/02-estacion-de-soldadura.md": (
        "Compara estaciones YiHUA 878D y 898D de aire caliente con cautín frente a Lüsqtoff ES3L45-8 de cautín regulado; especifica funciones, rango térmico y límites de ficha para distinguir retrabajo SMD de soldadura con estaño.",
        """| Modelo | Herramientas integradas | Temperaturas declaradas | Aire / potencia | Diferencia documentada |
| :--- | :--- | :--- | :--- | :--- |
| YiHUA 878D | Pistola de aire caliente y cautín | Aire 100–480 °C; cautín 200–480 °C | Aire máx. 120 L/min; estación 700 W máx. | Ficha agrupa versiones 878/878A/878AD/878D; verificar variante exacta |
| YiHUA 898D | Pistola de aire caliente y cautín | Aire 100–480 °C; cautín 200–480 °C | Aire máx. 120 L/min; estación 730 W | Dos pantallas LED y configuración de dos funciones |
| Lüsqtoff ES3L45-8 | Cautín regulable; no declara pistola de aire | Cautín 200–480 °C | Consumo/capacidad de entrada no queda claro en ficha comercial consultada | Estación compacta para trabajo con cautín, no especificada como retrabajo de aire |

**Dato verificado:** YiHUA publica estaciones 878D y 898D con pistola de aire y cautín; Lüsqtoff presenta ES3L45-8 como estación con regulación de temperatura de cautín. Se indican rangos y potencia según la fuente del fabricante, sin convertirlos en mediciones independientes.

**Análisis TallerLab:** si la tarea requiere retirar componentes SMD con aire, el tipo de herramienta incluida es una diferencia funcional que se puede verificar antes de comprar. Para soldadura puntual con cautín, comparar puntas, repuestos y control térmico del modelo exacto. Una lectura de temperatura de ficha no describe estabilidad real en la punta bajo carga.

**Desconocido:** la página YiHUA agrupa variantes; no confirma qué versión llega en cada oferta argentina, enchufe local, garantía ni disponibilidad de boquillas/puntas. La ficha ES3L45-8 publica datos de entrada ambiguos; no se convierten a watts sin manual legible. No se verificó precisión térmica con instrumentos.

## Fuentes consultadas

- **Documentación primaria:** [YiHUA 878/878A/878AD/878D](https://www.yihua-soldering.com/product-1-2-1-hot-air-rework-station-en/147657/); [YiHUA 898D/898D+](https://yihua-soldering.com/product-1-2-3-hot-air-rework-station-en/147659/); [Lüsqtoff ES3L45-8](https://lusqtoff.com.ar/ver-producto/ES3L45-8); [catálogo de soldadoras Lüsqtoff](https://lusqtoff.com.ar/ver-productos/13-soldadoras-inverter).
- **Opiniones de compradores:** no se revisó una muestra verificable.""",
        "/soldadura-electronica/", "/soldadura-electronica/gadnic-878d/", "estación de retrabajo YiHUA 878D: modelo y rangos declarados",
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
        f"**Dato verificado:** las especificaciones se atribuyen al fabricante y al modelo/código indicado. Los cálculos se identifican como **Análisis TallerLab**; lo no confirmado queda como **Desconocido**. Esta guía es documental, sin prueba física ni muestra de opiniones.\n\n"
        f"## Cómo investigamos esta guía\n\n"
        f"- Tipo de análisis: documental\n- Prueba física de TallerLab: no\n- Especificaciones contrastadas: sí\n- Opiniones de compradores: no\n- Fuentes primarias: sí\n- Última revisión: 27/09/2026\n\n"
        f"{body}\n\n"
        f"Para seguir comparando: [{sibling_title}]({sibling}).\n\n"
        f"Para conocer el criterio editorial: [Ver metodología de TallerLab](/como-trabajamos/).\n\n"
        f"Para explorar la categoría: [guías relacionadas]({hub}).\n"
    )
    path.write_text(f"---\n{front}\n---\n\n{newbody}", encoding="utf-8")
    print(relpath)
