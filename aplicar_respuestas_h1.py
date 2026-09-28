"""Coloca respuestas directas antes del primer H2 sin cambiar metadatos ni headings.

Uso: python aplicar_respuestas_h1.py --check | --apply
"""

import argparse
import re
from pathlib import Path

from respuestas_h1 import RESPUESTAS
from servidor_local import PAGES_DIR, extract_frontmatter


def headings(text):
    return re.findall(r"(?m)^#{1,2} .+$", text)


def updated_content(text, answer):
    first_h1 = re.search(r"(?m)^# .+\n", text)
    if not first_h1:
        raise ValueError("Falta H1")
    boundary = re.search(r"(?m)^## |^---\s*$", text[first_h1.end():])
    if not boundary:
        raise ValueError("Falta H2 o separador después de la introducción")
    end = first_h1.end() + boundary.start()
    result = text[:first_h1.end()] + "\n" + answer + "\n\n" + text[end:]
    if headings(text) != headings(result):
        raise ValueError("Cambió un H1 o H2")
    if extract_frontmatter(text)[0] != extract_frontmatter(result)[0]:
        raise ValueError("Cambió el frontmatter")
    return result


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    seen = set()
    changes = []
    for path in sorted(PAGES_DIR.rglob("*.md")):
        original_bytes = path.read_bytes()
        newline = "\r\n" if b"\r\n" in original_bytes else "\n"
        text = original_bytes.decode("utf-8").replace("\r\n", "\n")
        fm, _ = extract_frontmatter(text)
        url = fm.get("url", "")
        if url not in RESPUESTAS:
            continue
        if url in seen:
            raise ValueError(f"URL duplicada: {url}")
        seen.add(url)
        result = updated_content(text, RESPUESTAS[url])
        if result != text:
            changes.append((path, result, newline))
        elif args.check:
            first_h1 = re.search(r"(?m)^# .+\n", text)
            if text[first_h1.end():].lstrip().startswith(RESPUESTAS[url]) is False:
                raise ValueError(f"La respuesta de apertura no coincide: {url}")
    if seen != set(RESPUESTAS):
        raise ValueError(f"Faltan URLs: {sorted(set(RESPUESTAS) - seen)}")
    if args.check and changes:
        raise ValueError(f"{len(changes)} archivos requieren aplicar respuestas")
    if args.apply:
        for path, result, newline in changes:
            path.write_bytes(result.replace("\n", newline).encode("utf-8"))
    print(f"{len(seen)} URLs comprobadas; {len(changes)} archivos {'editados' if args.apply else 'por editar'}")


if __name__ == "__main__":
    main()
