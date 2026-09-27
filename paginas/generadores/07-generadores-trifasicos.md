---
title: "Generador trifásico: potencia, usos y cómo elegir"
h1: "Cómo elegir un generador trifásico"
url: "/generadores/trifasicos/"
description: "Guía técnica sobre generadores trifásicos (380V/220V) en Argentina: cuándo conviene, kVA vs kW, balanceo de fases y modelos para talleres e industrias."
author: "Taller Lab"
category: "Generadores y Grupos Electrógenos"
keywords: ["generador trifasico", "grupo electrogeno trifasico", "generador 380v", "diferencia kva y kw", "balanceo de fases generador"]
---

# Cómo elegir un generador trifásico

La elección de un grupo electrógeno trifásico representa uno de los puntos donde más errores de compra se cometen en el ámbito de las instalaciones eléctricas. Con frecuencia, usuarios residenciales o dueños de pequeños comercios que tienen contratada una bajada trifásica de red (380 V) asumen erróneamente que están obligados a comprar un generador trifásico, sin advertir que en realidad la totalidad de sus artefactos de consumo son monofásicos (220 V).

Un generador trifásico está diseñado con un bobinado estatórico en estrella con tres fases desfasadas $120^\circ$ entre sí. Si las cargas no se distribuyen equitativamente entre las tres líneas, el desbalanceo térmico y magnético resultante puede quemar el bobinado del alternador o provocar fluctuaciones severas de voltaje en los artefactos más sensibles.

En este informe técnico de **Taller Lab** analizamos cuándo es estrictamente indispensable un generador trifásico frente a la versatilidad de los [generadores monofásicos](/generadores/monofasicos/), cómo interpretar la relación entre kVA y kW según el factor de potencia, cómo se ubica en nuestra [guía comparativa general de generadores](/generadores/comparativa-general/) y qué modelos se adaptan mejor a cada segmento de uso.

---

## Cuándo necesitás alimentación trifásica

La regla de oro para decidir entre monofásico y trifásico es simple: **el generador debe elegirse en función de las cargas que va a alimentar, no del tipo de bajada que tiene el pilar de la calle**.

### Es estrictamente INDISPENSABLE un generador trifásico cuando:
1. **Tenés motores eléctricos trifásicos (380 V) que no pueden parar**:
   - Bombas sumergibles de pozo profundo para riego o abastecimiento rural (3 HP a 7,5 HP trifásicas).
   - Compresores de aire a pistón de taller mecánico de 5,5 HP a 10 HP.
   - Máquinas herramientas de carpintería y herrería: tornos mecánicos, fresadoras, sierras sin fin industriales o guillotinas de chapa.
   - Motores de ascensores o montacargas en edificios pequeños.
   - Equipos centrales de aire acondicionado comercial tipo Rooftop o VRF trifásicos.

### NO conviene un generador trifásico (conviene monofásico) cuando:
* Tenés una casa o comercio con acometida de tres fases pero **todos tus artefactos funcionan a 220 V** (heladeras, televisores, iluminación, computadoras y aires acondicionados split monofásicos).
* En estos casos, resulta técnicamente mucho más conveniente instalar un **generador monofásico potente** y puentear las tres fases en la llave conmutadora del tablero seccional durante el corte de luz (siempre que la potencia del generador alcance y los conductores de neutro estén correctamente dimensionados).

---

## Diferencias entre kVA y kW

En los generadores trifásicos, la potencia casi siempre viene expresada comercialmente en **kVA (kilovoltamperios)**, que representa la **potencia aparente ($S$)**, mientras que la energía consumida útil por las resistencias y motores es la **potencia activa ($P$)** medida en **kW (kilovatios)**.

```
Potencia Aparente (kVA) x Factor de Potencia (cos phi) = Potencia Activa Útil (kW)
                        [ 10 kVA x 0,8 = 8 kW ]
```

### Relación matemática fundamental:
$$P\text{ (kW)} = S\text{ (kVA)} \times \cos \varphi$$

En Argentina, los generadores trifásicos están estandarizados con un factor de potencia inductivo típico de $\cos \varphi = 0,8$:
* Un generador trifásico de **7 kVA** entrega: $7 \times 0,8 = \mathbf{5,6\text{ kW}}$.
* Un generador trifásico de **10 kVA** entrega: $10 \times 0,8 = \mathbf{8,0\text{ kW}}$.
* Un generador trifásico de **15 kVA** entrega: $15 \times 0,8 = \mathbf{12,0\text{ kW}}$.

> **Atención al cálculo de corriente por fase**: La corriente nominal admisible por fase ($I$) en un sistema trifásico de 380 V entre fases y 220 V entre fase y neutro se calcula como:
> $$I = \frac{S\text{ (VA)}}{\sqrt{3} \times 380\text{ V}} = \frac{S\text{ (VA)}}{658}$$
> En un equipo de $10\text{ kVA}\ (10.000\text{ VA})$, la corriente máxima por fase es de aproximadamente **15,2 A**. Si superás ese amperaje en una sola fase, saltará la protección térmica aunque las otras dos fases estén vacías.

