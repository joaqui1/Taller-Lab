"""Regresiones del relevamiento sin tocar respuestas reales."""
import os, re, tempfile, time, unittest
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
os.environ.update(RELEVAMIENTO_HABILITADO='1', RELEVAMIENTO_ADMIN_KEY='clave-pruebas', RELEVAMIENTO_SESSION_SECRET='sesion-pruebas-32-caracteres-minimo')
os.environ.pop('RELEVAMIENTO_DATABASE_URL',None)
import relevamiento_piloto as rel
from app import app

class SurveyTests(unittest.TestCase):
    def setUp(self):
        root=Path(__file__).resolve().parent/'tmp';root.mkdir(exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(prefix='rel-test-',dir=root)
        self.override=patch.object(rel,'DB_PATH',Path(self.temp.name)/'test.db');self.override.start()
        self.client=app.test_client()
        self.data=dict(form_start_timestamp=str(time.time()-35),oficio='herreria',provincia='Córdoba',tipo_uso='profesional',intensidad='diario_intensivo',marca_principal='Bosch',plataformas_bateria=['bosch_18v'],cantidad_baterias='3_4',proporcion_cable='50_50',canal_compra='ferreteria_local',reparaciones_12m='1',falla_frecuente='carbones',proxima_herramienta='taladro',horizonte_compra='30_dias',resena_modelo='Bosch GWS 770',resena_ventajas='Compacta',consent_review=True,consent_report=True,consent_commercial=False,contacto_email='informe@example.test')
    def tearDown(self): self.override.stop();self.temp.cleanup()
    def submit(self,changes=None): return self.client.post('/api/relevamiento/submit',json={**self.data,**(changes or {})})
    def login(self):
        html=self.client.get('/relevamiento-2027/admin/').get_data(as_text=True)
        token=re.search(r'name="csrf_token" value="([^"]+)"',html).group(1)
        self.assertEqual(self.client.post('/relevamiento-2027/admin/login',data={'key':rel.get_admin_key(),'csrf_token':token}).status_code,303)
        with self.client.session_transaction() as session: return session['rel_csrf']
    def test_form_and_flags(self):
        html=self.client.get('/relevamiento-2027/').get_data(as_text=True)
        self.assertIn("formData.getAll('plataformas_bateria')",html)
        self.assertGreater(html.count('name="plataformas_bateria"'),4)
        self.assertNotIn('select id="plataforma_bateria"',html)
        with patch.dict(os.environ,{'RELEVAMIENTO_HABILITADO':'0'}):
            self.assertEqual(self.submit().status_code,503)
            self.assertNotIn('id="relevamiento-form"',self.client.get('/relevamiento-2027/').get_data(as_text=True))
            self.assertEqual(rel.render_relevamiento_callout(),'')
        with patch.dict(os.environ,{'APP_ENV':'production'}):
            self.assertFalse(rel.relevamiento_abierto())
            with self.assertRaises(RuntimeError): rel.get_db_connection()
    def test_multiple_and_invalid(self):
        second=next(k for k,_ in rel.PLATAFORMAS_BATERIA if k not in ('bosch_18v','no_usa','no_sabe','otra'))
        r=self.submit({'plataformas_bateria':['bosch_18v',second]});self.assertEqual(r.status_code,200,r.data)
        self.assertEqual(len(rel.cargar_respuestas_analiticas()[0]['plataformas_bateria']),2)
        for change in ({'falla_frecuente':'inventada'},{'marca_principal':'inventada'},{'plataformas_bateria':['no_usa','bosch_18v']},{'plataformas_bateria':['no_sabe','bosch_18v']},{'plataformas_bateria':['no_usa']},{'plataformas_bateria':['otra']}):
            self.assertEqual(self.submit(change).status_code,400,change)
        self.assertIn(';',rel.exportar_dataset('analitica')[0])
    def test_admin_session_and_atomic_moderation(self):
        r=self.submit({'consent_review':False});self.assertEqual(r.status_code,200,r.data);rid=r.json['response_id']
        self.assertEqual(self.client.get('/relevamiento-2027/admin/?key='+rel.get_admin_key()).status_code,303)
        self.assertEqual(self.client.get('/api/relevamiento/export?key='+rel.get_admin_key()).status_code,403)
        token=self.login();html=self.client.get('/relevamiento-2027/admin/').get_data(as_text=True)
        self.assertNotIn(rel.get_admin_key(),html);self.assertNotIn('?key=',html)
        self.assertEqual(self.client.post('/api/relevamiento/moderar',json={'response_id':rid,'estado':'descartada'}).status_code,403)
        r=self.client.post('/api/relevamiento/moderar',json={'response_id':rid,'estado':'descartada','aprobar_resena':True},headers={'X-CSRF-Token':token})
        self.assertEqual(r.status_code,400);self.assertEqual(rel.cargar_respuestas_analiticas()[0]['estado'],'valida')
        self.assertEqual(self.client.get('/api/relevamiento/export?tipo=contactos').status_code,400)
        self.assertEqual(self.client.post('/relevamiento-2027/admin/logout',data={'csrf_token':token}).status_code,303)
        self.assertEqual(self.client.get('/api/relevamiento/export').status_code,403)
    def test_review_and_contact_purposes(self):
        r=self.submit();rid=r.json['response_id']
        self.assertTrue(rel.actualizar_estado_moderacion(rid,'revision_pendiente'))
        self.assertFalse(rel.actualizar_estado_moderacion(rid,aprobar_resena=True))
        self.assertTrue(rel.actualizar_estado_moderacion(rid,'valida'))
        self.assertTrue(rel.actualizar_estado_moderacion(rid,aprobar_resena=True))
        self.assertTrue(rel.actualizar_estado_moderacion(rid,'descartada'))
        self.assertFalse(rel.cargar_respuestas_analiticas()[0]['resena']['aprobada_publicacion'])
        self.assertEqual(self.submit({'contacto_email':'comercial@example.test','consent_report':False,'consent_commercial':True}).status_code,200)
        self.assertIn('informe@example.test',rel.exportar_dataset('informe')[0])
        self.assertNotIn('comercial@example.test',rel.exportar_dataset('informe')[0])
        self.assertNotIn('informe@example.test',rel.exportar_dataset('comercial')[0])
        self.assertNotIn('example.test',rel.exportar_dataset('publica')[0])
    def test_events(self):
        for bad in ([1],{'paso':[]},{'paso':'start','session_id':'short'}): self.assertEqual(self.client.post('/api/relevamiento/abandon',json=bad).status_code,400)
        for stage in ('start','start','completed'): self.assertEqual(self.client.post('/api/relevamiento/abandon',json={'paso':stage,'session_id':'sesion-pruebas-123456'}).status_code,200)
        stats=rel.calcular_estadisticas();self.assertEqual(stats['sesiones_iniciadas'],1);self.assertEqual(stats['completitud'],100);self.assertEqual(len(rel.cargar_abandonos()),2)
    def test_concurrency_and_persistent_limit(self):
        with ThreadPoolExecutor(max_workers=6) as pool: ids=list(pool.map(lambda i:rel.guardar_respuesta_y_contacto({**self.data,'response_id':f'concurrent-{i}'}),range(24)))
        self.assertEqual(len(set(ids)),24);self.assertEqual(len(rel.cargar_respuestas_analiticas()),24)
        with ThreadPoolExecutor(max_workers=6) as pool: limited=list(pool.map(lambda _:rel.check_ip_rate_limit('concurrent-limit',maximum=5),range(15)))
        self.assertEqual(limited.count(False),5);self.assertTrue(rel.check_ip_rate_limit('concurrent-limit',maximum=5))
    def test_bad_types_and_csv(self):
        for data in ([1],{'oficio':123},{'plataformas_bateria':{}}): self.assertEqual(self.client.post('/api/relevamiento/submit',json=data).status_code,400)
        self.assertTrue(rel.sanitize_csv_cell('=1+1').startswith("'"));self.assertTrue(rel.sanitize_csv_cell('\t=1+1').startswith("'"))
        self.assertEqual(self.submit({'resena_modelo':'x'*101}).status_code,400)
        self.assertEqual(self.submit({'resena_ventajas':[]}).status_code,400)

    def test_consent_version_and_revocation(self):
        r=self.submit();rid=r.json['response_id'];token=self.login()
        conn=rel.get_db_connection()
        self.assertEqual(conn.execute('SELECT version FROM consentimientos WHERE response_id=?',(rid,)).fetchone()['version'],rel.CONSENT_VERSION)
        conn.close()
        self.assertEqual(self.client.post('/api/relevamiento/revocar',json={'response_id':rid}).status_code,403)
        r=self.client.post('/api/relevamiento/revocar',json={'response_id':rid},headers={'X-CSRF-Token':token})
        self.assertEqual(r.status_code,200)
        self.assertEqual(rel.cargar_contactos(),[])
        self.assertFalse(rel.actualizar_estado_moderacion(rid,aprobar_resena=True))
        self.assertNotIn('informe@example.test',rel.exportar_dataset('informe')[0])

    def test_storage_rollback_and_session_expiry(self):
        with self.assertRaises(AttributeError):
            rel.guardar_respuesta_y_contacto({**self.data,'response_id':'rollback-test'},{'email':123})
        self.assertEqual(rel.cargar_respuestas_analiticas(),[])
        self.login()
        with self.client.session_transaction() as session: session['rel_expires']=time.time()-1
        self.assertEqual(self.client.get('/api/relevamiento/export').status_code,403)

if __name__=='__main__': unittest.main(verbosity=2)
