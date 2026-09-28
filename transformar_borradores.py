"""Primera pasada editorial conservadora sobre todos los borradores Markdown.

No atribuye datos a fuentes que no fueron comprobadas y no habilita publicación.
Ejecutar sin argumentos para ver el alcance; --apply escribe y guarda respaldo ZIP.
"""

import argparse
import re
import zipfile
from pathlib import Path

from servidor_local import _ALL_DRAFTS


ROOT = Path(__file__).resolve().parent
BACKUP = ROOT / "respaldo-borradores-antes-transformacion.zip"
SOURCE_STATUS = (
    "<!-- CLASIFICACION_FUENTES_178 -->\n"
    "- **Documentación primaria:** pendiente de cotejar con cada dato y código de modelo.\n"
    "- **Información comercial:** los avisos y enlaces de búsqueda no prueban prestaciones técnicas.\n"
    "- **Seguridad:** confirmar indicaciones del manual y organismo pertinente antes de publicar.\n"
    "- **Opiniones:** no hay muestra de compradores documentada para esta revisión.\n\n"
)
LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
TABLE_LINE = re.compile(r"^\|(.+)\|\s*$")
OPINION_HEADING = re.compile(r"^##\s+.*\b(?:opiniones|reseñas|valoraciones|experiencias de compradores)\b.*$", re.I)
AFFILIATE = ("meli.la/", "listado.mercadolibre.com.ar/")


def quote_yaml(value):
    return '"' + value.replace('"', '\\"') + '"'


def get_table_topics(body):
    lines = body.splitlines()
    for index, line in enumerate(lines):
        if not TABLE_LINE.match(line) or index + 1 >= len(lines):
            continue
        if not re.match(r"^\|\s*:?-{3,}", lines[index + 1]):
            continue
        topics = []
        for row in lines[index + 2:]:
            if not TABLE_LINE.match(row):
                break
            label = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", row.strip().strip("|").split("|")[0])
            label = re.sub(r"[*_`$]", "", label).strip()
            label = re.sub(r"\\(?:text|mathbf)\{([^}]+)\}", r"\1", label)
            if label and len(label) <= 90 and label.lower() not in {t.lower() for t in topics}:
                topics.append(label)
            if len(topics) == 4:
                return topics
        if topics:
            return topics
    headings = re.findall(r"^##\s+(.+)$", body, re.M)
    return [h for h in headings if not re.search(r"mercado libre|precios|fuentes", h, re.I)][:4]


def strip_unattributed_experience(body):
    lines = body.splitlines()
    result = []
    removed_sections = 0
    removed_quotes = 0
    skip = False
    for line in lines:
        if line.startswith("## "):
            skip = bool(OPINION_HEADING.match(line))
            if skip:
                removed_sections += 1
                continue
        if skip:
            continue
        if re.match(r"^>\s*\*\*(?:Regla de taller|Experiencia de taller|Probamos)\b", line, re.I):
            removed_quotes += 1
            continue
        result.append(line)
    return "\n".join(result).rstrip(), removed_sections, removed_quotes