---

## Distribución de cargas

El aspecto operativo más crítico de un generador trifásico es la **división equitativa de la potencia monofásica**:

```
              ALTERNADOR TRIFÁSICO EN ESTRELLA (10 kVA = 8 kW Totales)
                                        |
        -----------------------------------------------------------------
        |                               |                               |
    [ FASE R ]                      [ FASE S ]                      [ FASE T ]
   Máx. 2,66 kW                    Máx. 2,66 kW                    Máx. 2,66 kW
(Heladera + Luces)             (Aire Acondicionado)              (Bomba de Agua)
```

### La regla del tercio (1/3 de potencia por fase):
En un generador trifásico estándar con alternador bobinado en estrella, la potencia utilizable entre cualquier fase y el neutro común (220 V) es **exactamente un tercio (33%) de la potencia total**:
* Si tenés un generador trifásico de **6.000 W (7,5 kVA)**, cada fase individual solo puede entregar un máximo de **2.000 W a 220 V**.
* Si intentás conectar un aire acondicionado o una soldadora monofásica que consume 3.000 W a una sola toma de 220 V de ese generador trifásico, el equipo se vendrá abajo y disparará la térmica por sobrecarga en esa fase, a pesar de que el generador "en teoría" es de 6.000 W.

### Consecuencias del desbalanceo de fases:
1. **Calentamiento asimétrico del rotor**: Provoca distorsión en la onda magnética y vibraciones mecánicas dañinas para los rodamientos.
2. **Elevación de tensión en fases descargadas**: Al cargarse excesivamente la Fase R, la tensión puede caer a 195 V en esa línea, mientras que la Fase T (sin carga) puede dispararse peligrosamente a 245 V o más, quemando fuentes electrónicas.

---

## Modelos según el uso

La selección del equipo trifásico debe ajustarse a la potencia de los motores trifásicos que debas arrancar y, fundamentalmente, al límite de consumo monofásico admisible por línea:

| Marca y Modelo | Potencia Trifásica (kVA / kW) | Potencia Máx. por Fase a 220 V | Motor / Combustible | Arranque | Aplicación recomendada en Argentina |
| :--- | :---: | :---: | :--- | :--- | :--- |
| **Gamma Elite 7500 T** (G2858AR) | 7,0 kVA / 5,5 kW (6,0 kW máx) | **~1.830 W** (8,3 A por fase) | Nafta 4T 15 HP (420 cc) | Eléctrico + Manual | Obras civiles, bombas sumergibles chicas hasta 2 HP o trompitos hormigoneros trifásicos. |
| **Lüsqtoff LG7500EX-3** | 7,5 kVA / 6,0 kW (6,5 kW máx) | **~2.000 W** (9,1 A por fase) | Nafta 4T 16 HP (439 cc) | Eléctrico + Manual | Talleres mecánicos, gomerías con compresor trifásico de 3 HP y elevador para autos. |
| **[Niwa](/generadores/niwa/) GNW-70-ER/T** | 7,0 kVA / 5,5 kW (6,0 kW máx) | **~1.830 W** (8,3 A por fase) | Nafta 4T 16 HP (420 cc) | Eléctrico + Manual | Respaldo para pequeños talleres metalúrgicos y bombas de desagote pluvial en subsuelos. |
| **Hyundai DHY8600SE-T** | 7,9 kVA / 6,3 kW (6,8 kW máx) | **Full Power** (~5,5 kW en monofásico) | [Diésel](/generadores/diesel/) 12 HP (498 cc) cabinado | Eléctrico con ATS | **Selector dual**: permite entregar potencia balanceada en 380 V o el 100% en 220 V sin desbalancear el bobinado. Ideal comercios y consorcios. |
| **Honda ET12000** | 11,0 kVA / 8,5 kW (10,0 kW máx) | **~2.830 W** (12,8 A por fase) | Honda GX630 V-Twin (688 cc) | Eléctrico | Agro, galpones avícolas, tambos mecánicos y cámaras de frío comerciales de trabajo pesado. |

### Clave técnica antes de conectar el tablero:
Si vas a operar cargas mixtas en el inmueble (máquinas de 380 V en simultáneo con heladeras, computadoras e iluminación de 220 V), solicitá a un electricista matriculado que mida con una pinza amperométrica el consumo en amperes de cada fase bajo corte simulado. La diferencia de carga entre la fase más cargada y la menos cargada **jamás debe superar el 15% al 20%** para evitar quemar el regulador AVR o inducir sobretensiones destructivas en la fase libre.

[Ver generadores trifásicos en Mercado Libre](https://listado.mercadolibre.com.ar/generador-trifasico){:target="_blank" rel="sponsored" .btn-mercado-libre}
