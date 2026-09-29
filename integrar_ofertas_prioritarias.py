"""Edición puntual de las guías aprobadas; conserva el resto del contenido."""
from pathlib import Path

ROOT = Path(__file__).parent
SECTIONS = {
    'paginas/hidrolavadoras/01-hidrolavadoras.md': '''## Opciones eléctricas con enlace de compra

La comparación Gamma sirve para leer las fichas. Si querés consultar una oferta concreta, estas dos referencias eléctricas tienen enlaces de afiliado y documentación identificada:

| Modelo | Potencia / alimentación | Presión nominal / máxima | Caudal en la fuente | Qué falta confirmar | Consulta comercial |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Lüsqtoff HL100-7 | 1.200 W; 220 V–50 Hz | 70 / 100 bar | 5,5 L/min; la ficha no precisa condición | Kit, vendedor y manual de la unidad | [Consultar HL100-7](https://meli.la/1cZXqxL) |
| Logus HL-105 | 1.200 W; tensión de la unidad por confirmar | Nominal no localizada / 105 bar máximos | No localizado en la ficha consultada | Presión de servicio, caudal y accesorios | [Consultar HL-105](https://meli.la/2Rcddpg) |

**Dato documentado:** [Lüsqtoff HL100-7](https://www.lusqtoff.com.ar/ver-producto/HL100-7) separa presión nominal y máxima. [Logus HL-105](https://logus.com.ar/productos/hidrolavadora-105-bar-1200w-hl-105/) publica el máximo; no completamos sus campos ausentes con los de Gamma o Lüsqtoff.

**Análisis TallerLab:** HL100-7 permite contrastar su nominal de 70 bar con los campos nominales/de servicio de las fichas Gamma, conservando las condiciones de cada fuente. Los 105 bar máximos de HL-105 no prueban mayor capacidad de limpieza ni permiten compararla por presión de servicio.

### Si necesitás una opción a nafta

La [Logus GHL150 con referido](https://meli.la/1KQjHgT) cambia la alimentación: su [ficha Logus](https://logus.com.ar/productos/hidrolavadora-a-explosion-6-5hp-industrial-154-bar-ghl-150/) identifica motor de 6,5 hp y 154 bar, sin un punto de presión de servicio/caudal comparable localizado. Consultá la [guía de 150 bar](/hidrolavadoras/150-bar/) para revisar sus límites. La potencia del motor no equivale a potencia eléctrica y esa cifra de presión no la convierte en sustituta de las eléctricas de esta tabla.

Los enlaces son de afiliado. La identidad de la unidad, precio, stock y condiciones del vendedor se comprueban en la publicación.

''',
    'paginas/hidrolavadoras/03-hidrolavadoras-lusqtoff.md': '''## HL100-7: la referencia enlazada tiene ficha propia

| Campo | HL100-7: ficha oficial | Qué comprobar en la oferta |
| :--- | :--- | :--- |
| Potencia y red | 1.200 W; 220 V–50 Hz | Código HL100-7 y placa de la unidad |
| Presión nominal / máxima | 70 / 100 bar | No confundir el máximo con presión de servicio |
| Tasa de flujo | 5,5 L/min | La ficha no precisa si es nominal o máxima |
| Cable | 5 m | Manguera y accesorios del kit entregado |

**Dato documentado:** la [ficha oficial HL100-7](https://www.lusqtoff.com.ar/ver-producto/HL100-7) identifica ese código y los campos anteriores. Es distinta de HL100-8: en la comparación de catálogo, el -8 publica 2.000 W y 100 bar de trabajo. No trasladamos bomba, accesorios, repuestos ni datos de una variante a otra.

**Análisis TallerLab:** HL100-7 puede entrar en la comparación de eléctricas de menor potencia, pero no se declara equivalente al -8 por compartir «HL100». El ejemplo de consumo de agua de esta guía usa HL-120, cuyo caudal está publicado como de trabajo; no lo renombramos como si perteneciera al -7.

[Consultar la oferta de HL100-7](https://meli.la/1cZXqxL). Enlace de afiliado: confirmá modelo, contenido, precio, stock y garantía con el vendedor. **Desconocido:** no hay prueba de limpieza común entre estos modelos ni condición de caudal suficiente para ordenar su rendimiento.

''',
    'paginas/taladros/01-taladro-inalambrico.md': '''## Una alternativa con percusión y kit anunciado

| Referencia de la oferta | Alimentación anunciada | Torque / mandril anunciados | Configuración anunciada | Dato pendiente |
| :--- | :--- | :--- | :--- | :--- |
| Ingco CIDLI20668-4 | 20 V; condición nominal/máxima por confirmar | 66 Nm / 13 mm | Percutor; dos baterías, cargador y accesorios | Ah y códigos de baterías, tensión del cargador, manual del sufijo -4 |

**Declaración comercial:** esos datos corresponden a la [publicación Ingco registrada](https://www.mercadolibre.com.ar/atornillador-taladro-percutor-2-bateriasaccesorios-color-naranja-frecuencia-0/p/MLA42241463). La [ficha oficial CIDLI20668](https://www.ingco.com/in/product/compact-brushless-cordless-impact-drill/CIDLI20668) documenta el modelo base, pero no acredita por sí sola el kit argentino -4; sus Ah, rpm y accesorios no se transfieren automáticamente.

**Análisis TallerLab:** esta opción cambia la compra si necesitás percusión y empezar con baterías/cargador. Para comparar el costo de empezar, pedí el contenido completo de cada kit. No normalizamos su etiqueta 20 V a 18 V sin documentación de esa condición ni ordenamos 66 Nm comerciales contra los torques de la tabla como si fueran un ensayo común.

[Consultar el kit Ingco CIDLI20668-4](https://meli.la/2xvJRJp). Enlace de afiliado: precio, stock, contenido y garantía se confirman en la oferta. Revisá también la [guía específica de percutores inalámbricos](/taladros/taladro-percutor-inalambrico/). Para hormigón y accesorios SDS, la decisión puede cambiar hacia un [rotomartillo](/taladros/rotomartillos/).

''',
    'paginas/taladros/03-taladro-percutor.md': '''## Una opción comercial de percutor inalámbrico

El kit [Ingco CIDLI20668-4](https://meli.la/2xvJRJp) está registrado como percutor a batería con mandril de 13 mm, 20 V y 66 Nm anunciados, dos baterías y cargador. Es un enlace de afiliado; las cifras y el contenido provienen de la [publicación comercial](https://www.mercadolibre.com.ar/atornillador-taladro-percutor-2-bateriasaccesorios-color-naranja-frecuencia-0/p/MLA42241463).

**Análisis TallerLab:** puede entrar en tu evaluación si buscás un percutor inalámbrico con mandril convencional y un kit de inicio. Pedí código completo, Ah/códigos de baterías, tensión del cargador y manual de la variante antes de elegir. No le atribuimos las capacidades del GSB 18V-50 ni energía/encastre SDS del GBH 220.

**Desconocido:** no se confirmó la equivalencia de ese sufijo -4 con la [ficha oficial CIDLI20668](https://www.ingco.com/in/product/compact-brushless-cordless-impact-drill/CIDLI20668), ni sus diámetros máximos por material. La oferta no permite concluir que sustituya un rotomartillo. Consultá la [guía del percutor inalámbrico](/taladros/taladro-percutor-inalambrico/) y la [comparación de plataformas a batería](/taladros/inalambricos/) según la decisión que necesites resolver.

''',
    'paginas/taladros/04-taladro-de-banco.md': '''## Omaha AB550161K: alternativa con datos comerciales

| Campo | Omaha AB550161K anunciado | Comparación que sí permite |
| :--- | :--- | :--- |
| Potencia | 550 W; régimen no documentado aquí | No equipararla con potencia continua ni con 900 W S2 |
| Mandril | Hasta 16 mm | Coincide con la apertura máxima declarada del TB-16; no prueba capacidad de agujero |
| Velocidades | Cinco; rango de rpm por confirmar | No basta para decidir velocidad por material y broca |
| Contenido | Morsa de 3 pulgadas según publicación | Confirmar kit, fijación y dimensiones |
| Recorrido / mesa / ciclo | No confirmados en el registro | Pedir manual y ficha de ese código |

**Declaración comercial:** la [publicación registrada del taladro de banco](https://www.mercadolibre.com.ar/taladro-agujereadora-de-banco-16mm-550w-34-hp-5-vel-morsa/p/MLA68679095) es el respaldo comercial de esos campos, no una ficha primaria contrastada de precisión o régimen.

**Análisis TallerLab:** Omaha agrega otra configuración de mandril de 16 mm y cinco velocidades anunciadas. No lo elegimos por estar entre 450 y 710 W: faltan recorrido, rango de rpm y régimen para contrastar la tarea con los Lüsqtoff. Pedí también capacidad por material, peso y dimensiones de mesa.

[Consultar Omaha AB550161K](https://meli.la/2Znq55m). Enlace de afiliado: verificá código, tensión, morsa incluida, vendedor y garantía antes de comparar el costo completo.

''',
    'paginas/10-amoladoras-bosch.md': '''## GWS 770: la alternativa enlazada también tiene código

| Referencia documentada | Red / potencia | Disco / velocidad sin carga | Peso | Límite de correspondencia |
| :--- | :--- | :--- | :--- | :--- |
| GWS 770, 0 601 398 0E0, Bosch Brasil | 220 V / 770 W absorbidos | 115 mm / 12.000 rpm | 1,37 kg | Confirmar ese código en la unidad ofrecida en Argentina |

**Dato documentado:** la [ficha Bosch GWS 770 de Brasil](https://www.bosch-professional.com/br/pt/products/gws-770-06013980E0) respalda esos campos para 06013980E0. Es otro modelo que GWS 700: no hereda su peso, potencia o contenido.

**Análisis TallerLab:** la GWS 770 puede entrar en la rama con cable y disco de 115 mm del selector. Que publique 770 W frente a 710 W de GWS 700 no demuestra una mejora de corte o durabilidad. La diferencia documental de peso tampoco es un ensayo de ergonomía. Para 125 mm o regulación de velocidad, seguí comprobando esas funciones y la tensión de la variante.

[Consultar la oferta GWS 770](https://meli.la/1GRCAjZ). Enlace de afiliado: confirmá placa 06013980E0, 220 V, guarda, accesorios y garantía local. La ficha brasileña no acredita por sí sola el kit de la publicación argentina.

''',
    'paginas/compresores/01-compresor-de-aire-para-auto.md': '''## Cuatro configuraciones: alimentación y pistones son campos distintos

| Modelo | Alimentación | Construcción / controles publicados | Caudal declarado | Fuente y dato pendiente | Oferta |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Lüsqtoff MCL150-8 | 12 V; 275 W | Doble pistón; manómetro digital y parada automática | 60 L/min | Ficha Lüsqtoff; confirmar conexión y corriente | Referencia documental |
| Gadnic AV000009 | 12 V; 23 A anunciados | Controles y conexión a confirmar | 85 L/min | Página comercial Gadnic; condición de caudal no indicada | Referencia documental |
| Nictom IE01 | Batería incorporada | Pantalla digital, luz y PowerBank según la marca | 16 L/min máximos anunciados | Página Nictom; pedir manual, autonomía bajo carga y configuración | [Consultar IE01](https://meli.la/2m7TJWQ) |
| JD Extreme 107 | 12 V | Doble pistón y manómetro anunciados | 85 L/min anunciados | Publicación comercial; corriente, ciclo y condición de caudal pendientes | [Consultar JD 107](https://meli.la/274KM8a) |

**Dato documentado:** [Nictom IE01](https://www.nictom.com.ar/productos/inflador-compresor-de-aire-portatil-bateria-powerbank-ie01-gris/) tiene ficha de marca y acceso a manual. Sus afirmaciones de autonomía no representan una prueba de TallerLab. Para [JD Extreme 107](https://www.mercadolibre.com.ar/compresor-de-aire-portatil-jd-extreme-de-150-psi-con-doble-piston-para-auto-y-moto/p/MLA45403244), los campos anteriores provienen de la publicación comercial registrada.

**Análisis TallerLab:** batería/12 V identifica alimentación; doble pistón identifica construcción. MCL150-8 y JD 107 pueden compartir doble pistón y seguir teniendo conexiones, controles y ciclos distintos. Para evitar depender de la toma del vehículo, comprobá batería/autonomía de IE01; para 12 V, primero corriente, conexión y protección admitida. No elegimos el más rápido por 16, 60 u 85 L/min: faltan puntos de presión y ensayos equivalentes.

Los enlaces IE01 y JD 107 son de afiliado. Precio, stock, modelo, conexión y accesorios se confirman en cada aviso. La [guía de doble pistón 12 V](/compresores/12v-doble-piston/) detalla qué pedir para JD; la presión del neumático sigue siendo la de la etiqueta/manual del vehículo.

''',
    'paginas/sierras/04-sierra-caladora.md': '''## Consultar BES603: primero confirmar la variante

Si el máximo documentado de 65 mm en madera de BES603-B2 incluye el espesor que querés contrastar, podés [consultar la oferta Black+Decker BES603](https://meli.la/1ntghna) y pedir foto de placa, sufijo, 220 V, hoja tipo T y contenido del kit. Es un enlace de afiliado; el [registro comercial](https://www.mercadolibre.com.ar/sierra-caladora-black-decker-bes603-400w-3000-rpm/p/MLA39008702) identifica BES603 sin confirmar aquí el sufijo B2.

**Dato documentado:** la ficha BES603-B2 citada dice hasta 6 mm en **metal**, sin identificar acero en ese campo. Por eso el filtro de acero compara solo las dos Einhell cuya documentación identifica ese material. Para BES603-B2, 6 mm de metal queda como dato separado pendiente de especificación del material; no se convierte en capacidad genérica de acero.

**Análisis TallerLab:** estar dentro de un máximo de ficha no garantiza acabado, velocidad ni idoneidad de cualquier hoja. Si tu decisión depende del corte en acero, necesitás el dato específico del manual de la variante que se entrega. Revisá la [guía Black+Decker](/sierras/caladoras-black-decker/) para comparar control de velocidad y variantes BES602/BES603.

''',
    'paginas/generadores/01-grupos-electrogenos.md': '''## Opciones comerciales por escala de carga

Estas publicaciones con enlace de afiliado corresponden a equipos distintos de los Honda/Gamma de la tabla. La elección empieza por las cargas de marcha y arranque, la unidad de potencia y la placa del modelo que se entrega.

| Referencia registrada | Nominal | Máxima | Respaldo / qué falta | Consulta |
| :--- | :--- | :--- | :--- | :--- |
| Pektra GPK980, dos tiempos | 650 W anunciados | 720 W anunciados | Publicación comercial; confirmar nominal en placa/manual | [Consultar GPK980](https://meli.la/2jcLSy1) |
| Pektra GPK2200, nafta | No confirmada | 2,2 kVA anunciados | Publicación comercial; pedir nominal y condiciones | [Consultar GPK2200](https://meli.la/2bL6gVj) |
| Philco GE-PH2500ALP, nafta | 2.500 W anunciados | 2.800 W anunciados | Publicación comercial; contrastar manual de ese código | [Consultar Philco](https://meli.la/1nUAUuv) |

**Declaración comercial:** el respaldo registrado es el aviso de [Pektra GPK980](https://www.mercadolibre.com.ar/grupo-electrogeno-720w-pektra-072kva-34hp-980-nafta-generador-2t/p/MLA26044602), [Pektra GPK2200](https://www.mercadolibre.com.ar/grupo-electrogeno-generador-pektra-22kva-55-hp-nafta/p/MLA20005447) y [Philco GE-PH2500ALP](https://www.mercadolibre.com.ar/generador-electrico-philco-2500w-65hp-196cc-tanque-15l/p/MLA29450496). No se presenta como documentación primaria confirmada de todas sus capacidades.

**Análisis TallerLab:** GPK980 pertenece a una escala de carga pequeña; no se propone como sustituto de los Honda de varios kVA. GPK2200 queda condicionado a identificar nominal; GE-PH2500ALP requiere contrastar los W anunciados. No ordenamos 2,2 kVA contra 2.500 W ni elegimos por HP del motor. Calculá primero el [escenario de cargas de tu casa](/generadores/para-casa/) y revisá las guías de [equipos chicos](/generadores/chicos/) o [a nafta](/generadores/a-nafta/) según el requisito.

Los enlaces son de afiliado y no certifican disponibilidad. Confirmá modelo, manual, combustible, precio, stock, garantía y condiciones de uso antes de decidir.

''',
}

