"""Public aggregate health and external supervision of documentary maintenance."""
import argparse
import json
import os
from datetime import datetime, timezone
from compatibilidad import catalog
from compatibilidad.storage import StateStore

def capture_health():
    catalog.refresh_published_state()
    ready=False
    try:
        state=StateStore().current()
        ready=bool(state)
    except Exception:
        state=None
    metadata=(state or {}).get('metadata',catalog.CURRENT_METADATA)
    try:
        age=(datetime.now(timezone.utc)-datetime.fromisoformat(metadata['last_checked_at'])).total_seconds()
        fresh=0<=age<=26*3600
    except (KeyError,ValueError,TypeError):
        age=None;fresh=False
    sources=(state or {}).get('sources',[])
    failures=sum(s.get('status')!='accesible' for s in sources)
    verified=sum(p.status=='publicado' for p in catalog.CATALOG_PRODUCTS)
    ok=ready and fresh and bool(sources) and not failures and verified>0
    return {'status':'ok' if ok else 'degradado','version':metadata['version'],
        'storage_ready':ready,'fresh':fresh,'last_checked_at':metadata.get('last_checked_at'),
        'sources_checked':len(sources),'source_failures':failures,'verified_products':verified,
        'pending_products':len(catalog.CATALOG_PRODUCTS)-verified,'documented_relations':len(catalog.RELATIONS)}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('command',choices=['health','monitor'])
    args=parser.parse_args()
    if args.command=='health':
        health=capture_health()
    else:
        from urllib.request import urlopen
        from urllib.error import HTTPError
        url=os.environ.get('SITE_URL','https://www.tallerlab.com.ar').rstrip('/')+'/api/compatibilidad/estado'
        try:
            with urlopen(url,timeout=25) as response:health=json.load(response)
        except HTTPError as exc:
            try:health=json.load(exc)
            except Exception:health={'status':'degradado','http_status':exc.code}
    print(json.dumps(health,ensure_ascii=False))
    raise SystemExit(0 if health.get('status')=='ok' else 1)

if __name__=='__main__':main()
