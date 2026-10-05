"""Dated documentary evidence and reproducible publication snapshots."""
import hashlib
import json
import re
import unicodedata
from pathlib import Path
from functools import lru_cache

DATA = Path(__file__).resolve().parent / 'data'


def plain(value):
    return ''.join(c for c in unicodedata.normalize('NFKD', value.lower()) if not unicodedata.combining(c))


def compact(value):
    return re.sub(r'[^a-z0-9]', '', plain(value))


@lru_cache(maxsize=1)
def sources():
    path = DATA / 'documentary_sources.json'
    return {r['url']: r for r in json.loads(path.read_text(encoding='utf-8'))['sources']} if path.exists() else {}


def source_record(url):
    return sources().get(url, {})


@lru_cache(maxsize=512)
def text_for_code(url, code):
    record = source_record(url)
    if record.get('status') != 'recuperado':
        return '', False
    text = (DATA / record['text_file']).read_text(encoding='utf-8')
    identity = compact(code)
    matched = bool(identity and identity in compact(text))
    if matched and record.get('format') == 'pdf':
        pages = re.split(r'\[PÁGINA \d+\]', text)
        text = '\n'.join(page for page in pages if identity in compact(page))
    return text, matched


def assess(tool, spec):
    """Record conservative textual concordance, never certify performance.

    Identity is checked in document content, not its URL. A value must occur
    beside its physical unit. Missing/ambiguous content is a closed exclusion.
    """
    from tallerlab_data.quality import source_type_for
    record = source_record(spec.source_url)
    spec.source_type = source_type_for(spec.source_url, spec.source_name)
    if spec.source_type == 'referencia_externa' and record.get('format') == 'pdf':
        spec.source_type = 'documento_en_tercero'
    spec.evidence_reference = ''
    spec.evidence_excerpt = ''
    spec.document_page = None
    spec.condition_status = 'sin_respaldo'
    if record.get('status') != 'recuperado':
        spec.documentary_status = 'sin_respaldo'
        return
    text, identity_matches = text_for_code(spec.source_url, tool.mpn)
    # Bosch pages print part numbers with punctuation/spaces; exact MPN
    # removes those separators. No matching by model family or URL.
    if not identity_matches:
        spec.documentary_status = 'identidad_no_coincidente'
        return
    spec.evidence_reference = record['text_sha256']
    if spec.source_type in {'comercio', 'referencia_externa'}:
        spec.documentary_status = 'referencia_comercial'
        return
    raw = plain(re.sub(r'\([^)]*\)', '', spec.raw_value)).strip()
    values = re.findall(r'(?<![\w])\d+(?:[.,]\d+)?', raw)
    # Search the unit of the original observation. A converted unit with the
    # original number would describe a different quantity (360 L/h != 360 L/min).
    units = [spec.raw_unit] if spec.raw_unit else []
    # Full literal observations are preferable; a scalar comparison also
    # needs its unit adjacent so unrelated numbers cannot serve as evidence.
    normalized_text = plain(text)
    literal = re.sub(r'\s+', ' ', raw).strip()
    match = re.search(re.escape(literal), re.sub(r'\s+', ' ', normalized_text)) if len(literal) > 2 else None
    if literal in {'presente', 'incluido', 'incluida', 'si', 'no'}:
        match = None
    if not match and len(values) == 1:
        value = values[0]
        number = re.escape(value).replace(',', '[.,]').replace(r'\.', '[.,]')
        from tallerlab_data.pipeline import _clean_number_locale
        scalar = _clean_number_locale(value)
        if scalar is not None:
            if scalar.is_integer():
                digits = str(int(scalar))
                number = (digits[:-3] + r'[.,\s]?' + digits[-3:] if len(digits) > 3 else digits) + r'(?:[.,]0+)?'
            else:
                number = re.escape(str(scalar)).replace(r'\.', '[.,]') + '0*'
        aliases = {'w': r'(?:w|watts?)', 'kg': r'kg', 'bar': r'bar', 'nm': r'n\s*[·.]?\s*m', 'rpm': r'(?:rpm|r/min|min[−-]?1)', 'j': r'j', 'l': r'(?:l|litros?)', 'l/min': r'(?:l\s*/\s*min|lpm)', 'l/h': r'l\s*/\s*h'}
        unit_patterns = [aliases.get(plain(u), re.escape(plain(u))) for u in units if u]
        if unit_patterns:
            match = re.search(r'(?<![\d.,])'+number+r'\s*(?:'+'|'.join(unit_patterns)+r')(?![a-z])', normalized_text)
            if not match:
                # Spec tables often print the unit in a label column and may
                # qualify the figure: "(bar) 20 - max. 130", "(l/h) max. 420".
                # Only a qualifier or a range start may sit between unit and
                # number, so an unrelated figure cannot be borrowed.
                qualifier = r'(?:(?:max|maximo|maxima|min|minimo|minima|aprox|hasta|nominal)\.?\s*)?'
                range_start = r'(?:\d+(?:[.,]\d+)?\s*(?:-|a|hasta)\s*)?'
                match = re.search(r'\((?:'+'|'.join(unit_patterns)+r')\)\s*'+range_start+qualifier+number+r'(?![\d.,])', normalized_text)
    if not match and literal not in {'presente', 'incluido', 'incluida', 'si', 'no'}:
        match = _structured_match(spec.raw_value, normalized_text)
    if match:
        spec.documentary_status = 'concordancia_textual'
        # Keep factual match, not a large copyrighted document excerpt.
        spec.evidence_excerpt = match.group(0)[:100]
        if record.get('format') == 'pdf':
            full_text = (DATA / record['text_file']).read_text(encoding='utf-8')
            parts = re.split(r'\[PÁGINA (\d+)\]', full_text)
            pages = []
            fact = re.sub(r'\s+', ' ', match.group(0))
            for index in range(1, len(parts), 2):
                page = parts[index+1]
                if compact(tool.mpn) in compact(page) and fact in re.sub(r'\s+', ' ', plain(page)):
                    pages.append(parts[index])
            spec.document_page = ', '.join(pages) or None
        spec.consultation_date = record['checked_at'][:10]
        # Standards and test pressure must actually occur in the source;
        # neither seed notes nor a marketing label establish test conditions.
        condition = plain(spec.condition + ' ' + (spec.notes or ''))
        required = re.findall(r'(?:epta|iso\s*\d+|en\s*\d+(?:-\d+)*|\d+(?:[.,]\d+)?\s*(?:bar|psi))', condition)
        spec.condition_status = ('sin_protocolo_especifico' if not required else
                                 'referencias_presentes' if all(compact(token) in compact(normalized_text) for token in required) else 'sin_respaldo')
    else:
        spec.documentary_status = 'sin_respaldo'


