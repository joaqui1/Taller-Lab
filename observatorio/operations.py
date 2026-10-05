"""Cobertura real y monitor externo; una corrida vacía nunca acredita salud."""
import argparse
import json
import os
from datetime import datetime, timedelta, timezone
from observatorio import config
from observatorio.db import query_one

def capture_health():
    day=datetime.now(config.TZ_BUENOS_AIRES).date().isoformat()
    expected=query_one("""SELECT COUNT(*) AS c FROM offers off JOIN sources src ON src.id=off.source_id
        WHERE off.enabled=1 AND src.status='habilitada' AND src.capture_allowed=1 AND src.terms_verified_date IS NOT NULL""")['c']
    captured=query_one("""SELECT COUNT(*) AS c FROM offers off JOIN sources src ON src.id=off.source_id
        WHERE off.enabled=1 AND src.status='habilitada' AND src.capture_allowed=1 AND src.terms_verified_date IS NOT NULL
        AND EXISTS(SELECT 1 FROM observations o WHERE o.offer_id=off.id AND o.is_synthetic=0 AND o.capture_key=? || off.id)""",('real:'+day+':',))['c']
    last=query_one("SELECT * FROM collector_runs WHERE EXISTS (SELECT 1 FROM collector_attempts a WHERE a.run_id=collector_runs.id AND a.is_synthetic=0) ORDER BY started_at DESC LIMIT 1")
    stale=True
    if last:
        stale=(datetime.now(timezone.utc)-datetime.fromisoformat(last['started_at'])).total_seconds()>26*3600
    return {'status':'ok' if expected and captured==expected and not stale else 'degradado',
            'day_art':day,'expected_offers':expected,'captured_offers':captured,'pending_offers':max(0,expected-captured),'stale':stale}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('command',choices=['health','monitor','complete'])
    args=parser.parse_args()
    if args.command=='health':
        health=capture_health()
    else:
        import requests
        secret=os.environ.get('CRON_SECRET') or os.environ.get('OBSERVATORY_SECRET')
        if not secret: raise SystemExit('Falta configurar el secreto del monitor.')
        headers={'Authorization':'Bearer '+secret}
        if args.command=='complete':
            for _ in range(3):
                result=requests.post(config.SITE_URL+'/api/observatorio/ejecutar',headers=headers,timeout=310)
                result.raise_for_status()
                summary=result.json()
                if summary.get('pending_offers')==0: break
        response=requests.get(config.SITE_URL+'/api/observatorio/estado',headers=headers,timeout=20)
        response.raise_for_status()
        payload=response.json()
        health=payload.get('coverage',{'status':'degradado'})
        if payload.get('status')!='ok': health=dict(health,status='degradado')
    print(json.dumps(health,ensure_ascii=False))
    raise SystemExit(0 if health['status']=='ok' else 1)

if __name__=='__main__': main()
