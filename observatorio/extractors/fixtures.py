"""Muestras y fixtures representativos para auditorías y pruebas offline."""

# 1. Feed JSON de catálogo autorizado de distribuidor ferretero
FIXTURE_FEED_CATALOG_JSON = """{
  "version": "1.0",
  "actualizado_al": "2026-10-03T12:00:00Z",
  "moneda": "ARS",
  "productos": [
    {
      "mpn": "LC2550B-8",
      "sku": "LUS-LC2550B8",
      "marca": "Lüsqtoff",
      "modelo": "LC2550B-8",
      "titulo": "Compresor de Aire 50L 2.5 HP Lüsqtoff LC2550B-8 Monofásico",
      "precio_final": 289900.00,
      "precio_transferencia": 260910.00,
      "precio_referencia": 340000.00,
      "disponibilidad": "disponible",
      "stock_unidades": 15
    },
    {
      "mpn": "G2802AR",
      "sku": "GAM-G2802AR",
      "marca": "Gamma",
      "modelo": "G2802AR",
      "titulo": "Compresor Monofásico Gamma 50L 2 HP G2802AR",
      "precio_final": 315000.00,
      "precio_transferencia": 283500.00,
      "precio_referencia": 365000.00,
      "disponibilidad": "disponible",
      "stock_unidades": 8
    },
    {
      "mpn": "4020610",
      "sku": "EIN-4020610",
      "marca": "Einhell",
      "modelo": "TE-AC 270/50 Silent",
      "titulo": "Compresor Silencioso 50 Litros Einhell TE-AC 270/50 Silent",
      "precio_final": 495000.00,
      "precio_transferencia": 450000.00,
      "precio_referencia": 580000.00,
      "disponibilidad": "disponible",
      "stock_unidades": 4
    },
    {
      "mpn": "LC-0122",
      "sku": "LUS-LC0122",
      "marca": "Lüsqtoff",
      "modelo": "LC-0122",
      "titulo": "Compresor Silencioso 24L Lüsqtoff LC-0122 Libre de Aceite",
      "precio_final": 210000.00,
      "precio_transferencia": 189000.00,
      "precio_referencia": 245000.00,
      "disponibilidad": "disponible",
      "stock_unidades": 10
    },
    {
      "mpn": "MCL150-8",
      "sku": "LUS-MCL1508",
      "marca": "Lüsqtoff",
      "modelo": "MCL150-8",
      "titulo": "Mini Compresor Inflador Digital 12V Lüsqtoff MCL150-8 Auto",
      "precio_final": 48500.00,
      "precio_transferencia": 43650.00,
      "precio_referencia": 56000.00,
      "disponibilidad": "disponible",
      "stock_unidades": 25
    },
    {
      "mpn": "1.673-220.0",
      "sku": "KAR-16732200",
      "marca": "Kärcher",
      "modelo": "K2",
      "titulo": "Hidrolavadora de Alta Presión Kärcher K2 110 Bar 1400W",
      "precio_final": 178500.00,
      "precio_transferencia": 160650.00,
      "precio_referencia": 210000.00,
      "disponibilidad": "disponible",
      "stock_unidades": 18
    },
    {
      "mpn": "1.324-030.0",
      "sku": "KAR-13240300",
      "marca": "Kärcher",
      "modelo": "K4 Power Control",
      "titulo": "Hidrolavadora Kärcher K4 Power Control 130 Bar Motor Inducción",
      "precio_final": 645000.00,
      "precio_transferencia": 580500.00,
      "precio_referencia": 720000.00,
      "disponibilidad": "disponible",
      "stock_unidades": 6
    },
    {
      "mpn": "HL100-7",
      "sku": "LUS-HL1007",
      "marca": "Lüsqtoff",
      "modelo": "HL100-7",
      "titulo": "Hidrolavadora 100 Bar 1200W Lüsqtoff HL100-7 Hogar",
      "precio_final": 115000.00,
      "precio_transferencia": 103500.00,
      "precio_referencia": 135000.00,
      "disponibilidad": "disponible",
      "stock_unidades": 12
    },
    {
      "mpn": "HL-120",
      "sku": "LUS-HL120",
      "marca": "Lüsqtoff",
      "modelo": "HL-120",
      "titulo": "Hidrolavadora Eléctrica 120 Bar 1400W Lüsqtoff HL-120",
      "precio_final": 142000.00,
      "precio_transferencia": 127800.00,
      "precio_referencia": 165000.00,
      "disponibilidad": "disponible",
      "stock_unidades": 9
    },
    {
      "mpn": "G1902AR",
      "sku": "GAM-G1902AR",
      "marca": "Gamma",
      "modelo": "G130",
      "titulo": "Hidrolavadora Gamma G130 130 Bar 1600W G1902AR",
      "precio_final": 198000.00,
      "precio_transferencia": 178200.00,
      "precio_referencia": 230000.00,
      "disponibilidad": "disponible",
      "stock_unidades": 7
    }
  ]
}"""

