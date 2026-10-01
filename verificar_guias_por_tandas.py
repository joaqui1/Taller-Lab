"""Control por URL: estructura, anclas, comparación y fuentes externas.

Un HTTP 200 no confirma las cifras: las observaciones editoriales se registran
por separado, sin convertir este control en una certificación del contenido.
"""
import argparse
import concurrent.futures
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urljoin, urlsplit, unquote
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup
from app import app
import servidor_local as site

ROOT = Path(__file__).parent


def unavailable_page(title, headings):
    labels = [title] + headings
    return any(label.strip() == '404' for label in labels) or bool(re.search(
        r'\b(?:error\s*404|404\s*(?:not\s+found|no\s+encontrad[oa])|p[aá]gina\s+no\s+encontrada|page\s+not\s+found|producto\s+no\s+encontrado)\b',
        ' '.join(labels), re.I))


def probe(url):
    result = dict(url=url, checked=datetime.now(timezone.utc).isoformat())
    try:
        with urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0 TallerLab-source-QA'}), timeout=18) as response:
            result.update(status=response.status, final_url=response.url, content_type=response.headers.get('Content-Type', ''))
            expected_pdf = bool(re.search(r'\.pdf(?:$|[?&#])', unquote(url), re.I))
            prefix = b''
            if expected_pdf or 'pdf' in result['content_type'].lower():
                prefix = response.read(256)
                result['document_signature_valid'] = b'%PDF' in prefix
                if expected_pdf:
                    result['unexpected_document_type'] = not result['document_signature_valid']
            if 'html' in result['content_type'] and result.get('document_signature_valid') is not True:
                data = prefix + response.read(1500000 - len(prefix))
                soup = BeautifulSoup(data, 'html.parser')
                result['title'] = soup.title.get_text(' ', strip=True) if soup.title else ''
                result['headings'] = [h.get_text(' ', strip=True) for h in soup.select('h1')][:3]
                result['soft_not_found'] = unavailable_page(result['title'], result['headings'])
                result['generic_redirect'] = urlsplit(response.url).path.rstrip('/') in ('', '/products', '/productos', '/herramientas') and urlsplit(url).path.rstrip('/') != urlsplit(response.url).path.rstrip('/')
    except HTTPError as error:
        result.update(status=error.code, error=str(error))
    except Exception as error:
        result.update(status=None, error=str(error))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--section', required=True, choices=sorted({a['section'] for a in site.ALL_ARTICLES}))
    parser.add_argument('--external', action='store_true')
    args = parser.parse_args()
    client = app.test_client()
    pages = {p: BeautifulSoup(client.get(p).data, 'html.parser') for p in site.INDEXABLE_PATHS}
    rows, urls = [], set()
    destination = ROOT / ('qa-tanda-' + args.section + '.json')
    previous = json.loads(destination.read_text(encoding='utf-8')) if destination.exists() else {}
    ledger_path = ROOT / 'revision-editorial-por-tandas.json'
    ledger = json.loads(ledger_path.read_text(encoding='utf-8')) if ledger_path.exists() else {}
    for article in site.ALL_ARTICLES:
        if article['section'] != args.section:
            continue
        path, body = article['url'], article['body']
        doc = pages[path]
        issues = []
        if len(doc.select('h1')) != 1:
            issues.append('Cantidad de H1 distinta de uno')
        if doc.find('link', rel='canonical').get('href') != site.SITE_URL + path:
            issues.append('Canonical incorrecto')
        for anchor in doc.select('a[href]'):
            target = urlsplit(urljoin(site.SITE_URL + path, anchor['href']))
            if target.netloc != urlsplit(site.SITE_URL).netloc:
                continue
            if target.path not in pages:
                issues.append('Ruta interna inexistente: ' + anchor['href'])
            elif target.fragment and not pages[target.path].find(id=unquote(target.fragment)):
                issues.append('Sección de destino inexistente: ' + anchor['href'])
        for shelf in doc.select('.affiliate-shelf'):
            cards = shelf.select('.offer-card')
            if len(cards) < 2 and ('Compará' in shelf.select_one('.affiliate-heading').get_text() or shelf.select('.compare-checkbox')):
                issues.append('Comparador con menos de dos opciones')
        source_doc = BeautifulSoup(site.MARKDOWN.render(body), 'html.parser')
        sources = sorted({a['href'] for a in source_doc.select('a[href]') if a['href'].startswith('https://') and urlsplit(a['href']).netloc not in {'meli.la', 'www.mercadolibre.com.ar', 'mercadolibre.com.ar'}})
        urls.update(sources)
        digest = hashlib.sha256(body.encode()).hexdigest()
        review = ledger.get(path)
        status = 'revisión editorial registrada' if review and review.get('body_sha256') == digest else 'pendiente de revisión editorial actual'
        rows.append(dict(path=path, file=str(article['path']), body_sha256=digest, title=article['h1'], issues=issues, sources=sources, tables=len(source_doc.select('table')), offer_cards=len(doc.select('.offer-card')), editorial_status=status, editorial_review=review))
    sources = previous.get('sources', [])
    history = previous.get('source_history', [])
    known = {source['url']: source for source in sources}
    retired = {source['url']: source for source in history}
    retired.update({url: source for url, source in known.items() if url not in urls})
    history = list(retired.values())
    sources = [source for source in sources if source['url'] in urls]
    if args.external:
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
            sources = list(pool.map(probe, sorted(urls)))
        for source in sources:
            if known.get(source['url'], {}).get('access_review'):
                source['access_review'] = known[source['url']]['access_review']
    report = dict(section=args.section, checked=datetime.now(timezone.utc).isoformat(), articles=len(rows), structural_failures=[r for r in rows if r['issues']], sources=sources, source_history=history, rows=rows)
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(section=args.section, articles=len(rows), structural_failures=report['structural_failures'], sources=len(sources), source_alerts=[r for r in sources if r.get('status') != 200 or r.get('generic_redirect') or r.get('soft_not_found') or r.get('unexpected_document_type') or r.get('document_signature_valid') is False]), ensure_ascii=False))
    if report['structural_failures']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
