"""Editorial-first commercial callouts for the amoladora article cluster."""

from html import escape


# Product facts are limited to the cited manufacturer, manual, or listing.
# `checks` are shown below the CTA, separately from the product comparison.
AMOLADORA_CHOICES = {
    "/amoladoras/": {
        "title": "Tres opciones para comparar según tu compra",
        "items": [
            {
                "name": "Gamma G1910KAR · kit de 115 mm",
                "url": "https://meli.la/12aMvrG",
                "facts": ["750 W", "115 mm", "11.000 rpm"],
                "reason": "Opción de entrada con kit, para quien necesita máquina y accesorios en una misma compra.",
                "checks": ["Código G1910KAR y tensión de placa", "Granos, tipos y cantidad de discos incluidos", "Garantía, vendedor y contenido real del kit"],
            },
            {
                "name": "Bosch GWS 770 · referencia compacta",
                "url": "https://meli.la/1GRCAjZ",
                "facts": ["770 W", "115 mm", "12.000 rpm"],
                "reason": "Alternativa de marca para comparar una angular compacta con una ficha regional propia.",
                "checks": ["Código 0 601 398 0E0 y tensión 220 V", "Correspondencia entre código, placa y manual", "Kit y garantía local de la unidad"],
            },
            {
                "name": "Omaha AA-750 · angular de 115 mm",
                "url": "https://www.mercadolibre.com.ar/amoladora-angular-omaha-aa-750-roja-750w-disco-115mm-220v-con-accesorios/p/MLA22765820",
                "facts": ["750 W", "115 mm", "10.000 rpm · 220 V"],
                "reason": "Tercera referencia para comparar una opción compacta de 220 V junto al kit Gamma y la Bosch.",
                "checks": ["Modelo AA-750 y placa 220 V", "La ficha del aviso indica que no incluye disco", "Protector, accesorios, vendedor y garantía"],
            },
        ],
    },
    "/amoladoras/disco-flap/": {
        "title": "Opción para comparar: Lüsqtoff LQDFLAP60",
        "items": [{
            "name": "Lüsqtoff LQDFLAP60 · grano 60",
            "url": "https://www.mercadolibre.com.ar/disco-flap-desbaste-grano-60-amoladora-metal-115mm-lusqtoff/up/MLAU2944968836",
            "facts": ["Código publicado: LQDFLAP60", "115 mm", "Grano 60 · zirconio según publicación"],
            "reason": "Coincide con una guía centrada en elegir grano, abrasivo y forma para un flap; no se recomienda una amoladora como sustituto del accesorio.",
            "checks": ["Código LQDFLAP60, grano y diámetro de 115 mm", "Agujero 22,23 mm, rpm máximas y tipo T27/T29 en etiqueta", "Metal admitido, unidad o pack y garantía/devolución"],
        }],
    },
    "/amoladoras/dewalt/": {
        "title": "Opción para comparar: DeWalt DWE4120-AR",
        "items": [{
            "name": "DeWalt DWE4120-AR · angular compacta",
            "url": "https://meli.la/13LHGQm",
            "facts": ["900 W", "115 mm", "12.000 rpm · 220 V / 50 Hz"],
            "reason": "Coincide con la variante argentina de 115 mm y los datos que la guía ya documenta en su tabla.",
            "checks": ["Sufijo DWE4120-AR y placa 220 V", "Guarda, eje y accesorios del manual", "Contenido del paquete, garantía y servicio local"],
        }],
    },
    "/amoladoras/bosch/": {
        "title": "Opción para comparar: Bosch GWS 770",
        "items": [{"name": "Bosch GWS 770 · 0 601 398 0E0", "url": "https://meli.la/1GRCAjZ",
            "facts": ["770 W", "115 mm", "12.000 rpm · variante 220 V según ficha regional"],
            "reason": "La guía la documenta como referencia compacta Bosch; permite comparar esa compra con la GWS 850 sin mezclar códigos ni tensiones.",
            "checks": ["Código 0 601 398 0E0 y tensión de placa", "Correspondencia entre código, manual y variante ofrecida", "Contenido del kit y garantía local"]}],
    },
    "/amoladoras/gamma/": {
        "title": "Opción para comparar: Gamma G1910KAR en kit",
        "items": [{"name": "Gamma G1910KAR · 750 W", "url": "https://meli.la/12aMvrG",
            "facts": ["115 mm", "11.000 rpm", "Kit con discos y maletín según ficha Gamma"],
            "reason": "La diferencia útil frente a G1910AR es la presentación en kit que la ficha Gamma identifica.",
            "checks": ["Código G1910KAR y 220 V~50 Hz", "Discos, cantidad, granos y maletín entregados", "Garantía, vendedor y costo final"]}],
    },
    "/amoladoras/dowen-pagio/": {
        "title": "Opción para comparar: Dowen Pagio 9993220.7",
        "items": [{"name": "Dowen Pagio 9993220.7 / AA115H4", "url": "https://meli.la/1QUvfns",
            "facts": ["900 W", "115 mm", "12.000 rpm · velocidad fija"],
            "reason": "Encaja con el código cableado de 115 mm que la guía distingue de la alternativa regulable y de 125 mm.",
            "checks": ["Código 9993220.7 / AA115H4 y tensión de placa", "Rosca/eje según manual y accesorios compatibles", "Disco, contenido y garantía del vendedor"]}],
    },
    "/amoladoras/makita/": {
        "title": "Opción para comparar: Makita GA4534",
        "items": [{"name": "Makita GA4534 · angular compacta", "url": "https://meli.la/1uKuW67",
            "facts": ["720 W", "115 mm", "11.000 rpm"],
            "reason": "Coincide con la referencia Makita de 115 mm y paleta que abre la comparación de códigos locales.",
            "checks": ["Código GA4534 y tensión de placa", "Interruptor, guarda y accesorios incluidos", "Garantía y repuestos para el mercado local"]}],
    },
    "/amoladoras/de-banco/": {
        "title": "Opción para comparar: Shimura SH-A5506 de 150 mm",
        "items": [{"name": "Shimura SH-A5506 · amoladora de banco", "url": "https://www.mercadolibre.com.ar/amoladora-de-banco-shimura-34-hp-550w-sha5506-cpiedras-color-amarillo-frecuencia-hz/p/MLA25161108",
            "facts": ["550 W", "Muela de 150 mm", "2.950 rpm · 220 V según publicación"],
            "reason": "Coincide con la búsqueda de una amoladora de banco de 150 mm; es una opción de banco, no una angular.",
            "checks": ["Código SH-A5506 y tensión de placa", "Medida, ancho, agujero y rpm de las muelas; confirmar piedras incluidas", "Protectores, apoyos, garantía y contenido exacto"]}],
    },
    "/amoladoras/inalambricas/": {
        "title": "Opción para comparar: Bosch GWS 180-LI",
        "items": [{"name": "Bosch Professional GWS 180-LI · 18 V", "url": "https://meli.la/27U6siB",
            "facts": ["Plataforma Bosch Professional 18 V", "Disco de 125 mm", "11.000 rpm según ficha Bosch"],
            "reason": "Representa una compra de ecosistema profesional; compará el cuerpo con el costo de baterías y cargador si todavía no tenés la plataforma.",
            "checks": ["Código GWS 180-LI y variante regional", "Confirmar si la publicación incluye batería y cargador", "Compatibilidad de pack, guarda, accesorios y garantía local"]}],
    },
    "/amoladoras/lusqtoff/": {
        "title": "Opción para comparar: Lüsqtoff AML850-8",
        "items": [{"name": "Lüsqtoff AML850-8 · con cable", "url": "https://meli.la/2YseJTk",
            "facts": ["850 W", "115 mm", "11.000 rpm · 220 V~50 Hz"],
            "reason": "Coincide con la opción cableada de 115 mm que la guía desarrolla y permite comparar precio y prestaciones sin subir de tamaño.",
            "checks": ["Código AML850-8 y placa 220 V", "Guarda, rosca, disco y accesorios incluidos", "Kit, servicio y garantía local"]}],
    },
    "/amoladoras/9-pulgadas/": {
        "title": "Opción para comparar: Makita GA9020 de 230 mm",
        "items": [{"name": "Makita GA9020 · angular de 230 mm", "url": "https://meli.la/21s58cx",
            "facts": ["2.200 W", "230 mm", "6.000 rpm"],
            "reason": "Es una referencia de 230 mm con presencia comercial y documentación local, alineada con quien busca la categoría de 9 pulgadas.",
            "checks": ["Código GA9020 y tensión de placa", "Disco, bridas y guarda de 230 mm compatibles", "Peso/configuración, contenido y garantía local"]}],
    },
    "/amoladoras/skil-830w/": {
        "title": "Opción para comparar: Skil 9004",
        "items": [{"name": "Skil 9004 · amoladora angular", "url": "https://www.mercadolibre.com.ar/amoladora-angular-skil-metal-9004-de-50-hz60hz-negra-830w/p/MLA15453102",
            "facts": ["830 W", "115 mm", "4,7/5 y +10.000 vendidos según publicación (dato variable)"],
            "reason": "La búsqueda es específica de este modelo y la publicación corresponde a la Skil 9004 que la guía explica.",
            "checks": ["Código 9004 y tensión/frecuencia de la placa", "RPM, eje, guarda y accesorios de la variante entregada", "Contenido, garantía y vendedor de la publicación"]}],
    },
    "/amoladoras/disco-diamantado-segmentado/": {
        "title": "Opción para comparar: Hamilton DS115 segmentado de 115 mm",
        "items": [{"name": "Hamilton DS115 · disco diamantado segmentado", "url": "https://www.mercadolibre.com.ar/disco-diamantado-segmentado-115mm-hamilton-ds115/p/MLA22673677",
            "facts": ["115 mm", "Borde segmentado", "Distintivo “más vendido” en el aviso (dato variable)"],
            "reason": "Coincide con el formato de 115 mm tratado en esta guía; es una referencia comercial para quien busca corte segmentado.",
            "checks": ["Modelo DS115 y materiales indicados en etiqueta", "Agujero/buje, diámetro y RPM máxima compatibles", "Uso seco/húmedo, cantidad y vendedor del aviso"]}],
    },
    "/amoladoras/stanley/": {
        "title": "Opción para comparar: Stanley STGS8115-AR",
        "items": [{"name": "Stanley STGS8115-AR · angular 115 mm", "url": "https://meli.la/2PxaVDv",
            "facts": ["850 W", "115 mm", "11.000 rpm según manual"],
            "reason": "Es la opción compacta de 850 W que la guía desarrolla y cuenta con ficha y manual de la variante argentina.",
            "checks": ["Sufijo STGS8115-AR y tensión/frecuencia de placa", "Contenido, protector y accesorios", "Garantía limitada y servicio local"]}],
    },
    "/amoladoras/disco-de-corte/": {
        "title": "Opción para comparar: pack Bosch Standard for INOX & Metal",
        "items": [{"name": "Bosch 2608619383 · disco de corte INOX & Metal", "url": "https://www.mercadolibre.com.ar/disco-corte-115-x-1mm-pack-x10-bosch-amoladora-4-12-metal/up/MLAU266464914",
            "facts": ["Pack de 10 discos", "115 × 1 × 22,23 mm", "Para INOX y metal según código", "Código Bosch 2 608 619 383"],
            "reason": "Es un consumible de 115 mm que la ficha Bosch identifica para acero inoxidable y metal; el pack de 10 ofrece una entrada más doméstica que comprar una caja grande.",
            "checks": ["Código 2608619383 y materiales indicados en la etiqueta", "Agujero 22,23 mm y RPM máxima frente a tu amoladora", "Cantidad real del pack, vendedor y política de devolución"]}],
    },
    "/amoladoras/ingco/": {
        "title": "Opción para comparar: INGCO AG7118-4",
        "items": [{"name": "INGCO AG7118-4 · angular cableada", "url": "https://meli.la/1BuRQNe",
            "facts": ["710 W", "115 mm", "220–240 V · 12.000 rpm según catálogo local"],
            "reason": "Opción cableada compacta y localizada para Argentina; resuelve primero el uso general de 115 mm antes de pasar a una compra a batería.",
            "checks": ["Código AG7118-4 en placa/caja", "Tensión, rpm, rosca y accesorios de la variante", "Disponibilidad, contenido y garantía local"]}],
    },
    "/amoladoras/velocidad-variable/": {
        "title": "Opción para comparar: Dowen Pagio 9993224.2",
        "items": [{"name": "Dowen Pagio 9993224.2 / AA125SPL · velocidad variable", "url": "https://meli.la/1x65DAe",
            "facts": ["1.250 W", "Discos de 115 o 125 mm", "4.000–12.000 rpm · 220 V~50 Hz"],
            "reason": "Coincide con el modelo de velocidad variable que la guía ya documenta y suma las dos medidas de disco en una misma herramienta.",
            "checks": ["Código 9993224.2 / AA125SPL y placa 220 V~50 Hz", "Rango de rpm, M14 y diámetro permitido por la guarda", "La ficha indica que no incluye disco; confirmar kit y garantía"]}],
    },
    "/amoladoras/7-pulgadas/": {
        "title": "Opción para comparar: Bosch GWS 2200-180",
        "items": [{"name": "Bosch GWS 2200-180 · 0 601 8F1 1H0", "url": "https://meli.la/1EzeM6d",
            "facts": ["2.200 W", "180 mm", "8.500 rpm · 5 kg según ficha"],
            "reason": "Referencia de 180 mm documentada para tareas que requieren ese diámetro, distinta de angulares compactas y de 230 mm.",
            "checks": ["Código y tensión de la variante", "Disco, bridas y guarda admitidos", "Peso real de la configuración, contenido y garantía"]}],
    },
    "/amoladoras/115-o-125/": {
        "title": "Dos opciones para elegir por diámetro",
        "items": [
            {"name": "Elegí 115 mm · Bosch GWS 850", "url": "https://meli.la/1hDoFyN",
            "cta_label": "Elegí 115 mm → Ver precio y disponibilidad en Mercado Libre",
            "facts": ["850 W", "115 mm", "11.000 rpm · 220 V · código 0 601 377 5H0"],
            "reason": "Si el diámetro compacto de 115 mm alcanza para tu trabajo, esta es la referencia Bosch local que desarrolla la guía.",
            "checks": ["Código 0 601 377 5H0 y placa de 220 V", "Disco de 115 mm, eje M14 y guarda", "Contenido del paquete y garantía local"]},
            {"name": "Elegí 125 mm · Bosch GWS 9-125", "url": "https://www.mercadolibre.com.ar/amoladora-angular-profesional-bosch-gws-9-125-900-w-5-125/up/MLAU3332295568",
            "cta_label": "Elegí 125 mm → Ver precio y disponibilidad en Mercado Libre",
            "facts": ["900 W", "125 mm", "11.000 rpm · 220 V según publicación"],
            "reason": "Si necesitás un disco de 125 mm y la máquina correspondiente, esta variante Bosch está documentada para Argentina.",
            "checks": ["Código completo y tensión de la unidad (la familia tiene variantes)", "Diámetro de 125 mm, eje M14 y guarda compatible", "Contenido, vendedor y garantía de la publicación"]},
        ],
    },
    "/amoladoras/total/": {
        "title": "Total: entrada compacta de 115 mm",
        "items": [{"name": "Total TG10711576-4 · angular de 115 mm", "url": "https://meli.la/1WnXJFJ",
            "facts": ["710 W", "115 mm", "12.000 rpm · M14 según ficha citada"],
            "reason": "La opción de entrada de esta guía: coincide con quien necesita una angular cableada compacta de 115 mm.",
            "checks": ["Sufijo -4, placa y tensión", "Rpm, M14 y accesorios del manual", "Contenido de caja y garantía/importador local"]}],
    },
    "/amoladoras/discos-vidrio/": {
        "title": "Opción para comparar: Smart Ladike Design pack de 3",
        "items": [{"name": "Smart Ladike Design · disco diamantado para vidrio, pack x3", "url": "https://www.mercadolibre.com.ar/disco-para-cortar-vidrio-p-amoladora-angular-115mm-pack-x3-color-verde-lima/p/MLA57472920",
            "facts": ["Pack de 3 discos", "115 mm · 1,5 mm según publicación", "+5.000 vendidos · 4,7/5 en el aviso (dato variable)"],
            "reason": "La publicación identifica expresamente el corte de vidrio y coincide con la búsqueda de un consumible de 115 mm; el pack de tres permite comparar el costo por unidad.",
            "checks": ["Cantidad seleccionada y espesor declarados para la variante", "Agujero, RPM máxima y uso seco/húmedo en etiqueta/manual", "Tipo de vidrio admitido y compatibilidad con la amoladora"]}],
    },
    "/amoladoras/disco-de-desbaste/": {
        "title": "Opción para comparar: Bosch PRO Metal de 115 mm",
        "items": [{
            "name": "Bosch PRO Metal · 2 608 600 218",
            "url": "https://meli.la/1tL91SZ",
            "facts": ["115 × 6 × 22,23 mm", "A 30 T BF", "Desbaste de metal"],
            "reason": "La guía usa este mismo código como referencia técnica; la oferta queda alineada con material, operación y medidas ya explicados.",
            "checks": ["Código 2 608 600 218 y uso de desbaste", "Agujero, rpm máxima, guarda y bridas compatibles", "Unidad/pack, vendedor y política de devolución"],
        }],
    },
    "/amoladoras/recta/": {
        "title": "Opción para comparar: Makita GD0600",
        "items": [{
            "name": "Makita GD0600 · amoladora recta",
            "url": "https://meli.la/1vUCzGL",
            "facts": ["400 W", "25.000 rpm", "220 V · pinza y accesorios según manual"],
            "reason": "Es el mismo modelo que la guía compara con Bosch para trabajos localizados con accesorios de vástago.",
            "checks": ["Código GD0600 y tensión 220 V", "Diámetro de pinza y vástago del accesorio; no confundir con discos angulares", "Llaves, accesorios, vendedor y garantía"],
        }],
    },
    "/amoladoras/discos/": {
        "title": "Tres accesorios para comparar por operación",
        "items": [],
    },
    "/amoladoras/discos-ceramica/": {
        "title": "Opción para comparar: Ronix RH-3534 de borde continuo",
        "items": [{"name": "Ronix RH-3534 · disco diamantado para cerámica", "url": "https://www.mercadolibre.com.ar/disco-diamantado-continuo-ronix-para-ceramica-de-115-mm/p/MLA54243319",
            "facts": ["115 mm", "Borde diamantado continuo", "22,2 mm de agujero según publicación"],
            "reason": "Coincide con la búsqueda de un disco de borde continuo para cerámica; confirmá en el envase el material permitido y el modo de uso del código exacto.",
            "checks": ["Código RH-3534 y material admitido; no asumir porcelanato", "Diámetro, agujero, rpm máxima y sentido de giro", "Uso seco/húmedo solo según fabricante y equipo"]}],
    },
    "/amoladoras/total/": {
        "name": "Total TG109125565-4 · 125 mm con velocidad variable",
        "url": "https://www.mercadolibre.com.ar/amoladora-angular-total-900w-125-mm-velocidad-variable/up/MLAU3722400545",
        "facts": ["900 W", "125 mm", "Velocidad variable · 220 V según publicación"],
        "reason": "Para quien necesita pasar de la opción compacta de 115 mm a 125 mm y quiere regulación de velocidad, según catálogo y publicación del código indicado.",
        "checks": ["Código TG109125565-4 y tensión de la unidad", "Confirmar rango de rpm en placa/manual, pues los avisos difieren", "Disco, guarda, M14, contenido y garantía local"],
    },
    "/amoladoras/dowen-pagio/": {
        "name": "Dowen Pagio 9993224.2 / AA125SPL · velocidad variable",
        "url": "https://meli.la/1x65DAe",
        "facts": ["1.250 W", "Discos de 115 o 125 mm", "4.000–12.000 rpm · 220 V~50 Hz según ficha"],
        "reason": "Si vas a usar regulación o necesitás elegir entre 115 y 125 mm, este es el paso contextual desde la 9993220.7 de 900 W y velocidad fija.",
        "checks": ["Código 9993224.2 / AA125SPL y placa 220 V~50 Hz", "Rango de rpm, rosca y diámetro permitido por la guarda", "La ficha indica que no incluye disco; confirmar kit y garantía"],
    },
    "/amoladoras/discos-vidrio/": {
        "name": "Smart Ladike Design · disco para vidrio de 115 mm, unidad individual",
        "url": "https://www.mercadolibre.com.ar/disco-para-cortar-vidrio-para-amoladora-angular-115mm-smart-verde-lima/p/MLA78726320",
        "facts": ["1 disco", "115 mm", "4,7/5 y +5.000 vendidos en la publicación (dato variable)"],
        "reason": "Alternativa para quien prefiere comprar una unidad en lugar del pack x3; es la misma familia de disco orientada a vidrio.",
        "checks": ["Confirmar código y medidas de la unidad ofrecida", "Agujero, RPM máxima y proceso permitido", "Vidrio compatible según fabricante; no extrapolar a templado o laminado"],
    },
}

