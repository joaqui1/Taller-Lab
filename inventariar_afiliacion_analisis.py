import json
from pathlib import Path
from html.parser import HTMLParser
import servidor_local as s

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = set()
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            href = dict(attrs).get('href', '')
            if href.startswith('https://meli.la/'):
                self.links.add(href)

rows = []
for a in s._ALL_DRAFTS:
    parser = Links()
    parser.feed(s.render_article_page(a))
    rows.append(dict(url=a['url'],title=a['title'],h1=a['h1'],keywords=a['keywords'],file=str(a['path']),section=a['section'],published=a in s.ALL_ARTICLES,rendered_links=sorted(parser.links)))
Path('inventario-afiliacion-analisis.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(pages=len(rows),published=sum(a['published'] for a in rows),with_affiliate=sum(bool(a['rendered_links']) and a['published'] for a in rows),linked=[dict(url=a['url'],links=len(a['rendered_links'])) for a in rows if a['rendered_links'] and a['published']]),ensure_ascii=False))