def transform(article):
    path = article["path"]
    original = path.read_text(encoding="utf-8-sig")
    if article.get("published") == "true":
        return None, (0, 0)
    if "<!-- AUDITORIA_EDITORIAL_178 -->" in original:
        updated = original
        if not re.search(r"^specifications_contrasted\s*:", updated, re.M):
            updated = re.sub(
                r'^(physical_test:.*)$',
                r'\1\nspecifications_contrasted: "no"',
                updated,
                count=1,
                flags=re.M,
            )
        if "<!-- CLASIFICACION_FUENTES_178 -->" not in updated:
            needle = "No equivalen a especificaciones verificadas.\n\n"
            if needle not in updated:
                raise ValueError(f"Bloque de fuentes inesperado: {path}")
            updated = updated.replace(needle, needle + SOURCE_STATUS, 1)
        return (updated, (0, 0)) if updated != original else (None, (0, 0))
    match = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n(.*)\Z", original, re.S)
    if not match:
        raise ValueError(f"Frontmatter ausente: {path}")
    front, body = match.groups()
    original_links = [(label, url) for label, url in LINK.findall(body) if not any(part in url for part in AFFILIATE)]
    topics = get_table_topics(body)
    body, removed_sections, removed_quotes = strip_unattributed_experience(body)

    metadata = {
        "research_type": "documental, pendiente de contraste",
        "physical_test": "no documentada",
        "specifications_contrasted": "no",
        "buyer_opinions": "no documentadas",
        "primary_sources": "pendiente de verificar",
        "information_asset": "matriz de evidencia pendiente: " + ", ".join(topics[:3] or [article["h1"]]),
        "asset_status": "pendiente",
    }
    front_lines = front.splitlines()
    for key, value in metadata.items():
        if not re.search(rf"^{re.escape(key)}\s*:", front, re.M):
            front_lines.append(f"{key}: {quote_yaml(value)}")

    notice = (
        "<!-- AUDITORIA_EDITORIAL_178 -->\n"
        "> **Estado de esta guía: borrador documental.** Las cifras, prestaciones y conclusiones del texto siguiente "
        "todavía requieren contraste con documentación del modelo exacto. No se atribuye una prueba física "
        "ni una muestra de opiniones a TallerLab. Los datos sin fuente verificable se tratan como **desconocidos** "
        "hasta completar la revisión.\n"
    )
    h1 = re.search(r"^#\s+.+$", body, re.M)
    if not h1:
        raise ValueError(f"H1 ausente: {path}")
    body = body[: h1.end()] + "\n\n" + notice + body[h1.end():]

    rows = []
    for topic in topics[:4] or [article["h1"]]:
        safe = topic.replace("|", "/").replace("\n", " ")
        rows.append(f"| {safe} | Ficha o manual del código exacto y condición de medición, si corresponde | Pendiente |")
    evidence = (
        "## Matriz de evidencia pendiente\n\n"
        "**Análisis TallerLab del borrador.** Estos son los puntos concretos que deben sostenerse con documentación "
        "antes de convertir esta página en una recomendación de compra. La tabla registra preguntas de revisión; "
        "no valida las cifras que aparezcan arriba.\n\n"
        "| Dato o decisión de esta guía | Comprobación necesaria | Estado |\n"
        "| :--- | :--- | :--- |\n"
        + "\n".join(rows)
        + "\n\n**Desconocido.** Hasta verificar estas fuentes, TallerLab no afirma rendimiento real, durabilidad, "
        "superioridad ni compatibilidad de una variante por analogía con otra.\n"
    )
    seen = set()
    source_items = []
    for label, url in original_links:
        if url in seen:
            continue
        seen.add(url)
        source_items.append(f"- [{label}]({url}) — enlace presente en el borrador; confirmar que respalde el modelo y el dato citado.")
        if len(source_items) == 4:
            break
    sources = (
        "## Fuentes consultadas\n\n"
        "**Estado de fuentes:** referencias heredadas del borrador, aún no cotejadas afirmación por afirmación. "
        "No equivalen a especificaciones verificadas.\n\n"
        + SOURCE_STATUS
        + ("\n".join(source_items) if source_items else "No hay documentación técnica externa enlazada en este borrador. Hay que localizar 2–4 fuentes pertinentes antes de publicarlo.")
        + "\n"
    )
    hub = f'/{article["section"]}/'
    hub_line = f"\nPara explorar la categoría: [guías de {article['section'].replace('-', ' ')}]({hub}).\n" if f"]({hub})" not in body else ""
    body = body.rstrip() + "\n\n" + evidence + "\n" + sources + hub_line
    return "---\n" + "\n".join(front_lines) + "\n---\n\n" + body.rstrip() + "\n", (removed_sections, removed_quotes)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    changes = []
    removed_sections = removed_quotes = 0
    for article in _ALL_DRAFTS:
        new, removed = transform(article)
        if new is not None:
            changes.append((article["path"], new))
            removed_sections += removed[0]
            removed_quotes += removed[1]
    print(f"Borradores a modificar: {len(changes)}; secciones de opiniones sin muestra retiradas: {removed_sections}; reglas de taller sin prueba retiradas: {removed_quotes}")
    if not args.apply:
        print("Vista previa. Usar --apply para escribir.")
        return
    if not BACKUP.exists():
        with zipfile.ZipFile(BACKUP, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path, _ in changes:
                archive.write(path, path.relative_to(ROOT))
    for path, new in changes:
        path.write_text(new, encoding="utf-8")
    print(f"Respaldo: {BACKUP}")


if __name__ == "__main__":
    main()