CONTEXTUAL_CHOICES = {
    "/amoladoras/disco-flap/": {
        "name": "Lüsqtoff LQDFLAP80 · grano 80",
        "url": "https://www.mercadolibre.com.ar/disco-flap-desbaste-115mm-grano-80-lusqtoff-lqdflap80/p/MLA32166032",
        "facts": ["115 mm", "Grano 80", "Zirconio · 22,23 mm en la ficha de publicación"],
        "reason": "Si buscás una terminación más fina que la referencia G60, el grano 80 es una variante distinta para contrastar; no garantiza un acabado final por sí solo.",
        "checks": ["Código LQDFLAP80 y grano elegido", "Agujero, rpm máxima, forma y metal admitido", "Cantidad, vendedor y devolución"],
    },
    "/amoladoras/dewalt/": {
        "name": "DeWalt DWE4212-AR · angular de 125 mm",
        "url": "https://www.mercadolibre.com.ar/amoladora-angular-115mm--125mm-1200w-dewalt-dwe4212-dewalt/up/MLAU279595785",
        "facts": ["1.200 W", "125 mm", "11.000 rpm · 220 V según publicación oficial"],
        "reason": "Opción contextual si el trabajo necesita el formato de 125 mm que no cubre la DWE4120-AR de 115 mm.",
        "checks": ["DWE4212-AR y placa 220 V", "Diámetro máximo, guarda y disco según manual", "Kit, accesorios y condiciones de garantía local"],
    },
    "/amoladoras/de-banco/": {
        "name": "Makita GB801 · amoladora de banco de 205 mm",
        "url": "https://articulo.mercadolibre.com.ar/MLA-619099060-oferta-amoladora-banco-makita-gb801-205mm-550w-clupaluz-_JM",
        "facts": ["550 W", "Muela de 205 mm", "2.850 rpm a 50 Hz según catálogo Makita"],
        "reason": "Para quien necesita una máquina de banco mayor que la Shimura de 150 mm y acepta la medida específica de 205 mm.",
        "checks": ["Código GB801, tensión 220 V y frecuencia", "Muela de 205 × 19 mm, agujero 15,88 mm y rpm compatibles", "Stock, lupas/luces incluidas y garantía de la publicación"],
    },
    "/amoladoras/makita/": {
        "name": "Makita GA9020 · angular de 230 mm",
        "url": "https://meli.la/21s58cx",
        "facts": ["2.200 W", "230 mm", "6.000 rpm"],
        "reason": "Variante para trabajos que requieren una angular grande; la GA4534 de 115 mm cubre la compra compacta.",
        "checks": ["Código GA9020 y tensión de placa", "Disco, guarda y bridas admitidos por el manual", "Peso, contenido del paquete y garantía local"],
    },
    "/amoladoras/inalambricas/": {
        "name": "KTO TLD21-5 · kit inalámbrico de entrada",
        "url": "https://www.mercadolibre.com.ar/kit-amoladora-angular-21v-ktotaladro-percutor-brushless-21v/p/MLA2062845699",
        "facts": ["Kit de amoladora y herramientas", "La publicación ofrece dos baterías", "Familia anunciada como 21 V"],
        "reason": "Alternativa de kit completo para quien empieza sin baterías; contrasta con la compra de ecosistema Bosch Professional.",
        "checks": ["Confirmar código exacto TLD21-5 y tensión nominal", "Capacidad y cantidad de baterías, cargadores y accesorios entregados", "Garantía, repuestos y compatibilidad de baterías del kit"],
    },
    "/amoladoras/discos-ceramica/": {
        "name": "Bosch PRO Ceramic · 2 608 602 478",
        "url": "https://meli.la/1khPuL9",
        "facts": ["115 mm", "Borde turbo", "Para azulejos según ficha Bosch"],
        "reason": "Segunda referencia de fabricante con perfil turbo documentado; permite contrastar el borde continuo del Ronix con una geometría distinta.",
        "checks": ["Código 2 608 602 478 y material declarado", "Diámetro, agujero, rpm máxima y guarda", "No asumir corte húmedo; seguir manual de disco y herramienta"],
    },
    "/amoladoras/bosch/": {
        "name": "Bosch GWS 850 · alternativa de 115 mm",
        "url": "https://meli.la/1hDoFyN",
        "facts": ["850 W", "115 mm", "11.000 rpm · 220 V para el código argentino citado"],
        "reason": "Alternativa con demanda de búsqueda propia para comparar frente a la GWS 770, sin tomar potencia o rpm como prueba de rendimiento.",
        "checks": ["Código 0 601 377 5H0 y tensión 220 V", "Ficha, placa y contenido exactos de la unidad", "Garantía local y peso/configuración de la variante"],
    },
    "/amoladoras/lusqtoff/": {
        "name": "Lüsqtoff AML1010-8 · más potencia y velocidad regulable",
        "url": "https://meli.la/1GVNNxZ",
        "facts": ["1.010 W", "Hasta 125 mm", "0–11.000 rpm · seis posiciones según ficha"],
        "reason": "Para quien necesita más potencia nominal, admite el diámetro de 125 mm de su ficha o quiere regular la velocidad frente a la AML850-8 fija de 115 mm.",
        "checks": ["Código AML1010-8 y tensión 220 V~50 Hz", "Disco, eje M14 y RPM apropiados para la tarea", "Contenido del paquete y garantía aplicable al código"],
    },
    "/amoladoras/9-pulgadas/": {
        "name": "Bosch GWS 30-230 PB · 2.800 W con motor brushless",
        "url": "https://meli.la/33JWgGN",
        "facts": ["2.800 W", "230 mm", "6.500 rpm · 5,9 kg según ficha"],
        "reason": "Alternativa de 230 mm para quien prioriza la potencia y funciones declaradas de la Bosch; contrasta con la Makita GA9020 de 2.200 W.",
        "checks": ["Código 0 601 8G1 1H0 y tensión de placa", "Variante PB, freno, guarda y accesorios confirmados en la publicación", "Peso, kit, garantía y disponibilidad local"],
    },
    "/amoladoras/disco-diamantado-segmentado/": {
        "name": "DeWalt DW47452L · segmentado de 115 mm",
        "url": "https://www.mercadolibre.com.ar/disco-diamantado-4-12-dewalt-dw47452hp-segmentado-115mm/up/MLAU266079391",
        "facts": ["115 mm", "Borde segmentado", "Para concreto y bloque según publicación"],
        "reason": "Una segunda marca para comparar el formato segmentado de 115 mm; verificá el montaje exacto porque la publicación mezcla códigos DW47452L y DW47452HP.",
        "checks": ["Código grabado DW47452L/HP y materiales permitidos", "Agujero central y buje que correspondan al eje de la máquina", "RPM máxima y condiciones seco/húmedo de la etiqueta"],
    },
    "/amoladoras/stanley/": {
        "name": "Stanley STGS9115-AR · 900 W",
        "url": "https://meli.la/33ypj4z",
        "facts": ["900 W", "115 mm", "12.000 rpm según manual"],
        "reason": "Alternativa de más potencia nominal y velocidad publicada dentro de la línea argentina de 115 mm, frente a los 850 W de la STGS8115-AR.",
        "checks": ["Sufijo STGS9115-AR y placa 220 V / 50 Hz", "Manual y contenido de accesorios del código ofrecido", "Dos años de garantía limitada y servicio local confirmados"],
    },
    "/amoladoras/ingco/": {
        "name": "INGCO CAGLI271532-4 · kit inalámbrico P20S de 20 V",
        "url": "https://www.mercadolibre.com.ar/amoladora-angular-2-bat-4a-cargador-ingco-cagli271532/p/MLA49486654",
        "facts": ["115 mm · 3.000/6.000/9.000 rpm", "2 baterías de 4 Ah", "Cargador 20 V y 10 discos de corte según publicación"],
        "reason": "Alternativa para quien necesita movilidad y quiere entrar al kit P20S local; la AG7118-4 con cable sigue siendo la opción principal de uso general.",
        "checks": ["Confirmar SKU CAGLI271532-4 y contenido del lote", "Capacidad de baterías, modelo de cargador y entrada 220–240 V", "Garantía local y compatibilidad de otros packs P20S"],
    },
    "/amoladoras/velocidad-variable/": {
        "name": "Total TG109125565-4 · alternativa variable de 125 mm",
        "url": "https://www.mercadolibre.com.ar/amoladora-angular-total-900w-125-mm-velocidad-variable/up/MLAU3722400545",
        "facts": ["900 W", "125 mm", "Velocidad variable · 220 V según publicación"],
        "reason": "Una alternativa de entrada de 125 mm con regulador para comparar frente a la Dowen Pagio; no ofrece la misma potencia ni el mismo rango declarado.",
        "checks": ["Código TG109125565-4 y tensión 220 V", "La publicación muestra variaciones en el rango de rpm: confirmar en placa/manual", "Eje M14, contenido y garantía local"],
    },
    "/amoladoras/7-pulgadas/": {
        "name": "DeWalt DWE4557-AR · angular de 180 mm",
        "url": "https://www.mercadolibre.com.ar/amoladora-angular-dwe4557ar-180mm-7-pulgadas-2400w/up/MLAU284272305",
        "facts": ["2.400 W", "180 mm", "8.500 rpm · 220 V según publicación"],
        "reason": "Alternativa de 180 mm para comparar con la Bosch GWS 2200-180; la ficha del vendedor declara más potencia nominal, sin que eso sea una prueba de rendimiento.",
        "checks": ["Código DWE4557-AR y placa 220 V~50 Hz", "Guarda, disco de 180 mm, eje y accesorios del manual", "Peso y paquete varían entre publicaciones; confirmar garantía local"],
    },
}


