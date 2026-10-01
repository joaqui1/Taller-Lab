"""Resume evidencia actual por URL; un control técnico no aprueba el contenido."""
import json
from pathlib import Path

ROOT = Path(__file__).parent


def main():
    reports = [json.loads(p.read_text(encoding='utf-8')) for p in sorted(ROOT.glob('qa-tanda-*.json'))]
    rows = [row for report in reports for row in report['rows']]
    reviewed = [row for row in rows if row['editorial_status'] == 'revisión editorial registrada']
    lines = ['# Revisión de guías por tandas — 01/10/2026', '',
             f'Inventario técnico actual: {len(rows)} guías. Lectura editorial registrada en esta ronda: {len(reviewed)}. La revisión completa sigue en curso; un HTTP 200 y una tabla visible no certifican las especificaciones ni el stock de un producto.', '',
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
    lines += ['', '## Fuentes externas por categoría', '',
              f'Los informes conservan {len(probes)} sondeos de {unique} direcciones distintas. Incluyen el historial de direcciones sustituidas. Un sondeo verifica acceso y destino, no todas las afirmaciones del artículo. Los bloqueos HTTP o de certificado requieren comprobación independiente; no prueban que el producto o documento no exista.', '',
              '| Categoría | Sondeos | Alertas de acceso o destino conservadas |',
              '| --- | --- | --- |']
    for report in reports:
        sources = report.get('sources', [])
        alerts = sum(source.get('status') != 200 or source.get('generic_redirect', False) for source in sources)
        lines.append(f"| {report['section']} | {len(sources)} | {alerts} |")
    lines += ['', 'Se corrigió la dirección oficial Makita DHS710Z y se retiró el enlace comercial Hyundai HHY9500LE que redirigía a una portada. Su precio queda identificado como histórico, sin confirmar stock actual. El folleto Norton fue sustituido por la URL oficial completa. Las alertas originales se mantienen como evidencia del sondeo.', '',
              '## Próxima tanda', '',
              'Continuar la lectura por artículo y contrastar las alternativas con su finalidad, material, instalación y compatibilidad. Completar las cifras pendientes antes de declarar terminada la revisión editorial. El registro usa una huella del cuerpo de cada artículo: una modificación posterior invalida la coincidencia con la lectura registrada.', '']
    (ROOT / 'revision-guias-por-tandas-2026-10-01.md').write_text('\n'.join(lines), encoding='utf-8')
    print(f'{len(rows)} URLs registradas; {len(reviewed)} lecturas editoriales. Revisión completa pendiente.')


if __name__ == '__main__':
    main()