# 2. Página HTML válida con datos estructurados JSON-LD, precio tachado y transferencia
FIXTURE_BULONERA_HTML_VALID = """<!DOCTYPE html>
<html lang="es">
<head>
    <title>Compresor de Aire Lüsqtoff 50 Litros LC2550B-8 | Bulonera Central</title>
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "Product",
      "name": "Compresor de Aire Lüsqtoff 50 Litros LC2550B-8",
      "brand": {
        "@type": "Brand",
        "name": "Lüsqtoff"
      },
      "mpn": "LC2550B-8",
      "sku": "BULO-94821",
      "description": "Compresor de aire monofásico con tanque de 50L y motor de 2.5 HP.",
      "offers": {
        "@type": "Offer",
        "priceCurrency": "ARS",
        "price": 298500.00,
        "availability": "https://schema.org/InStock",
        "itemCondition": "https://schema.org/NewCondition",
        "seller": {
          "@type": "Organization",
          "name": "Bulonera Central"
        }
      }
    }
    </script>
</head>
<body>
    <h1>Compresor de Aire Lüsqtoff 50 Litros LC2550B-8</h1>
    <div class="precio-box">
        <span class="precio-lista tachado">$ 355.000,00</span>
        <span class="precio-actual">$ 298.500,00</span>
        <p class="promo-transferencia">Pagando con transferencia 10% OFF: <strong>$ 268.650,00 con transferencia</strong></p>
    </div>
    <div class="stock-status">Disponible para retiro en sucursal y envío</div>
</body>
</html>"""

# 3. Página HTML con desglose de cuotas financiada vs precio de lista único
FIXTURE_EASY_HTML_WITH_INSTALLMENTS = """<!DOCTYPE html>
<html lang="es">
<head>
    <title>Compresor de aire 50L 2.5HP Lüsqtoff LC-2550B-8 | Easy</title>
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "Product",
      "name": "Compresor de aire 50L 2.5HP Lüsqtoff LC-2550B-8",
      "mpn": "LC2550B-8",
      "sku": "1249912",
      "offers": {
        "@type": "Offer",
        "priceCurrency": "ARS",
        "price": 312000.00,
        "availability": "https://schema.org/InStock"
      }
    }
    </script>
</head>
<body>
    <h1>Compresor de aire 50L 2.5HP Lüsqtoff LC-2550B-8</h1>
    <div class="product-price">
        <span class="best-price">$ 312.000,00</span>
        <div class="installments">
            <span>O hasta 12 cuotas fijas de $ 42.120,00 (Total financiado: $ 505.440,00)</span>
        </div>
    </div>
    <button class="add-to-cart">Agregar al carrito</button>
</body>
</html>"""

# 4. Producto agotado con OutOfStock
FIXTURE_HTML_OUT_OF_STOCK = """<!DOCTYPE html>
<html lang="es">
<head>
    <title>Compresor Monofásico Gamma 50L G2802AR | Bulonera Central</title>
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "Product",
      "name": "Compresor Monofásico Gamma 50L G2802AR",
      "mpn": "G2802AR",
      "sku": "BULO-11048",
      "offers": {
        "@type": "Offer",
        "priceCurrency": "ARS",
        "price": 315000.00,
        "availability": "https://schema.org/OutOfStock"
      }
    }
    </script>
</head>
<body>
    <h1>Compresor Monofásico Gamma 50L G2802AR</h1>
    <span class="sin-stock">Artículo temporalmente sin stock</span>
</body>
</html>"""

# 5. Discrepancia de variante: es un repuesto o manguera y no el equipo
FIXTURE_HTML_VARIANT_MISMATCH = """<!DOCTYPE html>
<html lang="es">
<head>
    <title>Manguera de repuesto para Kärcher K2 | Bulonera Central</title>
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "Product",
      "name": "Manguera de repuesto para Kärcher K2 4 metros",
      "mpn": "REP-MANG-K2",
      "sku": "BULO-REP-01",
      "offers": {
        "@type": "Offer",
        "priceCurrency": "ARS",
        "price": 28000.00,
        "availability": "https://schema.org/InStock"
      }
    }
    </script>
</head>
<body>
    <h1>Manguera de repuesto para Kärcher K2 4 metros</h1>
</body>
</html>"""

# 6. Salto extraordinario anómalo (ej. precio irrisorio por error de tipeo)
FIXTURE_HTML_PRICE_JUMP = """<!DOCTYPE html>
<html lang="es">
<head>
    <title>Compresor de Aire Lüsqtoff 50 Litros LC2550B-8 | Tienda</title>
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "Product",
      "name": "Compresor de Aire Lüsqtoff 50 Litros LC2550B-8",
      "mpn": "LC2550B-8",
      "offers": {
        "@type": "Offer",
        "priceCurrency": "ARS",
        "price": 28990.00,
        "availability": "https://schema.org/InStock"
      }
    }
    </script>
</head>
<body>
    <h1>Compresor de Aire Lüsqtoff 50 Litros LC2550B-8</h1>
</body>
</html>"""

# 7. Precio ausente o nulo (no debe inferirse como 0)
FIXTURE_HTML_MISSING_PRICE = """<!DOCTYPE html>
<html lang="es">
<head>
    <title>Compresor de Aire Lüsqtoff 50 Litros LC2550B-8</title>
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "Product",
      "name": "Compresor de Aire Lüsqtoff 50 Litros LC2550B-8",
      "mpn": "LC2550B-8",
      "offers": {
        "@type": "Offer",
        "priceCurrency": "ARS"
      }
    }
    </script>
</head>
<body>
    <h1>Compresor de Aire Lüsqtoff 50 Litros LC2550B-8</h1>
    <p>Consultar precio con un asesor comercial</p>
</body>
</html>"""

# 8. Moneda inesperada (ej. USD)
FIXTURE_HTML_NON_ARS_CURRENCY = """<!DOCTYPE html>
<html lang="es">
<head>
    <title>Generador Honda EU22i Inverter</title>
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "Product",
      "name": "Generador Honda EU22i",
      "mpn": "EU22i",
      "offers": {
        "@type": "Offer",
        "priceCurrency": "USD",
        "price": 1850.00,
        "availability": "https://schema.org/InStock"
      }
    }
    </script>
</head>
<body>
    <h1>Generador Honda EU22i</h1>
    <span>U$S 1.850,00</span>
</body>
</html>"""
