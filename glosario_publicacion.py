"""Carga, render y enlaces internos del glosario editorial de TallerLab."""

import json
import re
from html import escape
from pathlib import Path

from markdown_it.token import Token


GLOSSARY_DIR = Path(__file__).parent / "glosario"
GLOSSARY_HUB_PATH = "/glosario/"


def _parse_value(value):
    value = value.strip()
    if value.startswith(("[", '"')):
        return json.loads(value)
    if value in ("true", "false"):
        return value == "true"
    return value


def parse_glossary_file(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"Falta el frontmatter YAML en {path}")
    _, frontmatter, body = text.split("---", 2)
    metadata = {}
    for line in frontmatter.splitlines():
        if not line.strip():
            continue
        key, separator, value = line.partition(":")
        if not separator:
            raise ValueError(f"Frontmatter inválido en {path}: {line}")
        metadata[key.strip()] = _parse_value(value)
    for key in ("unidades", "terminos_relacionados", "guias", "fuentes"):
        metadata.setdefault(key, [])
    metadata.setdefault("variantes", [])
    metadata.setdefault("definicion_corta", "")
    metadata.setdefault("reviewed", "")
    metadata.setdefault("estado", "borrador")
    metadata["body"] = body.strip()
    metadata["filename"] = path.name
    if metadata.get("slug") != path.stem:
        raise ValueError(f"El slug del glosario debe coincidir con el archivo: {path}")
    return metadata


def load_glossary_terms(directory=None):
    directory = Path(directory) if directory else GLOSSARY_DIR
    if not directory.exists():
        return []
    return [parse_glossary_file(path) for path in sorted(directory.glob("*.md"))]


def published_glossary_terms(directory=None):
    return [term for term in load_glossary_terms(directory) if term["estado"] == "publicado"]


def published_glossary_paths(directory=None):
    terms = published_glossary_terms(directory)
    if not terms:
        return ()
    return (GLOSSARY_HUB_PATH,) + tuple(f'{GLOSSARY_HUB_PATH}{term["slug"]}/' for term in terms)


def get_published_glossary_term(slug, directory=None):
    return next((term for term in published_glossary_terms(directory) if term["slug"] == slug), None)


def _aliases(terms):
    aliases = []
    for term in terms:
        for label in [term["termino"], *term.get("variantes", [])]:
            label = str(label).strip()
            if label:
                aliases.append((label, term))
    return sorted(aliases, key=lambda item: (-len(item[0]), item[1]["slug"], item[0].casefold()))


def _link_text_token(token, aliases, linked_slugs, max_links):
    text = token.content
    output = []
    cursor = 0
    while cursor < len(text):
        match = None
        owner = None
        if len(linked_slugs) < max_links:
            for label, term in aliases:
                if term["slug"] in linked_slugs:
                    continue
                pattern = re.compile(r"(?<!\w)" + re.escape(label) + r"(?!\w)", re.IGNORECASE)
                candidate = pattern.search(text, cursor)
                if candidate and (match is None or candidate.start() < match.start() or
                                  (candidate.start() == match.start() and len(candidate.group(0)) > len(match.group(0)))):
                    match, owner = candidate, term
        if not match:
            remainder = text[cursor:]
            if remainder:
                plain = Token("text", "", 0)
                plain.content = remainder
                output.append(plain)
            break
        if match.start() > cursor:
            plain = Token("text", "", 0)
            plain.content = text[cursor:match.start()]
            output.append(plain)
        opener = Token("link_open", "a", 1)
        opener.attrSet("href", f'{GLOSSARY_HUB_PATH}{owner["slug"]}/')
        opener.attrSet("class", "glossary-term-link")
        linked_text = Token("text", "", 0)
        linked_text.content = match.group(0)
        closer = Token("link_close", "a", -1)
        output.extend((opener, linked_text, closer))
        linked_slugs.add(owner["slug"])
        cursor = match.end()
    return output


def render_markdown_with_glossary(markdown_renderer, markdown_text, max_links=5):
    """Render Markdown and link each published term once, outside headings/links."""
    terms = published_glossary_terms()
    if not terms:
        return markdown_renderer.render(markdown_text)

    aliases = _aliases(terms)
    tokens = markdown_renderer.parse(markdown_text)
    linked_slugs = set()
    in_heading = False
    inside_link = 0
    for token in tokens:
        if token.type == "heading_open":
            in_heading = True
        elif token.type == "heading_close":
            in_heading = False
        elif token.type == "inline" and token.children and not in_heading:
            rewritten = []
            for child in token.children:
                if child.type == "link_open":
                    inside_link += 1
                    rewritten.append(child)
                elif child.type == "link_close":
                    inside_link = max(0, inside_link - 1)
                    rewritten.append(child)
                elif child.type == "text" and inside_link == 0:
                    rewritten.extend(_link_text_token(child, aliases, linked_slugs, max_links))
                else:
                    rewritten.append(child)
            token.children = rewritten
    return markdown_renderer.renderer.render(tokens, markdown_renderer.options, {})


def _schema_script(data):
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False).replace("<", "\\u003c") + "</script>"


