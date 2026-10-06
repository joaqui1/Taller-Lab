"""Regresiones operativas: almacén real SQLite, fuentes aisladas y API Flask."""
import argparse
import copy
import json
import os
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import verificar_alertas  # Dependencias locales de QA, sin instalaciones globales.
import test_alertas_regresiones as regression
import alertas_datos as d
import alertas_operacion as op
import sincronizador_alertas as sync
import gestionar_alertas as editorial
from alertas_almacen import guardar_estado, archivar_payload, leer_captura, captura_verificable, serializado
from alertas_persistencia import AlmacenOcupado
import app


class OperacionAlertas(unittest.TestCase):
    def setUp(self):
        self.environment = patch.dict(os.environ, {'ALERTAS_DATABASE_URL': '', 'DATABASE_URL': '',
            'ALERTAS_STATE_PATH': '', 'VERCEL': '', 'ALERTAS_SOLO_LECTURA': '',
            'CRON_SECRET': 'cron-prueba', 'ALERTAS_EDITOR_TOKEN': 'editor-prueba'})
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.seed = regression.AlertasRegresiones()
        self.seed.setUp()
        self.addCleanup(self.seed.doCleanups)
        self.client = app.app.test_client()

    def sqlite(self):
        os.environ['ALERTAS_STATE_PATH'] = str(self.seed.root / 'operacion.sqlite3')

    def test_respaldo_diario_no_reemplaza_version_previa_y_exige_autenticacion(self):
        from alertas_respaldo import automatico, anteriores
        self.sqlite()
        self.assertEqual(automatico()['estado'], 'guardado')
        fecha = anteriores()[0]['fecha']
        raw = anteriores(fecha)
        self.seed.ingest()
        automatico()
        self.assertEqual(anteriores(fecha), raw)
        self.assertEqual(self.client.get('/api/alertas/respaldos').status_code, 401)
        headers = {'Authorization': 'Bearer editor-prueba'}
        self.assertEqual(self.client.get('/api/alertas/respaldos/'+fecha, headers=headers).data, raw)

    def test_snapshot_local_no_acredita_automatizacion_vercel(self):
        with patch.dict(os.environ, {'VERCEL': '1'}):
            self.assertEqual(op.estado_publico()['estado'], 'sin_programacion_verificada')
            self.assertEqual(op.estado_publico()['persistencia'], 'snapshot')

    def test_clave_unicode_devuelve_no_autorizado(self):
        self.assertEqual(self.client.get('/api/alertas/editorial', headers={'Authorization': 'Bearer clave-con-ñ'}).status_code, 401)

    def test_revision_antigua_muestra_advertencia(self):
        exp = d.obtener_expediente('dewalt-dws713')
        exp['fecha_revision'] = '2025-01-01'
        self.assertTrue(any('90 días' in aviso for aviso in d.expediente_publico(exp)['avisos_actualizacion']))

    def test_variantes_compuestas_se_detectan_por_codigo_individual(self):
        for code in ('XPG01Z', 'XPG01SR1', 'XPG01S1'):
            result = sync._buscar_modelos_candidatos('Makita '+code)
            self.assertEqual(result[0][0], 'makita-dgp180')
        result = sync._buscar_modelos_candidatos('', [{'Name': 'Makita XPG01Z grease gun'}])
        self.assertEqual(result[0][0], 'makita-dgp180')

    def test_no_se_cambia_mercado_de_cpsc_a_argentina(self):
        self.seed.ingest()
        with self.assertRaises(SystemExit):
            editorial.cmd_aprobar_candidato(self.seed.args(pais_mercado='Argentina'))
        self.assertEqual(d.obtener_expediente('dewalt-dws713')['alertas'], [])

    def test_fuente_sin_cambios_recupera_coincidencia_de_catalogo(self):
        with patch.object(sync, '_buscar_modelos_candidatos', return_value=[]):
            self.seed.ingest()
        self.assertIsNone(d.cargar_candidatos()[0]['coincidencia_modelo'])
        self.seed.ingest()
        self.assertEqual(d.cargar_candidatos()[0]['coincidencia_modelo'], 'dewalt-dws713')

    def test_sqlite_guarda_capturas_y_publicacion_sin_editar_snapshot(self):
        self.sqlite()
        snapshot_before = d.MODELOS_FILE.read_bytes()
        self.seed.ingest()
        editorial.cmd_aprobar_candidato(self.seed.args(revisado_por=d.EDITOR_RESPONSABLE))
        exp = d.obtener_expediente('dewalt-dws713')
        self.assertEqual(exp['editor_responsable'], 'Joaquín Vallasciani')
        self.assertTrue(captura_verificable(exp['alertas'][0]['evidencia_fuente']['version_fuente']))
        self.assertEqual(snapshot_before, d.MODELOS_FILE.read_bytes())
        page = self.client.get('/alertas/dewalt-dws713/')
        self.assertEqual(page.status_code, 200)
        self.assertIn('Reparación gratuita en Estados Unidos'.encode(), page.data)

    def test_transaccion_sqlite_revierte_toda_decision_interrumpida(self):
        self.sqlite()
        initial = d.cargar_candidatos()
        @serializado
        def fail():
            guardar_estado(candidatos=[{'id': 'no-publicar'}])
            raise ValueError('Interrupción')
        with self.assertRaises(ValueError):
            fail()
        self.assertEqual(initial, d.cargar_candidatos())

    def test_recoleccion_no_autopublica_y_resiste_ejecucion_duplicada(self):
        self.sqlite()
        self.seed.ingest()
        with patch.object(op, 'sincronizar_cpsc', return_value={'exito': True}), patch.object(op, 'sincronizar_defensa_consumidor', return_value={'exito': True}), patch.object(op, 'sincronizar_sernac', return_value={'exito': True}):
            self.assertEqual(op.ejecutar()['estado'], 'correcto')
            self.assertEqual(op.ejecutar()['estado'], 'correcto')
        self.assertEqual(len(d.cargar_candidatos()), 1)
        self.assertEqual(d.obtener_expediente('dewalt-dws713')['alertas'], [])
        self.assertEqual(op.estado_publico()['estado'], 'correcto')

    def test_reintenta_fuente_y_muestra_caida(self):
        with patch.object(op, 'sincronizar_cpsc', return_value={'exito': True}), patch.object(op, 'sincronizar_defensa_consumidor', return_value={'exito': False}) as failing, patch.object(op, 'sincronizar_sernac', return_value={'exito': True}):
            result = op.ejecutar()
        self.assertEqual(result['estado'], 'parcial')
        self.assertEqual(failing.call_count, 2)
        self.assertEqual(op.estado_publico()['estado'], 'requiere_atencion')

    def test_lease_impide_solapamiento_y_recupera_ejecucion_abandonada(self):
        first, _ = op.iniciar()
        with self.assertRaises(AlmacenOcupado):
            op.iniciar()
        reg = d.cargar_registro_fuentes()
        reg['operacion']['inicio'] = (datetime.now(timezone.utc)-timedelta(days=1)).isoformat()
        guardar_estado(registro=reg)
        second, _ = op.iniciar()
        self.assertNotEqual(first, second)

    def test_api_autorizacion_y_parametros(self):
        self.assertEqual(self.client.get('/api/alertas/ejecutar').status_code, 401)
        self.assertEqual(self.client.get('/api/alertas/editorial').status_code, 401)
        self.assertEqual(self.client.get('/api/alertas/editorial', headers={'Authorization': 'Bearer cron-prueba'}).status_code, 401)
        self.assertEqual(self.client.get('/api/alertas/ejecutar?fixtures=1', headers={'Authorization': 'Bearer cron-prueba'}).status_code, 400)

    def test_revision_api_exige_version_actual_y_publica_decision(self):
        self.sqlite()
        self.seed.ingest()
        cand = d.cargar_candidatos()[0]
        payload = {'id': cand['id'], 'version_fuente': 'version-obsoleta', 'accion_editorial': 'aprobar',
            'slug': 'dewalt-dws713', 'modelos': 'DWS713', 'lotes': 'ABC', 'excepciones': 'Lote X excluido'}
        headers = {'Authorization': 'Bearer editor-prueba'}
        self.assertEqual(self.client.post('/api/alertas/editorial/decision', json=payload, headers=headers).status_code, 409)
        payload['version_fuente'] = cand['version_fuente']
        response = self.client.post('/api/alertas/editorial/decision', json=payload, headers=headers)
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(d.obtener_expediente('dewalt-dws713')['revisado_por'], d.EDITOR_RESPONSABLE)
        self.assertIn('DWS713'.encode(), self.client.get('/datos/alertas/avisos.json').data)

    def test_paginas_y_dataset_indican_editor_y_limites(self):
        for path in ('/alertas/editorial/', '/alertas/metodologia/', '/alertas/estado/', '/datos/alertas/avisos.json', '/datos/alertas/avisos.csv'):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200, path)
            self.assertIn('Joaquín Vallasciani'.encode(), response.data)
        self.assertIn('noindex', self.client.get('/alertas/editorial/').headers['X-Robots-Tag'])

    def test_vercel_sin_base_no_ejecuta_ingesta(self):
        os.environ['VERCEL'] = '1'
        with self.assertRaises(RuntimeError):
            op.ejecutar()

    def test_respaldo_y_restauracion_recuperan_version_y_captura(self):
        from alertas_respaldo import respaldo, restaurar
        self.sqlite()
        self.seed.ingest()
        original = d.cargar_candidatos()
        raw = respaldo()
        guardar_estado(candidatos=[])
        result = restaurar(raw)
        self.assertEqual(d.cargar_candidatos(), original)
        self.assertGreater(result['capturas'], 0)
        self.assertTrue(captura_verificable(original[0]['version_fuente']))

    def test_respaldo_corrupto_no_modifica_publicacion(self):
        from alertas_respaldo import respaldo, restaurar
        import io, zipfile
        self.sqlite()
        original = d.cargar_expedientes()
        raw = respaldo()
        output = io.BytesIO()
        with zipfile.ZipFile(io.BytesIO(raw)) as source, zipfile.ZipFile(output, 'w') as target:
            for name in source.namelist():
                target.writestr(name, b'[]' if name == 'modelos_expedientes.json' else source.read(name))
        with self.assertRaises(ValueError):
            restaurar(output.getvalue())
        self.assertEqual(original, d.cargar_expedientes())

    def test_historico_no_oculta_fallo_del_diario(self):
        registro = d.cargar_registro_fuentes()
        registro['operacion'] = {'estado': 'parcial', 'fin': op.ahora()}
        guardar_estado(registro=registro)
        with patch.object(op, 'sincronizar_cpsc', return_value={'exito': True}):
            self.assertEqual(op.ejecutar(historico=True)['estado'], 'correcto')
        self.assertEqual(op.estado_publico()['estado'], 'requiere_atencion')

    def test_cpsc_error_interno_disfrazado_de_aviso_no_es_exito(self):
        self.seed.response([{'RecallID': 0, 'RecallNumber': None, 'Title': 'Error retrieving Recalls'}])
        result = sync.sincronizar_cpsc('novedades', desde='2026-09-27')
        self.assertFalse(result['exito'])
        self.assertEqual(d.cargar_candidatos(), [])

    def test_sernac_cambio_real_genera_candidato_y_conserva_texto_publicado(self):
        from unittest.mock import MagicMock
        aviso = d.obtener_expediente('dewalt-dw8307')['alertas'][0]
        html = '<html><h1>Alerta de seguridad DeWalt DW8307</h1><p>'+('DeWalt DW8307 lote 3531. '*25)+'</p></html>'
        self.seed.response(html, csv=True)
        result = op.sincronizar_sernac(aviso)
        self.assertTrue(result['exito'])
        self.assertEqual(d.cargar_candidatos()[0]['estado_revision'], 'PENDIENTE')
        self.assertEqual(d.obtener_expediente('dewalt-dw8307')['alertas'][0], aviso)
        self.seed.response(html.replace('3531', '3532'), csv=True)
        op.sincronizar_sernac(aviso)
        self.assertEqual(d.cargar_candidatos()[0]['estado_revision'], 'MODIFICADO_PENDIENTE')


if __name__ == '__main__':
    unittest.main()
