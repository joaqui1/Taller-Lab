"""Inventario reproducible de pendientes editoriales; no publica páginas."""

import csv
import re
from pathlib import Path

from servidor_local import _ALL_DRAFTS, REQUIRED_RESEARCH_FIELDS


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "estado-editorial-178.csv"
RISK = re.compile(
    r"\b(?:el mejor|la mejor|ideal|durabilidad|confiabilidad|"
    r"calidad profesional|uso profesional|relación precio.calidad|"
    r"probamos|nuestra experiencia|usuarios coinciden|"
    r"compradores destacan)\b",
    re.IGNORECASE,
)
EXTERNAL = re.compile(r"\[[^\]]+\]\((https?://[^)\s]+)\)")
COMMERCIAL = ("meli.la", "mercadolibre.com.ar")
FIELDS = (
    "url", "archivo", "estado", "enlaces_externos_no_comerciales", "bloque_fuentes",
    "activo_de_informacion", "activo_verificado", "categorias_visibles", "enlace_hub", "frases_para_revisar",
)


def inspect(article):
    body = article["body"]
    links = [url for url in EXTERNAL.findall(body) if not any(host in url for host in COMMERCIAL)]
    sources = bool(re.search(r"^## Fuentes consultadas\s*$", body, re.MULTILINE))
    labels = "Dato verificado" in body and "Análisis TallerLab" in body
    asset = bool(article.get("information_asset"))
    hub = f'/{article["section"]}/' in body
    ready = (
        article.get("published") == "true" and bool(article["reviewed"])
        and all(article.get(field) for field in REQUIRED_RESEARCH_FIELDS)
        and sources and labels and article.get("primary_sources") == "sí"
        and article.get("specifications_contrasted") == "sí"
        and article.get("asset_status") == "verificado"
    )
    return {
        "url": article["url"],
        "archivo": str(article["path"].relative_to(ROOT)),
        "estado": "publicada" if ready else "borrador",
        "enlaces_externos_no_comerciales": len(set(links)),
        "bloque_fuentes": "sí" if sources else "no",
        "activo_de_informacion": "sí" if asset else "no",
        "activo_verificado": "sí" if article.get("asset_status") == "verificado" else "no",
        "categorias_visibles": "sí" if labels else "no",
        "enlace_hub": "sí" if hub else "no",
        "frases_para_revisar": len(RISK.findall(body)),
    }


def main():
    rows = [inspect(article) for article in sorted(_ALL_DRAFTS, key=lambda a: a["url"])]
    with OUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(rows)} URL; {sum(row['estado'] == 'publicada' for row in rows)} publicadas; {len(rows) - sum(row['estado'] == 'publicada' for row in rows)} borradores")
    print(f"Inventario: {OUT}")


if __name__ == "__main__":
    main()
