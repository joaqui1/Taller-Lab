---
title: "Grupos electrógenos: cómo elegir y comparar modelos"
h1: "Grupos electrógenos: guía para elegir el adecuado"
url: "/generadores/comparativa-general/"
description: "Guía completa de Taller Lab sobre grupos electrógenos en Argentina: funcionamiento, cálculo de potencia (kVA y kW), tipos, marcas (Honda, Gamma, Lusqtoff) y precios."
author: "Taller Lab"
category: "Generadores y Grupos Electrógenos"
keywords: ["grupos electrógenos", "generador electrico", "elegir grupo electrogeno", "grupo electrogeno argentina", "potencia generador"]
---

# Grupos electrógenos: guía para elegir el adecuado

Quedarse sin suministro eléctrico en el hogar, el comercio o el taller no solo representa una incomodidad, sino que puede comprometer la conservación de alimentos en frío, detener bombas de agua de pozo o paralizar trabajos de obra con herramientas eléctricas. En Argentina, donde los cortes de luz por sobrecarga en verano o tormentas en invierno son frecuentes, contar con un grupo electrógeno confiable se transformó en una necesidad operativa de primer orden. Si buscás abastecimiento familiar, te recomendamos leer nuestra guía sobre cómo elegir un [generador para casa](/generadores/para-casa/) o consultar el informe sobre [precios de grupos electrógenos](/generadores/precios/) en Argentina.

Sin embargo, elegir un equipo no consiste únicamente en buscar la mayor cantidad de watts al menor costo. Existen alternativas muy específicas según el entorno de uso: desde [generadores portátiles](/generadores/portatiles/) tipo valija para emergencias o viajes, hasta [generadores silenciosos](/generadores/silenciosos/) cabinados y [estaciones de energía portátiles](/generadores/estacion-de-energia-portatil/) de litio para departamentos o barrios con restricción sonora.

En esta guía de **Taller Lab** desglosamos los fundamentos de funcionamiento de los generadores eléctricos, cómo calcular la potencia real necesaria considerando el factor de arranque, qué tipos convienen según cada entorno y cómo comparar las marcas líderes disponibles en el mercado local.

---

## Cómo funciona un generador eléctrico

Un grupo electrógeno es una máquina electromecánica compuesta esencialmente por dos bloques acoplados: un **motor de combustión interna** (que actúa como motor térmico primario) y un **alternador eléctrico** (que transforma la energía mecánica en energía eléctrica utilizable a 220 V y 50 Hz en corriente alterna).

```
[ Motor Térmico ] ---> (Eje de rotación a 3.000 RPM) ---> [ Alternador ] ---> [ Regulador AVR / Inverter ] ---> [ Tomas 220V ]
(Nafta / Diésel / Gas)                                    (Rotor + Estator)     (Estabilización de tensión)
```

### Componentes clave del sistema:

1. **Motor de combustión**: Suele ser de cuatro tiempos (4T) con válvulas a la cabeza (OHV), refrigerado por aire forzado. Funciona habitualmente a un régimen gobernado constante de 3.000 RPM (para generar 50 Hz con 2 polos magnéticos).
2. **Alternador (Rotor y Estator)**: El rotor (inductor móvil) gira dentro del estator (inducido fijo bobinado en cobre o aluminio). Por la ley de inducción de Faraday, la variación del campo magnético induce una fuerza electromotriz (tensión alterna senoidal).
3. **Sistema de regulación de voltaje (AVR vs. Capacitor vs. Inverter)**:
   - **Regulación por capacitor**: Presente en equipos básicos económicos. Mantiene el voltaje en un rango aceptable, pero sufre caídas notables ante cargas elevadas.
   - **AVR (Automatic Voltage Regulator)**: Plaqueta electrónica que sensa la tensión de salida y ajusta continuamente la corriente de excitación del rotor. Mantiene el voltaje en $220\text{ V} \pm 2\%$, apto para iluminación, herramientas y motores.
   - **Módulo Inverter**: Convierte la corriente alterna del alternador en corriente continua (DC) y luego la recompone mediante microprocesadores en una onda senoidal pura sin distorsión armónica (THD < 3%).
4. **Panel de control y protecciones**: Incluye disyuntor térmico contra sobrecargas, sensor de bajo nivel de aceite con corte automático (*Oil Alert*) y voltímetro/frecuencímetro digital.

> **Regla de taller**: El bobinado de cobre soporta mucho mejor las altas temperaturas y las corrientes de arranque repetidas que el bobinado de aluminio. Aunque encarece el equipo, para uso frecuente o profesional la durabilidad del alternador con cobre es indiscutiblemente superior.

---

## Qué potencia necesitás

El error más común al comprar un grupo electrógeno es sumar únicamente los consumos nominales (en watts) declarados en las etiquetas de los aparatos. Cuando se conectan cargas inductivas (aparatos con motor eléctrico como heladeras, bombas centrífugas o acondicionadores de aire), se produce un **pico de arranque** que puede demandar entre 2 y 4 veces su potencia de régimen.

| Tipo de Carga | Ejemplos | Comportamiento al encender | Factor de sobredimensionamiento |
| :--- | :--- | :--- | :---: |
| **Resistiva pura** | Luces LED/halógenas, estufas de cuarzo, pava eléctrica, TV | El consumo es constante. No genera picos de corriente. | $\times 1,0$ |
| **Inductiva moderada** | Ventiladores, taladros con variador, PC, cargadores | Pico breve durante la aceleración del motor. | $\times 1,5$ a $\times 2,0$ |
| **Inductiva pesada** | Heladera con motocompresor, freezer, bomba elevadora de agua, aire acondicionado | Alto torque de arranque inicial contra presión de gas o columna de agua. | $\times 2,5$ a $\times 3,5$ |

