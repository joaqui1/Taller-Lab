"""Pruebas de recorridos completos; fuentes simuladas y almacenamiento aislado."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import shutil
import os
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import alertas_datos as d
import alertas_almacen as storage
import gestionar_alertas as editorial
import sincronizador_alertas as sync
from render_alertas import render_model_dossier_page, render_alerts_hub_page


class AlertasRegresiones(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path.cwd(), prefix=".qa-alertas-")
        self.root = Path(self.temp.name)
        shutil.copy(d.MODELOS_FILE, self.root / "modelos_expedientes.json")
        (self.root / "candidatos_revision.json").write_text("[]", encoding="utf-8")
        (self.root / "registro_fuentes.json").write_text("{}", encoding="utf-8")
        for key, value in (("DATOS_DIR", self.root),
                           ("MODELOS_FILE", self.root / "modelos_expedientes.json"),
                           ("CANDIDATOS_FILE", self.root / "candidatos_revision.json"),
                           ("FUENTES_FILE", self.root / "registro_fuentes.json")):
            p = patch.object(d, key, value)
            p.start()
            self.addCleanup(p.stop)
        self.addCleanup(self.temp.cleanup)
        self.network = patch("urllib.request.urlopen")
        self.urlopen = self.network.start()
        self.addCleanup(self.network.stop)

    def response(self, payload, csv=False):
        response = MagicMock()
        response.read.return_value = (payload if csv else json.dumps(payload)).encode("utf-8")
        response.__enter__.return_value = response
        self.urlopen.side_effect = None
        self.urlopen.return_value = response

    def aviso(self, **changes):
        aviso = {"RecallNumber": "TEST1", "Title": "DeWalt DWS713",
                 "Description": "DWS713 fecha de producción ABC, excepto lote X",
                 "Products": [{"Name": "DeWalt DWS713"}],
                 "Hazards": [{"Name": "Riesgo de corte"}],
                 "Remedies": [{"Name": "Reparación gratuita en Estados Unidos"}],
                 "URL": "https://www.cpsc.gov/Recalls/test", "RecallDate": "2026-10-03"}
        aviso.update(changes)
        return aviso

    def ingest(self, **changes):
        self.response([self.aviso(**changes)])
        return sync.sincronizar_cpsc("DeWalt")

    def args(self, **changes):
        values = dict(cand_id="cand-cpsc-TEST1", slug="dewalt-dws713", alcance=None,
                      pais_mercado=None, modelos="DWS713", lotes="ABC",
                      periodo=None, ubicacion=None, unidades=None,
                      excepciones="Lote X excluido", defecto=None, accion=None,
                      revisado_por="Revisor de prueba")
        values.update(changes)
        return argparse.Namespace(**values)

    def test_reordenar_y_insertar_fila_no_modifica_avisos(self):
        header = "Fecha,Marca,Producto,Defecto,Riesgos\n"
        a = "2023/05/09,DeWalt,DWS780,Guarda rota,Cortes\n"
        b = "2025/04/14,Makita,DGP180,Manguera rota,Lesiones\n"
        self.response(header + a + b, csv=True)
        self.assertEqual(sync.sincronizar_defensa_consumidor()["nuevos"], 2)
        cands = d.cargar_candidatos()
        for c in cands:
            c["estado_revision"] = "APROBADO"
        d.guardar_candidatos(cands)
        self.response(header + "2026/01/01,Otra,Automóvil,Motor,Incendio\n" + b + a, csv=True)
        result = sync.sincronizar_defensa_consumidor()
        self.assertEqual((result["modificados"], result["sin_cambios"]), (0, 2))
        self.assertTrue(all(c["estado_revision"] == "APROBADO" for c in d.cargar_candidatos()))

    def test_fallo_real_se_muestra_sin_borrar_antecedentes(self):
        exp = copy.deepcopy(d.obtener_expediente("dewalt-dws713"))
        exp["fuentes_consultadas"] = [{"fuente": "CPSC API", "estado": "EXITOSA",
            "fecha_consulta": "2026-10-01", "resultado": "Sin coincidencias en consulta editorial"}]
        exp["estado_general"] = "SIN_ALERTAS"
        self.urlopen.side_effect = TimeoutError("Fallo simulado")
        self.assertFalse(sync.sincronizar_cpsc("DeWalt")["exito"])
        html = render_model_dossier_page(exp)
        self.assertIn("último intento de actualización fallido", html)
        self.assertIn("2026-10-01", html)
        self.assertIn("Consulta de fuentes externas no completada", html)
        positive = d.obtener_expediente("dewalt-dws780")
        html = render_model_dossier_page(positive)
        self.assertIn("último intento de actualización fallido", html)
        self.assertIn("Alerta oficial confirmada", html)
        self.assertGreater(len(positive["alertas"]), 0)

    def test_fallo_de_otra_marca_no_se_atribuye_al_modelo(self):
        self.urlopen.side_effect = TimeoutError("Fallo simulado")
        sync.sincronizar_cpsc("DeWalt")
        self.assertNotIn("último intento de actualización fallido",
                         render_model_dossier_page(d.obtener_expediente("makita-dgp180")))

    def test_payloads_invalidos_no_declaran_exito(self):
        for payload in ([{}], [None], [self.aviso(Products=[None])],
                        [self.aviso(Products="error")], [self.aviso(RecallNumber=None)]):
            with self.subTest(payload=payload):
                self.response(payload)
                self.assertFalse(sync.sincronizar_cpsc()["exito"])
                self.assertEqual(d.cargar_registro_fuentes()["cpsc"]["estado"], "FALLIDA")
                self.assertEqual(d.cargar_candidatos(), [])

    def test_id_nulo_usa_recallid_y_lista_vacia_es_valida(self):
        self.response([self.aviso(RecallNumber=None, RecallID=77, Products=[{"Model": None}])])
        self.assertTrue(sync.sincronizar_cpsc()["exito"])
        self.assertEqual(d.cargar_candidatos()[0]["id_externo"], "77")
        self.response([])
        self.assertTrue(sync.sincronizar_cpsc()["exito"])

    def test_pendiente_o_sin_evidencia_no_es_resultado_negativo(self):
        for fuente in ({"estado": "PENDIENTE"}, {"estado": "EXITOSA"},
                       {"estado": "EXITOSA", "fecha_consulta": "2026-10-03",
                        "resultado": "Sin alertas", "evidencia_consulta": False}):
            self.assertEqual(d.derivar_estado_expediente([], [fuente]), "NO_REVISADO")
        html = render_model_dossier_page(d.obtener_expediente("dewalt-dws713"))
        self.assertIn("Relevamiento documental en proceso", html)
        self.assertNotIn("Verificado con fuentes primarias", html)
        self.assertNotIn("expedientes técnicos verificados", render_alerts_hub_page())

    def test_aprobacion_incompleta_no_modifica_archivos(self):
        self.ingest()
        before = d.MODELOS_FILE.read_bytes()
        for field in ("modelos", "lotes", "excepciones", "revisado_por"):
            with self.subTest(field=field), self.assertRaises(SystemExit):
                editorial.cmd_aprobar_candidato(self.args(**{field: None}))
            self.assertEqual(d.MODELOS_FILE.read_bytes(), before)
        with self.assertRaises(SystemExit):
            editorial.cmd_aprobar_candidato(self.args(alcance="SIN_ALERTAS"))
        self.assertEqual(d.MODELOS_FILE.read_bytes(), before)

    def test_aprobacion_conserva_version_y_modelos_pendientes(self):
        self.ingest(Title="DeWalt DWS713 y DWS780", Products=[{"Name": "DeWalt DWS713 y DWS780"}])
        editorial.cmd_aprobar_candidato(self.args())
        cand = d.cargar_candidatos()[0]
        self.assertEqual(cand["modelos_pendientes"], ["dewalt-dws780"])
        self.assertEqual(cand["estado_revision"], "PENDIENTE")
        al = d.obtener_expediente("dewalt-dws713")["alertas"][0]
        version = al["evidencia_fuente"]["version_fuente"]
        self.assertTrue((self.root / "capturas" / (version + ".json")).exists())
        self.assertEqual(al["pais_mercado"], "Estados Unidos")
        self.assertEqual(al["estado_alcance"], "POSIBLE_COINCIDENCIA")

    def test_identificador_cpsc_con_prefijo_no_duplica_alerta(self):
        self.ingest()
        editorial.cmd_aprobar_candidato(self.args())
        expedientes = d.cargar_expedientes()
        exp = next(e for e in expedientes if e["slug"] == "dewalt-dws713")
        exp["alertas"][0]["id_aviso"] = "CPSC-TEST1"
        d.guardar_expedientes(expedientes)
        editorial.cmd_aprobar_candidato(self.args())
        self.assertEqual(len(d.obtener_expediente("dewalt-dws713")["alertas"]), 1)

    def test_consulta_negativa_exige_captura_modelos_y_metodo(self):
        digest = storage.archivar_payload({"url": "https://www.cpsc.gov/consulta-test",
                                         "contenido": "Respuesta de prueba sin coincidencias"})
        args = argparse.Namespace(slug="dewalt-dws713", fuente="cpsc", captura=digest,
                                  modelos=["DWS713"], metodo="Relevamiento de prueba",
                                  revisado_por="Tester")
        with self.assertRaises(SystemExit):
            editorial.cmd_registrar_consulta(args)
        exp = d.obtener_expediente(args.slug)
        args.modelos += [v["codigo"] for v in exp["variantes"]]
        editorial.cmd_registrar_consulta(args)
        updated = d.obtener_expediente(args.slug)
        fuente = next(f for f in updated["fuentes_consultadas"] if d.fuente_clave(f["fuente"]) == "cpsc")
        self.assertTrue(d.evidencia_negativa_completa(fuente))
        self.assertEqual(updated["estado_general"], "NO_REVISADO")  # Las otras fuentes siguen pendientes.
        (self.root / "capturas" / (digest + ".json")).write_text("corrupto", encoding="utf-8")
        self.assertFalse(d.evidencia_negativa_completa(fuente))

    def test_aviso_nuevo_pendiente_visible_sin_publicacion_automatica(self):
        self.ingest()
        editorial.cmd_aprobar_candidato(self.args())
        self.ingest(Description="Nueva restricción oficial")
        exp = d.obtener_expediente("dewalt-dws713")
        self.assertNotIn("Nueva restricción oficial", exp["alertas"][0]["defecto_riesgo"])
        self.assertIn("pendiente de cotejo con la versión publicada", render_model_dossier_page(exp))

    def test_historial_recupera_version_aprobada(self):
        self.ingest()
        editorial.cmd_aprobar_candidato(self.args())
        aprobado = d.obtener_expediente("dewalt-dws713")["alertas"][0]["evidencia_fuente"]["version_fuente"]
        self.ingest(Description="Cambio de lote")
        self.ingest(Description="Segundo cambio de lote")
        cand = d.cargar_candidatos()[0]
        self.assertEqual(cand["estado_revision"], "MODIFICADO_PENDIENTE")
        hashes = {aprobado, cand["version_fuente"]}
        for change in cand["historial_cambios"]:
            hashes.update((change["hash_anterior"], change["hash_nuevo"]))
        self.assertEqual(len(hashes), 3)
        for digest in hashes:
            raw = (self.root / "capturas" / (digest + ".json")).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), digest)

    def test_transaccion_interrumpida_se_recupera_al_leer(self):
        original = storage._reemplazar
        def interrupted(path, value):
            if path.name == "candidatos_revision.json":
                raise OSError("Interrupción simulada")
            original(path, value)
        with patch.object(storage, "_reemplazar", interrupted), self.assertRaises(OSError):
            storage.guardar_estado(registro={"prueba": 1}, candidatos=[{"id": "prueba"}])
        self.assertTrue((self.root / "transaccion.json").exists())
        self.assertEqual(d.cargar_candidatos(), [{"id": "prueba"}])
        self.assertEqual(d.cargar_registro_fuentes(), {"prueba": 1})
        self.assertFalse((self.root / "transaccion.json").exists())

    def test_snapshot_vercel_no_intenta_escribir_en_readonly(self):
        with patch.dict("os.environ", {"ALERTAS_SOLO_LECTURA": "1"}):
            self.assertGreater(len(d.cargar_expedientes()), 0)
            with self.assertRaises(RuntimeError):
                storage.guardar_estado(candidatos=[])

    def test_dos_procesos_no_pierden_candidatos(self):
        code = """
import sys,time
import alertas_datos as d
from alertas_almacen import bloqueo_datos, guardar_estado
for i in range(3):
    with bloqueo_datos():
        candidatos = d.cargar_candidatos()
        time.sleep(0.03)
        candidatos.append({'id': sys.argv[1] + str(i)})
        guardar_estado(candidatos=candidatos)
"""
        env = dict(os.environ, ALERTAS_DATA_DIR=str(self.root), ALERTAS_SOLO_LECTURA="0")
        processes = [subprocess.Popen([sys.executable, "-c", code, name], env=env,
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                     for name in ("uno", "dos")]
        for process in processes:
            self.addCleanup(lambda p=process: p.kill() if p.poll() is None else None)
            stdout, stderr = process.communicate(timeout=30)
            self.assertEqual(process.returncode, 0, stderr.decode(errors="replace"))
        self.assertEqual(len({c["id"] for c in d.cargar_candidatos()}), 6)


if __name__ == "__main__":
    unittest.main()
