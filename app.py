"""Entrada Flask para Vercel; reutiliza las mismas páginas del servidor local."""

import json

from flask import Flask, Response, redirect, request, send_from_directory

from servidor_local import (
    ALL_ARTICLES,
    ASSETS_DIR,
    CATEGORY_META,
    INDEXABLE_PATH_SET,
    render_article_page,
    render_category_page,
    render_home_page,
    render_not_found,
    render_robots,
    render_search_cards,
    render_sitemap,
    validate_affiliate_click,
)

app = Flask(__name__, static_folder=None)
ARTICLES_BY_URL = {article["url"]: article for article in ALL_ARTICLES}
FAVICON = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">&#x1F527;</text></svg>'


@app.route("/assets/<path:filename>", methods=["GET", "HEAD"])
def asset(filename):
    response = send_from_directory(ASSETS_DIR, filename)
    response.headers["Cache-Control"] = "no-store" if filename.endswith(".css") else "public, max-age=3600"
    return response


@app.route("/api/affiliate-click", methods=["POST"])
def affiliate_click():
    payload = request.get_data(cache=False)
    if not 0 < len(payload) <= 2048:
        return Response(status=400)
    try:
        event = validate_affiliate_click(json.loads(payload))
    except (ValueError, TypeError):
        return Response(status=400)

    # El sistema de archivos de la función no es almacenamiento persistente.
    # Los eventos quedan en los logs de la función hasta conectar una base externa.
    print(json.dumps({"type": "affiliate_click", **event}, ensure_ascii=False), flush=True)
    return Response(status=204, headers={"Cache-Control": "no-store"})


@app.route("/", defaults={"path": ""}, methods=["GET", "HEAD"])
@app.route("/<path:path>", methods=["GET", "HEAD"], strict_slashes=False)
def page(path):
    url_path = "/" + path

    if url_path == "/robots.txt":
        return Response(render_robots(), content_type="text/plain; charset=utf-8")
    if url_path == "/sitemap.xml":
        return Response(render_sitemap(), content_type="application/xml; charset=utf-8")
    if url_path == "/search-cards.html":
        return Response(render_search_cards(), content_type="text/html; charset=utf-8", headers={"X-Robots-Tag": "noindex"})
    if url_path in ("/favicon.ico", "/favicon.svg"):
        return Response(FAVICON, content_type="image/svg+xml")

    if not url_path.endswith("/") and url_path + "/" in INDEXABLE_PATH_SET:
        destination = url_path + "/"
        if request.query_string:
            destination += "?" + request.query_string.decode("ascii")
        return redirect(destination, code=301)

    if url_path == "/":
        html = render_home_page()
    elif url_path in ARTICLES_BY_URL:
        html = render_article_page(ARTICLES_BY_URL[url_path])
    elif url_path.endswith("/") and url_path[1:-1] in CATEGORY_META:
        html = render_category_page(url_path[1:-1])
    else:
        return Response(render_not_found(url_path), status=404, content_type="text/html; charset=utf-8")

    return Response(html, content_type="text/html; charset=utf-8")
