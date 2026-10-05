"""Comparaciones editoriales seleccionadas por utilidad y demanda técnica real."""

from typing import Any, Dict, List, Optional
from tallerlab_data.comparator import compare_tools
from tallerlab_data.storage import get_tool

EDITORIAL_COMPARISONS = {
    "lusqtoff-lc2550b-vs-gamma-g2802ar": {
        "slug": "lusqtoff-lc2550b-vs-gamma-g2802ar",
        "title": "Lüsqtoff LC2550B-8 vs Gamma G2802AR: comparativa de 50 litros",
        "h1": "Lüsqtoff LC2550B-8 frente a Gamma G2802AR: qué revelan sus fichas",
        "description": "Comparativa técnica entre los dos compresores de 50 litros más populares de Argentina: potencia documentada, discrepancias de catálogo y caudal.",
        "category": "compresores",
        "tool_slugs": ["lusqtoff-lc2550b-8", "gamma-g2802ar"],
        "editorial_analysis": """
### Contexto de Decisión y Análisis Técnico

Tanto el **Lüsqtoff LC2550B-8** como el **Gamma G2802AR** dominan el segmento de compresores de 50 litros lubricados por aceite en talleres particulares y mantenimiento ligero en Argentina. Ambos equipos comparten arquitectura horizontal con ruedas y corte de presostato a 8 bar (115–116 PSI).

#### 1. Potencia documentada y discrepancia de fábrica
- En el **Lüsqtoff LC2550B-8**, la ficha técnica oficial declara uniformemente **2,5 HP (1.750 W)**.
- En el **Gamma G2802AR**, la auditoría documental de TallerLab identificó una **contradicción no resuelta**: el manual de servicio oficial de fábrica declara **2,5 HP (1,85 kW)** en su tabla de especificaciones (pág. 2), mientras que la web oficial de Gamma Herramientas publica **2,0 HP (1,5 kW)**. TallerLab no asume cuál es el dato verdadero: ambos constan en la ficha y se recomienda verificar la placa metálica de la unidad adquirida.

#### 2. Caudales teóricos y entrega de aire bajo presión
- Lüsqtoff publica **206 L/min** de flujo declarado, sin indicar la entrega de aire libre (FAD) a 4 o 7 bar.
- Gamma declara **203 L/min** de desplazamiento volumétrico teórico en el manual (cálculo de cilindrada por rpm sin pérdidas volumétricas ni térmicas).
- **Límite de comparación:** Ninguno de los dos fabricantes suministra en su folleto público la curva FAD calibrada bajo norma ISO 1217. Por tanto, no es técnicamente válido asegurar que uno infle más rápido que el otro basándose únicamente en la diferencia de 3 L/min declarada.

#### 3. Recomendación de selección técnica
Ambos equipos entregan una reserva de 50 L adecuada para inflado, soplado por intervalos y clavadoras neumáticas. En términos de instalación, los motores de inducción de 2,0 a 2,5 HP presentan picos transitorios de arranque que multiplican sensiblemente la corriente nominal, en particular al arrancar contra contrapresión residual en el cabezal. Por ello, se recomienda alimentar el equipo desde una línea eléctrica debidamente dimensionada (conductores de sección adecuada, baja caída de tensión y protección termomagnética con curva de disparo apta para motores según reglamentación AEA 90364), evitando compartir el circuito o recurrir a prolongadores de sección insuficiente. Si requerís pintar piezas completas o arenar de forma continua, el factor limitante será la tasa de reposición volumétrica de la bomba y no la capacidad geométrica del tanque.
""",
    },
    "einhell-te-ac-270-50-vs-lusqtoff-lc2550b": {
        "slug": "einhell-te-ac-270-50-vs-lusqtoff-lc2550b",
        "title": "Einhell TE-AC 270/50 Silent vs Lüsqtoff LC2550B-8: silencioso o tradicional",
        "h1": "Einhell Silent 50L frente a Lüsqtoff 50L: ruido, aceite y entrega real a 7 bar",
        "description": "Comparativa entre un compresor libre de aceite de bajo nivel sonoro (70 dB(A) LpA) con entrega calibrada (Einhell) y un equipo tradicional lubricado de 2,5 HP (Lüsqtoff).",
        "category": "compresores",
        "tool_slugs": ["einhell-te-ac-270-50-silent", "lusqtoff-lc2550b-8"],
        "editorial_analysis": """
### Ruido acústico frente a caudal de recuperación

Esta comparación enfrenta dos filosofías de diseño para un mismo volumen de 50 litros:

#### 1. Nivel sonoro y ambiente de trabajo
- **Einhell TE-AC 270/50 Silent:** La ficha técnica oficial de Einhell Argentina declara **70 dB(A) LpA** (nivel de presión acústica normalizado). Folletos comerciales previos citaban 65 dB(A) medidos a 7 metros de distancia. Su doble cabezal de bajas revoluciones (1.450 rpm) libre de aceite reduce notablemente la emisión sonora frente a modelos de 2.850 rpm, facilitando su integración en garajes o talleres urbanos. No obstante, la exigencia de protectores auditivos debe regirse por la dosis acústica y la acústica del local conforme a la normativa laboral (Res. SRT 295/03).
- **Lüsqtoff LC2550B-8:** Equipo lubricado convencional cuyo nivel sonoro típico supera los 85 dB en marcha; exige aislamiento acústico o trabajar con protectores en recintos cerrados.

#### 2. La brecha de información de caudal útil
- Einhell es uno de los pocos fabricantes en el mercado argentino que explicita su entrega de aire a presiones de trabajo: **135 L/min a 4 bar** y **98 L/min a 7 bar**.
- Lüsqtoff publica **206 L/min** aspirados sin presión de referencia. Al someter a compresión contra 7 bar, las pérdidas volumétricas reducen el caudal efectivo en equipos de este porte. La cifra mayor de Lüsqtoff no acredita necesariamente mayor volumen útil a 7 bar.

#### 3. Mantenimiento y aire limpio
- Einhell opera sin aceite: el aire no contiene vapores oleosos, ideal para pintura al agua, barnizado y aerografía. No requiere cambios de aceite periódicos.
- Lüsqtoff requiere control de nivel de aceite y recambios periódicos (10W40 o SAE30 según estación), pero sus componentes mecánicos bañados en aceite disipan mejor el calor en usos continuados.
""",
    },
    "karcher-k4-vs-bosch-ghp-220": {
        "slug": "karcher-k4-vs-bosch-ghp-220",
        "title": "Kärcher K4 Power Control vs Bosch GHP 220: comparativa de hidrolavadoras",
        "h1": "Kärcher K4 Power Control frente a Bosch GHP 220: motor, presión y caudal",
        "description": "Contraste técnico entre la hidrolavadora residencial de inducción Kärcher K4 y la máquina profesional compacta Bosch GHP 220.",
        "category": "hidrolavadoras",
        "tool_slugs": ["karcher-k4-power-control", "bosch-ghp-220"],
        "editorial_analysis": """
### Residencial avanzada frente a profesional de inducción

#### 1. Presión de trabajo frente a presión de corte
- **Bosch GHP 220:** Declara en su manual oficial (pág. 14) **101,2 bar de presión de trabajo sostenida** y **151,8 bar de presión máxima** en la válvula de alivio.
- **Kärcher K4 Power Control:** Declara una presión de **20 a 130 bar** ajustables en la lanza Vario Power.
- **Condición técnica:** Los 151,8 bar máximos de Bosch no deben contrastarse con los 130 bar de Kärcher para declarar una ganadora: la presión que efectivamente lava la superficie en la boquilla es la de trabajo continuo (101 bar en Bosch).

#### 2. Caudal de agua y poder de arrastre
- Bosch GHP 220 entrega **6,1 L/min nominales (366 L/h)** continuos y 7,4 L/min máximos.
- Kärcher K4 entrega hasta **420 L/h (7,0 L/min)** máximos.
- La velocidad de limpieza en pisos y terrazas depende fuertemente del caudal: un equipo con más de 400 L/h remueve barro y verdín mucho más rápido que uno con alta presión pero escaso caudal.

#### 3. Construcción del motor y manguera
- Kärcher K4 incorpora motor refrigerado por agua (WCM), lo que extiende su ciclo útil antes de cortes térmicos. Su manguera es de 8 metros.
- Bosch GHP 220 utiliza motor de inducción tradicional con bomba metálica y manguera de PVC reforzado de 8 metros, orientada a exigencia continua en talleres y lavaderos.
""",
    },
    "dewalt-dch273-vs-bosch-gbh-180-li": {
        "slug": "dewalt-dch273-vs-bosch-gbh-180-li",
        "title": "DeWalt DCH273 vs Bosch GBH 180-LI: rotomartillos SDS Plus a batería",
        "h1": "DeWalt DCH273 frente a Bosch GBH 180-LI: energía EPTA, vibración y plataformas",
        "description": "Comparativa de rotomartillos inalámbricos SDS Plus de 18V y 20V: energía de impacto, amortiguación y costo por perforación.",
        "category": "taladros",
        "tool_slugs": ["dewalt-dch273", "bosch-gbh-180-li"],
        "editorial_analysis": """
### Electroneumáticos sin cable para hormigón y anclajes

#### 1. Energía de impacto estandarizada EPTA
- Ambos fabricantes miden bajo la norma internacional **EPTA 05/2016**:
  - **DeWalt DCH273:** **2,1 Joules**.
  - **Bosch GBH 180-LI:** **2,0 Joules**.
- La diferencia de 0,1 J es despreciable en obra diaria para brocas de 6 a 12 mm en mampostería y hormigón estándar.

#### 2. Control de vibraciones (SHOCKS)
- El DeWalt DCH273 incorpora empuñadura flotante desacoplada mecánicamente con tecnología SHOCKS, reduciendo significativamente la fatiga en jornadas de perforación intensiva en techos o vigas.
- El Bosch GBH 180-LI utiliza un formato en línea tradicional más rígido, pero es significativamente más económico de adquirir en kits con dos baterías de 4.0 Ah en el mercado argentino.

#### 3. Compatibilidad de plataforma
- La decisión clave entre estos dos modelos reside en tu ecosistema previo de herramientas: si ya contás con cargadores y baterías DeWalt 20V MAX o Bosch Professional 18V, la adquisición del cuerpo solo ('Bare tool') amortiza la inversión sin duplicar cargadores.
""",
    },
    "esab-handyarc-162i-vs-lusqtoff-sml120-8dk": {
        "slug": "esab-handyarc-162i-vs-lusqtoff-sml120-8dk",
        "title": "ESAB HandyArc 162i vs Lüsqtoff SML120-8DK: electrodo o alambre flux",
        "h1": "ESAB HandyArc 162i frente a Lüsqtoff SML120-8DK: proceso MMA o MIG sin gas",
        "description": "Comparación técnica entre una inverter MMA para electrodos de 3,25 mm y una máquina multiproceso con alambre tubular flux.",
        "category": "soldadoras",
        "tool_slugs": ["esab-handyarc-162i", "lusqtoff-sml120-8dk"],
        "editorial_analysis": """
### Dos procesos de unión para aplicaciones distintas

#### 1. Proceso de soldadura y espesor de material
- **ESAB HandyArc 162i (MMA):** Fuente inverter dedicada para electrodos revestidos (E6013, E7018). Entrega hasta 160 A al 20% y 72 A continuo al 100%. Excelente para perfiles de hierro de 2 mm a 8 mm de espesor, trabajos al aire libre con viento y reparaciones de rejas o maquinaria.
- **Lüsqtoff SML120-8DK (MIG Flux):** Fuente multiproceso optimizada para alambre tubular sin gas (FLUX) de 0,8 mm. Entrega hasta 120 A en FLUX y 100 A en MMA. Ideal para chapa fina de 0,9 mm a 2 mm (chasis, carrocería, muebles metálicos) donde el electrodo revestido perfora con facilidad.

#### 2. Alimentación eléctrica y advertencia de ficha
- La ficha de ESAB especifica claramente 220 V / 50–60 Hz con compatibilidad para generadores.
- La ficha web de Lüsqtoff SML120-8DK registra una discrepancia documental imprimiendo '200 V - 50 Hz'. TallerLab conserva esta advertencia para que el comprador corrobore la placa de la máquina física recibida.

#### 3. Costo operativo de consumibles
- El electrodo revestido es económico y fácil de almacenar.
- El rollo de alambre flux es más costoso por kilogramo depositado y genera escoria que debe ser removida, aunque permite una velocidad de avance mayor en cordones continuos sobre chapa delgada.
""",
    },
    "honda-eu22i-vs-gamma-inverter-2kw": {
        "slug": "honda-eu22i-vs-gamma-inverter-2kw",
        "title": "Honda EU22i vs Gamma Inverter 2 kW: generadores inverter portátiles",
        "h1": "Honda EU22i frente a Gamma G2301AR: onda senoidal, autonomía y respaldo",
        "description": "Comparativa entre el estándar industrial Honda EU22i y la alternativa nacional Gamma Inverter de 2 kW.",
        "category": "generadores",
        "tool_slugs": ["honda-eu22i", "gamma-inverter-2kw"],
        "editorial_analysis": """
### Tecnología inverter para electrónica sensible y emergencias

#### 1. Potencia nominal continua
- **Honda EU22i:** Declara **1,8 kVA (1.800 W)** continuos y 2,2 kVA (2.200 W) de pico con motor Honda GXR120 comercial.
- **Gamma G2301AR:** Declara **2,0 kW (2.000 W)** continuos y 2,2 kW de pico.
- Ambos equipos entregan onda senoidal mediante puente inversor electrónico con distorsión armónica total reducida (THD típica inferior al 3%), lo que brinda tensión y frecuencia estables aptas para electrónica sensible como computadoras, calderas con control digital y electrodomésticos con placas inverter. (Para equipamiento de electromedicina o soporte vital deben consultarse siempre los requerimientos de aislamiento y certificación hospitalaria exigidos por el fabricante del instrumental).

#### 2. Insonorización y peso
- Honda pesa 21,1 kg en seco con una carcasa insonorizada de doble pared que reduce el ruido a rangos de 53–59 dB(A) con sistema Eco-Throttle.
- Gamma pesa 17,0 kg, siendo más ligero de transportar individualmente, aunque su aislamiento acústico es más básico bajo cargas exigentes.

#### 3. Relación de costo y disponibilidad de repuestos
- El generador Honda representa una inversión de grado profesional, con despieces completos garantizados por la red Honda Power Equipment en todo el país.
- El modelo Gamma ofrece una relación costo/prestaciones accesible para usuarios que requieren respaldo ocasional durante tormentas o salidas de pesca recreativa.
""",
    },
}


from dataclasses import dataclass

@dataclass
class EditorialComparison:
    slug: str
    title: str
    h1: str
    description: str
    category: str
    tool_slugs: List[str]
    editorial_analysis: str

    @property
    def meta_description(self) -> str:
        return self.description

    @property
    def model_a_slug(self) -> str:
        return self.tool_slugs[0] if len(self.tool_slugs) > 0 else ""

    @property
    def model_b_slug(self) -> str:
        return self.tool_slugs[1] if len(self.tool_slugs) > 1 else ""


def get_editorial_comparison(slug: str) -> Optional[EditorialComparison]:
    comp_dict = EDITORIAL_COMPARISONS.get(slug)
    if not comp_dict:
        return None
    return EditorialComparison(**comp_dict)


def list_editorial_comparisons() -> List[EditorialComparison]:
    return [EditorialComparison(**c) for c in EDITORIAL_COMPARISONS.values()]


get_all_editorial_comparisons = list_editorial_comparisons

