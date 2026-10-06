"""Transport requests from a browser to the real Flask test client over stdio."""
import base64
import json
import os
import sys
import tempfile
from pathlib import Path
os.environ.update(COMUNIDAD_HABILITADA='1', COMUNIDAD_DATABASE_URL='', APP_ENV='test', VERCEL='', VERCEL_ENV='')
from app import app
from comunidad import storage
with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent.parent/'tmp') as folder:
    storage.DB_PATH = Path(folder)/'browser.db'
    app.config.update(SECRET_KEY='browser-qa-only-secret', SESSION_COOKIE_SECURE=False)
    client = app.test_client()
    for line in sys.stdin:
        payload = json.loads(line)
        response = client.open(payload['path'], method=payload['method'], data=payload.get('body'),
            content_type=payload.get('type') or None)
        headers = {k:v for k,v in response.headers if k.lower() not in ('set-cookie','content-length','connection')}
        print(json.dumps(dict(status=response.status_code, headers=headers,
            body=base64.b64encode(response.data).decode())), flush=True)
