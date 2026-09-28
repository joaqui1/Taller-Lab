from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
DATE = "27/09/2026"

PAGES = {
    "paginas/soldadura-electronica/03-gadnic-878d.md": {
        "asset": "comparación de potencia, rangos térmicos y contenido declarado para Gadnic 878D y Yihua 878D/898D, con discrepancia 750 W frente a 370 W visible",
        "description": "Ficha documental de la Gadnic 878D: contraste entre los 750 W del texto comercial y los 370 W del cuadro técnico, accesorios y diferencias frente a Yihua.",
        "body": r'''**Dato documentado:** la página argentina de Gadnic identifica el producto como 878D y ofrece dos valores de potencia en la misma ficha: el texto descriptivo menciona 750 W, mientras que la tabla de especificaciones indica **370 W nominales**. La misma tabla declara alimentación de 220 V, aire a 100–450 °C, cautín a 200–480 °C, estabilidad de ±2 °C, caudal de 120 L/min y peso de 2,3 kg. Son datos publicados por el vendedor/fabricante; TallerLab no los midió.

| Equipo y fuente | Potencia publicada | Aire caliente | Cautín | Caudal / peso | Qué permite concluir |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Gadnic 878D, ficha argentina | 370 W en especificaciones; 750 W en descripción | 100–450 °C | 200–480 °C | 120 L/min; 2,3 kg | La propia página presenta una discrepancia de potencia que debe confirmarse en la etiqueta o manual de la unidad ofrecida |
| Yihua 878D, serie OEM | 700 W ±10% máx. de máquina; aire 650 W | 100–450 °C | 200–480 °C, salida 50 W | 120 L/min máx.; 2,6 kg | Es otra ficha y no demuestra que la Gadnic tenga la misma configuración |
| Yihua 898D/898D+ | 730 W de máquina; aire 650 W | 100–480 °C | 200–480 °C; 50/75 W según versión | 120 L/min máx.; 2,65 kg | El sufijo y la versión cambian los datos; no trasladarlos a la 878D |

**Declaración del fabricante:** Gadnic enumera estación, cautín, soporte, paño de limpieza, bomba de aire, soporte para bomba, tres punteras y manual en español. La ficha ofrece garantía de 12 meses. Es preciso revisar el contenido de la oferta concreta porque los combos comerciales pueden modificarse.

**Análisis TallerLab:** la cifra de 750 W no queda conciliada con los 370 W del cuadro de especificaciones. Para comparar esta unidad, tomamos como referencia provisional el dato tabulado de 370 W, pero la diferencia sigue abierta hasta cotejar placa/manual del ejemplar vendido. La ficha OEM Yihua solo sirve como comparación documental entre modelos: ni acredita equivalencia técnica ni valida el dato de Gadnic. La potencia total tampoco permite deducir por sí sola la temperatura efectiva en la unión.

**Desconocido:** no se comprobó físicamente una unidad, la revisión del manual descargable no resolvió la discrepancia, y no se revisó una muestra de opiniones. Tampoco se confirma que los repuestos Yihua sean compatibles con esta Gadnic.

## Cómo investigamos esta guía

- Tipo de análisis: documental.
- Prueba física de TallerLab: no.
- Especificaciones contrastadas: sí; discrepancia registrada, no resuelta.
- Opiniones de compradores: no.
- Fuentes primarias: sí.
- Última revisión: 27/09/2026.

## Fuentes consultadas

- **Ficha local y datos publicados por Gadnic/Bidcom:** [Estación Gadnic 878D, código SOLD0002](https://www.gadnic.com.ar/soldadoras/estacion-de-soldado-smd-750w). La URL incluye “750w”, pero la ficha hoy presenta 370 W nominales en el apartado de especificaciones y 750 W en el texto descriptivo.
- **Comparación de fabricante OEM, no equivalencia:** [Yihua serie 878/878A/878AD/878D](https://www.yihuasoldering.com/product-1-2-1-hot-air-rework-station/147657/) y [Yihua serie 898D/898D+](https://yihua-soldering.com/product-1-2-3-hot-air-rework-station-en/147659/).
- **Opiniones:** no se analizó una muestra verificable.

La selección depende de confirmar la potencia y la variante de la publicación. Consultá también la [estación de soldadura electrónica](/soldadura-electronica/estacion-de-soldadura/), el [kit de soldador de estaño](/soldadura-electronica/kit-soldador-de-estano/) y el [soporte con lupa](/soldadura-electronica/soporte-para-soldar-con-lupa/).

**Aviso de afiliados:** Taller Lab puede recibir una comisión por compras realizadas desde estos enlaces.

[Ver Gadnic 878D en Mercado Libre](https://meli.la/21VNNVW){:target="_blank" rel="sponsored" .btn-mercado-libre}

[Ver metodología de TallerLab](/como-trabajamos/)
'''
    },
    "paginas/soldadura-electronica/04-yihua-898d.md": {
        "asset": "tabla documental de parámetros y accesorios declarados para Yihua 898D/898D+ frente a la serie Yihua 878D, con límites entre variantes",
        "description": "Ficha de la Yihua 898D: potencia, rangos y accesorios según fabricante, con diferencias explícitas frente a 898D+ y 878D.",
        "body": r'''**Dato documentado:** Yihua publica la serie 898D/898D+ con tensión nominal de 220 V ±10% y potencia de máquina de 730 W. El fabricante declara para el aire caliente 650 W, rango de 100–480 °C y caudal máximo de 120 L/min; para el cautín, 200–480 °C y 50 W o 75 W según la variante. La ficha presenta estabilidad estática de ±5 °C para la tabla de la serie.

| Parámetro publicado | Yihua 898D/898D+ | Comparación con serie 878D | Límite de lectura |
| :--- | :--- | :--- | :--- |
| Potencia de máquina | 730 W | 700 W ±10% máx. | No es una medición de consumo sostenido en TallerLab |
| Temperatura de aire | 100–480 °C | 100–450 °C | Rango de control declarado, no perfil recomendado para toda placa |
| Temperatura de cautín | 200–480 °C | 200–480 °C | La ficha OEM no acredita estabilidad bajo carga real |
| Caudal máximo | 120 L/min | 120 L/min | Máximo declarado; no indica caudal en cada ajuste |
| Peso | 2,65 kg | 2,6 kg | Datos de fabricante para las series respectivas |
| Cautín | 50/75 W, según versión | 50 W | Confirmar modelo y mango incluidos en la oferta |

**Declaración del fabricante:** la configuración estándar de la página Yihua enumera máquina, pistola de aire, tres boquillas de 5, 8 y 10 mm, extractor de IC, soporte de mango, mango de cautín y soporte de cautín. La ficha agrupa 898D y 898D+; no se debe asumir que todos los vendedores entregan el mismo contenido.

**Análisis TallerLab:** frente a la 878D, la tabla del fabricante eleva el rango superior de aire de 450 a 480 °C y la potencia de máquina de 700 W ±10% máximo a 730 W. Esa diferencia describe lo publicado, no prueba una mejora de rendimiento en una reparación. Para una compra, cotejá el sufijo, la tensión de placa, el mango/calentador, las boquillas y la garantía local. No confundas el máximo de 120 L/min con una recomendación de caudal.

**Desconocido:** la ficha conjunta no permite atribuir automáticamente a una unidad 898D todas las opciones enumeradas para 898D+. No confirmamos disponibilidad de repuestos, contenido de una oferta argentina ni resultados térmicos reales. No se revisaron opiniones de compradores.

## Cómo investigamos esta guía

- Tipo de análisis: documental.
- Prueba física de TallerLab: no.
- Especificaciones contrastadas: sí, entre las fichas publicadas por Yihua para las series 898D y 878D.
- Opiniones de compradores: no.
- Fuentes primarias: sí.
- Última revisión: 27/09/2026.

## Fuentes consultadas

- **Fabricante:** [Yihua 898D/898D+](https://yihua-soldering.com/product-1-2-3-hot-air-rework-station-en/147659/).
- **Fabricante, serie comparada:** [Yihua 878/878A/878AD/878D](https://www.yihuasoldering.com/product-1-2-1-hot-air-rework-station/147657/).
- **Opiniones:** no se analizó una muestra verificable.

Si solo necesitás cautín, compará la [guía de estaciones electrónicas](/soldadura-electronica/estacion-de-soldadura/) y el [kit de estaño](/soldadura-electronica/kit-soldador-de-estano/). Para inmovilizar una placa, revisá el [soporte para soldar con lupa](/soldadura-electronica/soporte-para-soldar-con-lupa/).

**Aviso de afiliados:** Taller Lab puede recibir una comisión por compras realizadas desde estos enlaces.

[Ver Yihua 898D en Mercado Libre](https://meli.la/2du1wYY){:target="_blank" rel="sponsored" .btn-mercado-libre}

[Ver metodología de TallerLab](/como-trabajamos/)
'''
    },
    "paginas/soldadura-electronica/05-soporte-para-soldar-con-lupa.md": {
        "asset": "comparación documental entre Pro'sKit 608-391E, Weller WLACCHHB-02 y Velleman VTHH3N por aumento, pinzas, base o luz; dimensiones faltantes señaladas",
        "description": "Comparación de soportes para soldar con lupa por aumento declarado, brazos, pinzas, base y luz, con especificaciones atribuidas a cada fabricante.",
        "body": r'''**Dato documentado:** las fichas de fabricante describen soportes con configuraciones distintas. Pro’sKit 608-391E declara lente de vidrio de 60 mm y aumento 3X, dos brazos ajustables con pinzas cocodrilo, bandeja para esponja y base de hierro fundido de 55 × 55 × 35 mm. Weller WLACCHHB-02 declara aumento 4X y dos pinzas cocodrilo con giro de cuatro vías. Velleman VTHH3N agrega lupa con luz LED y requiere tres pilas AAA según la declaración de conformidad.

| Modelo | Aumento/lente declarado | Sujeción | Base, luz y límites publicados |
| :--- | :--- | :--- | :--- |
| Pro’sKit 608-391E | Lente de vidrio Ø60 mm; 3X (8D) | Dos brazos ajustables con pinzas cocodrilo | Base de hierro fundido 55 × 55 × 35 mm; bandeja para esponja; no se declara luz |
| Weller WLACCHHB-02 | 4X; el fabricante no detalla diámetro en la ficha consultada | Dos pinzas cocodrilo con giro de cuatro vías | La ficha consultada no especifica alimentación de luz ni dimensiones |
| Velleman VTHH3N | La declaración consultada no fija aumento | Pinzas cocodrilo y soporte para cautín | Lámpara LED; alimentación declarada: 3 pilas AAA; no se trasladan datos de otros Velleman |

**Declaración del fabricante:** las cifras de aumento, materiales y accesorios anteriores proceden de las páginas/fichas de producto identificadas. El aumento nominal no equivale a una evaluación de distancia de trabajo, nitidez o comodidad visual.

**Análisis TallerLab:** si necesitás una base con medida y lente de vidrio documentadas, Pro’sKit ofrece esos dos campos explícitos. Weller publica mayor aumento nominal (4X frente a 3X de Pro’sKit), pero no el diámetro de la lupa en la página consultada. Para trabajar con poca luz, Velleman documenta LED y alimentación por pilas. No comparamos estabilidad ni resistencia al calor porque no hay ensayos propios equivalentes.

**Desconocido:** no se revisó el modelo genérico enlazado en la oferta comercial original; por eso no se le atribuyen brazos, lupa, luz, dimensiones o accesorios de marcas comparables. No se analizaron opiniones de compradores.

## Cómo investigamos esta guía

- Tipo de análisis: documental.
- Prueba física de TallerLab: no.
- Especificaciones contrastadas: sí, entre tres fichas de producto identificadas.
- Opiniones de compradores: no.
- Fuentes primarias: sí.
- Última revisión: 27/09/2026.

## Fuentes consultadas

- **Fabricante:** [Pro’sKit 608-391E](https://www.proskit.com/Product/608-391E?hl=en-US); [Weller WLACCHHB-02](https://www.weller-tools.com/us/en/consumer/products/soldering-accessories/helping-hands-magnifier); [Velleman VTHH3N, declaración de conformidad](https://cdn.velleman.eu/downloads/doc/1950001-vthh3n_ce.pdf).
- **Opiniones:** no se analizó una muestra verificable.

Para el resto del puesto de trabajo, consultá el [kit de soldador de estaño](/soldadura-electronica/kit-soldador-de-estano/) y la [guía de estaciones electrónicas](/soldadura-electronica/estacion-de-soldadura/).

**Aviso de afiliados:** Taller Lab puede recibir una comisión por compras realizadas desde estos enlaces.

[Ver soporte con lupa en Mercado Libre](https://meli.la/1XdM9ut){:target="_blank" rel="sponsored" .btn-mercado-libre}

[Ver metodología de TallerLab](/como-trabajamos/)
'''
    },
    "paginas/soldadura-electronica/01-kit-soldador-de-estano.md": {
        "asset": "tabla comparativa de tres kits documentados por herramientas incluidas, potencia, tensión y límite de mercado; guía de elección según alcance",
        "description": "Guía de kits para soldar estaño con comparación de componentes, potencia y tensión declaradas por Pro’sKit, Velleman y Weller.",
        "body": r'''**Dato documentado:** las fichas de Pro’sKit y Velleman documentan kits de cautín con herramientas básicas para soldar y desoldar; Weller publica un kit regional de 60 W y 120 V. Son productos con distinta tensión y contenido, no tres variantes de un mismo modelo.

| Kit / mercado indicado | Cautín | Elementos incluidos según fabricante | Alimentación declarada | Límite de comparación |
| :--- | :--- | :--- | :--- | :--- |
| Pro’sKit PK-916G, mercado de China | 30 W; 220–240 V; 460 °C ±10% | Punta de repuesto, bomba desoldadora, alambre Ø0,8 mm (~10 g), soporte y aceite de resina | 220–240 V; ficha especifica enchufe G | Fabricante indica “solo mercado de China”; no confirma enchufe ni garantía argentina |
| Velleman K/SOLD2N | 25 W; máximo declarado 420 °C | Bomba desoldadora, soporte con esponja y estaño | 220–240 V, 50 Hz; enchufe E/F | La página es europea; disponibilidad y garantía local no confirmadas |
| Weller WLC100K, versión estadounidense | 60 W | Cautín, base/soporte y accesorios según la configuración regional | 120 V | No conectar directamente a una red de 220 V; no es una recomendación para Argentina sin confirmar un transformador adecuado |

**Declaración del fabricante:** Pro’sKit especifica composición y cantidad aproximada de soldadura, pero también restringe PK-916G al mercado chino. Velleman enumera hierro, soporte, bomba y soldadura. Weller publica el kit WLC100K como versión de 120 V. Las ofertas locales pueden modificar contenido, ficha o cobertura.

**Análisis TallerLab:** para empezar, compará primero la tensión compatible con la instalación, el tipo de punta y si el kit incluye soporte y herramienta de desoldado. Un cautín de mayor potencia no es automáticamente mejor para una unión concreta: importan la transferencia térmica de la punta, la regulación disponible y el trabajo previsto. Para placas que requieren retrabajo con aire, la comparación cambia; revisá la [guía de estaciones electrónicas](/soldadura-electronica/estacion-de-soldadura/).

**Desconocido:** no se validó qué kit genérico entrega cada vendedor argentino, ni su garantía, certificación local o disponibilidad de puntas. No se hizo una prueba de calentamiento ni se revisaron opiniones de compradores.

## Cómo investigamos esta guía

- Tipo de análisis: documental.
- Prueba física de TallerLab: no.
- Especificaciones contrastadas: sí, entre fichas de kits concretos.
- Opiniones de compradores: no.
- Fuentes primarias: sí.
- Última revisión: 27/09/2026.

## Fuentes consultadas

- **Fabricantes:** [Pro’sKit PK-916G](https://www.proskit.com/Product/PK-916G?hl=en-US); [Velleman K/SOLD2N](https://www.velleman.eu/products/view/electric-soldering-set-k-sold2n/?id=353840&lang=en); [Weller WLC100K, 120 V](https://www.weller-tools.com/us/en/consumer/products/corded-soldering-irons/soldering-iron-kit-60w120v-us).
- **Opiniones:** no se analizó una muestra verificable.

También podés comparar componentes individuales en la guía de [soportes con lupa](/soldadura-electronica/soporte-para-soldar-con-lupa/) y revisar estaciones de [aire caliente y cautín](/soldadura-electronica/gadnic-878d/).

**Aviso de afiliados:** Taller Lab puede recibir una comisión por compras realizadas desde estos enlaces.

[Ver kit de soldador de estaño en Mercado Libre](https://meli.la/2q7fy7p){:target="_blank" rel="sponsored" .btn-mercado-libre}

[Ver metodología de TallerLab](/como-trabajamos/)
'''
    },
}

