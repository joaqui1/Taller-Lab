"""Aclara la evidencia y los límites de guías ya documentadas, sin inventar ensayos."""
from pathlib import Path
import re

# Resúmenes de las comparaciones existentes: no agrega cifras ni nuevos modelos.
EVIDENCE = {
    '00-amoladoras.md': (
        'Las fichas Bosch citadas separan las angulares compactas de las variantes de 180 y 230 mm, con potencia y velocidad publicadas para cada código.',
        'La matriz inicial organiza la elección por operación, diámetro y alimentación. El diámetro no demuestra profundidad efectiva ni ritmo de corte: faltan una geometría y un ensayo comparables.'),
    '01-disco-flap.md': (
        'Las referencias Bosch PRO X571 identifican forma, grano, diámetro y orificio; Norton y 3M aportan criterios de abrasivo y geometría en las fuentes enlazadas.',
        'La matriz cruza la terminación buscada con grano, forma y material permitido. No se compararon remoción por minuto, temperatura ni vida útil; las RPM deben comprobarse en la variante exacta.'),
    '03-amoladoras-dewalt.md': (
        'Las fichas y manuales regionales enlazados identifican las variantes DWE4020-AR, DWE4120-AR, DWE4212-AR, DWE4314-AR y DWE4557-AR. La DWE402 estadounidense es una referencia diferente.',
        'La tabla distingue código, medida y alimentación antes de comparar potencia. Una oferta DWE4214 o DWE4314N requiere su propia placa y manual: no hereda automáticamente las especificaciones de los códigos -AR comparados.'),
    '04-disco-de-desbaste.md': (
        'Bosch PRO Metal y Norton Clipper publican referencias concretas con dimensiones y especificación abrasiva; la tabla conserva el código y la aplicación de cada una.',
        'Compartir medida no vuelve equivalentes dos abrasivos. La comparación sirve para identificar compatibilidad y material autorizado; sin una prueba común no permite ordenar duración, costo por trabajo ni remoción.'),
    '05-amoladora-recta.md': (
        'Las fichas Bosch GGS 28 L, Makita GD0600 y Chicago Pneumatic CP9104Q/CP872 documentan modelos distintos; las fichas neumáticas diferencian consumo promedio y con carga.',
        'La conversión de litros por segundo a litros por minuto usa el factor 60. Para elegir la instalación se debe comparar salida a la presión requerida, ciclo y pérdidas; potencia eléctrica y consumo neumático no son una escala común de rendimiento.'),
    '07-amoladoras-makita.md': (
        'Las fichas Makita Argentina y Latinoamérica citadas identifican diámetros, códigos e interruptores. La guía registra la discrepancia entre el nombre de variante y el SKU de una página inalámbrica.',
        'La elección parte del código completo y el diámetro. No se trasladan automáticamente datos de GA4530 a GA4534 ni se resuelve una discrepancia de SKU por semejanza de nombres; hace falta confirmar la unidad y su manual.'),
    '08-amoladoras-inalambricas.md': (
        'Las fuentes Bosch, INGCO, DeWalt y Makita enlazadas describen modelos y plataformas; las fuentes comerciales locales permiten distinguir cuerpo solo de kit.',
        'El costo de entrada debe incluir cuerpo, batería y cargador compatibles. Voltaje y Ah no permiten predecir cortes por carga o autonomía entre equipos distintos; esas prestaciones no se midieron.'),
    '09-disco-para-cortar-ceramica.md': (
        'Bosch publica geometrías turbo y continua para las referencias PRO Ceramic y EXPERT HardCeramic de la tabla, junto con diámetro, orificio y dimensiones del segmento.',
        'La matriz distingue geometría y aplicación documentada. El perfil del borde no garantiza el acabado ni autoriza cualquier porcelanato; deben coincidir el material, código, fijación y condiciones de trabajo de las instrucciones.'),
    '11-amoladoras-lusqtoff.md': (
        'Las fichas Lüsqtoff enlazadas separan AML850-8, AML1010-8, AML115-9B y AML115-9BK, incluidos diámetro, regulación y composición publicada de cuerpo o kit.',
        'La matriz compara configuraciones completas: el cuerpo sin batería tiene costos pendientes y el kit exige verificar el contenido ofrecido. Potencia nominal, velocidades y tensión no demuestran autonomía ni rendimiento bajo carga.'),
    '12-amoladora-de-9-pulgadas.md': (
        'Las fichas argentinas citadas identifican Bosch GWS 25-230 y GWS 30-230 PB, Makita GA9020 y Stanley STGL2223-AR; la tabla mantiene desconocidos los campos no publicados.',
        'La diferencia geométrica entre 180 y 230 mm no equivale a la misma diferencia de profundidad de corte. Guarda, cabezal, desgaste y pieza condicionan el alcance; no se deduce capacidad efectiva solo del diámetro.'),
    '13-amoladora-skil-830w.md': (
        'El manual histórico Skil 9002/9004 y el catálogo argentino enlazados distinguen 9002AR de 9004AR, con tensión, potencia, diámetro y peso para esas referencias.',
        'El cálculo de diferencia nominal de potencia no representa una mejora medida de corte. La contradicción del título comercial de 9002 y las diferencias de kits requieren confirmación de placa y caja; no se certifica vigencia del catálogo ni stock actual.'),
    '14-disco-diamantado-segmentado.md': (
        'Bosch publica referencias PRO Concrete y EXPERT Multi Material por código, con materiales y dimensiones diferentes para 115 y 230 mm.',
        'Segmentado describe una geometría, no una autorización universal de material o uso húmedo. La matriz separa perfil, aplicación y montaje; no se extrapolan dimensiones ni régimen de uso entre variantes.'),
    '15-amoladoras-stanley.md': (
        'Las fichas y manuales Stanley separan STGS7115-AR, STGS8115-AR y STGS9115-AR de las variantes V20 regionales; las fuentes de garantía corresponden al mercado indicado.',
        'La comparación conserva sufijos y mercados para no trasladar tensión, contenido o cobertura de un país a otro. La mayor potencia nominal no demuestra mejor desempeño; el cuerpo V20 solo requiere batería y cargador compatibles adicionales.'),
    '16-disco-de-corte.md': (
        'Las fichas y el catálogo Bosch citados identifican discos de corte PRO Metal y Stainless Steel and Metal y los distinguen de los accesorios de desbaste.',
        'La matriz empieza por material y operación y después verifica medida, espesor, fijación y RPM. Igual diámetro no prueba compatibilidad de montaje ni habilita usar lateralmente un disco destinado a corte.'),
    '17-amoladoras-ingco.md': (
        'Las fuentes argentinas y regionales INGCO identifican códigos con cable y P20S; la tabla conserva las diferencias entre máquina sola, kit y referencias anunciadas como próximas.',
        'La decisión compara SKU y configuración completa. Un catálogo regional no confirma stock, garantía ni contenido de caja argentino; las discrepancias entre listados requieren confirmar la oferta concreta.'),
    '18-amoladora-velocidad-variable.md': (
        'Las fichas Bosch, Dowen Pagio y Hamilton y las fuentes identificadas de Total publican rangos de velocidad en vacío; la tabla señala los campos discordantes o no informados.',
        'Un regulador permite seleccionar dentro del rango declarado, pero no mide las RPM bajo carga ni autoriza accesorios incompatibles. No se asigna una velocidad universal por material y debe confirmarse el máximo de la variante Total ofrecida.'),
    '19-amoladora-7-pulgadas.md': (
        'Las fichas Bosch GWS 2200-180, Makita GA7010C/GA7020 y DeWalt DWE4557-AR documentan referencias de 180 mm, con características propias por código.',
        'La comparación separa diámetro, potencia, peso y funciones. Ninguno de esos campos aislado acredita rendimiento o profundidad efectiva; la elección depende del disco autorizado, acceso a la pieza y control de la herramienta.'),
    '21-amoladoras-gamma.md': (
        'Las fichas Gamma citadas distinguen modelos G1922AR, G1923AR, G1910AR, G1910KAR y G1917AR. El fabricante enumera el contenido del kit G1910KAR y publica condiciones de servicio.',
        'G1910AR y G1910KAR se distinguen por configuración, no por una mejora de potencia. La decisión debe cotejar código y caja; las declaraciones de garantía y red de servicio no prueban inventario ni cobertura de una oferta concreta.'),
    '22-amoladoras-total.md': (
        'El catálogo regional y las publicaciones locales citadas identifican TG10711576-4, TG109125565-4 y TG12018026-4; las fuentes extranjeras sin sufijo muestran una discrepancia de RPM.',
        'La matriz compara referencias locales completas por medida y regulación. No se atribuye la discrepancia extranjera exclusivamente al sufijo ni se deduce profundidad de corte del diámetro; prevalecen la placa y el manual de la unidad.'),
    '24-disco-para-cortar-vidrio.md': (
        'Las fichas Tork Craft y Husqvarna citadas declaran aplicaciones específicas en vidrio o azulejo de vidrio; las fuentes Lüsqtoff identifican DVC115-9 como referencia local.',
        'La matriz distingue material autorizado, medida, RPM y uso seco o húmedo. Una ficha de vidrio no autoriza cualquier vidrio templado o laminado; no se extrapola el uso de agua a una amoladora eléctrica común.'),
}

def main():
    for filename, (documented, analysis) in EVIDENCE.items():
        path = Path('paginas') / filename
        text = path.read_text(encoding='utf-8')
        text = re.sub(r'^## (?:Fuentes y alcance|Fuentes del fabricante)\s*$', '## Fuentes consultadas', text, flags=re.M)
        if '## Lectura de la evidencia de esta comparación' not in text:
            block = ('## Lectura de la evidencia de esta comparación\n\n'
                     f'**Dato documentado:** {documented} Las referencias están identificadas en [Fuentes consultadas](#fuentes-consultadas).\n\n'
                     f'**Análisis TallerLab:** {analysis}\n\n'
                     '**Límites:** investigación documental, sin prueba física propia ni muestra verificable de opiniones de compradores. Precio, stock y configuración deben comprobarse en la publicación del vendedor.\n\n')
            assert '## Fuentes consultadas' in text, filename
            text = text.replace('## Fuentes consultadas', block + '## Fuentes consultadas', 1)
        path.write_text(text,encoding='utf-8')
    print(f'{len(EVIDENCE)} guías: evidencia, interpretación y límites explícitos; fechas documentales conservadas.')

if __name__ == '__main__': main()
