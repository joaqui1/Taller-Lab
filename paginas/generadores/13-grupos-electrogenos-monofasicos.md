---
title: "Grupo electrógeno monofásico: cómo elegir"
h1: "Grupos electrógenos monofásicos: potencia y usos"
url: "/generadores/monofasicos/"
description: "Guía técnica sobre grupos electrógenos monofásicos (220V 50Hz) en Argentina: qué significa monofásico, comparativa con trifásico, cálculo de carga y modelos."
author: "Taller Lab"
category: "Generadores y Grupos Electrógenos"
keywords: ["grupos electrogenos monofasicos", "generador monofasico", "generador 220v", "monofasico o trifasico generador", "calcular potencia generador monofasico"]
---

# Grupos electrógenos monofásicos: potencia y usos

En el universo de las instalaciones eléctricas residenciales y comerciales pequeñas, los grupos electrógenos monofásicos representan la solución técnica más eficiente, simple y segura. Diseñados para generar corriente alterna senoidal a una tensión nominal de 220 voltios y una frecuencia de 50 hercios (el estándar domiciliario oficial en Argentina), estos equipos permiten abastecer directamente cualquier electrodoméstico o herramienta sin las complejidades de distribución de fases que conllevan los sistemas trifásicos.

A pesar de su aparente sencillez, dimensionar y conectar correctamente un generador monofásico exige comprender cómo se comporta la corriente en dos conductores (fase y neutro), por qué en el 90% de los casos una casa con acometida trifásica debe instalar un generador monofásico, y cómo evitar sobrecargas que dañen el alternador o los cables de la instalación fija.

En esta guía práctica de **Taller Lab** analizamos los fundamentos de la energía monofásica, comparamos sus ventajas frente a los [generadores trifásicos](/generadores/trifasicos/), te enseñamos cómo dimensionar un [generador para casa](/generadores/para-casa/) y cómo se posiciona dentro de nuestra [guía comparativa general de generadores](/generadores/comparativa-general/).

---

## Qué significa monofásico

Un sistema eléctrico monofásico es aquel que transporta la energía a través de un único circuito de corriente alterna formado por **dos conductores principales**: un conductor activo (**Fase**) y un conductor de retorno (**Neutro**), complementados obligatoriamente por un conductor de protección a tierra (**Tierra PE**).

```
                      ALTERNADOR MONOFÁSICO (220 V / 50 Hz)
                      
   [ FASE (L) ]   -----------------~ 220 V ~-----------------> [ Cargas Hogar ]
                                                               (Heladera, TV, Luces)
   [ NEUTRO (N) ] --------------------------------------------> [ Retorno ]
   
   [ TIERRA (PE)] ----------------- (Jabalina a Tierra) -----> [ Seguridad Chasis ]
```

### Características operativas en Argentina:
1. **Tensión de servicio**: $220\text{ V}$ nominales entre fase y neutro.
2. **Frecuencia fija**: $50\text{ Hz}$ (la onda senoidal oscila y cambia de polaridad 50 veces por segundo).
3. **Entrega de potencia directa**: A diferencia de un alternador trifásico (donde la potencia total se reparte en tres bobinas separadas), en un generador monofásico **toda la capacidad del motor y del alternador está disponible en una sola línea**.
4. **Relación entre Watts, Voltios y Amperes**:
   $$\text{Potencia (W)} = \text{Tensión (V)} \times \text{Corriente (A)} \times \cos \varphi$$
   Por ejemplo, un generador monofásico de **5.500 W útiles** entrega una corriente máxima disponible de:
   $$I = \frac{5.500\text{ W}}{220\text{ V}} \approx \mathbf{25\text{ Amperes}}$$

---

## Cuándo conviene frente a trifásico

Existe una confusión sumamente extendida entre propietarios de viviendas o locales comerciales: creer que porque Edenor, Edesur o la cooperativa eléctrica del pueblo les suministra energía mediante un medidor trifásico (380 V), el grupo electrógeno de respaldo debe ser obligatoriamente trifásico.

**En la inmensa mayoría de los casos, esta creencia es un grave error técnico**:

