"""Identidad compartida por HTML y feeds; contradicciones nunca se resuelven por título."""
import re
import unicodedata

def normalized(value):
    text = unicodedata.normalize('NFKD', str(value or ''))
    return re.sub(r'[^A-Z0-9]', '', ''.join(c for c in text if not unicodedata.combining(c)).upper())

def identity_error(target, mpn='', title='', voltage='', condition='', kit=''):
    if target is None:
        return 'Producto desconocido'
    expected = normalized(target.mpn)
    if mpn and normalized(mpn) != expected:
        return 'Código de fabricante contradictorio'
    if not mpn:
        pattern = r'(?<![A-Za-z0-9])' + r'[-\s]*'.join(re.escape(c) for c in expected) + r'(?![A-Za-z0-9-])'
        if normalized(target.brand) not in normalized(title) or not re.search(pattern, title, re.I):
            return 'Identidad sin código exacto verificable'
    expected_volts = set(re.findall(r'\b\d{2,3}\b', str(target.voltage)))
    offered_volts = set(re.findall(r'(\d{2,3})\s*[vV]\b', title)) | set(re.findall(r'\b\d{2,3}\b', str(voltage)))
    if expected_volts and offered_volts and not offered_volts.issubset(expected_volts):
        return 'Tensión incompatible'
    if target.item_condition == 'nuevo' and any(v in str(condition).lower() for v in ('used','refurbished','usado','reacondicionado')):
        return 'Condición incompatible'
    offered = (title+' '+str(kit)).lower()
    expected_kit = target.kit_content.lower()
    if ('sin batería' in offered or 'solo cuerpo' in offered) and 'bater' in expected_kit and 'sin batería' not in expected_kit:
        return 'Contenido del kit incompatible'
    return None
