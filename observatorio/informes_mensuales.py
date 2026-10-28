"""Cálculo de informes mensuales del observatorio a partir del historial publicado.

Este módulo usa solamente la biblioteca estándar para poder ejecutarse en el
entorno gratuito y en el CLI sin cargar el recolector.
"""
import calendar
import csv
import io
import json
import re
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_HISTORY = ROOT / 'assets' / 'datos' / 'precios-observatorio.json'
DEFAULT_MANIFEST = Path(__file__).resolve().parent / 'piloto_gratuito.json'
DEFAULT_IPC = Path(__file__).resolve().parent / 'ipc_indec.json'
EDITORIAL_DIR = Path(__file__).resolve().parent / 'informes'
MONTH_RE = re.compile(r'^\d{4}-(0[1-9]|1[0-2])$')
EDITORIAL_RE = re.compile(r'^\d{4}-(0[1-9]|1[0-2])\.json$')
OFFER_KINDS = ('offer_ended', 'offer_started', 'offer_changed')


def validate_month(month):
    if not isinstance(month, str) or not MONTH_RE.fullmatch(month):
        raise ValueError('El mes debe tener formato AAAA-MM')
    return month


def _day_of(observation):
    """Usa el día argentino ya publicado; observaciones nuevas siempre lo traen."""
    value = observation.get('day_art')
    if value:
        try:
            return date.fromisoformat(value)
        except (TypeError, ValueError):
            return None
    value = str(observation.get('observed_at') or '')[:10]
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _priced(observation):
    if observation.get('availability') != 'disponible' or not observation.get('price_ars'):
        return False
    try:
        return Decimal(str(observation['price_ars'])) > 0
    except (InvalidOperation, TypeError, ValueError):
        return False


def _median(values):
    if not values:
        return None
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / Decimal(2)


def load_ipc(path=DEFAULT_IPC):
    """Lee IPC cargado por el dueño; no completa ni estima meses faltantes."""
    try:
        data = json.loads(Path(path).read_text(encoding='utf-8'))
    except FileNotFoundError:
        return {}
    if not isinstance(data, dict):
        raise ValueError('ipc_indec.json debe contener un objeto JSON')
    months = data.get('meses', {})
    if not isinstance(months, dict):
        raise ValueError('ipc_indec.json: "meses" debe ser un objeto')
    result = {}
    for month, item in months.items():
        validate_month(month)
        if not isinstance(item, dict):
            raise ValueError(f'IPC {month}: se esperaba un objeto')
        try:
            value = Decimal(str(item['variacion_mensual_pct']))
        except (KeyError, InvalidOperation, TypeError, ValueError) as exc:
            raise ValueError(f'IPC {month}: falta una variación mensual válida') from exc
        if not value.is_finite() or value <= -100:
            raise ValueError(f'IPC {month}: la variación debe ser finita y mayor a -100%')
        link = str(item.get('url', '')).strip()
        if not re.fullmatch(r'https?://[^\s<>]+', link):
            raise ValueError(f'IPC {month}: falta el enlace de la publicación del INDEC')
        result[month] = {'variacion_mensual_pct': value, 'url': link}
    return result


