"""Revisión documental manual del primer lote de diez guías de sierras."""
from pathlib import Path
import re

ROOT = Path(__file__).parent / "paginas" / "sierras"
PAGES = {
"24-stanley-sc16.md": ("SC16-AR: ficha y medida de disco", "La denominación comercial 7-1/4 pulgadas aparece junto con 180 mm en la ficha argentina. El manual que incluye la variante -AR indica un diámetro máximo distinto; documentamos la discrepancia antes de recomendar un repuesto.", """| Dato documentado | SC16-AR | Fuente |
| :--- | :--- | :--- |
| Potencia anunciada | 1.600 W | Ficha Stanley Argentina |
| Diámetro anunciado | 180 mm | Ficha Stanley Argentina |
| Diámetro máximo en manual | 190 mm | Manual Stanley SC16, tabla de variantes |
| Orificio en manual | 16 mm | Manual Stanley SC16 |
| Profundidad máxima a 90° / 45° en manual | 65 / 50 mm | Manual Stanley SC16 |
| Alimentación | Con cable | Ficha Stanley Argentina |
| Garantía publicada | 2 años limitada | Ficha Stanley Argentina |

**Análisis TallerLab.** La ficha dice «7-1/4 pulgadas» y «180 mm» en el mismo título. Como 7,25 × 25,4 = 184,15 mm, hay una diferencia de unos 4 mm entre ambas expresiones. El manual compartido de SC16, que incluye -AR en la tabla, permite hasta 190 mm y señala eje de 16 mm. Los documentos no explican por qué la página comercial ofrece 180 mm. Antes de instalar otro tamaño, confirmá la placa y el manual que acompañan la unidad concreta.

**Desconocido.** No verificamos qué disco viene dentro de cada caja ni el rendimiento de corte. La ficha comercial no da profundidad; la cifra de la tabla proviene del manual y debe contrastarse con la revisión de la unidad ofrecida.

Para comparar capacidades documentadas, mirá la [Bosch GKS 150](/sierras/bosch-gks-150/) y la [DeWalt DWE560](/sierras/sierra-circular-dewalt-dwe560/). La potencia anunciada por sí sola no prueba calidad de corte.

## Fuentes consultadas

- **Documentación primaria:** [ficha Stanley SC16-AR](https://ar.stanleytools.global/producto/sc16-ar/sierra-circular-7-14-pulg-180mm-1600w); [manual Stanley SC16 con variante -AR](https://www.toolservicenet.com/i/STANLEY/GLOBALBOM/B3/SC16D2/1/Instruction_Manual/EN/N611276_SC16_T1_LAG.pdf).
- **Información comercial:** no se utilizó para validar prestaciones.
- **Opiniones:** no se revisó una muestra verificable.
"""),
"23-sierra-circular-dewalt-dwe560.md": ("DWE560-AR: prestaciones publicadas", "La variante argentina tiene datos suficientes para verificar potencia, disco y bisel; la profundidad de corte requiere documentación adicional.", """| Dato documentado | DWE560-AR |
| :--- | :--- |
| Potencia | 1.400 W |
| Disco anunciado | 185 mm |
| Bisel máximo | 48°; topes a 22,5° y 45° |
| Motor | Con carbones |
| Alimentación en manual | 220 V, 50 Hz |
| Velocidad en vacío en manual | 5.500 rpm |
| Incluye según ficha | Llave de ajuste y disco de 24 dientes |

**Análisis TallerLab.** La DWE560-AR anuncia 185 mm de disco y la [Stanley SC16-AR](/sierras/stanley-sc16/) 180 mm. Esa diferencia nominal es de 5 mm; no autoriza a intercambiar hojas. Comprobá diámetro permitido, eje y velocidad admisible en cada herramienta y disco.

**Declaración del fabricante.** DeWalt describe la guarda y la zapata de 3 mm como elementos de diseño. TallerLab no verificó físicamente que eviten atascos o aumenten la durabilidad.

**Desconocido.** La ficha y la tabla técnica del manual consultados no publican profundidad máxima a 90° o 45° ni peso. No inferimos esos valores de otra variante DWE560. Para trabajo con guía, verificá compatibilidad de la base antes de comprar el accesorio.

## Fuentes consultadas

- **Documentación primaria:** [ficha DeWalt DWE560-AR](https://www.dewalt.com.ar/es-ar/producto/dwe560-ar/sierra-circular-electrica-de-7-14-pulg-185mm); [manual DeWalt DWE560-AR](https://www.toolservicenet.com/i/DEWALT/GLOBALBOM/AR/DWE560/1/Instruction_Manual/EN/N141338_DWE560.pdf).
- **Información comercial:** no se usó como fuente técnica.
- **Opiniones:** no se revisó una muestra verificable.
"""),
"16-sierra-circular-bosch-gks-150.md": ("GKS 150: ficha, manual y límite de corte", "Contrastamos ficha argentina y manual del código 0 601 6B3 0H0. La capacidad del manual se refiere al disco de 184 mm indicado.", """| Dato documentado | GKS 150 |
| :--- | :--- |
| Potencia absorbida | 1.500 W |
| Disco / eje | 184 mm / 20 mm |
| Velocidad en vacío | 6.000 rpm |
| Peso | 3,7 kg |
| Profundidad máxima a 90° | 64 mm con disco de 184 mm |
| Compatible con carril guía Bosch | La ficha indica que no |

**Análisis TallerLab.** El dato de 64 mm responde a una condición concreta del manual: disco de 184 mm y corte perpendicular. Si tu pieza supera ese espesor, la potencia de 1.500 W no cambia el límite geométrico. El orificio de 20 mm también debe coincidir con el repuesto.

**Declaración del fabricante.** Bosch lista guía paralela, llave y disco de 24 dientes en la variante argentina. Confirmá el contenido del kit al comprar. La ausencia de compatibilidad con carril guía en la ficha no impide usar una regla externa, pero exige comprobar el apoyo de la base.

**Desconocido.** No se midió precisión, limpieza de canto ni duración de disco. Esos resultados dependen de hoja, material y ajuste. Compará con la [DWE560](/sierras/sierra-circular-dewalt-dwe560/) solo usando prestaciones publicadas para cada código.

## Fuentes consultadas

- **Documentación primaria:** [ficha Bosch GKS 150 Argentina](https://www.bosch-professional.com/ar/es/products/gks-150-06016B30H0); [manual Bosch GKS 150](https://www.bosch-professional.com/binary/manualsmedia/o406577v21_160992A8F5_202212.pdf).
- **Opiniones:** no se revisó una muestra verificable.
"""),
"22-caladoras-bosch.md": ("Tres códigos Bosch que conviene separar", "Comparamos fichas argentinas de GST 650, GST 680 y GST 185-LI. Una publicación de GST 75 E no debe usarse para completar los datos de estas variantes.", """| Dato documentado | GST 650 | GST 680 | GST 185-LI |
| :--- | :--- | :--- | :--- |
| Alimentación | Cable | Cable | Batería 18 V |
| Potencia absorbida declarada | 450 W | 500 W | No comparable en W de red |
| Carrera | 18 mm | 20 mm | Consultar ficha de variante |
| Peso publicado | 1,9 kg | 2,07 kg | Consultar ficha de variante |

**Análisis TallerLab.** Entre las dos máquinas con cable hay 50 W y 2 mm de diferencia en los valores publicados. Eso no demuestra una mejora visible en cada material: elección de hoja, velocidad y soporte de la pieza también intervienen. La GST 185-LI responde a otra decisión: acceso a una plataforma de baterías de 18 V. Su ficha argentina muestra una variante en caja con una hoja; no asumimos que incluya batería y cargador.

**Declaración del fabricante.** Bosch atribuye a la GST 680 una rueda de preselección de velocidad y protección contra astillas en el kit indicado. Es una prestación declarada, no una medición de calidad de corte de TallerLab.

**Desconocido.** No se cotejó la GST 75 E de la descripción histórica con una ficha argentina vigente. Confirmá código de pedido, contenido y garantía antes de aplicar la comparación a una oferta.

## Fuentes consultadas

- **Documentación primaria:** [Bosch GST 650](https://www.bosch-professional.com/ar/es/products/gst-650-06015A80H0); [Bosch GST 680](https://www.bosch-professional.com/ar/es/products/gst-680-06015B40H0); [Bosch GST 185-LI](https://www.bosch-professional.com/ar/es/products/gst-185-li-06015B30E1).
- **Opiniones:** no se revisó una muestra verificable.
"""),
"26-sierra-de-banco-lusqtoff.md": ("Tres códigos de banco y una discrepancia documental", "Las fichas actuales y un catálogo de Lüsqtoff no expresan de igual modo la potencia y el disco de SML2000-8. Registramos la diferencia sin resolverla por suposición. **Dato documentado** significa aquí que la cifra aparece en el documento citado, no que haya sido medida por TallerLab.", """| Dato publicado | SML2000-8 | SML2000-9 | SML2000B-9 |
| :--- | :--- | :--- | :--- |
| Potencia anunciada en ficha | 2.000 W | 1.800 W de entrada; 2.000 W máx. S6 | 2.000 W máx. |
| Diámetro en ficha | 255 mm | 255 mm | 255 mm |
| Corte a 90° | 85 mm | 85 mm | 85 mm |
| Peso publicado | 21,5 kg | 23 kg | 19,6 kg |

**Análisis TallerLab.** El catálogo 2024–2025 describe la SML2000-8 con 1.800 W de entrada y 2.000 W máximos S6 25 %, además de disco de 250 mm, mientras la ficha web anuncia 2.000 W y 255 mm. Son documentos del mismo fabricante con cifras distintas. Una diferencia de 5 mm en el disco afecta la compra de repuestos: pedí foto de la placa, manual y disco de la unidad ofrecida.

La SML2000-9 publica 60 mm a 45°; la SML2000B-9, 55 mm. Si hacés cortes inclinados en madera gruesa, esa diferencia publicada de 5 mm importa más que comparar solo el nombre comercial.

**Desconocido.** No probamos estabilidad de mesa, precisión de guía ni duración. Tampoco afirmamos que las potencias con distinta condición S6 sean directamente comparables.

## Fuentes consultadas

- **Documentación primaria:** [SML2000-8](https://lusqtoff.com.ar/ver-producto/SML2000-8); [SML2000-9](https://lusqtoff.com.ar/ver-producto/SML2000-9); [SML2000B-9](https://lusqtoff.com.ar/ver-producto/SML2000B-9); [catálogo Lüsqtoff 2024–2025](https://www.lusqtoff.com.ar/2023/uploads/Catalogos/CAT%C3%81LOGO%20LQ%202024-2025%20-%20web%20%281%29.pdf).
- **Opiniones:** no se revisó una muestra verificable.
"""),
"28-sierra-sin-fin-lusqtoff.md": ("SFL250-8, SFL300-8 y SFL1100-9: qué está documentado", "El catálogo menciona tres escalas; la documentación pública consultada permite comparar con detalle dos códigos. El tercero queda deliberadamente incompleto.", """| Dato documentado | SFL250-8 | SFL300-8 | SFL1100-9 |
| :--- | :--- | :--- | :--- |
| Estado en catálogo/ficha | Discontinuada | Listada como banco 200 mm | Ficha activa |
| Potencia | 250 W | Sin ficha detallada cotejada | 1.100 W |
| Altura máxima de corte | 80 mm | Desconocida | 206 mm |
| Garganta | 200 mm | Desconocida | 305 mm |
| Peso | 16,5 kg | Desconocido | 84 kg |

**Análisis TallerLab.** Entre los dos modelos con ficha detallada, la altura publicada difiere 126 mm y el peso 67,5 kg. Eso separa una máquina compacta de una instalación de taller; no dice cuál corta con mayor precisión. La SFL300-8 aparece en el catálogo de la marca, pero «200 mm» en el nombre comercial no demuestra una altura de corte de 200 mm.

**Declaración del fabricante.** La ficha SFL1100-9 anuncia cinta de 2.360 mm, mesa de 548 × 400 mm y garantía de tres años. Verificá tensión, espacio y repuestos con el vendedor.

**Desconocido.** No se confirmó una ficha técnica detallada de SFL300-8 ni se probaron las tres. No trasladamos medidas de una variante a otra.

## Fuentes consultadas

- **Documentación primaria:** [SFL250-8](https://www.lusqtoff.com.ar/ver-producto/SFL250-8); [catálogo de herramientas de pie y banco](https://lusqtoff.com.ar/categorias/herramientas-de-pie-y-banco); [SFL1100-9](https://lusqtoff.com.ar/ver-producto/SFL1100-9).
- **Opiniones:** no se revisó una muestra verificable.
"""),
"27-sensitiva-lusqtoff.md": ("CM-14K: código, capacidad y contenido de caja", "Separamos CM-14K de la variante CM14K-9 y de catálogos antiguos porque las potencias y accesorios publicados difieren.", """| Dato documentado | CM-14K actual | CM14K-9 |
| :--- | :--- | :--- |
| Potencia anunciada | 2.000 W | 2.200 W |
| Disco | 355 mm | Verificar ficha y unidad |
| Velocidad en vacío | 3.800 rpm | Verificar ficha |
| Estado de ficha | Publicada | Discontinuada |
| Disco incluido | 1 según ficha actual | Confirmar contenido |

**Análisis TallerLab.** Una oferta que combina el código CM-14K con 2.200 W puede mezclar datos de CM14K-9. Además, un catálogo anterior informa otro peso y más accesorios que la ficha actual de CM-14K. Para presupuestar discos y traslado, solicitá foto de la placa y del contenido de caja de la unidad concreta.

**Declaración del fabricante.** Lüsqtoff publica para CM-14K capacidad de tubo redondo de 110 mm y perfil cuadrado de 100 × 100 mm. Son capacidades declaradas para geometrías específicas; no equivalen al máximo en cualquier material o posición.

**Desconocido.** No se midió velocidad de corte, escuadra real ni duración del disco. Leé el [manual CM-14K](https://www.lusqtoff.com.ar/2023/uploads/Productos/12.%20HERRAMIENTAS%20DE%20PIE%20Y%20BANCO/CM-14K/MANUAL/CM-14k.pdf) y respetá el tipo de disco y su velocidad permitida.

## Fuentes consultadas

- **Documentación primaria:** [CM-14K](https://www.lusqtoff.com.ar/ver-producto/CM-14K); [CM14K-9](https://www.lusqtoff.com.ar/ver-producto/CM14K-9); [catálogo histórico Lüsqtoff](https://lusqtoff.com.ar/files/Catalogo_Lusqtoff_2020.pdf); [manual CM-14K](https://www.lusqtoff.com.ar/2023/uploads/Productos/12.%20HERRAMIENTAS%20DE%20PIE%20Y%20BANCO/CM-14K/MANUAL/CM-14k.pdf).
- **Opiniones:** no se revisó una muestra verificable.
"""),
"08-ingletadora-einhell.md": ("Dos modelos Einhell con capacidades publicadas", "Comparamos códigos argentinos exactos TC-MS 2112 y TC-SM 2131/2 Dual. La variante TC-SM no es la TE-SM 2131 Dual de la descripción histórica; son productos distintos.", """| Dato documentado | TC-MS 2112 (4300295) | TC-SM 2131/2 Dual (4300390) |
| :--- | :--- | :--- |
| Mecanismo | Fijo | Deslizante |
| Disco | 210 mm | 210 mm |
| Ancho a 90° | 120 mm | 310 mm |
| Ancho a 45° | 80 mm | 210 mm |
| Profundidad a 90° | 55 mm | 62 mm |
| Peso | 7,1 kg | 11 kg |
| Potencia publicada | 1.600 W S6 40 % | 1.500 W S1 / 1.800 W S2 |

**Análisis TallerLab.** La deslizante admite, según ficha, 190 mm más de ancho a 90° y 130 mm más a 45°. Pesa 3,9 kg más. Si tus piezas no superan 120 mm a 90°, esa mayor capacidad puede no justificar espacio y costo. Los watts no se comparan sin atender a S1, S2 y S6: son condiciones de servicio diferentes.

**Declaración del fabricante.** Einhell anuncia inclinación a ambos lados en la TC-SM 2131/2 Dual; la TC-MS 2112 inclina hacia la izquierda. Confirmá el código 4300390 en la oferta, ya que el nombre TE-SM 2131 Dual refiere a otra variante.

**Desconocido.** No probamos exactitud de ángulos, aspiración ni calidad del disco incluido.

## Fuentes consultadas

- **Documentación primaria:** [TC-MS 2112](https://www.einhell.com.ar/p/4300295-tc-ms-2112/); [TC-SM 2131/2 Dual](https://www.einhell.com.ar/p/4300390-tc-sm-2131-2-dual/).
- **Opiniones:** no se revisó una muestra verificable.
"""),
"12-sensitiva-dewalt.md": ("D28730: identificar la variante argentina", "El manual latinoamericano distingue D28730AR de otras versiones de tensión. Una oferta de D28730-B3 no basta para asegurar alimentación compatible en Argentina.", """| Dato documentado en manual | D28730AR |
| :--- | :--- |
| Tensión / frecuencia | 220 V / 50 Hz |
| Potencia | 2.300 W |
| Velocidad en vacío | 4.200 rpm |
| Disco | 355 mm |
| Peso | 16 kg |

**Análisis TallerLab.** El código final importa: la ficha mexicana D28730-B3 y el manual D28730AR no son la misma identificación comercial. Verificá foto de la placa, enchufe y garantía local. El disco también debe admitir por lo menos la velocidad indicada para la máquina; 355 mm de diámetro no alcanza para decidir compatibilidad.

**Declaración del fabricante.** DeWalt describe morsa de liberación rápida y guía pivotante a 45° para la familia D28730. No medimos capacidad efectiva en perfiles ni estabilidad del conjunto.

**Desconocido.** No se verificaron accesorios incluidos en una oferta argentina concreta. Tampoco se comparó rendimiento real con la [CM-14K de Lüsqtoff](/sierras/sensitivas-lusqtoff/).

## Fuentes consultadas

- **Documentación primaria:** [manual D28730 para Latinoamérica](https://assets.dewalt.com.mx/GLOBALBOM/B3/D28730/1/Instruction_Manual/EN/NB075052_D28730_T1_LA.pdf); [ficha DeWalt D28730-B3, variante distinta](https://www.dewalt.com.mx/es-mx/producto/d28730-b3/cortadora-de-metal-de-14-355mm-con-cable).
- **Opiniones:** no se revisó una muestra verificable.
"""),
"21-ingletadoras.md": ("Elegir por sección de pieza, no solo por disco", "La capacidad publicada de dos máquinas Einhell con disco de 210 mm muestra cuánto cambia el ancho útil al incorporar un carro deslizante. **Dato documentado:** las capacidades de la tabla proceden de las dos fichas oficiales enlazadas.", """| Ancho de pieza que necesitás cortar a 90° | Dato documental | Decisión que permite |
| :--- | :--- | :--- |
| Hasta 120 mm | TC-MS 2112: 120 mm | Ambas entran por capacidad publicada |
| Más de 120 y hasta 310 mm | TC-SM 2131/2 Dual: 310 mm | De estas dos, solo la deslizante cubre ese ancho |
| Más de 310 mm | Ninguna de las dos lo documenta | Buscar otra máquina o método |

**Análisis TallerLab.** Las dos usan disco de 210 mm, pero sus anchos a 90° difieren 190 mm. El diámetro del disco por sí solo no predice ancho de corte. A 45°, la fija declara 80 mm y la deslizante 210 mm; medí la sección en la orientación real del trabajo. La profundidad a 90° es 55 y 62 mm, respectivamente: ancho y altura se deben comprobar por separado.

**Declaración del fabricante.** Einhell publica 7,1 kg para la fija y 11 kg para la deslizante. Usá esas cifras si la vas a trasladar; no inferimos estabilidad o precisión por peso.

**Desconocido.** No medimos espacio trasero con los carros extendidos ni exactitud de cortes. Antes de comprar, pedí dimensiones de instalación, sujeción de pieza, disco adecuado al material y tensión de la variante. Para los códigos exactos, consultá la [comparación Einhell](/sierras/ingletadoras-einhell/).

## Fuentes consultadas

- **Documentación primaria:** [Einhell TC-MS 2112](https://www.einhell.com.ar/p/4300295-tc-ms-2112/); [Einhell TC-SM 2131/2 Dual](https://www.einhell.com.ar/p/4300390-tc-sm-2131-2-dual/).
- **Opiniones:** no se revisó una muestra verificable.
"""),
}