def snapshot_payload():
    from tallerlab_data import storage
    return {'schema_version': 1, 'scope': 'Investigación documental, sin ensayos propios',
            'tools': [t.to_dict() for t in storage.list_tools()],
            'candidates': [dict(c) for c in storage.list_candidates()],
            'corrections': [dict(c) for c in storage.list_corrections()]}


def export_snapshot():
    payload = snapshot_payload()
    public = {key: value for key, value in payload.items() if key != 'candidates'}
    canonical = json.dumps(public, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    payload['version'] = hashlib.sha256(canonical.encode()).hexdigest()
    return payload


def write_snapshot():
    payload = export_snapshot()
    path = DATA / 'catalog_snapshot.json'
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    temp.replace(path)
    return payload['version']


def evidence_source_label(spec, record=None):
    """Name the document a value was actually located in.

    Seed labels sometimes name a manual page ("Manual X (pág. 14)") while the
    located text comes from the manufacturer's web page; the label must follow
    the evidence, not the seed.
    """
    record = record if record is not None else (source_record(spec.source_url) if getattr(spec, 'source_url', '') else {})
    label = re.sub(r'\s*\((?:p[áa]g\.?|p[áa]gina)\s*[^)]*\)', '', getattr(spec, 'source_name', '') or '').strip() or 'Documento'
    if record.get('status') == 'recuperado' and record.get('format') == 'html' and 'manual' in label.lower():
        title = (record.get('title') or '').replace(' | ', ' — ').strip()
        return f"{title} (página web)" if title else 'Página web del fabricante'
    return label


# --- Structured matching -------------------------------------------------
# Manufacturers print the same declared figure in different shapes: a range
# ("20 a 120 A" / "flux: 20 a 120 a"), a unit label column ("(bar) 20 - max.
# 130"), an equivalent in brackets ("8 bar (115 PSI)") or two units for one
# quantity ("2,5 HP / 1750 W"). Every number of the observation must be found
# beside its own unit; nothing is inferred from a figure without its unit.
_UNIT_ALIASES = {
    'w': r'(?:w|watts?)', 'kw': r'kw', 'kva': r'kva', 'hp': r'(?:hp|cv)',
    'v': r'v', 'a': r'(?:a|amp|amperes?|amper)', 'kg': r'(?:kg|kilos?)',
    'bar': r'bar', 'psi': r'psi', 'mpa': r'mpa', 'nm': r'n\s*[·.]?\s*m',
    'rpm': r'(?:rpm|r\s*/\s*min|r\.\s*p\.\s*m\.?|min[−-]?1)',
    'gpm': r'(?:gpm|ipm|bpm|golpes\s*/\s*min)', 'ipm': r'(?:ipm|gpm|bpm)',
    'j': r'(?:j|joules?)', 'l': r'(?:l|lts?\.?|litros?)', 'mm': r'mm', 'm': r'm',
    'l/min': r'(?:l\s*/\s*min|lpm)', 'l/h': r'l\s*/\s*h', 'db(a)': r'db\s*\(?a\)?',
}
_QUAL = r'(?:(?:max|maximo|maxima|min|minimo|minima|aprox|hasta|nominal)\.?\s*)?'
_SEP = r'\s*(?:-|–|—|a|hasta|/)\s*'


def _num_pattern(value):
    from tallerlab_data.pipeline import _clean_number_locale
    scalar = _clean_number_locale(value)
    if scalar is None:
        return None
    if scalar.is_integer():
        digits = str(int(scalar))
        return (digits[:-3] + r'[.,\s]?' + digits[-3:] if len(digits) > 3 else digits) + r'(?:[.,]0+)?'
    return re.escape(str(scalar)).replace(r'\.', '[.,]') + '0*'


def _parts(raw):
    """Split an observation into (numbers, unit) claims that must all be found."""
    text = plain(raw).replace('–', '-').replace('—', '-')
    chunks = [text]
    bracket = re.findall(r'\(([^)]*)\)', text)
    base = re.sub(r'\([^)]*\)', ' ', text)
    if bracket:
        chunks = [base] + bracket
    claims = []
    for chunk in chunks:
        pieces = re.split(r'\s+/\s+(?=\d)', chunk)
        parsed = []
        for piece in pieces:
            m = re.match(r'^\s*(\d+(?:[.,]\d+)?)\s*(?:-|a|hasta)?\s*(\d+(?:[.,]\d+)?)?\s*([a-z/()°]+(?:/[a-z]+)?)?', piece.strip())
            if not m:
                parsed.append(None)
                continue
            unit = (m.group(3) or '').strip('.').strip()
            parsed.append(([n for n in (m.group(1), m.group(2)) if n], unit))
        if any(p is None for p in parsed):
            continue
        # "42 / 27 Nm": a bare figure shares the unit printed after it.
        for i in range(len(parsed) - 2, -1, -1):
            if not parsed[i][1]:
                parsed[i] = (parsed[i][0], parsed[i + 1][1])
        if any(unit not in _UNIT_ALIASES for _, unit in parsed):
            continue
        claims.extend(parsed)
    return claims


def _find_claim(numbers, unit, text):
    nums = [_num_pattern(n) for n in numbers]
    if any(n is None for n in nums):
        return None
    u = _UNIT_ALIASES[unit]
    body = _SEP.join(f'{_QUAL}{n}' for n in nums)
    for pattern in (r'(?<![\d.,])' + body + r'\s*' + u + r'(?![a-z])',
                    r'\(\s*' + u + r'\s*\)\s*' + body + r'(?![\d.,])',
                    r'(?<![\d.,])' + body + r'\s*\(\s*' + u + r'\s*\)'):
        found = re.search(pattern, text)
        if found:
            return found
    return None


def _structured_match(raw_value, normalized_text):
    claims = _parts(raw_value or '')
    if not claims:
        return None
    text = re.sub(r'\s+', ' ', normalized_text)
    # Brackets hold an equivalent of the main figure: one form suffices.
    # Slash-separated parts are separate claims: all must be present.
    groups = {}
    base = re.sub(r'\([^)]*\)', ' ', plain(raw_value))
    main_count = len([c for c in _parts(base)])
    main, equivalents = claims[:main_count], claims[main_count:]
    found = [_find_claim(n, u, text) for n, u in main]
    if main and all(found):
        return found[0]
    if len(main) == 1:
        for numbers, unit in equivalents:
            hit = _find_claim(numbers, unit, text)
            if hit:
                return hit
    return None