for relative, section in SECTIONS.items():
    path = ROOT / relative
    text = path.read_text(encoding='utf-8')
    assert section.splitlines()[0] not in text, relative
    assert text.count('## Fuentes consultadas') == 1, relative
    text = text.replace('## Fuentes consultadas', section + '## Fuentes consultadas')
    text = text.replace('reviewed: "27/09/2026"', 'reviewed: "28/09/2026"')
    text = text.replace('Última revisión: 27/09/2026', 'Última revisión: 28/09/2026')
    if relative.endswith('04-sierra-caladora.md'):
        text = text.replace('| Acero máximo |', '| Material metálico y máximo |')
        text = text.replace('| 65 mm | 6 mm |', '| 65 mm | Metal: 6 mm; acero no especificado |')
        text = text.replace('| 85 mm | 8 mm |', '| 85 mm | Acero: 8 mm |')
        text = text.replace('| 100 mm | 10 mm |', '| 100 mm | Acero: 10 mm |')
        text = text.replace('la diferencia declarada es 35 mm en madera y 4 mm en acero', 'la diferencia declarada es 35 mm en madera; no restamos los máximos de metal/acero como si identificaran un mismo material')
    if relative.endswith('04-taladro-de-banco.md'):
        text = text.replace('[guías de amoladoras](/taladros/)', '[guías de taladros](/taladros/)')
    path.write_text(text, encoding='utf-8')

print(f'Integradas {len(SECTIONS)} guías; conservada la captura histórica de precios.')
