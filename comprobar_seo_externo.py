"""Controles públicos adicionales de redirecciones y PageSpeed."""
import json
from pathlib import Path
from urllib.request import Request, build_opener, HTTPRedirectHandler, urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError

class Redirects(HTTPRedirectHandler):
    def __init__(self): self.hops = []
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self.hops.append({'from':req.full_url, 'status':code, 'to':newurl})
        return super().redirect_request(req, fp, code, msg, headers, newurl)

output = {'redirects':[]}
for url in ['http://tallerlab.com.ar/','http://www.tallerlab.com.ar/','https://tallerlab.com.ar/','https://www.tallerlab.com.ar/compresores/50-litros']:
    handler = Redirects()
    with build_opener(handler).open(url, timeout=25) as r:
        output['redirects'].append({'url':url,'hops':handler.hops,'final_status':r.status,'final_url':r.url})
try:
    url = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?' + urlencode({'url':'https://www.tallerlab.com.ar/','strategy':'mobile','category':'performance'})
    with urlopen(url, timeout=55) as r:
        data = json.load(r)
    output['pagespeed'] = data
except HTTPError as e:
    output['pagespeed'] = {'status':e.code,'error':e.read().decode()[:1500]}
except Exception as e: output['pagespeed'] = {'error':str(e)}
Path('seo-redirecciones-pagespeed-2026-09-30.json').write_text(json.dumps(output, ensure_ascii=False, indent=2),encoding='utf-8')
print(json.dumps(output,ensure_ascii=False)[:5500])
