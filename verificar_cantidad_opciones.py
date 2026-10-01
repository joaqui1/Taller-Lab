"""Audita títulos y controles comerciales según las opciones realmente publicadas."""
import json
from collections import Counter
from pathlib import Path
from bs4 import BeautifulSoup
from app import app
import servidor_local as site

def audit(validate=True):
    if validate:
        hydro = [('hidrolavadoras', item) for item in site.AFFILIATE_PRODUCTS['hidrolavadoras'][:2]]
        assert site.render_affiliate_shelf('hidrolavadoras', []) == ''
        assert 'compare-checkbox' not in site.render_affiliate_shelf('hidrolavadoras', hydro[:1])
        assert site.render_affiliate_shelf('hidrolavadoras', hydro).count('class="compare-checkbox"') == 2
        mixed = [hydro[0], ('compresores', site.AFFILIATE_PRODUCTS['compresores'][0])]
        mixed_html = site.render_affiliate_shelf('inicio', mixed)
        assert 'compare-checkbox' not in mixed_html and 'compare-panel' not in mixed_html
    rows = []
    client = app.test_client()
    for path in site.INDEXABLE_PATHS:
        soup = BeautifulSoup(client.get(path).get_data(as_text=True), 'html.parser')
        for shelf in soup.select('.affiliate-shelf'):
            cards = shelf.select('.offer-card')
            heading = shelf.select_one('.affiliate-heading h2, .affiliate-heading h3')
            counts = Counter(card.get('data-compare-type') for card in cards)
            row = dict(path=path, count=len(cards), heading=heading.get_text(strip=True) if heading else '', filters=len(shelf.select('.offer-filters select')), checks=len(shelf.select('.compare-checkbox')))
            rows.append(row)
            if validate:
                if len(cards) == 1:
                    assert not shelf.select('.offer-filters,.compare-checkbox,.compare-panel,.offer-empty'), row
                    assert 'compar' not in row['heading'].lower() and 'opciones' not in row['heading'].lower() and 'Publicaciones' not in row['heading'], row
                for card in cards:
                    if card.select_one('.compare-checkbox'):
                        assert counts[card['data-compare-type']] >= 2, row
                assert bool(shelf.select_one('.compare-panel')) == bool(row['checks']), row
    report = dict(pages=len(site.INDEXABLE_PATHS), shelves=len(rows), singletons=[row for row in rows if row['count'] == 1], rows=rows)
    Path('qa-cantidad-opciones.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(dict(pages=report['pages'], shelves=report['shelves'], singleton_blocks=len(report['singletons'])), ensure_ascii=False))
    return report

if __name__ == '__main__':
    import sys
    audit(validate='--before' not in sys.argv)
