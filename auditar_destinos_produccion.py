"""Rastrea cada destino externo y de afiliación; conserva evidencia, sin certificar stock."""
import concurrent.futures
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import time
from urllib.parse import urlsplit, urlunsplit
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import servidor_local as s

class Evidence(HTMLParser):
    def __init__(self, html):
        super().__init__(); self.title = ''; self.parts = []; self.in_title = False
        self.meta = {}; self.links = []; self.feed(html)
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'title': self.in_title = True
        if tag == 'meta': self.meta[a.get('property', a.get('name', ''))] = a.get('content', '')
        if tag == 'a' and a.get('href', '').startswith(('https://', 'http://')): self.links.append(a['href'])
        if tag == 'img' and a.get('src', '').startswith(('https://', 'http://')): self.links.append(a['src'])
    def handle_data(self, data):
        if self.in_title: self.parts.append(data)
    def handle_endtag(self, tag):
        if tag == 'title': self.in_title = False; self.title = ''.join(self.parts)

def inspect(url):
    start = time.monotonic()
    try:
        with urlopen(Request(url, headers={'User-Agent':'Mozilla/5.0 (compatible; TallerLab-LinkAudit/1.0)'}), timeout=18) as r:
            body = r.read(1_500_000)
            result = {'url':url,'status':r.status,'final_url':r.url,'content_type':r.headers.get('Content-Type','')}
            if 'html' in result['content_type']:
                d = Evidence(body.decode('utf-8',errors='replace'))
                result.update(title=d.title, og_title=d.meta.get('og:title'), description=d.meta.get('description'), canonical_hint=d.meta.get('og:url'))
                result['challenge'] = bool(re.search(r'captcha|verify you are human|verifica que eres|security check|robot check|auth/authorize|account-verification', (d.title+' '+r.url+' '+body[:10000].decode('utf-8',errors='replace')), re.I))
            result['seconds'] = round(time.monotonic()-start,2)
            return result
    except HTTPError as e: return {'url':url,'status':e.code,'final_url':e.url,'error':str(e)}
    except Exception as e: return {'url':url,'error':str(e)}

def main():
    destinations = {}
    for a in s._ALL_DRAFTS:
        for url in re.findall(r'https?://[^\s<>"\)]+',a['body']):
            parsed = urlsplit(url)
            url = urlunsplit((parsed.scheme,parsed.netloc,parsed.path,parsed.query,''))
            if parsed.netloc in ('www.tallerlab.com.ar','tallerlab.com.ar'): continue
            destinations.setdefault(url,[]).append(a['url'])
    from app import app
    client = app.test_client()
    for path in s.INDEXABLE_PATHS:
        html = client.get(path).get_data(as_text=True)
        for url in Evidence(html).links:
            parsed = urlsplit(url)
            url = urlunsplit((parsed.scheme, parsed.netloc, parsed.path, parsed.query, ''))
            if parsed.netloc in ('www.tallerlab.com.ar', 'tallerlab.com.ar'): continue
            destinations.setdefault(url, []).append(path)
    output = Path('destinos-produccion-2026-09-30.json')
    existing = json.loads(output.read_text(encoding='utf-8')) if output.exists() else []
    done = {r['url'] for r in existing if r.get('status') == 200 and not r.get('challenge')}
    pending = [u for u in destinations if u not in done]
    results = {r['url']:dict(r, pages=sorted(set(destinations[r['url']]))) for r in existing if r['url'] in destinations}
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
        for i, r in enumerate(pool.map(inspect,pending),1):
            r['pages'] = sorted(set(destinations[r['url']]))
            results[r['url']] = r
            if i % 25 == 0:
                output.write_text(json.dumps(list(results.values()),ensure_ascii=False,indent=2),encoding='utf-8')
                print(f'{i}/{len(pending)} destinos comprobados',flush=True)
    output.write_text(json.dumps(list(results.values()),ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'destinations':len(results),'http_200':sum(r.get('status')==200 for r in results.values()),'challenges':sum(bool(r.get('challenge')) for r in results.values()),'affiliate':sum(urlsplit(r['url']).netloc=='meli.la' for r in results.values())}))

if __name__ == '__main__': main()
