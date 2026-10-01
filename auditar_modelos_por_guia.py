"""Inventario editorial por artículo: tablas, referencias y tarjetas publicadas."""
import json
import re
import sys
from pathlib import Path
from bs4 import BeautifulSoup
import servidor_local as site

def inventory():
    rows = []
    for article in site.ALL_ARTICLES:
        soup = BeautifulSoup(site.render_article_page(article), 'html.parser')
        body = article['body']
        tables = []
        for match in re.finditer(r'(?m)^\|[^\n]*\n(?:\|[^\n]*\n)+', body):
            before = body[:match.start()]
            headings = re.findall(r'(?m)^#{2,3} (.+)$', before)
            cells = [line.strip().strip('|').split('|')[0].strip() for line in match[0].splitlines()[2:]]
            tables.append(dict(heading=headings[-1] if headings else '', rows=cells))
        rows.append(dict(path=article['url'], section=article['section'], file=str(article['path']), title=article['h1'], description=article['description'], headings=re.findall(r'(?m)^## (.+)$', body), tables=tables, cards=[card.select_one('h3').get_text(' ',strip=True) for card in soup.select('.offer-card') if card.select_one('h3')], model_sources=[dict(label=label,url=url) for label,url in re.findall(r'\[([^\]]+)\]\((https://[^)]+)\)', body) if 'meli.la/' not in url]))
    Path('auditoria-modelos-por-guia.json').write_text(json.dumps(rows, ensure_ascii=False,indent=2),encoding='utf-8')
    return rows

if __name__ == '__main__':
    rows=inventory()
    for row in rows:
        if len(sys.argv)>1 and row['section']!=sys.argv[1]: continue
        print(row['path'], '|',row['description'], '| cards:', '; '.join(row['cards']) or 'ninguna')
        for table in row['tables']:
            if re.search(r'model|compar|gama|version|document|referenc|ficha|configur|ejemplo|elegir|elegí|consumo', table['heading'],re.I):
                print(' ',table['heading'],':','; '.join(table['rows']))
