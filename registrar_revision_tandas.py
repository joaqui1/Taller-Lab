"""Resume evidencia actual por URL; un control técnico no aprueba el contenido."""
import json
from pathlib import Path

ROOT = Path(__file__).parent


def main():
    reports = [json.loads(p.read_text(encoding='utf-8')) for p in sorted(ROOT.glob('qa-tanda-*.json'))]
    rows = [row for report in reports for row in report['rows']]
    reviewed = [row for row in rows if row['editorial_status'] == 'revisión editorial registrada']
    lines = ['# Revisión de guías por tandas — 01/10/2026', '',
             f'Inventario técnico actual: {len(rows)} guías. Evaluación registrada de selección y comparación: {len(reviewed)}. Cada registro indica su alcance: lectura editorial o evaluación de tablas y modelos. No equivale a certificar todas las cifras ni el stock; los controles de imágenes e interacciones se conservan por separado.', '',
             'Se revisan por URL la respuesta a la consulta, las alternativas, la identidad de cada modelo, el montaje y las condiciones de uso, la procedencia de cifras, la navegación, las imágenes y las interacciones. Los controles técnicos generales previos se conservan como evidencia separada.', '',
             ]
    batches = sorted({row['editorial_review']['batch'] for row in reviewed})
    for batch in batches:
        lines += [f'## Tanda {batch}', '']
        for row in reviewed:
            if row['editorial_review']['batch'] == batch:
                lines.append(f"- [{row['path']}](https://www.tallerlab.com.ar{row['path']}): {row['editorial_review']['notes']}")
        lines.append('')
    lines += ['', '## Inventario por URL', '', '| URL | Estructura y enlaces | Revisión editorial de esta ronda |', '| --- | --- | --- |']
    for row in rows:
        structural = 'Sin fallas detectadas' if not row['issues'] else '; '.join(row['issues'])
        status = row['editorial_status']
        if (row.get('editorial_review') or {}).get('full_claim_verification') == 'pendiente':
            status += '; contraste completo de cifras pendiente'
        lines.append(f"| [{row['path']}](https://www.tallerlab.com.ar{row['path']}) | {structural} | {status} |")
    probes = [source for report in reports for source in report.get('sources', [])]
    unique = len({source['url'] for source in probes})
    historical = sum(len(report.get('source_history', [])) for report in reports)
    lines += ['', '## Fuentes externas por categoría', '',
              f'Los informes conservan {len(probes)} sondeos de {unique} direcciones distintas y {historical} registros de direcciones retiradas o sustituidas en source_history. Un sondeo verifica acceso, destino y tipo de documento, no todas las afirmaciones del artículo. Los bloqueos HTTP o de certificado requieren comprobación independiente; no prueban que el producto o documento no exista.', '',
              '| Categoría | Sondeos | Alertas de acceso o destino conservadas |',
              '| --- | --- | --- |']
    for report in reports:
        sources = report.get('sources', [])
        alerts = sum(source.get('status') != 200 or source.get('generic_redirect', False) or source.get('soft_not_found', False) or source.get('unexpected_document_type', False) or source.get('document_signature_valid') is False for source in sources)
        lines.append(f"| {report['section']} | {len(sources)} | {alerts} |")
    lines += ['', 'Se corrigió la dirección oficial Makita DHS710Z y se retiró el enlace comercial Hyundai HHY9500LE que redirigía a una portada. Su precio queda identificado como histórico, sin confirmar stock actual. El folleto Norton fue sustituido por la URL oficial completa. Las alertas originales se mantienen como evidencia del sondeo.', '',
              '## Alcance y seguimiento', '',
              'La revisión de selección y comparaciones cubre las 179 guías. Los registros de evaluación de tablas no afirman lectura integral de todos los párrafos. Los contrastes completos de especificaciones señalados como pendientes conservan ese estado. El registro usa una huella del cuerpo de cada artículo para detectar cambios posteriores.', '']
    (ROOT / 'revision-guias-por-tandas-2026-10-01.md').write_text('\n'.join(lines), encoding='utf-8')
    print(f'{len(rows)} URLs; {len(reviewed)} evaluaciones registradas con alcance individual. Los contrastes de cifras pendientes conservan su estado.')


if __name__ == '__main__':
    main()