DESCRIPTIONS = {
    "16-sierra-circular-bosch-gks-150.md": "Ficha y manual de la Bosch GKS 150: potencia, disco, eje, corte a 90 grados y compatibilidad con guías.",
    "08-ingletadora-einhell.md": "Comparación documental de Einhell TC-MS 2112 y TC-SM 2131/2 Dual: ancho y profundidad de corte, peso y potencia según ciclo.",
}

for filename, (section, lead, content) in PAGES.items():
    path = ROOT / filename
    original = path.read_text(encoding="utf-8")
    match = re.match(r"---\n(.*?)\n---\n", original, flags=re.S)
    if not match:
        raise RuntimeError(f"Missing front matter: {path}")
    front = match.group(1)
    if filename in DESCRIPTIONS:
        front = re.sub(r'^description:.*$', lambda _: f'description: "{DESCRIPTIONS[filename]}"', front, flags=re.M)
    h1 = re.search(r'^h1: "(.+)"$', front, re.M).group(1)
    fields = {
        "research_type": "documental", "physical_test": "no",
        "specifications_contrasted": "sí", "buyer_opinions": "no",
        "primary_sources": "sí", "information_asset": section,
        "asset_status": "verificado", "reviewed": "27/09/2026", "published": "true",
    }
    for key, value in fields.items():
        line = f'{key}: "{value}"' if key != "published" else "published: true"
        if re.search(rf'^{key}:.*$', front, re.M):
            front = re.sub(rf'^{key}:.*$', lambda _: line, front, flags=re.M)
        else:
            front += "\n" + line
    body = f"# {h1}\n\n{lead}\n\n## {section}\n\n{content.strip()}\n\n[Ver todas las guías de sierras](/sierras/).\n"
    path.write_text(f"---\n{front}\n---\n\n{body}", encoding="utf-8")
print(f"Revisadas {len(PAGES)} páginas")
