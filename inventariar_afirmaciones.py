"""Clasifica conservadoramente las afirmaciones de las 178 guías.

Una etiqueta automática nunca verifica un dato. Toda frase sin etiqueta editorial
explícita queda DESCONOCIDO y exige revisión antes de publicarse.
"""

import csv
import re
from pathlib import Path

from servidor_local import _ALL_DRAFTS


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "afirmaciones-178.csv"
LABELS = {
    "dato verificado": "DATO VERIFICADO",
    "declaración del fabricante": "DECLARACIÓN DEL FABRICANTE",
    "experiencia de compradores": "EXPERIENCIA DE COMPRADORES",
    "análisis tallerlab": "ANÁLISIS TALLERLAB",
    "desconocido": "DESCONOCIDO",
}
INLINE_LINK = re.compile(r"\[[^\]]+\]\((https?://[^)\s]+)\)")
RISK = re.compile(r"\b(?:el mejor|la mejor|ideal|durabilidad|confiabilidad|calidad profesional|uso profesional|relación precio.calidad|probamos|nuestra experiencia|usuarios coinciden|compradores destacan)\b", re.I)


def blocks(article):
    body = article["body"].split("## Matriz de evidencia pendiente", 1)[0]
    current_label = "DESCONOCIDO"
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", "---", "<!--")):
            continue
        if stripped.startswith("|") and re.match(r"^\|\s*:?-{3,}", stripped):
            continue
        if stripped.startswith(("|", "- ", "* ", "> ")):
            text = stripped.strip("|> *-").strip()
        else:
            text = stripped
        if len(text) < 20 or text.startswith("[Ver "):
            continue
        found = next((value for key, value in LABELS.items() if re.search(rf"\*\*{re.escape(key)}(?:[.:, ]|\*\*)", text, re.I)), None)
        if found:
            current_label = found
        elif not stripped.startswith("|"):
            current_label = "DESCONOCIDO"
        yield text, found or current_label


def main():
    rows = []
    for article in sorted(_ALL_DRAFTS, key=lambda a: a["url"]):
        for text, label in blocks(article):
            links = INLINE_LINK.findall(text)
            rows.append({
                "url": article["url"],
                "categoria": label,
                "estado": "revisada" if article.get("asset_status") == "verificado" else "pendiente",
                "requiere_revisión_de_claim": "sí" if RISK.search(text) else "no",
                "enlace_en_misma_linea": links[0] if links else "",
                "afirmacion": re.sub(r"\s+", " ", text)[:500],
            })
    with OUT.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=("url", "categoria", "estado", "requiere_revisión_de_claim", "enlace_en_misma_linea", "afirmacion"))
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(rows)} bloques de afirmaciones inventariados en {len(_ALL_DRAFTS)} URL; archivo: {OUT}")


if __name__ == "__main__":
    main()