def calculate_report(month, history, manifest, ipc_by_month=None):
    """Calcula medianas del mes con cobertura en ambas semanas extremas.

    Una comparación exige precios disponibles en los primeros siete y últimos
    siete días calendario. Se compara el primer y el último precio del mes. Los
    movimientos que la página actual clasifica como ofertas no entran en la
    mediana de precio publicado. Los fines de oferta se cuentan como transiciones
    consecutivas dentro del mes, con la misma clasificación.
    """
    validate_month(month)
    year, month_number = map(int, month.split('-'))
    last_day = calendar.monthrange(year, month_number)[1]
    start_date = date(year, month_number, 1)
    end_date = date(year, month_number, last_day)
    first_week_end = date(year, month_number, min(7, last_day))
    last_week_start = date(year, month_number, max(1, last_day - 6))
    ipc_by_month = ipc_by_month or {}

    from observatorio.estatico import classify_change

    models = manifest.get('models', [])
    by_id = {model['id']: model for model in models}
    observed_by_id = {model_id: [] for model_id in by_id}
    for observation in history.get('observations', []):
        model_id = observation.get('model_id')
        day = _day_of(observation)
        if model_id not in observed_by_id or day is None or not (start_date <= day <= end_date):
            continue
        observed_by_id[model_id].append((day, observation))

    categories = {}
    for model in models:
        category = model['category']
        row = categories.setdefault(category, {
            'category': category,
            'models_in_sample': 0,
            'models_with_coverage': 0,
            'models_in_median': 0,
            'median_change_pct': None,
            'out_of_stock': 0,
            'offers_ended': 0,
            'real_median_change_pct': None,
            '_price_changes': [],
        })
        row['models_in_sample'] += 1

    comparisons = []
    month_observations = []
    for model in models:
        month_rows = sorted(observed_by_id[model['id']], key=lambda pair: (pair[0], pair[1].get('observed_at', '')))
        if not month_rows:
            continue
        month_observations.extend(observation for _, observation in month_rows)
        category_row = categories[model['category']]
        if month_rows[-1][1].get('availability') == 'agotado':
            category_row['out_of_stock'] += 1

        priced_rows = [(day, observation) for day, observation in month_rows if _priced(observation)]
        for (_, previous), (_, current) in zip(priced_rows, priced_rows[1:]):
            if classify_change(previous, current) == 'offer_ended':
                category_row['offers_ended'] += 1

        in_first_week = any(start_date <= day <= first_week_end for day, _ in priced_rows)
        in_last_week = any(last_week_start <= day <= end_date for day, _ in priced_rows)
        if not (in_first_week and in_last_week):
            continue

        start = priced_rows[0][1]
        end = priced_rows[-1][1]
        kind = classify_change(start, end)
        change = (Decimal(end['price_ars']) / Decimal(start['price_ars']) - 1) * 100
        category_row['models_with_coverage'] += 1
        if kind not in OFFER_KINDS:
            category_row['_price_changes'].append(change)
            category_row['models_in_median'] += 1
        comparisons.append({
            'model_id': model['id'],
            'brand': model['brand'],
            'model': model['model'],
            'variant': model.get('variant', ''),
            'category': model['category'],
            'model_path': _model_path(model),
            'start_at': start.get('observed_at', ''),
            'end_at': end.get('observed_at', ''),
            'start_price_ars': str(Decimal(start['price_ars'])),
            'end_price_ars': str(Decimal(end['price_ars'])),
            'change_pct': float(round(change, 4)),
            'movement_kind': kind,
        })

    ipc = ipc_by_month.get(month)
    for row in categories.values():
        median = _median(row.pop('_price_changes'))
        if median is not None:
            row['median_change_pct'] = float(round(median, 4))
            if ipc:
                real = ((Decimal(1) + median / 100) / (Decimal(1) + ipc['variacion_mensual_pct'] / 100) - 1) * 100
                row['real_median_change_pct'] = float(round(real, 4))

    categories = list(categories.values())
    result = {
        'schema_version': 1,
        'month': month,
        'coverage': {
            'first_week': [start_date.isoformat(), first_week_end.isoformat()],
            'last_week': [last_week_start.isoformat(), end_date.isoformat()],
            'price_change': 'Primer y último precio disponible del mes, para modelos con capturas con precio en ambas semanas extremas.',
            'offers': 'Las transiciones de oferta se excluyen de la mediana; los fines se cuentan entre capturas consecutivas del mes.',
        },
        'categories': categories,
        'comparisons': sorted(comparisons, key=lambda item: (item['category'], item['brand'], item['model'])),
        'models_with_capture': len({o['model_id'] for o in month_observations}),
        'capture_count': len(month_observations),
        'last_capture_at': max((o.get('observed_at', '') for o in month_observations), default=''),
        'ipc': ({'variacion_mensual_pct': str(ipc['variacion_mensual_pct']), 'url': ipc['url']} if ipc else None),
    }
    return result


def _model_path(model):
    import unicodedata
    text = unicodedata.normalize('NFKD', f"{model['brand']} {model['model']}")
    text = ''.join(char for char in text if not unicodedata.combining(char)).lower()
    slug = re.sub(r'[^a-z0-9]+', '-', text).strip('-')
    return f"/datos/precios/{model['category']}/{slug}/"


def report_csv(report, category_names=None):
    category_names = category_names or {}
    output = io.StringIO(newline='')
    writer = csv.writer(output)
    writer.writerow(['mes', 'categoria', 'modelos_en_muestra', 'modelos_con_cobertura',
                     'modelos_en_mediana', 'variacion_mediana_pct', 'agotados',
                     'ofertas_terminadas', 'ipc_indec_pct', 'variacion_real_mediana_pct'])
    ipc_value = report['ipc']['variacion_mensual_pct'] if report.get('ipc') else ''
    for row in report['categories']:
        writer.writerow([
            report['month'], category_names.get(row['category'], row['category']),
            row['models_in_sample'], row['models_with_coverage'], row['models_in_median'],
            '' if row['median_change_pct'] is None else row['median_change_pct'],
            row['out_of_stock'], row['offers_ended'], ipc_value,
            '' if row['real_median_change_pct'] is None else row['real_median_change_pct'],
        ])
    return output.getvalue()


def generate_report(month, history_path=DEFAULT_HISTORY, manifest_path=DEFAULT_MANIFEST,
                    ipc_path=DEFAULT_IPC):
    history = json.loads(Path(history_path).read_text(encoding='utf-8'))
    manifest = json.loads(Path(manifest_path).read_text(encoding='utf-8'))
    return calculate_report(month, history, manifest, load_ipc(ipc_path))


def editorial_reports(directory=EDITORIAL_DIR):
    """Devuelve solo notas completas con publicación autorizada explícitamente."""
    directory = Path(directory)
    if not directory.is_dir():
        return []
    reports = []
    for path in sorted(directory.iterdir()):
        if not EDITORIAL_RE.fullmatch(path.name):
            continue
        month = path.stem
        content = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(content, dict):
            raise ValueError(f'{path}: se esperaba un objeto JSON')
        if content.get('mes', month) != month:
            raise ValueError(f'{path}: el campo mes debe coincidir con el nombre del archivo')
        if content.get('publicado') is not True:
            continue
        reading = str(content.get('lectura_del_mes') or '').strip()
        if not reading:
            raise ValueError(f'{path}: completá lectura_del_mes antes de publicar')
        reports.append({'month': month, 'reading': reading})
    return reports


def cmd_report(args):
    """Función compartida por el subcomando del CLI."""
    report = generate_report(
        args.mes,
        args.history or DEFAULT_HISTORY,
        args.manifest or DEFAULT_MANIFEST,
        args.ipc or DEFAULT_IPC,
    )
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        output.with_suffix('.csv').write_text(report_csv(report), encoding='utf-8-sig', newline='')
        print(f'Informe calculado: {output} (CSV: {output.with_suffix(".csv")})')
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))
