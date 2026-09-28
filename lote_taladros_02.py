"""Quinto lote: revisión documental de diez páginas de taladros y accesorios."""
from pathlib import Path
import re

ROOT = Path(__file__).parent

PAGES = {
"02-rotomartillo.md": ("Matriz documental: energía, encastre y límites de tres rotomartillos", """| Modelo documentado | Alimentación | Energía declarada | Capacidad máxima en hormigón | Peso publicado | Encastre |
| :--- | :--- | ---: | ---: | ---: | :--- |
| Bosch GBH 220 | Cable, 720 W | 2,0 J | 22 mm | 2,3 kg | SDS plus |
| Bosch GBH 2-26 DRE | Cable, 800 W | 2,7 J | 26 mm | 2,9 kg | SDS plus |
| Einhell TE-RH 28 5F | Cable, 950 W | 3,0 J | 28 mm | 3,81 kg | SDS plus |

**Dato verificado:** las cifras corresponden a las fichas enlazadas y a esos modelos exactos. La ficha de Einhell indica además cinco modos de funcionamiento. Las capacidades máximas son límites publicados por cada fabricante, no una recomendación para mantener ese diámetro durante jornadas continuas.

**Análisis TallerLab:** en esta selección, pasar del GBH 220 al GBH 2-26 DRE suma 0,7 J y 4 mm de capacidad máxima declarada; el TE-RH 28 5F declara 0,3 J y 2 mm más que el GBH 2-26 DRE, y pesa 0,91 kg más. Son diferencias aritméticas entre fichas, no resultados de una prueba común. No se debe ordenar marcas por joules sin confirmar que las magnitudes se midieron bajo el mismo protocolo.

**Declaración del fabricante:** SDS plus identifica el sistema de inserción compatible con accesorios de ese encastre. No se debe confundir con SDS max; una broca debe corresponder al portaherramientas o a un adaptador aprobado para ese modelo.

**Desconocido:** no se verificaron kits, garantía ni disponibilidad local de cada variante. La potencia eléctrica en W no permite deducir por sí sola la energía de impacto ni el avance real en una obra.

## Criterio de elección documental

| Necesidad que define la compra | Dato que conviene contrastar | Límite de esta guía |
| :--- | :--- | :--- |
| Agujeros de diámetro moderado | Capacidad en hormigón y encastre | El máximo publicado no establece ritmo de trabajo |
| Más funciones de cincelado | Modos explícitos del modelo | No todos los modelos incluyen los mismos modos |
| Menor masa declarada | Peso y condición de medición | Puede variar si incluye cable, tope o batería |

Esta comparación sirve para acotar modelos por ficha. No determina cuál perfora más rápido ni cuál conviene para una tarea sin conocer material, broca, cantidad de agujeros y ciclo de uso.

## Fuentes consultadas

- **Documentación primaria:** [Bosch GBH 220 Argentina](https://www.bosch-professional.com/ar/es/products/gbh-220-06112A60H0); [Bosch GBH 2-26 DRE](https://www.bosch-professional.com/bo/es/products/gbh-2-26-dre-06112537E0); [Einhell TE-RH 28 5F](https://www.einhell.de/en/p/4257970/).
- **Seguridad:** consultar el manual del código exacto y usar accesorios compatibles.
- **Opiniones de compradores:** no se revisó una muestra verificable.""", "Comparación documental de tres rotomartillos SDS plus: energía, capacidad máxima, peso y función."),
"03-taladro-percutor.md": ("Decisión de herramienta: percusión mecánica o mecanismo SDS", """| Criterio documental | Taladro percutor | Rotomartillo SDS plus |
| :--- | :--- | :--- |
| Mecanismo | Percusión mecánica asociada a la rotación | Percusión electro-neumática con portaherramientas SDS |
| Ejemplo oficial consultado | Bosch GSB 18V-50: hasta 27.000 impactos/min | Bosch GBH 220: 2,0 J declarados |
| Inserción de accesorio | Mandril de 13 mm en el GSB 18V-50 | SDS plus en el GBH 220 |
| Límite verificable | La ficha consultada no expresa energía por golpe | 22 mm máximo en hormigón para GBH 220 |

**Dato verificado:** estas cifras describen dos ejemplos concretos, no todos los taladros percutores ni todos los rotomartillos. El GSB 18V-50 es un modelo a batería de 18 V; la cifra de 27.000 impactos/min aparece en su ficha de fabricante. Bosch publica 2,0 J y 22 mm como datos del GBH 220.

**Análisis TallerLab:** las unidades publicadas no permiten comparar directamente “impactos por minuto” con “joules”. La primera expresa frecuencia; la segunda, energía por impacto según la ficha. Para elegir por documentación, primero verificá el material y diámetro requeridos, luego el tipo de mandril y el límite que publica el fabricante. No inferimos velocidad de perforación ni superioridad a partir de estas magnitudes diferentes.

**Declaración del fabricante:** el GSB 18V-50 incorpora selección de atornillado, perforación y percusión. En ambos tipos de máquina, el accesorio y el modo deben seguir el manual del modelo y del material.

**Desconocido:** no hay una prueba comparativa bajo el mismo hormigón, diámetro, broca y operador. Las fichas citadas no determinan qué herramienta resulta más conveniente para un trabajo específico.

## Matriz rápida de decisión

| Si el requisito es… | Verificá… | No deduzcas… |
| :--- | :--- | :--- |
| Usar brocas cilíndricas de varios diámetros | Apertura y tipo de mandril | Que cualquier broca admita percusión |
| Usar accesorios SDS plus | Que el equipo tenga portaherramientas SDS plus | Que SDS plus sea intercambiable con SDS max |
| Taladrar mampostería | Capacidad indicada para material y diámetro | Que los impactos/min sean energía por golpe |

## Fuentes consultadas

- **Documentación primaria:** [Bosch GSB 18V-50 Argentina](https://www.bosch-professional.com/ar/es/products/gsb-18v-50-06019H51E2); [Bosch GBH 220 Argentina](https://www.bosch-professional.com/ar/es/products/gbh-220-06112A60H0).
- **Seguridad:** respetar modo, broca y material indicados en el manual.
- **Opiniones de compradores:** no se revisó una muestra verificable.""", "Matriz documental que distingue frecuencia de impactos, energía declarada, mandril y encastre SDS."),
"06-rotomartillo-bosch.md": ("GBH 220, GBH 2-26 DRE y GBH 18V-26 D: comparar datos de modelos identificados", """| Modelo | Alimentación | Energía declarada | Capacidad máxima en hormigón | Peso publicado | Encastre |
| :--- | :--- | ---: | ---: | ---: | :--- |
| GBH 220 | Cable, 720 W | 2,0 J | 22 mm | 2,3 kg | SDS plus |
| GBH 2-26 DRE | Cable, 800 W | 2,7 J | 26 mm | 2,9 kg | SDS plus |
| GBH 18V-26 D | Batería 18 V | 2,5 J | 26 mm | 2,6 kg sin batería | SDS plus |

**Dato verificado:** la tabla combina fichas Bosch de regiones distintas; el GBH 2-26 DRE consultado no es una confirmación de configuración argentina. En el GBH 18V-26 D, el peso explícitamente excluye la batería, por lo que no es directamente equivalente a los pesos de herramientas con cable.

**Análisis TallerLab:** frente al GBH 220, el GBH 2-26 DRE declara 0,7 J y 4 mm más de capacidad máxima; también publica 0,6 kg más de peso. El modelo 18V-26 D declara 0,5 J más y 4 mm más que el GBH 220, pero su peso sin batería impide una comparación de masa del conjunto listo para trabajar. Son diferencias de catálogo, no pruebas de perforación.

**Declaración del fabricante:** Bosch identifica SDS plus en los tres modelos. El GBH 18V-26 D publica 0–4350 impactos/min y 0–980 rpm; la versión “D” y la versión “F” tienen configuraciones distintas, y no trasladamos a este modelo los datos del mandril intercambiable de la versión F.

**Desconocido:** no confirmamos que todos los códigos estén disponibles actualmente en Argentina, qué batería/cargador incluye cada publicación ni garantía local. Confirmá el número de pedido completo y el contenido del kit.

## Lectura de la tabla

| Prioridad de compra | Campo relevante | Qué queda por verificar |
| :--- | :--- | :--- |
| Menor peso con cable | Peso y alcance de cable | No hay comparación de peso con el cable incluido expresamente |
| Trabajo sin cable | Peso sin batería y plataforma | Peso de batería y cargador compatibles |
| Diámetro máximo publicado | Capacidad en hormigón | El máximo no representa ritmo de uso continuo |

## Fuentes consultadas

- **Documentación primaria:** [Bosch GBH 220 Argentina](https://www.bosch-professional.com/ar/es/products/gbh-220-06112A60H0); [Bosch GBH 2-26 DRE](https://www.bosch-professional.com/bo/es/products/gbh-2-26-dre-06112537E0); [Bosch GBH 18V-26 D Argentina](https://www.bosch-professional.com/ar/es/products/gbh-18v-26-d-0611916001).
- **Seguridad:** consultar manual y límites del accesorio del modelo exacto.
- **Opiniones de compradores:** no se revisó una muestra verificable.""", "Comparación documental de rotomartillos Bosch GBH 220, GBH 2-26 DRE y GBH 18V-26 D."),
"11-rotomartillo-dewalt.md": ("DCH273: especificaciones documentadas y alcance de SHOCKS", """| Campo | Dato publicado para DCH273B |
| :--- | :--- |
| Plataforma de etiqueta | 20 V MAX; DeWalt indica 18 V nominales |
| Motor | Brushless, según fabricante |
| Energía de impacto | 2,1 J |
| Portaherramientas | SDS plus |
| Modos | Taladrado, taladrado con percusión y cincelado |
| Alimentación de la variante consultada | Herramienta sola; batería y cargador no incluidos |

**Dato verificado:** las especificaciones corresponden al código DCH273B de la página estadounidense de DeWalt. No describen automáticamente el DCH273 vendido en otros mercados ni los modelos con cable D25133/D25263.

**Declaración del fabricante:** DeWalt describe SHOCKS como un sistema de control activo de vibración que reduce la vibración percibida en la empuñadura frente a la herramienta sin esa función. Esta declaración no equivale a afirmar protección de articulaciones, ausencia de riesgo ni una medición realizada por TallerLab.

**Análisis TallerLab:** la ficha permite filtrar por SDS plus, tres modos y plataforma, pero no basta para concluir qué tan rápido perfora frente a otro modelo. La etiqueta 20 V MAX puede inducir a confusión: DeWalt explica que el valor nominal es 18 V. El sufijo B identifica la configuración de herramienta sola de la página consultada.

**Desconocido:** no verificamos autonomía, vibración medida en una prueba común, kit argentino, garantía local ni contenido de otras terminaciones. Para comparar con un rotomartillo con cable, considerá también batería y cargador si no los tenés.

## Matriz de compra por dato comprobable

| Pregunta | Dato de esta ficha | Comprobación pendiente en el aviso |
| :--- | :--- | :--- |
| ¿Qué accesorio recibe? | SDS plus | Confirmar encastre en la unidad ofrecida |
| ¿Incluye energía? | 2,1 J declarados | No confundir energía con impactos/min |
| ¿Qué incluye el código B? | Herramienta sola según ficha | Baterías, cargador, valija y región |
| ¿Qué significa SHOCKS? | Declaración de reducción de vibración en empuñadura | No asumir resultado clínico o prueba de TallerLab |

## Fuentes consultadas

- **Documentación primaria:** [DeWalt DCH273B, ficha oficial](https://www.dewalt.com/en-us/product/dch273b/20v-max-xr-sds-plus-brushless-1-l-shape-rotary-hammer-tool-only); [manual DeWalt D25133, referencia separada para la línea con cable](https://www.dewalt.com/GLOBALBOM/QU/D25133K/1/Instruction_Manual/EN/N401624_D25133.pdf).
- **Seguridad:** seguir el manual de la variante y las indicaciones de EPP.
- **Opiniones de compradores:** no se revisó una muestra verificable.""", "Ficha documental del DeWalt DCH273B con atribución precisa de SHOCKS y límites de mercado y kit."),
"10-rotomartillo-einhell.md": ("TE-RH 28 5F: ficha del código 4257970 y comparación de catálogo", """| Dato publicado | Einhell TE-RH 28 5F (4257970) |
| :--- | :--- |
| Alimentación | Cable, 950 W |
| Energía de impacto | 3 J |
| Capacidad máxima en hormigón | 28 mm |
| Portaherramientas | SDS plus |
| Modos | 5 funciones según ficha del fabricante |
| Peso publicado | 3,81 kg |

**Dato verificado:** la fuente consultada es la ficha Einhell del artículo 4257970. La ficha nombra las cinco funciones, entre ellas taladrado, taladrado con percusión y cincelado; no suponemos que todo modelo TE o TC incluya el mismo selector.

**Análisis TallerLab:** frente al Bosch GBH 2-26 DRE (800 W, 2,7 J, máximo 26 mm y peso 2,9 kg), el Einhell declara 150 W y 0,3 J más, 2 mm más de capacidad máxima y 0,91 kg más de peso. Es una comparación aritmética de datos publicados. No demuestra mayor velocidad, vida útil ni conveniencia; las cifras de energía no se sometieron aquí a ensayo común.

**Declaración del fabricante:** SDS plus y las capacidades publicadas delimitan los accesorios y materiales indicados por Einhell. La ficha alemana consultada no prueba disponibilidad, tensión de red, contenido de caja o garantía de un kit argentino.

**Desconocido:** no se confirmó contenido de accesorios en ofertas locales, duración de garantía vigente ni resultados bajo uso prolongado. Para comprar, verificá placa de tensión, código de artículo y manual que acompañe la unidad.

## Comparación de referencia

| Modelo | W | J declarados | Máximo hormigón | Peso publicado |
| :--- | ---: | ---: | ---: | ---: |
| Einhell TE-RH 28 5F | 950 | 3,0 | 28 mm | 3,81 kg |
| Bosch GBH 2-26 DRE | 800 | 2,7 | 26 mm | 2,9 kg |

La selección ayuda a ver el compromiso entre valores de ficha y peso. El uso real también depende de broca, material, diámetro, presión y pausas; esta página no mide esas variables.

## Fuentes consultadas

- **Documentación primaria:** [Einhell TE-RH 28 5F, artículo 4257970](https://www.einhell.de/en/p/4257970/); [Bosch GBH 2-26 DRE](https://www.bosch-professional.com/bo/es/products/gbh-2-26-dre-06112537E0).
- **Seguridad:** verificar tensión y seguir el manual de la unidad.
- **Opiniones de compradores:** no se revisó una muestra verificable.""", "Ficha contrastada del Einhell TE-RH 28 5F frente a Bosch GBH 2-26 DRE en potencia, joules, capacidad y peso."),
"17-brocas-para-ceramica.md": ("Compatibilidad Bosch CYL-9 y EXPERT HEX-9: cerámica blanda y azulejo duro", """| Broca identificada | Material que indica Bosch | Modo documentado | Rango de diámetro consultado |
| :--- | :--- | :--- | :--- |
| CYL-9 Soft Ceramic | Cerámica blanda | Rotación, a baja velocidad | 3–16 mm |
| EXPERT HEX-9 HardCeramic | Cerámica dura, incluidos azulejos duros | Rotación; Bosch indica menos de 500 rpm | 3–12 mm en la gama consultada |

**Dato verificado:** Bosch separa sus brocas por aplicación: CYL-9 Soft Ceramic se destina a cerámica blanda, mientras EXPERT HEX-9 HardCeramic se describe para cerámica dura. Las medidas disponibles varían por mercado y número de pieza; confirmar el diámetro exacto del producto publicado.

**Declaración del fabricante:** para HEX-9, Bosch recomienda perforación rotativa sin percusión y velocidad inferior a 500 rpm. La guía de Bosch indica aplicar presión y mantener control de la herramienta; no convertimos recomendaciones de un modelo en regla universal para todas las brocas. Las pruebas de número de agujeros que publica Bosch son ensayos del fabricante, no experiencia de compradores ni prueba de TallerLab.

**Análisis TallerLab:** el valor práctico de separar las dos guías es identificar el tipo de cerámica antes de elegir. El diámetro por sí solo no define compatibilidad: una CYL-9 puede tener la medida buscada y aun así no estar destinada al mismo tipo de revestimiento que HEX-9 HardCeramic. Para porcelanato, consultá además [la guía específica de mechas para porcelanato](/taladros/mecha-porcelanato/), comprobando siempre el modelo exacto.

**Desconocido:** esta comparación no cubre todas las marcas, brocas tipo flecha o coronas diamantadas. No verificamos una regla de refrigeración común ni garantizamos resultados en vidrio, piedra u otro material. Usá la ficha del accesorio comprado.

## Selección por sustrato y límite

| Sustrato declarado | Referencia que aparece en esta revisión | Decisión que falta antes de perforar |
| :--- | :--- | :--- |
| Cerámica blanda | Bosch CYL-9 Soft Ceramic | Código y diámetro exactos |
| Cerámica dura / azulejo duro | Bosch EXPERT HEX-9 HardCeramic | Respetar velocidad y modo indicados |
| Porcelanato u otro revestimiento | Guía de porcelanato y ficha de la broca | Confirmar compatibilidad explícita del modelo |

## Fuentes consultadas

- **Documentación primaria:** [Bosch CYL-9 Soft Ceramic](https://www.bosch-professional.com/gb/en/cyl-9-soft-ceramic-drill-bit-7724656-ocs-ac/); [Bosch EXPERT HEX-9 HardCeramic](https://www.bosch-professional.com/es/es/broca-expert-hex-9-hard-ceramic-2867225-ocs-ac/); [guía Bosch para perforar azulejos](https://www.bosch-professional.com/gb/en/innovation/tile-drilling/).
- **Seguridad:** no activar percusión salvo que la ficha del accesorio lo autorice expresamente.
- **Opiniones de compradores:** no se revisó una muestra verificable.""", "Matriz de compatibilidad entre dos familias Bosch de brocas para cerámica blanda y dura."),
"14-mecha-para-porcelanato.md": ("Bosch HEX-9 HardCeramic: diámetro, espesor y modo documentados", """| Característica publicada | Bosch EXPERT HEX-9 HardCeramic |
| :--- | :--- |
| Sustrato indicado | Azulejo/cerámica dura; Bosch incluye porcelanato en su descripción de aplicación |
| Diámetros en gama consultada | 3–12 mm; confirmar disponibilidad de cada medida |
| Modo de perforación indicado | Rotación, sin percusión |
| Velocidad indicada por Bosch | Menos de 500 rpm |
| Espesor descrito para esta aplicación | Hasta 10 mm, según página del fabricante |

**Dato verificado:** estos límites corresponden a la familia Bosch EXPERT HEX-9 HardCeramic, no a todas las brocas para porcelanato. El espesor de hasta 10 mm y el rango de diámetros dependen de la variante y página de mercado consultada. Confirmá la referencia y el diámetro exactos antes de comprar.

**Declaración del fabricante:** Bosch presenta HEX-9 HardCeramic como una broca de carburo para azulejo duro y recomienda velocidad baja, rotación sin percusión y presión controlada. El fabricante publica ensayos propios de perforación; esos resultados son declaraciones de Bosch y no pruebas realizadas por TallerLab.

**Análisis TallerLab:** frente a una búsqueda genérica por “mecha para porcelanato”, esta ficha aporta una ruta concreta: identificar un accesorio cuya documentación mencione el sustrato, después revisar diámetro, espesor permitido, modo y velocidad. Si la broca elegida no especifica porcelanato o azulejo duro, la compatibilidad queda **desconocida**; no se completa por analogía con otra familia Bosch. Para cerámica blanda también existe la familia CYL-9, con alcance diferente ([comparación de brocas para cerámica](/taladros/brocas-ceramica/)).

**Desconocido:** no se generalizan aquí diámetros grandes, coronas diamantadas, refrigeración, adaptadores M14 ni compatibilidad con amoladora. Estas condiciones dependen de la herramienta y del accesorio exacto.

## Comprobación antes del agujero

| Revisar en el envase/ficha | Por qué importa |
| :--- | :--- |
| Nombre completo HEX-9 HardCeramic y diámetro | Evita trasladar datos de otra broca |
| Material admitido y espesor | La etiqueta “diamantada” o “para cerámica” no basta para identificar el rango |
| Modo y velocidad | La fuente de esta broca indica rotación y menos de 500 rpm |
| Tipo de encastre | Debe sujetarse en el mandril compatible de la herramienta |

## Fuentes consultadas

- **Documentación primaria:** [Bosch EXPERT HEX-9 HardCeramic, ficha en español](https://www.bosch-professional.com/es/es/broca-expert-hex-9-hard-ceramic-2867225-ocs-ac/); [guía Bosch de perforación de azulejos](https://www.bosch-professional.com/gb/en/innovation/tile-drilling/).
- **Seguridad:** seguir límites del accesorio y del manual del taladro.
- **Opiniones de compradores:** no se revisó una muestra verificable.""", "Ficha de aplicación para una broca concreta para porcelanato, con diámetro, espesor y modo de trabajo documentados."),
"22-mecha-forstner-35-mm.md": ("Bosch Forstner Expert Wood 35 mm: medidas de vástago y profundidad", """| Dato de producto | Bosch Expert Forstner Wood 35 mm, ref. 2 608 901 837 |
| :--- | :--- |
| Diámetro de corte | 35 mm |
| Diámetro de vástago | 10 mm |
| Largo total | 88 mm |
| Largo de trabajo | 56 mm |
| Material indicado | Madera |

**Dato verificado:** Bosch publica estas dimensiones para la referencia indicada. La ficha de otra Forstner Bosch de 35 mm (2 608 596 977) informa 90 mm de largo total; no mezclar ambas referencias como si fueran idénticas.

**Análisis TallerLab:** 35 mm describe el diámetro de la cavidad, no la profundidad máxima de perforación. En la Expert Wood consultada, el largo de trabajo publicado es 56 mm. El vástago de 10 mm también debe caber en el mandril. Para una bisagra cazoleta, plantilla, tope y guía ayudan a repetir posición y profundidad, pero esta ficha no certifica dimensiones universales de bisagras ni una configuración de plantilla concreta.

**Declaración del fabricante:** Bosch describe la línea Expert Wood como diseñada para perforaciones en madera y anuncia “3x vida útil” respecto de una broca estándar en sus condiciones de prueba. Es una afirmación comparativa del fabricante; no es una medición independiente de TallerLab ni permite prometer una vida útil concreta.

**Desconocido:** no verificamos compatibilidad con todos los tableros, bisagras, plantillas o taladros de banco. Tampoco hay una medición propia de astillado, perpendicularidad o número de perforaciones. Revisá la ficha del código que se ofrece, no solo el título “Forstner 35 mm”.

## Decisión de compra

| Si necesitás… | Verificá… | Resultado de esta revisión |
| :--- | :--- | :--- |
| Cavidad nominal de bisagra | Diámetro de corte | 35 mm en la referencia citada |
| Controlar cuánto entra | Largo de trabajo y tope | 56 mm publicados; el tope es un accesorio aparte si no viene en kit |
| Montar en mandril | Diámetro de vástago | 10 mm publicado |
| Repetir la posición en varias puertas | Plantilla y topes compatibles | No se evaluó una plantilla específica |

## Fuentes consultadas

- **Documentación primaria:** [Bosch Expert Forstner Wood 35 mm, ref. 2608901837](https://www.bosch-professional.com/es/es/broca-forstner-expert-wood-7427439-ocs-ac/); [Bosch Forstner estándar 35 mm, ref. 2608596977](https://www.bosch-professional.com/ec/es/brocas-para-madera-forstner-2907460-ocs-ac/).
- **Seguridad:** sujetar la pieza y usar la broca conforme al manual del taladro.
- **Opiniones de compradores:** no se revisó una muestra verificable.""", "Ficha dimensional de una Forstner de 35 mm que distingue diámetro, largo útil y vástago."),
"21-mechas-escalonadas.md": ("Bosch HSS 4–20 mm: pasos y compatibilidad de una broca escalonada", """| Dato publicado | Bosch HSS Step Drill Bit |
| :--- | :--- |
| Rango de diámetros | 4–20 mm |
| Incremento entre escalones | 4 mm |
| Largo total | 70,5 mm |
| Vástago | Hexagonal de 1/4 in |
| Materiales listados | Metales, aluminio y plástico, según ficha |

**Dato verificado:** los datos corresponden a la broca escalonada Bosch Professional HSS consultada. En el rango 4–20 mm con pasos de 4 mm, las medidas sucesivas son 4, 8, 12, 16 y 20 mm. El valor se deriva del paso y los extremos publicados.

**Análisis TallerLab:** la utilidad de una escalonada es cubrir varios diámetros en una misma broca dentro de su rango; no ofrece todas las medidas intermedias. Para un agujero nominal de 10 mm, esta referencia no tiene un escalón de 10 mm según el intervalo indicado. El vástago hexagonal de 1/4 in debe sujetarse en un portabrocas compatible. El rango no informa por sí solo el espesor máximo de chapa.

**Declaración del fabricante:** Bosch lista uso con taladros y atornilladores de rotación/impacto según la ficha de la familia; la presencia de una herramienta percutora no autoriza a activar percusión para perforar chapa. El tratamiento superficial o material exacto debe leerse en el código del accesorio vendido.

**Desconocido:** no se verificó una ficha primaria equivalente para variantes de 4–32 mm ni para juegos de tres piezas mencionados en borradores comerciales. No inferimos que tengan el mismo paso, acero, recubrimiento o espesor admisible. Consultá esos valores en la referencia exacta.

## Revisión antes de comprar

| Necesidad | Lo que permite confirmar la fuente | Lo que sigue pendiente |
| :--- | :--- | :--- |
| Abrir distintos diámetros | Escalones de 4, 8, 12, 16 y 20 mm | La medida de cada referencia concreta |
| Montaje rápido | Hexágono de 1/4 in | Compatibilidad y retención del portaherramientas |
| Perforar chapa | Metales listados por Bosch | Espesor, lubricación y velocidad para la pieza concreta |
| Alcanzar 32 mm | Nada en esta ficha | Elegir otro código con ese rango declarado |

## Fuentes consultadas

- **Documentación primaria:** [Bosch Professional HSS Step Drill Bit 4–20 mm](https://www.bosch-professional.com/gb/en/hss-step-drill-bits-with-hex-shank-2868008-ocs-ac/).
- **Seguridad:** seguir las instrucciones de velocidad, fijación de la pieza y protección del manual.
- **Opiniones de compradores:** no se revisó una muestra verificable.""", "Tabla dimensional y lista derivada de escalones de una broca Bosch HSS de 4–20 mm."),
"08-atornillador-para-durlock.md": ("Bosch GTB 650 y GTB 18V-45: comparar cable, batería y control de profundidad", """| Dato publicado | Bosch GTB 650 | Bosch GTB 18V-45 / GTB 185-LI |
| :--- | ---: | ---: |
| Alimentación | Cable, 650 W | Batería 18 V |
| Velocidad sin carga | 0–5.000 rpm | Hasta 4.500 rpm |
| Torque máximo publicado | 12 Nm | 6 Nm |
| Portapuntas | Hexagonal 1/4 in | Hexagonal 1/4 in |
| Peso publicado | 1,4 kg | 0,95 kg sin batería |
| Diámetro máximo de tornillo | 4 mm | 6 mm |
| Control de profundidad | Tope de profundidad | Tope de profundidad |

**Dato verificado:** los valores se extraen de las fichas Bosch indicadas. La denominación comercial puede variar por país; GTB 18V-45 aparece como GTB 185-LI en algunas páginas regionales. El peso inalámbrico excluye la batería y no se compara como peso del conjunto listo para usar.

**Análisis TallerLab:** la GTB 650 publica 500 rpm más y 6 Nm más de torque; la variante a batería publica un diámetro máximo de tornillo 2 mm mayor y elimina el cable, pero la ficha citada informa 0,95 kg sin batería. Estas diferencias describen números de catálogo, no velocidad de fijación, autonomía, comodidad o calidad de acabado. Elegí con base en disponibilidad de energía, contenido del kit y los tornillos admitidos.

**Declaración del fabricante:** Bosch indica que la GTB 650 puede trabajar con el alimentador MA55 compatible. La compatibilidad del alimentador y su disponibilidad deben comprobarse por código. Para placas, la función del tope es limitar la profundidad según el ajuste; no garantiza por sí sola que cada tornillo quede correctamente asentado.

**Desconocido:** no se verificó una configuración idéntica de batería/cargador para Argentina ni una garantía local actual de la variante 18 V. No hay ensayo propio sobre placas, tornillos T1/T2 o ritmo de colocación. Consultá el manual del código concreto y la especificación del tornillo/placa.

## Qué cambia la decisión

| Prioridad | Revisar en la ficha o publicación | Límite |
| :--- | :--- | :--- |
| Trabajo fijo en un ambiente | Cable y alimentación local | Requiere acceso al tomacorriente |
| Movimiento entre puestos | Plataforma, batería y cargador incluidos | El peso publicado puede excluir batería |
| Repetir profundidad | Tope compatible y ajuste | No reemplaza la técnica ni verifica el acabado |
| Alimentación automática | Compatibilidad MA55 por modelo | No asumir que viene incluido |

## Fuentes consultadas

- **Documentación primaria:** [Bosch GTB 650 Argentina](https://www.bosch-professional.com/ar/es/products/gtb-650-06014A20H0); [Bosch GTB 18V-45 / GTB 185-LI](https://www.bosch-professional.com/gb/en/products/gtb-185-li-06019K7000); [atornilladores Bosch con limitador de profundidad](https://www.bosch-professional.com/ar/es/atornilladores-con-limitador-de-profundidad-131443-ocs-c/).
- **Seguridad:** consultar manual para ajuste de profundidad, tornillos y accesorios.
- **Opiniones de compradores:** no se revisó una muestra verificable.""", "Comparación documental entre dos atornilladores Bosch para placas: rpm, torque, peso y alimentación."),
}