### Distinción entre Potencia Nominal (COP) y Potencia Máxima (MAX):
* **Potencia Nominal / Continua (PRP / COP)**: La carga real que el generador puede alimentar de forma ininterrumpida durante horas sin sobrecalentarse (generalmente el 80-90% del valor comercial).
* **Potencia Máxima (LTP / Pico)**: La capacidad de reserva puntual que puede soportar el equipo durante unos pocos segundos para absorber el arranque de un motor eléctrico.

### Conversión de kVA a kW:
Muchos generadores declaran su potencia en kilovoltamperios (kVA). Para calcular la potencia activa útil en kilovatios (kW) en corriente alterna monofásica se aplica el factor de potencia ($\cos \varphi$):
$$\text{kW} = \text{kVA} \times 0,8$$
Por ejemplo, un equipo promocionado como de $6,5\text{ kVA}$ entrega en realidad una potencia activa útil continua de:
$$6,5 \times 0,8 = 5,2\text{ kW}\ (5.200\text{ W})$$

---

## Tipos de generadores

Para definir la compra correcta, el mercado se clasifica según tres criterios técnicos determinantes:

### 1. Según el combustible empleado:
* **Nafta (Gasolina 4T)**: Los [generadores a nafta](/generadores/a-nafta/) son los más difundidos en potencias de 1 kW a 8 kW. Fáciles de arrancar en frío, menor peso y costo inicial accesible. Requieren vaciar la cuba del carburador si quedan almacenados por meses para evitar que la nafta vieja tape los chicleres.
* **Diésel (Gasoil)**: Los [generadores diésel](/generadores/diesel/) utilizan motores pesados y robustos, diseñados para trabajo continuo intensivo (obras, industrias, comercios grandes). Consumen significativamente menos litros por hora y el motor tiene una vida útil tres veces más prolongada, aunque son más ruidosos y costosos.
* **Gas (GLP / Gas Natural)**: Los [generadores a gas](/generadores/a-gas/) son equipos estacionarios o duales. No sufren degradación de combustible en el tanque y emiten gases de escape más limpios, requiriendo conexión reglamentaria por gasista matriculado.

### 2. Según la tecnología de regulación:
* **Generadores Convencionales con AVR**: Chasis tubular de caño abierto. Relación costo/potencia insuperable. Ideales para obras, bombas, iluminación de emergencia y motores de inducción.
* **Generadores Inverter**: Basados en [tecnología inverter](/generadores/inverter/), disponen de gabinete cerrado e insonorizado. Su aceleración electrónica variable según la demanda de carga ahorra combustible en cargas parciales y entrega energía limpia apta para notebooks, televisores Smart, placas de calderas y electrónica fina.

### 3. Según la configuración de fases:
* **Monofásicos (220 V)**: Los [generadores monofásicos](/generadores/monofasicos/) son el estándar indiscutible para viviendas, departamentos y talleres con maquinaria de dos conductores (fase y neutro).
* **Trifásicos (380 V / 220 V)**: Los [generadores trifásicos](/generadores/trifasicos/) son indispensables si tenés motores trifásicos (compresores industriales, bombas de pozo profundo, tornos). Requieren balancear cuidadosamente las fases al conectar consumos monofásicos.

---

## Comparativa de marcas y modelos

En el mercado argentino encontramos marcas con perfiles, calidades de componentes y redes de servicio técnico bien diferenciadas:

| Marca | Segmento / Origen | Fortalezas | Puntos a considerar | Modelos destacados |
| :--- | :--- | :--- | :--- | :--- |
| **[Honda](/generadores/honda/)** | Premium / Japón-Tailandia-Brasil | Confiabilidad legendaria, arranque al primer tirón, bajísimo nivel de ruido y durabilidad extrema de motor (GX/iGX). | Precio inicial elevado frente a marcas genéricas. | EU22i (Inverter), EG6500CX, EZ6500 |
| **[Gamma](/generadores/gamma/)** | Comercial masivo / Importado | Amplia presencia nacional, red de repuestos extendida, chasis robusto con ruedas en potencias altas. | Nivel sonoro elevado en línea abierta; regulación AVR estándar. | Gamma 950 (2T compacto), Elite 6500 |
| **[Lusqtoff](/generadores/lusqtoff/)** | Bricolaje y taller / Importado | Excelente relación precio-prestaciones, catálogo muy completo (convencionales, duales e inverter). | Se recomienda asentar bien el motor con cambio de aceite a las primeras 20 horas. | LG3500EX, LG6500EX, LG2000i |
| **[Hyundai](/generadores/hyundai/)** | Semi-profesional / Corea-China | Motores de buen torque, tableros con display digital multifunción, alternadores bien balanceados. | Disponibilidad de algunos repuestos específicos según distribuidor. | HHY3000FE, HHY7200FE, Inverter HY3000i |
| **[Niwa](/generadores/niwa/)** | Agro y obra / Importado | Diseñados para entornos de trabajo rústico, buena autonomía y tanques de combustible grandes. | Mayor peso estructural; arranque manual algo duro en cilindradas altas sin batería. | GNW-55-ER, GNW-70-ER |

Al momento de definir tu compra, priorizá la disponibilidad de filtros, bujías y servicio técnico oficial en tu localidad por sobre un ahorro marginal en el precio de lista.

Si buscás un equipo de baja potencia para iluminación o cargas pequeñas, compará el **Pektra 720 W** y el **Konan 800 W** en nuestra [guía de grupos electrógenos chicos](/generadores/chicos/). Ambos declaran 650 W nominales; los modelos de 2,2 kVA y 2500 W pertenecen a otro escalón y aparecen en la [guía de precios](/generadores/precios/).

[Comparar dos grupos electrógenos chicos](/generadores/chicos/)