def render_glossary_page(path, *, canonical_tag, absolute_url):
    """Return a glossary page, or None for a slug that is not published."""
    from servidor_local import ALL_ARTICLES, HTML_SHELL, LOGO_SRC, PORT

    normalized = path.rstrip("/") or "/"
    if normalized == GLOSSARY_HUB_PATH.rstrip("/"):
        public_terms = published_glossary_terms()
        title = "Glosario de herramientas"
        description = "Definiciones breves de términos técnicos usados en las guías de TallerLab."
        cards = "".join(
            f'<li><a href="{GLOSSARY_HUB_PATH}{escape(term["slug"], quote=True)}/">{escape(term["termino"])}</a>'
            f'<p>{escape(term["definicion_corta"])}</p></li>'
            for term in public_terms
        )
        content = (
            '<div class="editorial-container glossary-page"><nav class="breadcrumb" aria-label="Ubicación">'
            '<a href="/">Inicio</a><span>/</span><span>Glosario</span></nav>'
            f'<header class="article-header"><h1>{title}</h1><p>{description}</p></header>'
            + (f'<ul class="glossary-list">{cards}</ul>' if public_terms else
               '<p class="glossary-empty">Todavía no hay términos publicados en el glosario.</p>')
            + '</div>'
        )
        set_schema = {
            "@context": "https://schema.org", "@type": "DefinedTermSet",
            "name": title, "description": description, "url": absolute_url(GLOSSARY_HUB_PATH),
            "hasDefinedTerm": [
                {"@type": "DefinedTerm", "name": term["termino"], "url": absolute_url(f'{GLOSSARY_HUB_PATH}{term["slug"]}/')}
                for term in public_terms
            ],
        }
        robots = None if public_terms else "noindex, follow"
        head = canonical_tag(GLOSSARY_HUB_PATH, title=title + " | TallerLab", description=description, robots=robots)
        head += _schema_script(set_schema)
        return HTML_SHELL.format(PAGE_TITLE=title + " | TallerLab", CANONICAL_TAG=head, PAGE_DESC=description, PORT=PORT, CONTENT=content, LOGO_SRC=LOGO_SRC)

    slug = normalized[len(GLOSSARY_HUB_PATH.rstrip("/")) + 1:]
    term = get_published_glossary_term(slug)
    if not term:
        return None
    title = term["termino"]
    description = term["definicion_corta"] or f"Término técnico de herramientas: {title}."
    related = [get_published_glossary_term(item) for item in term.get("terminos_relacionados", [])]
    related_html = " · ".join(
        f'<a href="{GLOSSARY_HUB_PATH}{escape(item["slug"], quote=True)}/">{escape(item["termino"])}</a>'
        for item in related if item
    )
    article_titles = {article["url"]: article["h1"] for article in ALL_ARTICLES}
    guides_html = "".join(
        f'<li><a href="{escape(url, quote=True)}">{escape(article_titles.get(url, "Guía relacionada"))}</a></li>'
        for url in term.get("guias", [])
    )
    sources_html = "".join(
        f'<li><a href="{escape(url, quote=True)}" target="_blank" rel="nofollow noopener noreferrer">Fuente del fabricante: {escape(url.split("//", 1)[-1].split("/", 1)[0])}</a></li>'
        for url in term.get("fuentes", [])
    )
    breadcrumbs = (
        '<nav class="breadcrumb" aria-label="Ubicación"><a href="/">Inicio</a><span>/</span>'
        f'<a href="{GLOSSARY_HUB_PATH}">Glosario</a><span>/</span><span>{escape(title)}</span></nav>'
    )
    definition_html = f'<p>{escape(term["definicion_corta"])}</p>' if term["definicion_corta"] else ""
    details = ""
    if term.get("unidades"):
        details += '<p><strong>Unidades:</strong> ' + ", ".join(escape(str(value)) for value in term["unidades"]) + "</p>"
    if related_html:
        details += '<p><strong>Términos relacionados:</strong> ' + related_html + "</p>"
    if guides_html:
        details += '<section><h2>Guías que lo explican</h2><ul>' + guides_html + "</ul></section>"
    if sources_html:
        details += '<section><h2>Fuentes del fabricante</h2><ul>' + sources_html + "</ul></section>"
    content = (
        f'<div class="article-container glossary-page">{breadcrumbs}<header class="article-header"><h1>{escape(title)}</h1></header>'
        f'<section class="markdown-body glossary-definition"><h2>Definición</h2>{definition_html or "<p>La definición está pendiente de revisión editorial.</p>"}{details}</section></div>'
    )
    term_schema = {
        "@context": "https://schema.org", "@type": "DefinedTerm", "name": title,
        "description": term["definicion_corta"] or description,
        "url": absolute_url(f'{GLOSSARY_HUB_PATH}{term["slug"]}/'),
        "inDefinedTermSet": {"@id": absolute_url(GLOSSARY_HUB_PATH)},
    }
    route = f'{GLOSSARY_HUB_PATH}{term["slug"]}/'
    head = canonical_tag(route, title=title + " | TallerLab", description=description)
    head += _schema_script(term_schema)
    return HTML_SHELL.format(PAGE_TITLE=title + " | TallerLab", CANONICAL_TAG=head, PAGE_DESC=description, PORT=PORT, CONTENT=content, LOGO_SRC=LOGO_SRC)