def render_amoladora_choice(article_url):
    choice = AMOLADORA_CHOICES.get(article_url)
    if not choice:
        return ""
    rendered_items = []
    for item in choice["items"]:
        facts = "".join(f"<li>{escape(value)}</li>" for value in item["facts"])
        checks = "".join(f"<li>{escape(value)}</li>" for value in item["checks"])
        cta_label = escape(item.get("cta_label", "Ver precio y disponibilidad en Mercado Libre"))
        rendered_items.append(f'''<article class="editorial-product-choice">
          <h3>{escape(item["name"])}</h3>
          <ul class="offer-specs">{facts}</ul>
          <p>{escape(item["reason"])}</p>
          <a class="buying-link btn-mercado-libre" href="{escape(item["url"], quote=True)}" target="_blank" rel="nofollow sponsored noopener noreferrer" data-affiliate-placement="editorial-choice">{cta_label}</a>
          <div class="product-before-buying"><h4>Antes de comprar</h4><ul>{checks}</ul></div>
        </article>''')
    if not rendered_items:
        return ""
    affiliate_note = "Los enlaces afiliados cortos pueden generar una comisión para TallerLab." if any(item["url"].startswith("https://meli.la/") for item in choice["items"]) else "El enlace abre una publicación directa; no se confirmó seguimiento de afiliado."
    direct_note = " Las publicaciones enlazadas pueden cambiar de precio, disponibilidad, variante y contenido." if any(not item["url"].startswith("https://meli.la/") for item in choice["items"]) else " Confirmá precio, disponibilidad y variante en el aviso."
    return f'''<aside class="amoladora-editorial-choice" aria-label="{escape(choice["title"], quote=True)}">
      <span class="resource-kicker">OPCIONES PARA ESTA GUÍA · TALLERLAB</span>
      <h2>{escape(choice["title"])}</h2>
      <div class="editorial-product-grid">{"".join(rendered_items)}</div>
      <p class="buying-disclosure">{escape(affiliate_note + direct_note)}</p>
    </aside>'''


def render_contextual_choice(article_url):
    item = CONTEXTUAL_CHOICES.get(article_url)
    if not item:
        return ""
    facts = "".join(f"<li>{escape(value)}</li>" for value in item["facts"])
    checks = "".join(f"<li>{escape(value)}</li>" for value in item["checks"])
    return f'''<aside class="contextual-product-choice">
      <span class="resource-kicker">OTRA VARIANTE PARA ESTA NECESIDAD</span>
      <h3>{escape(item["name"])}</h3>
      <ul class="offer-specs">{facts}</ul>
      <p>{escape(item["reason"])}</p>
      <a class="buying-link btn-mercado-libre" href="{escape(item["url"], quote=True)}" target="_blank" rel="nofollow sponsored noopener noreferrer" data-affiliate-placement="editorial-choice">Ver precio y disponibilidad en Mercado Libre</a>
      <div class="product-before-buying"><h4>Antes de comprar</h4><ul>{checks}</ul></div>
      <p class="buying-disclosure">Enlace directo a la publicación; no se confirmó seguimiento de afiliado.</p>
    </aside>'''
