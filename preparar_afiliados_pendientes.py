"""Consolida espacios de afiliado identificados, sin inventar enlaces de compra."""
import json
from pathlib import Path

ROOT = Path(__file__).parent
path = ROOT / 'afiliados-por-completar.json'
slots = json.loads(path.read_text(encoding='utf-8'))
for model, guides, detail in [
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
path.write_text(json.dumps(slots, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
lines = ['# Enlaces de afiliado para completar', '', 'Pegá el enlace junto al modelo. Los enlaces se incorporan después de comprobar modelo, variante y kit. Este archivo administrativo no muestra botones vacíos en la web.', '', '| Modelo y presentación | Enlace de afiliado | Qué confirmar |', '| --- | --- | --- |']
for model, slot in slots.items():
    lines.append(f"| {model} | {slot['affiliate_url']} | {slot.get('configuration', 'Código y contenido de la publicación.')} |")
(ROOT/'afiliados-pendientes.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
print(len(slots), 'espacios de afiliado preparados')
