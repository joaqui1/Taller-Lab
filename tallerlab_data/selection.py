"""Application families and documentary ordering, independent of monetization."""
from html import escape

LABELS = {
    'taladro': 'Taladros y percutores', 'rotomartillo': 'Rotomartillos SDS Plus',
    'atornillador-impacto': 'Atornilladores de impacto', 'taladro-banco': 'Taladros de banco',
    'amoladora-angular': 'Amoladoras angulares', 'amoladora-banco': 'Amoladoras de banco',
    'inflador': 'Infladores portátiles', 'aerografo': 'Compresores para aerógrafo',
    'compresor-tanque': 'Compresores con tanque',
}


def family(tool):
    name = tool.commercial_name.lower()
    if tool.category == 'taladros':
        if tool.slug in {'bosch-gdr-120-li', 'dewalt-dcf887'}:
            return 'atornillador-impacto'
        if 'banco' in name or tool.slug == 'omaha-ab550161k':
            return 'taladro-banco'
        if 'sds' in name or tool.slug.startswith(('bosch-gbh-', 'dewalt-dch')):
            return 'rotomartillo'
        return 'taladro'
    if tool.category == 'amoladoras':
        return 'amoladora-banco' if 'banco' in name else 'amoladora-angular'
    if tool.category == 'compresores':
        if tool.slug == 'fengda-as-186':
            return 'aerografo'
        if tool.slug.startswith(('einhell-pressito', 'gadnic-av', 'lusqtoff-mcl', 'makita-dmp')):
            return 'inflador'
        return 'compresor-tanque'
    return tool.category


def family_label(tool):
    return LABELS.get(family(tool), tool.category.title())


def evidence_counts(tool):
    supported = sum(s.documentary_status == 'concordancia_textual' for s in tool.specs.values())
    return supported, len(tool.specs)


def documentary_order(tool):
    supported, total = evidence_counts(tool)
    return (-supported / max(total, 1), -supported, tool.brand.casefold(), tool.model_name.casefold())


GUIDANCE = {
    'taladro': ('Perforación y atornillado', 'Elegí primero material, diámetro y necesidad de percusión. Compará capacidad de mandril y torque solo bajo la misma condición. En batería, sumá cargador y baterías compatibles al presupuesto.'),
    'rotomartillo': ('Perforación con encastre SDS Plus', 'Revisá el diámetro requerido, encastre y modos del modelo. Los joules requieren el mismo protocolo declarado; no convierten por sí solos una máquina en más rápida. Confirmá si el trabajo requiere cincelado.'),
    'atornillador-impacto': ('Fijaciones con impacto de giro', 'Confirmá encastre y puntas adecuadas a la fijación. El torque de impacto no equivale al torque duro de un taladro. No elegir esta familia como sustituto automático de un rotomartillo.'),
    'taladro-banco': ('Perforación con máquina fija', 'Revisá recorrido, distancias útiles, sujeción y velocidades que exige el trabajo. El diámetro del mandril no expresa por sí solo capacidad en acero; comprobá requisitos de instalación en el manual.'),
    'amoladora-angular': ('Corte o desbaste con disco', 'Elegí diámetro, accesorio, velocidad admisible y alimentación compatibles. Confirmá protector y montaje según el manual; más potencia declarada no demuestra mejor acabado.'),
    'amoladora-banco': ('Trabajo con amoladora fija', 'Confirmá dimensiones, eje y velocidad admisible del abrasivo, además de sujeción e instalación. No trasladar datos ni accesorios de una amoladora angular.'),
    'inflador': ('Inflado portátil', 'Revisá la presión admitida por el elemento a inflar, alimentación y ciclo declarado. Una presión máxima alta no demuestra rapidez; no extrapolar su caudal a alimentar herramientas neumáticas.'),
    'aerografo': ('Alimentación de aerógrafo', 'Buscá caudal entregado a la presión requerida por el aerógrafo, regulación y requisitos del accesorio. No trasladar cifras de infladores ni asumir uso continuo sin documento.'),
    'compresor-tanque': ('Alimentación neumática', 'Primero buscá consumo de la herramienta y caudal entregado a su presión de trabajo. El tanque es reserva; aspiración y HP no acreditan entrega ni ciclo continuo. Confirmá instalación en el manual.'),
    'hidrolavadoras': ('Limpieza con agua a presión', 'Compará presión de trabajo y caudal bajo la misma condición. La presión máxima no es presión sostenible. Revisá abastecimiento de agua, alimentación, manguera y accesorios incluidos.'),
    'soldadoras': ('Selección por proceso y consumible', 'Confirmá proceso, consumible, polaridad y corriente requeridos. Compará ciclo de trabajo al mismo punto y condición; el amperaje del nombre comercial no define funcionamiento continuo.'),
    'generadores': ('Selección para una carga identificada', 'Revisá potencia nominal, demanda de arranque, tensión y frecuencia de la carga. kVA no equivale a kW. Autonomía requiere la misma carga declarada; seguí el manual para ubicación y uso.'),
}


def render_decision_guidance(tools, comparison=None):
    groups = list(dict.fromkeys(family(t) for t in tools))
    cards = []
    for group in groups:
        title, text = GUIDANCE.get(group, ('Elegir por aplicación', 'Confirmá aplicación, alimentación y variante en el documento original.'))
        cards.append(f'<li><strong>{escape(title)}:</strong> {escape(text)}</li>')
    if comparison is not None:
        usable = [r.name for r in comparison.rows if r.is_comparable]
        conclusion = ('Esta selección permite contrastar: ' + ', '.join(usable) + '.') if usable else 'Esta selección no permite una conclusión numérica respaldada. Usá las fichas para revisar aplicación y documentos; no hay un ganador técnico establecido.'
    else:
        n, total = evidence_counts(tools[0])
        conclusion = f'{n} de {total} datos de esta ficha tienen fuente oficial comprobada. Compará siempre valores medidos en la misma condición.'
    return '<section class="tl-card"><h2>Cómo usar estos datos para elegir</h2><p>'+escape(conclusion)+'</p><ul>'+''.join(cards)+'</ul><p>Antes de comprar, confirmá código completo, tensión, contenido del kit y garantía de la oferta. Los enlaces comerciales no modifican el orden documental ni la comparabilidad.</p></section>'
