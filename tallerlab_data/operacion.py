"""Operación de ediciones documentales: cerrar, verificar y respaldar.

Publicación: el JSON versionado viaja con el código. En Vercel, SQLite se
reconstruye en almacenamiento temporal desde ese JSON, sin prometer que las
escrituras de una instancia serverless actualicen el catálogo publicado.
"""
import argparse
import json
import re
import shutil
import copy
import sqlite3
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
from tallerlab_data import storage
from tallerlab_data.documentary import assess, write_snapshot, DATA, sources


def close_edition():
    storage.init_db()
    backup = DATA / 'respaldos'
    backup.mkdir(exist_ok=True)
    with storage.get_connection() as original, sqlite3.connect(backup / ('catalogo-' + datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S') + '.db')) as copied:
        original.backup(copied)
    date = datetime.now(timezone.utc).date().isoformat()
    tools = storage.list_tools()
    history_path = DATA / 'editorial_history.json'
    if not history_path.exists():
        history_path.write_text(json.dumps({t.slug: {'summary': t.summary, 'limits_and_warnings': t.limits_and_warnings} for t in tools}, ensure_ascii=False, indent=2), encoding='utf-8')
    alternatives = json.loads((DATA / 'additional_sources.json').read_text(encoding='utf-8'))
    outcomes = Counter()
    reviewed_path = DATA / 'reviewed_observations.json'
    reviewed = json.loads(reviewed_path.read_text(encoding='utf-8')) if reviewed_path.exists() else []
    # Seed values contradicted by the recovered manufacturer document are
    # corrected here and logged in the public corrections register.
    fixes_path = DATA / 'correcciones_documentales.json'
    documentary_fixes = json.loads(fixes_path.read_text(encoding='utf-8')) if fixes_path.exists() else []
    for tool in tools:
        for observation in reviewed:
            if observation['slug'] == tool.slug and observation['spec_key'] not in tool.specs:
                added = copy.deepcopy(tool.specs[observation['base_key']])
                for key, value in observation.items():
                    if key not in {'slug', 'base_key'}:
                        setattr(added, key, value)
                added.status = 'declarado'
                assess(tool, added)
                if added.documentary_status != 'concordancia_textual':
                    raise ValueError(f'La incorporación revisada no localiza su evidencia: {tool.slug}:{added.spec_key}')
                tool.specs[added.spec_key] = added
                storage.add_correction(date, tool.slug, added.spec_key, 'Sin observación separada', added.raw_value, 'Incorporación documental con identidad, valor y fuente conservados; no ensayo físico.', added.source_url)
                if not any(s.get('url') == added.source_url for s in tool.primary_sources):
                    tool.primary_sources.append({'url': added.source_url, 'label': added.source_name})
        for fix in documentary_fixes:
            spec = tool.specs.get(fix['spec_key']) if fix['slug'] == tool.slug else None
            if spec is None or spec.raw_value != fix['from']:
                continue
            storage.add_correction(date, tool.slug, spec.spec_key, spec.raw_value, fix['raw_value'], fix['reason'], spec.source_url)
            spec.raw_value = fix['raw_value']
            spec.normalized_value = fix.get('normalized_value')
            if fix.get('condition'):
                spec.condition = fix['condition']
        for spec in tool.specs.values():
            if tool.slug == 'bosch-ghp-220' and spec.spec_key == 'potencia' and spec.raw_value == '2200 W':
                storage.add_correction(date, tool.slug, spec.spec_key, spec.raw_value, '2100 W', 'La ficha Bosch recuperada declara 2100 W en la descripción técnica del motor. No se extrapola potencia desde el nombre GHP 220.', spec.source_url)
                spec.raw_value, spec.normalized_value = '2100 W', 2100.0
            if re.search(r'\d+(?:[.,]\d+)?\s*(?:[–—-]|a|hasta)\s*\d', spec.raw_value) or re.search(r'\d\s*/\s*\d', spec.raw_value):
                spec.normalized_value = None
            assess(tool, spec)
            if spec.documentary_status in {'sin_respaldo', 'identidad_no_coincidente'}:
                for url in alternatives:
                    if sources().get(url, {}).get('status') != 'recuperado':
                        continue
                    alternate = copy.deepcopy(spec)
                    alternate.source_url = url
                    alternate.source_name = 'Manual del fabricante recuperado' if 'article_attachments' in url else 'Catálogo del fabricante recuperado'
                    assess(tool, alternate)
                    if alternate.documentary_status == 'concordancia_textual':
                        storage.add_correction(date, tool.slug, spec.spec_key + ':fuente', spec.source_url, url, 'Se recuperó una fuente alternativa con el código de producto y el valor citado; no se extrapola a otros códigos.', url)
                        spec.source_url, spec.source_name = alternate.source_url, alternate.source_name
                        spec.source_type = alternate.source_type
                        spec.documentary_status, spec.evidence_reference, spec.evidence_excerpt = alternate.documentary_status, alternate.evidence_reference, alternate.evidence_excerpt
                        spec.consultation_date = alternate.consultation_date
                        spec.condition_status = alternate.condition_status
                        spec.document_page = alternate.document_page
                        if not any(s.get('url') == url for s in tool.primary_sources):
                            tool.primary_sources.append({'url': url, 'label': alternate.source_name})
                        break
            outcomes[spec.documentary_status] += 1
        # Historical values without retained captures are archived, not queued.
        for offer in tool.offers:
            if not offer.evidence_reference:
                offer.verification_status = 'archivado_sin_evidencia'
        supported = sum(s.documentary_status == 'concordancia_textual' for s in tool.specs.values())
        tool.summary = f'Ficha documental de {tool.brand} {tool.model_name}. {supported} de {len(tool.specs)} observaciones tienen concordancia textual con una fuente recuperada; consultá el código de producto y la variante.'
        tool.limits_and_warnings = [
            'Las especificaciones declaradas no acreditan rendimiento, durabilidad ni resultados de ensayo propios.',
            'Confirmá alimentación, código de producto, accesorios y requisitos de instalación en el manual de tu unidad. Los registros históricos de variantes y kits no certifican esa correspondencia.',
            'Las referencias excluidas por falta de respaldo no se utilizan para establecer equivalencias numéricas.',
        ]
        tool.last_reviewed = date
        storage.save_tool(tool)
    with storage.get_connection() as conn:
        for candidate in storage.list_candidates(include_test=True):
            if candidate['status'] in {'pendiente', 'validado_para_revision'}:
                reason = 'Excluido de esta edición: ' + candidate['rejection_or_pending_reason'].replace('Pendiente de verificación de lote físico importado en Argentina.', 'No se establece correspondencia documental con un lote argentino; el catálogo no realiza ensayos físicos.')
                conn.execute('UPDATE candidates SET status=?, rejection_or_pending_reason=? WHERE id=?', ('excluido', reason, candidate['id']))
            elif candidate['status'] == 'excluido' and 'pendiente de contrastar' in candidate['rejection_or_pending_reason']:
                reason = candidate['rejection_or_pending_reason'].replace('pendiente de contrastar con código', 'no se establece equivalencia con el código')
                conn.execute('UPDATE candidates SET rejection_or_pending_reason=? WHERE id=?', (reason, candidate['id']))
        conn.commit()
    version = write_snapshot()
    return {'models': len(tools), 'observations': sum(outcomes.values()), 'documentary_outcomes': dict(outcomes), 'version': version}


def verify():
    tools = storage.list_tools()
    issues = []
    for tool in tools:
        for spec in tool.specs.values():
            if not spec.documentary_status:
                issues.append(f'{tool.slug}:{spec.spec_key}: decisión documental ausente')
            if spec.documentary_status == 'concordancia_textual' and (not spec.evidence_reference or not spec.evidence_excerpt):
                issues.append(f'{tool.slug}:{spec.spec_key}: falta evidencia')
    if any(c['status'] == 'pendiente' for c in storage.list_candidates(include_test=True)):
        issues.append('Hay decisiones de incorporación sin cerrar')
    if any(o.verification_status == 'pendiente_relevamiento' for t in tools for o in t.offers):
        issues.append('Hay cotizaciones sin decisión editorial')
    return {'models': len(tools), 'issues': issues}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['cerrar-edicion', 'verificar'])
    args = parser.parse_args()
    result = close_edition() if args.command == 'cerrar-edicion' else verify()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result.get('issues'):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
