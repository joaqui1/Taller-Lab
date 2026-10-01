"""Auditoría de lectura del HTML local y público; no modifica el sitio."""
import concurrent.futures
from collections import Counter, defaultdict, deque
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import xml.etree.ElementTree as ET

os.environ['SITE_URL'] = 'https://www.tallerlab.com.ar'
import servidor_local as s
from app import app

class Doc(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.meta = {}; self.links = []; self.images = []; self.ids = []
        self.headings = []; self.titles = []; self.canonicals = []; self.schemas = []
        self.capture = None; self.parts = []; self.text = []; self.lang = ''
        self.feed(html)
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'html': self.lang = a.get('lang', '')
        if a.get('id'): self.ids.append(a['id'])
        if tag == 'meta': self.meta[a.get('name', a.get('property', ''))] = a.get('content', '')
        if tag == 'link' and a.get('rel') == 'canonical': self.canonicals.append(a.get('href'))
        if tag == 'a': self.links.append(a)
        if tag == 'img': self.images.append(a)
        if tag == 'title' or re.fullmatch('h[1-6]', tag) or (tag == 'script' and a.get('type') == 'application/ld+json'):
            self.capture = tag; self.parts = []
    def handle_data(self, data):
        if self.capture: self.parts.append(data)
        self.text.append(data)
    def handle_endtag(self, tag):
        if self.capture != tag: return
        value = ''.join(self.parts).strip()
        if tag == 'title': self.titles.append(value)
        elif tag == 'script':
            try: self.schemas.append(json.loads(value))
            except ValueError: self.schemas.append({'error': 'JSON inválido'})
        else: self.headings.append([tag, value])
        self.capture = None

def fetch(url):
    try:
        with urlopen(Request(url, headers={'User-Agent': 'TallerLab-SEO-audit/1.0', 'Accept-Encoding': 'identity'}), timeout=25) as r:
            body = r.read().decode('utf-8', errors='replace')
            return {'url': url, 'final_url': r.url, 'status': r.status, 'headers': dict(r.headers), 'body': body}
    except HTTPError as e: return {'url': url, 'status': e.code, 'headers': dict(e.headers)}
    except Exception as e: return {'url': url, 'error': str(e)}

def inspect(path, html, status, headers):
    d = Doc(html)
    issues = []
    if status != 200: issues.append('HTTP distinto de 200')
    if len(d.titles) != 1 or not d.titles[0]: issues.append('title ausente o múltiple')
    if not d.meta.get('description'): issues.append('descripción ausente')
    if len([h for h in d.headings if h[0] == 'h1']) != 1: issues.append('cantidad de H1 distinta de uno')
    if d.canonicals != [s.SITE_URL + path]: issues.append('canonical incorrecto')
    if 'noindex' in (d.meta.get('robots', '') + headers.get('X-Robots-Tag', '')).lower(): issues.append('noindex')
    if not d.lang: issues.append('lang ausente')
    if any('error' in x for x in d.schemas): issues.append('JSON-LD inválido')
    return {'path': path, 'status': status, 'bytes': len(html.encode()), 'title': d.titles,
            'description': d.meta.get('description'), 'canonical': d.canonicals,
            'headings': d.headings, 'schemas': d.schemas, 'issues': issues,
            'images': d.images, 'links': d.links, 'ids': d.ids,
            'og': d.meta.get('og:title'), 'twitter': d.meta.get('twitter:card'),
            'unverified_mentions': len(re.findall('destino sin verificar', html, re.I))}

def main():
    client = app.test_client()
    local = []
    for path in sorted(s.INDEXABLE_PATHS):
        r = client.get(path)
        local.append(inspect(path, r.get_data(as_text=True), r.status_code, dict(r.headers)))
    graph = {}; broken = []; bad_anchors = []; assets = set(); affiliate_bad_rel = []
    bypath = {p['path']: p for p in local}
    for p in local:
        graph[p['path']] = set()
        for link in p['links']:
            href = link.get('href', '')
            u = urlsplit(urljoin(s.SITE_URL + p['path'], href))
            if u.netloc == urlsplit(s.SITE_URL).netloc:
                if u.path in bypath:
                    graph[p['path']].add(u.path)
                    if u.fragment and u.fragment not in bypath[u.path]['ids']: bad_anchors.append([p['path'], href])
                elif not u.path.startswith('/assets/'): broken.append([p['path'], href])
            if u.netloc == 'meli.la' and 'sponsored' not in link.get('rel', '').split(): affiliate_bad_rel.append([p['path'], href])
        for img in p['images']: assets.add(urljoin(s.SITE_URL, img.get('src', '')))
    depth = {'/': 0}; queue = deque(['/'])
    while queue:
        for target in graph[queue.popleft()]:
            if target not in depth:
                depth[target] = min(depth[src] + 1 for src in depth if target in graph[src])
                queue.append(target)
    excluded = [{'path': a['url'], 'file': str(a['path']), 'published': a['published']} for a in s._ALL_DRAFTS if a not in s.ALL_ARTICLES]
    urls = {s.SITE_URL+p for p in s.INDEXABLE_PATHS} | {s.SITE_URL+a['path'] for a in excluded}
    urls |= {s.SITE_URL+p for p in ['/robots.txt','/sitemap.xml','/search-cards.html','/seo-audit-inexistente/','/privacidad/','/contacto/','/compresores/50-litros']}
    urls |= {'http://tallerlab.com.ar/', 'http://www.tallerlab.com.ar/', 'https://tallerlab.com.ar/'}
    urls |= assets
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool: remote = list(pool.map(fetch, sorted(urls)))
    live = []
    for r in remote:
        path = urlsplit(r['url']).path
        if r['url'].startswith(s.SITE_URL) and path in bypath and 'body' in r:
            live.append(inspect(path, r['body'], r['status'], r['headers']))
    duplicates = {}
    for field in ['title', 'description']:
        groups = defaultdict(list)
        for p in local: groups[str(p[field])].append(p['path'])
        duplicates[field] = {k:v for k,v in groups.items() if len(v)>1}
    sitemap = next(r for r in remote if r['url'] == s.SITE_URL+'/sitemap.xml')
    sitemap_urls = []
    if 'body' in sitemap:
        sitemap_urls = [n.text for n in ET.fromstring(sitemap['body']).findall('{*}url/{*}loc')]
    summary = {'drafts': len(s._ALL_DRAFTS), 'articles': len(s.ALL_ARTICLES), 'routes':len(local),
               'local_issues':[{'path':p['path'],'issues':p['issues']} for p in local if p['issues']],
               'live_issues':[{'path':p['path'],'issues':p['issues']} for p in live if p['issues']],
               'live_checked':len(live), 'broken_internal':broken, 'bad_anchors':bad_anchors,
               'orphan_paths':sorted(set(bypath)-set(depth)), 'max_depth':max(depth.values()),
               'duplicate_metadata':duplicates, 'affiliate_without_sponsored':affiliate_bad_rel,
               'sitemap_count':len(sitemap_urls), 'sitemap_matches_local':set(sitemap_urls)=={s.SITE_URL+p for p in bypath},
               'missing_image_alt':sum('alt' not in i for p in local for i in p['images']),
               'missing_image_dimensions':sum(not (i.get('width') and i.get('height')) for p in local for i in p['images']),
               'pages_without_og':sum(not p['og'] for p in local),
               'pages_with_unverified_mentions':sum(bool(p['unverified_mentions']) for p in local),
               'excluded':excluded,
               'remote_failures':[{'url':r['url'],'status':r.get('status'),'error':r.get('error')} for r in remote if r.get('status') != 200]}
    evidence = {'summary':summary, 'local':local, 'live':live,
                'remote':[{k:v for k,v in r.items() if k!='body'} for r in remote],
                'robots':next(r.get('body') for r in remote if r['url']==s.SITE_URL+'/robots.txt')}
    Path('auditoria-seo-consultor-2026-09-30.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2), encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__ == '__main__': main()