| Criterio de Selección | Generador Monofásico (220 V) | Generador Trifásico (380 V / 220 V) |
| :--- | :--- | :--- |
| **Tipo de artefactos a alimentar** | **Aparatos de 220 V**: heladeras, televisores, luces, PC, bombas monofásicas, aires split. | **Motores trifásicos de 380 V**: bombas de pozo profundo, compresores industriales, tornos. |
| **Riesgo de desbalanceo** | **Cero**. Toda la potencia se toma de una única fuente común. | **Alto**. Si una fase se sobrecarga y las otras no, el equipo se apaga o sufre calentamiento. |
| **Aprovechamiento de potencia** | **100% de la potencia nominal** utilizable en cualquier aparato conectado. | **Solo el 33% de la potencia total** utilizable por cada toma individual de 220 V. |
| **Instalación y conmutación** | Llave conmutadora bipolar o tetrapolar simple; no requiere balancear líneas. | Requiere distribuir cuidadosamente las cargas monofásicas del tablero en partes iguales. |
| **Costo de compra y mantenimiento** | Más económico en repuestos de alternador y placa AVR. | Más costoso; alternadores y térmicas de cuatro polos más caras. |

### Cómo respaldar una casa con red trifásica usando un generador monofásico:
Si tu casa recibe bajada trifásica de la calle pero no tenés ningún motor de 380 V, un electricista matriculado puede instalar una **llave conmutadora de 4 polos (Tetrapolar)** en el tablero principal. En la posición "Generador", la única fase del equipo monofásico alimenta en paralelo las tres fases del hogar. De esa forma, todas las luces y tomas de la vivienda tienen luz durante el corte sin riesgo de desbalanceo.

---

## Cómo calcular la carga

Para que el generador monofásico trabaje en su zona de eficiencia sin disparar la protección térmica, es necesario calcular el consumo simultáneo real:

```
Consumo Simultáneo Máximo (W) = Suma de Cargas Continuas (W) + Pico de Arranque Inductivo (W)
```

### Tabla de dimensionamiento para cargas monofásicas típicas:

| Dispositivo Monofásico | Potencia de Régimen (W) | Corriente de Régimen (A) | Pico de Arranque Típico (W) |
| :--- | :---: | :---: | :---: |
| **Luminaria LED integral (20 lámparas)** | 200 W | ~0,9 A | 200 W |
| **Heladera con freezer / No-Frost** | 200 W | ~1,0 A | 1.000 W a 1.200 W |
| **Televisor Smart 55" + Audio + Wi-Fi** | 180 W | ~0,8 A | 180 W |
| **Bomba de elevación centrífuga ½ HP** | 375 W | ~2,0 A | 1.400 W |
| **Bomba sumergible de pozo 1 HP monofásica** | 750 W | ~4,2 A | 2.500 W |
| **Aire acondicionado split 3.000 frigorías** | 1.100 W | ~5,5 A | 3.500 W |
| **Microondas hogareño** | 1.200 W | ~5,5 A | 1.500 W |

> **Regla de taller**: Para una vivienda estándar sin aire acondicionado encendido, un generador monofásico de **2.500 W a 3.000 W** es más que suficiente. Si querés mantener encendido un split de 3.000 frigorías y la bomba de agua, necesitás dimensionar un equipo de **5.500 W a 6.500 W monofásicos**.

---

## Modelos para hogares y comercios

De acuerdo al volumen de potencia y exigencia de horas, recomendamos las siguientes configuraciones de equipos monofásicos (ya sean convencionales con AVR o con [tecnología inverter](/generadores/inverter/) si necesitás alimentar electrónica delicada y bajo nivel sonoro):

### 1. Escala Hogareña Básica (2.500 W a 3.500 W)
* **Destino**: Departamentos amplios con patio, PHs y casas familiares con consumos esenciales (heladera, freezer, luces, electrónica y bomba chica).
* **Modelos líderes**:
  - **Lusqtoff LG3500EX**: Chasis abierto, motor 7 HP, tanque de 15 litros y repuestos en todo el país.
  - **Gamma Elite 3500**: Excelente terminación de bobinado y panel con doble salida normalizada.

### 2. Escala Residencial Confort y Comercios (5.500 W a 7.500 W)
* **Destino**: Casas grandes con climatización, locales comerciales (fiambrerías, panaderías, farmacias) con heladeras exhibidoras y cortinas de aire.
* **Modelos líderes**:
  - **Gamma Elite 6500 E**: Arranque eléctrico, motor 13 HP, alternador de cobre con AVR y tanque de 25 litros.
  - **Hyundai HHY7200FE**: Motor 15 HP de alta cilindrada con display digital 3 en 1 para control de horas.
  - **Honda EZ6500CXS / EG6500CX**: La referencia máxima en durabilidad y estabilidad de voltaje profesional.

Al instalar tu equipo monofásico, asegurate de conectar la **jabalina de puesta a tierra** al borne específico del chasis para garantizar que los disyuntores diferenciales de la casa sigan protegiendo a las personas contra contactos indirectos.

[Ver grupos electrógenos monofásicos en Mercado Libre](https://listado.mercadolibre.com.ar/grupo-electrogeno-monofasico){:target="_blank" rel="sponsored" .btn-mercado-libre}