RELATED = {
"02-rotomartillo.md": ("/taladros/rotomartillos/", "taladros percutores", "/taladros/percutores/"),
"03-taladro-percutor.md": ("/taladros/rotomartillos/", "rotomartillos", "/taladros/rotomartillos/"),
"06-rotomartillo-bosch.md": ("/taladros/rotomartillos/", "rotomartillos", "/taladros/rotomartillos/"),
"11-rotomartillo-dewalt.md": ("/taladros/rotomartillos/", "rotomartillos", "/taladros/rotomartillos/"),
"10-rotomartillo-einhell.md": ("/taladros/rotomartillos/", "rotomartillos", "/taladros/rotomartillos/"),
"17-brocas-para-ceramica.md": ("/taladros/", "mechas para porcelanato", "/taladros/mecha-porcelanato/"),
"14-mecha-para-porcelanato.md": ("/taladros/", "brocas para cerámica", "/taladros/brocas-ceramica/"),
"22-mecha-forstner-35-mm.md": ("/taladros/", "guías de taladros", "/taladros/"),
"21-mechas-escalonadas.md": ("/taladros/", "guías de taladros", "/taladros/"),
"08-atornillador-para-durlock.md": ("/taladros/", "guías de taladros", "/taladros/"),
}

for filename, (asset, body, description) in PAGES.items():
    path = ROOT / "paginas" / "taladros" / filename
    old = path.read_text(encoding="utf-8")
    fm = re.match(r"---\r?\n(.*?)\r?\n---\r?\n", old, re.S)
    if not fm:
        raise RuntimeError(f"No frontmatter: {path}")
    front = fm.group(1)
    front = re.sub(r'(?m)^description:.*$', 'description: "' + description.replace('"', '\\"') + '"', front)
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
    h1 = re.search(r"(?m)^# .+$", old)
    if not h1:
        raise RuntimeError(f"No H1: {path}")
    hub, anchor, sibling = RELATED[filename]
    lead = re.sub(r"(?m)^.*$", lambda m: m.group(0), "")
    newbody = f"# {h1.group(0)[2:]}\n\n<!-- AUDITORIA_EDITORIAL_178 -->\n\n{body}\n\nPara seguir comparando: [{anchor}]({sibling}).\n\nPara explorar la categoría: [guías de taladros]({hub}).\n"
    path.write_text(f"---\n{front}\n---\n\n{newbody}", encoding="utf-8")
    print(path.relative_to(ROOT))
