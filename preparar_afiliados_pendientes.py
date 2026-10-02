"""Consolida espacios de afiliado identificados, sin inventar enlaces de compra."""
import json
from pathlib import Path

ROOT = Path(__file__).parent
path = ROOT / 'afiliados-por-completar.json'
slots = json.loads(path.read_text(encoding='utf-8'))
# El usuario no encuentra G2802 en su catálogo: pedir los modelos disponibles
# para las guías de su capacidad, sin reutilizar las especificaciones del de 50 L.
for unavailable in ('Gamma G2802AR', 'Gamma G2802KAR'):
    slots.pop(unavailable, None)
for model, guides, detail in [
    ('Gamma G2801AR', ['/compresores/24-litros/'], 'Oferta de 24 L; Gamma lo presenta como 25 L. Confirmar código, placa y kit; no corresponde a G2802 de 50 L.'),
    ('Gamma G2803AR', ['/compresores/100-litros/'], '100 L; código exacto G2803AR. No confundir con G2858AR ni trasladar datos del G2802.'),
    ('STIHL RE 90 · RE020114544 · 50 Hz', ['/hidrolavadoras/stihl/'], 'Reemplazar el referido recibido de 60 Hz o acreditar placa del código argentino.'),
    ('Kärcher K5 · 9.398-295.0', ['/hidrolavadoras/karcher-k5/'], 'El referido anterior no acredita este código. Confirmar versión y caudal.'),
    ('Bosch GSA 1100 E', ['/sierras/sable/'], 'Reemplazo del referido retirado: publicación activa con código y potencia consistentes.'),
    ('Bosch PRO Multi Material · 190 mm · 54 dientes · eje 30 mm', ['/sierras/disco-para-sierra-circular/'], 'Disco para sierra manual; confirmar referencia, geometría y material.'),
    ('ESAB/Conarco WELD ER70S-6 · 0,8 mm × 5 kg', ['/soldadoras/soldadora-mig-con-gas/','/soldadoras/alambre-para-soldadura-mig/'], 'Macizo para acero al carbono; no sustituir por aluminio o inoxidable ni por 18 kg.'),
    ('ESAB Gas Free E71T-GS · 1,0 mm × 1 kg', ['/soldadoras/alambre-flux/'], 'Presentación y diámetro exactos; la oferta de 0,8 mm × 5 kg es otra alternativa.'),
    ('Hyundai HHY2200F', ['/generadores/hyundai/'], 'Sufijo F documentado; no asignar automáticamente el referido HHY2200 sin sufijo.'),
]:
    slot = slots.setdefault(model, dict(affiliate_url='', guides=guides, configuration=detail))
    slot['guides'] = guides
# Enlaces recibidos: se conservan como registro, fuera de la lista de pendientes.
received = {'Gamma G2801AR':'https://meli.la/1vR4xKe', 'Gamma G2803AR':'https://meli.la/1jaQvxd', 'Lüsqtoff LC-2550VS':'https://meli.la/1Rjz39S', 'Lüsqtoff LCS50-8':'https://meli.la/27nVFRy', 'Lüsqtoff LCS100-8':'https://meli.la/21fBeVj'}
for model, url in received.items():
    slots[model]['affiliate_url'] = url
slots['Lüsqtoff LC40100-8'] = dict(affiliate_url='https://meli.la/1GRiWbV',guides=['/compresores/100-litros/','/compresores/lusqtoff-100-litros/'],configuration='100 L, 220 V, mando directo; distinto de LC40200-8 de 200 L y 380 V.')
for model in ('Einhell TE-AC 270/50 Silent','Einhell TE-AC 430/90/10'):
    slots[model]['availability_review']='2026-10-02: no se encontró publicación activa exacta confirmada en Mercado Libre Argentina. Conserva ficha documental.'
path.write_text(json.dumps(slots, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
lines = ['# Enlaces de afiliado para completar', '', 'Pegá el enlace junto al modelo. Los enlaces se incorporan después de comprobar modelo, variante y kit. Este archivo administrativo no muestra botones vacíos en la web.', '', '| Modelo y presentación | Enlace de afiliado | Qué confirmar |', '| --- | --- | --- |']
for model, slot in slots.items():
    if slot['affiliate_url']:
        continue
    lines.append(f"| {model} | {slot['affiliate_url']} | {slot.get('configuration', 'Código y contenido de la publicación.')} |")
(ROOT/'afiliados-pendientes.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
print(sum(not slot['affiliate_url'] for slot in slots.values()), 'espacios pendientes;',sum(bool(slot['affiliate_url']) for slot in slots.values()),'recibidos')