for relpath, data in PAGES.items():
    path = ROOT / relpath
    old = path.read_text(encoding="utf-8")
    match = re.match(r"---\r?\n(.*?)\r?\n---\r?\n", old, re.S)
    if not match:
        raise RuntimeError(f"No se encontró frontmatter: {relpath}")
    front = match.group(1)
    original_title = re.search(r"(?m)^title:.*$", front).group()
    original_h1 = re.search(r"(?m)^h1:.*$", front).group()
    original_url = re.search(r"(?m)^url:.*$", front).group()
    fields = {
        "description": '"' + data["description"].replace('"', '\\"') + '"',
        "research_type": '"documental"',
        "physical_test": '"no"',
        "specifications_contrasted": '"sí"',
        "buyer_opinions": '"no"',
        "primary_sources": '"sí"',
        "information_asset": '"' + data["asset"].replace('"', '\\"') + '"',
        "asset_status": '"verificado"',
        "reviewed": f'"{DATE}"',
        "published": "true",
    }
    for key, value in fields.items():
        if re.search(rf"(?m)^{key}:", front):
            front = re.sub(rf"(?m)^{key}:.*$", f"{key}: {value}", front)
        else:
            front += f"\n{key}: {value}"
    assert original_title == re.search(r"(?m)^title:.*$", front).group()
    assert original_h1 == re.search(r"(?m)^h1:.*$", front).group()
    assert original_url == re.search(r"(?m)^url:.*$", front).group()
    h1 = original_h1.split(":", 1)[1].strip().strip('"\'')
    body = f"# {h1}\n\n<!-- AUDITORIA_EDITORIAL_178 -->\n\n" + data["body"].replace("\n+", "\n")
    path.write_text(f"---\n{front}\n---\n\n{body}", encoding="utf-8")
    print(f"Actualizada {relpath} | {original_url}")
