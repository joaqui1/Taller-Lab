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
             '## Tanda amoladoras-01', '']
    for row in reviewed:
        lines.append(f"- [{row['path']}](https://www.tallerlab.com.ar{row['path']}): {row['editorial_review']['notes']}")
    lines += ['', '## Inventario por URL', '', '| URL | Estructura y enlaces | Revisión editorial de esta ronda |', '| --- | --- | --- |']
    for row in rows:
        structural = 'Sin fallas detectadas' if not row['issues'] else '; '.join(row['issues'])
        status = row['editorial_status']
        if (row.get('editorial_review') or {}).get('full_claim_verification') == 'pendiente':
            status += '; contraste completo de cifras pendiente'
        lines.append(f"| [{row['path']}](https://www.tallerlab.com.ar{row['path']}) | {structural} | {status} |")
    lines += ['', '## Fuentes externas de amoladoras', '',
              'Se sondearon 163 direcciones únicas. No se detectaron respuestas 404. Seis consultas dieron bloqueo HTTP 403 o error de certificado: cinco fichas fueron localizadas mediante consulta web; el folleto Norton se sustituyó por la dirección oficial completa que entrega el documento de cinco páginas. El resultado del sondeo y la resolución de cada caso están en qa-tanda-amoladoras.json. Los bloqueos de acceso no se interpretan como prueba de que un producto o documento no existe.', '',
              '## Próxima tanda', '',
              'Completar los contrastes pendientes de DeWalt, banco e inalámbricas; después continuar con Bosch, Lusqtoff, diámetros grandes, Skil y accesorios. El registro usa una huella del cuerpo de cada artículo: una modificación posterior invalida la coincidencia con la lectura registrada.', '']
    (ROOT / 'revision-guias-por-tandas-2026-10-01.md').write_text('\n'.join(lines), encoding='utf-8')
    print(f'{len(rows)} URLs registradas; {len(reviewed)} lecturas editoriales. Revisión completa pendiente.')


if __name__ == '__main__':
    main()
