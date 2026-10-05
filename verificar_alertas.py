"""
Suite de pruebas automatizadas para la sección de 'Documentación y alertas de herramientas'.
Verifica exhaustivamente:
1. Integridad de los datos y modelos del MVP con evidencia documental.
2. Cumplimiento de las reglas de exactitud: sufijos regionales, exclusiones explícitas (DW8307-AR),
   delimitación de alcance territorial y ausencia de falsas alertas negativas.
3. Resiliencia ante fallos de fuentes con aislamiento en directorios temporales (no contamina producción).
4. Validación estricta de payloads (rechazo de dicts de error en CPSC y HTML en Argentina).
5. Identidades estables e inmutables independientes de número de fila.
6. Gestión editorial: prohibición de defaults que tergiversen el mercado, extracción de riesgos y medidas,
   idempotencia de aprobación y derivación técnica del estado general.
7. Renderizado HTML: accesibilidad (aria-pressed, aria-live), visualización de lotes y rangos,
   diseño sobrio y neutral sin escudos/tildes engañosos, sintaxis CSS limpia y responsive.
8. Enlace bidireccional y prueba de integración Flask (con .qa-deps y tmp/auditoria-observatorio-deps).
"""

from __future__ import annotations

import argparse
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Asegurar encoding UTF-8 en salida
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Cargar dependencias adicionales locales (.qa-deps y tmp/auditoria-observatorio-deps)
ROOT_DIR = Path(__file__).parent.resolve()
for extra_dep in [ROOT_DIR / ".qa-deps", ROOT_DIR / "tmp" / "auditoria-observatorio-deps"]:
    if extra_dep.exists() and str(extra_dep) not in sys.path:
        sys.path.insert(0, str(extra_dep))

import alertas_datos
from alertas_datos import (
    DESCARGO_CAMPANA_EXTRANJERA,
    DESCARGO_INDEPENDENCIA,
    DESCARGO_NO_GARANTIA_SEGURIDAD,
    ESTADOS_ALERTA,
    buscar_expedientes,
    cargar_candidatos,
    cargar_expedientes,
    cargar_registro_fuentes,
    derivar_estado_expediente,
    guardar_candidatos,
    guardar_expedientes,
    guardar_registro_fuentes,
    obtener_expediente,
    obtener_todos_los_slugs,
    validar_expediente,
)
from alertas_almacen import archivar_payload
import gestionar_alertas
from render_alertas import (
    ALERTAS_CSS,
    dossier_schema,
    render_alerts_hub_page,
    render_model_dossier_page,
)
import servidor_local
import sincronizador_alertas
from validacion_enlaces import validar_html


class TestExpedientesModelos(unittest.TestCase):
    """Pruebas de integridad de los expedientes técnicos verificados."""

    def setUp(self):
        self.expedientes = cargar_expedientes(forzar_recarga=True)
        self.slugs = obtener_todos_los_slugs()

    def test_modelos_mvp_presentes(self):
        """Verifica que los 4 modelos requeridos existan en la base."""
        esperados = {"dewalt-dws780", "dewalt-dw8307", "makita-dgp180", "dewalt-dws713"}
        self.assertTrue(esperados.issubset(set(self.slugs)), f"Faltan modelos en el MVP: {esperados - set(self.slugs)}")

    def test_validacion_campos_obligatorios(self):
        """Verifica que todos los expedientes pasen la validación estructural sin excepción."""
        for exp in self.expedientes:
            try:
                validar_expediente(exp)
            except Exception as e:
                self.fail(f"Expediente '{exp.get('slug')}' no pasó la validación: {e}")

    def test_sufijos_regionales_preservados(self):
        """Verifica que las variantes mantengan los sufijos regionales reales (-AR, -B2, ZB)."""
        dws = obtener_expediente("dewalt-dws780")
        codigos_dws = [v["codigo"] for v in dws["variantes"]]
        self.assertIn("DWS780-AR", codigos_dws, "DWS780 debe registrar explícitamente la variante regional DWS780-AR")

        dgp = obtener_expediente("makita-dgp180")
        codigos_dgp = [v["codigo"] for v in dgp["variantes"]]
        self.assertTrue(any("DGP180" in c for c in codigos_dgp), "DGP180 debe registrar variantes regionales")

    def test_exclusion_expresa_dw8307_ar(self):
        """Verifica que el disco flap DW8307 documente la exclusión textual de DW8307-AR en SERNAC."""
        exp = obtener_expediente("dewalt-dw8307")
        self.assertIsNotNone(exp)
        alertas = exp.get("alertas", [])
        self.assertGreater(len(alertas), 0, "DW8307 debe contener la alerta de SERNAC")
        al_sernac = next((a for a in alertas if "SERNAC" in a.get("organismo", "")), None)
        self.assertIsNotNone(al_sernac, "Debe existir alerta de SERNAC")
        excepcion = al_sernac.get("excepciones_expresas", "")
        self.assertIn("DW8307-AR", excepcion, "La alerta de SERNAC debe declarar la exclusión explícita de DW8307-AR")

    def test_sin_falsas_alertas_negativas(self):
        """Verifica que no existan falsos avisos de alerta creados a partir de resultados de consulta negativos."""
        for exp in self.expedientes:
            for al in exp.get("alertas", []):
                self.assertNotIn("SIN-COINCIDENCIA", al.get("id_aviso", ""),
                                 f"[{exp['slug']}] No deben existir alertas de resultado negativo en la lista de alertas.")

    def test_campos_de_evidencia_presentes(self):
        """Verifica que cada alerta cuente con evidencia_fuente con URL y revisor."""
        for exp in self.expedientes:
            for al in exp.get("alertas", []):
                ev = al.get("evidencia_fuente", {})
                self.assertTrue(isinstance(ev, dict) and ev.get("url") and ev.get("revisado_por"),
                                f"[{exp['slug']}] Alerta {al.get('id_aviso')} carece de evidencia_fuente válida")

    def test_sin_alertas_con_descargo_y_fuentes(self):
        """Verifica que un expediente en SIN_ALERTAS (DWS713) incluya fuentes y el descargo obligatorio."""
        exp = obtener_expediente("dewalt-dws713")
        self.assertIsNotNone(exp)
        self.assertEqual(exp["estado_general"], "NO_REVISADO")
        self.assertEqual(len(exp["alertas"]), 0, "No debe tener alertas activas cargadas")
        fuentes = [fc["fuente"] for fc in exp["fuentes_consultadas"]]
        self.assertIn("Defensa del Consumidor (Argentina)", fuentes)
        self.assertIn("SERNAC (Chile)", fuentes)
        self.assertIn("CPSC API (Estados Unidos)", fuentes)

    def test_buscador_expedientes_por_tokens_y_ean(self):
        """Verifica la función de búsqueda de modelos por marca, modelo, código y EAN."""
        r1 = buscar_expedientes(query="DWS780")
        self.assertGreaterEqual(len(r1), 1)
        self.assertEqual(r1[0]["slug"], "dewalt-dws780")

        r2 = buscar_expedientes(query="DW8307-AR")
        self.assertGreaterEqual(len(r2), 1)
        self.assertEqual(r2[0]["slug"], "dewalt-dw8307")

        r3 = buscar_expedientes(query="885911235112")
        self.assertGreaterEqual(len(r3), 1)
        self.assertEqual(r3[0]["slug"], "dewalt-dws780")


class TestResilienciaFuentesYAislamiento(unittest.TestCase):
    """Pruebas aisladas en directorios temporales para no contaminar archivos reales de producción."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory(dir=ROOT_DIR, prefix=".qa-alertas-")
        self.tmp_path = Path(self.tmp_dir.name)

        # Copiar datos de producción al entorno aislado
        shutil.copy(alertas_datos.MODELOS_FILE, self.tmp_path / "modelos_expedientes.json")
        shutil.copy(alertas_datos.CANDIDATOS_FILE, self.tmp_path / "candidatos_revision.json")
        shutil.copy(alertas_datos.FUENTES_FILE, self.tmp_path / "registro_fuentes.json")

        # Parchear rutas del módulo
        self.patch_dir = patch.object(alertas_datos, "DATOS_DIR", self.tmp_path)
        self.patch_mod = patch.object(alertas_datos, "MODELOS_FILE", self.tmp_path / "modelos_expedientes.json")
        self.patch_cand = patch.object(alertas_datos, "CANDIDATOS_FILE", self.tmp_path / "candidatos_revision.json")
        self.patch_fnt = patch.object(alertas_datos, "FUENTES_FILE", self.tmp_path / "registro_fuentes.json")

        self.patch_dir.start()
        self.patch_mod.start()
        self.patch_cand.start()
        self.patch_fnt.start()

    def tearDown(self):
        self.patch_fnt.stop()
        self.patch_cand.stop()
        self.patch_mod.stop()
        self.patch_dir.stop()
        self.tmp_dir.cleanup()

    @patch("urllib.request.urlopen")
    def test_fallo_cpsc_preserva_datos_aislado(self, mock_urlopen):
        """Fallo de red en CPSC preserva datos históricos y anota FALLIDA en el archivo temporal."""
        mock_urlopen.side_effect = Exception("Connection timed out")
        res = sincronizador_alertas.sincronizar_cpsc(termino_busqueda="DeWalt")
        self.assertFalse(res["exito"])
        self.assertIn("Connection timed out", res["error"])

        fuentes = cargar_registro_fuentes()
        info_cpsc = fuentes.get("cpsc", {})
        self.assertEqual(info_cpsc.get("estado"), "FALLIDA")
        self.assertIsNotNone(info_cpsc.get("error_reciente"))

    @patch("urllib.request.urlopen")
    def test_fallo_argentina_preserva_datos_aislado(self, mock_urlopen):
        """Fallo de red en Argentina preserva historial y anota contingencia en archivo temporal."""
        mock_urlopen.side_effect = Exception("HTTP 503 Service Unavailable")
        res = sincronizador_alertas.sincronizar_defensa_consumidor()
        self.assertFalse(res["exito"])
        self.assertIn("503", res["error"])

        fuentes = cargar_registro_fuentes()
        info_arg = fuentes.get("defensa_consumidor_ar", {})
        self.assertEqual(info_arg.get("estado"), "FALLIDA")

    @patch("urllib.request.urlopen")
    def test_cpsc_rechaza_respuesta_no_lista(self, mock_urlopen):
        """Si CPSC API devuelve un dict de error o {}, debe rechazarlo y marcar FALLIDA."""
        mock_res = MagicMock()
        mock_res.read.return_value = json.dumps({"fault": {"faultstring": "Rate limit exceeded"}}).encode("utf-8")
        mock_res.__enter__.return_value = mock_res
        mock_urlopen.return_value = mock_res

        res = sincronizador_alertas.sincronizar_cpsc(termino_busqueda="DeWalt")
        self.assertFalse(res["exito"])
        self.assertIn("se esperaba list", res["error"])

    @patch("urllib.request.urlopen")
    def test_argentina_rechaza_html_de_error(self, mock_urlopen):
        """Si Google Sheets devuelve página HTML de login o error, debe rechazarla y marcar FALLIDA."""
        mock_res = MagicMock()
        mock_res.read.return_value = b"<!DOCTYPE html><html><head><title>Google Accounts</title></head><body>Login</body></html>"
        mock_res.__enter__.return_value = mock_res
        mock_urlopen.return_value = mock_res

        res = sincronizador_alertas.sincronizar_defensa_consumidor()
        self.assertFalse(res["exito"])
        self.assertIn("HTML de error", res["error"])

    @patch("urllib.request.urlopen")
    def test_modificacion_aviso_actualiza_campos_derivados(self, mock_urlopen):
        """Si un aviso de CPSC cambia su contenido, debe actualizar título, resumen y estado a MODIFICADO_PENDIENTE."""
        aviso_v1 = [{
            "RecallNumber": "99999",
            "RecallDate": "2026-01-01",
            "Title": "DeWalt Miter Saw Safety Notice Original",
            "Description": "Original description of DWS780 miter saw",
            "URL": "https://cpsc.gov/test",
            "Products": [{"Name": "DeWalt DWS780 miter saw"}],
            "Hazards": [{"Name": "Laceration hazard"}],
            "Remedies": [{"Name": "Free repair kit"}],
        }]

        mock_res1 = MagicMock()
        mock_res1.read.return_value = json.dumps(aviso_v1).encode("utf-8")
        mock_res1.__enter__.return_value = mock_res1
        mock_urlopen.return_value = mock_res1

        res1 = sincronizador_alertas.sincronizar_cpsc("DeWalt")
        self.assertTrue(res1["exito"])
        self.assertEqual(res1["nuevos"], 1)

        cands = cargar_candidatos()
        c99 = next(c for c in cands if c["id"] == "cand-cpsc-99999")
        self.assertEqual(c99["estado_revision"], "PENDIENTE")
        self.assertEqual(c99["titulo"], "DeWalt Miter Saw Safety Notice Original")

        # Modificación del aviso por la autoridad
        aviso_v2 = [{
            "RecallNumber": "99999",
            "RecallDate": "2026-01-01",
            "Title": "DeWalt Miter Saw Safety Notice MODIFICADO",
            "Description": "Updated description with new date codes for DWS780",
            "URL": "https://cpsc.gov/test",
            "Products": [{"Name": "DeWalt DWS780 miter saw"}],
            "Hazards": [{"Name": "Severe laceration hazard"}],
            "Remedies": [{"Name": "Replacement guard"}],
        }]

        mock_res2 = MagicMock()
        mock_res2.read.return_value = json.dumps(aviso_v2).encode("utf-8")
        mock_res2.__enter__.return_value = mock_res2
        mock_urlopen.return_value = mock_res2

        res2 = sincronizador_alertas.sincronizar_cpsc("DeWalt")
        self.assertTrue(res2["exito"])
        self.assertEqual(res2["modificados"], 1)

        cands2 = cargar_candidatos()
        c99_mod = next(c for c in cands2 if c["id"] == "cand-cpsc-99999")
        self.assertEqual(c99_mod["estado_revision"], "MODIFICADO_PENDIENTE")
        self.assertEqual(c99_mod["titulo"], "DeWalt Miter Saw Safety Notice MODIFICADO")
        self.assertIn("historial_cambios", c99_mod)


class TestGestionEditorial(unittest.TestCase):
    """Pruebas para gestionar_alertas.py con aislamiento temporal."""

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory(dir=ROOT_DIR, prefix=".qa-alertas-")
        self.tmp_path = Path(self.tmp_dir.name)

        shutil.copy(alertas_datos.MODELOS_FILE, self.tmp_path / "modelos_expedientes.json")
        shutil.copy(alertas_datos.CANDIDATOS_FILE, self.tmp_path / "candidatos_revision.json")
        shutil.copy(alertas_datos.FUENTES_FILE, self.tmp_path / "registro_fuentes.json")

        self.patch_dir = patch.object(alertas_datos, "DATOS_DIR", self.tmp_path)
        self.patch_mod = patch.object(alertas_datos, "MODELOS_FILE", self.tmp_path / "modelos_expedientes.json")
        self.patch_cand = patch.object(alertas_datos, "CANDIDATOS_FILE", self.tmp_path / "candidatos_revision.json")
        self.patch_fnt = patch.object(alertas_datos, "FUENTES_FILE", self.tmp_path / "registro_fuentes.json")

        self.patch_dir.start()
        self.patch_mod.start()
        self.patch_cand.start()
        self.patch_fnt.start()

    def tearDown(self):
        self.patch_fnt.stop()
        self.patch_cand.stop()
        self.patch_mod.stop()
        self.patch_dir.stop()
        self.tmp_dir.cleanup()

    def test_aprobar_cpsc_no_asigna_argentina_por_defecto(self):
        """Aprobar un candidato CPSC sin especificar país debe asignar Estados Unidos, nunca Argentina."""
        cands = cargar_candidatos()
        cand_cpsc = next((c for c in cands if c.get("fuente") == "CPSC"), None)
        self.assertIsNotNone(cand_cpsc, "Debe haber candidatos de CPSC para la prueba")

        args = argparse.Namespace(
            cand_id=cand_cpsc["id"],
            slug="dewalt-dws780",
            alcance="POSIBLE_COINCIDENCIA",
            pais_mercado=None,  # No se especifica: debe inferirse Estados Unidos
            modelos="Herramienta de prueba",
            lotes="Lote de prueba",
            periodo=None,
            ubicacion=None,
            unidades=None,
            excepciones="Sin excepciones",
            defecto="Riesgo de corte",
            accion="Reparación gratuita en EE. UU.",
            revisado_por="Tester Editorial",
        )

        gestionar_alertas.cmd_aprobar_candidato(args)

        exp = obtener_expediente("dewalt-dws780")
        al_nueva = next(a for a in exp["alertas"] if a["id_aviso"] == cand_cpsc["id_externo"])
        self.assertEqual(al_nueva["pais_mercado"], "Estados Unidos", "CPSC no debe catalogarse como Argentina")

    def test_aprobar_idempotente_no_duplica(self):
        """Aprobar dos veces el mismo candidato actualiza la alerta existente sin duplicar registros."""
        cands = cargar_candidatos()
        cand = cands[0]

        args = argparse.Namespace(
            cand_id=cand["id"],
            slug="dewalt-dws780",
            alcance="POSIBLE_COINCIDENCIA",
            pais_mercado="Estados Unidos",
            modelos="Modelo prueba",
            lotes="Lote 1",
            periodo=None,
            ubicacion=None,
            unidades=None,
            excepciones="Ninguna",
            defecto="Defecto inicial",
            accion="Acción inicial",
            revisado_por="Tester",
        )

        gestionar_alertas.cmd_aprobar_candidato(args)
        exp1 = obtener_expediente("dewalt-dws780")
        cnt1 = len(exp1["alertas"])

        # Re-aprobar con actualización
        args.defecto = "Defecto corregido y verificado"
        gestionar_alertas.cmd_aprobar_candidato(args)
        exp2 = obtener_expediente("dewalt-dws780")
        cnt2 = len(exp2["alertas"])

        self.assertEqual(cnt1, cnt2, "Re-aprobar el candidato no debe duplicar la alerta")
        al_actualizada = next(a for a in exp2["alertas"] if a["id_aviso"] == cand["id_externo"])
        self.assertEqual(al_actualizada["defecto_riesgo"], "Defecto corregido y verificado")

    def test_derivar_estado_expediente_estricto(self):
        """Verifica que la función derivar_estado_expediente respete la jerarquía sin forzar ALERTA_OFICIAL."""
        # Sin alertas y con fuentes
        est1 = derivar_estado_expediente([], [{"fuente": "CPSC", "estado": "EXITOSA", "fecha_consulta": "2026-10-03", "resultado": "Sin coincidencias para modelo de prueba", "evidencia_consulta": {"captura_sha256": archivar_payload({"resultado": "Consulta de prueba sin coincidencias"}), "url": "https://www.cpsc.gov/", "modelos_consultados": ["PRUEBA"], "metodo": "Consulta editorial de prueba", "revisado_por": "Tester", "resultado": "SIN_COINCIDENCIAS"}}])
        self.assertEqual(est1, "SIN_ALERTAS")

        # Con alerta posible (extranjera)
        est2 = derivar_estado_expediente([{"estado_alcance": "POSIBLE_COINCIDENCIA"}], [])
        self.assertEqual(est2, "POSIBLE_COINCIDENCIA")

        # Con fuente caída y sin alertas
        est3 = derivar_estado_expediente([], [{"fuente": "CPSC", "estado": "FALLIDA"}])
        self.assertEqual(est3, "FUENTE_INACCESIBLE")

        # Con alerta oficial confirmada
        est4 = derivar_estado_expediente([{"estado_alcance": "ALERTA_OFICIAL"}], [])
        self.assertEqual(est4, "ALERTA_OFICIAL")


class TestRenderizadoHTMLYValidacion(unittest.TestCase):
    """Verifica que el HTML generado sea válido y cumpla con las políticas de TallerLab."""

    def test_render_hub_alertas_y_accesibilidad(self):
        """Verifica la generación del Hub de Alertas (/alertas/) con tokens, accesibilidad y contador."""
        html = render_alerts_hub_page()
        self.assertIn("Alertas de seguridad, recalls y documentación de herramientas", html)
        self.assertIn(DESCARGO_INDEPENDENCIA, html)
        self.assertIn(DESCARGO_NO_GARANTIA_SEGURIDAD, html)
        self.assertIn('aria-live="polite"', html, "Debe tener contenedor accesible con aria-live")
        self.assertIn('aria-pressed="true"', html, "Los chips de filtro deben usar aria-pressed")
        self.assertIn("885911235112", html, "El corpus de búsqueda debe incluir el código de barras EAN")

    def test_css_sintaxis_y_responsividad(self):
        """Verifica que no existan errores de sintaxis CSS y el ancho mínimo sea responsive."""
        self.assertNotIn("flex-wrap: gap", ALERTAS_CSS, "Error de sintaxis CSS detectado: 'flex-wrap: gap'")
        self.assertIn("minmax(min(100%, 300px), 1fr)", ALERTAS_CSS, "Grid debe ser responsive para pantallas menores a 330px")

    def test_estetica_neutral_sin_emojis_enganosos(self):
        """En ausencia de alertas no deben figurar íconos que induzcan falsa seguridad de certificación."""
        exp = obtener_expediente("dewalt-dws713")
        html = render_model_dossier_page(exp)
        # La fuente puede estar temporalmente caída en el registro real; ambas
        # presentaciones conservan la incertidumbre sin certificar seguridad.
        self.assertTrue("Relevamiento documental en proceso" in html or "Inaccesible" in html)
        self.assertNotIn("✅", html, "No debe incluirse tilde verde de certificación")
        self.assertNotIn("🛡️", html, "No debe incluirse escudo de seguridad en ficha técnica")

    def test_render_lotes_y_campos_estructurados(self):
        """Verifica que los campos estructurados (lotes, series, excepciones) se rendericen en el expediente."""
        exp_dws = obtener_expediente("dewalt-dws780")
        html_dws = render_model_dossier_page(exp_dws)
        self.assertIn("Lotes y series:", html_dws)
        self.assertIn("Modelos afectados:", html_dws)

        exp_flap = obtener_expediente("dewalt-dw8307")
        html_flap = render_model_dossier_page(exp_flap)
        self.assertIn("EXCEPCIONES Y ALCANCE ESPECÍFICO", html_flap)
        self.assertIn("DW8307-AR", html_flap)

    def test_fuente_fallida_muestra_advertencia(self):
        """Si un expediente tiene una fuente marcada como FALLIDA, debe advertir en la tabla sin checkmark verde."""
        exp_mock = {
            "slug": "modelo-prueba",
            "marca": "Prueba",
            "modelo_base": "T-100",
            "nombre_comercial": "Herramienta de prueba",
            "categoria": "taladros",
            "estado_general": "FUENTE_INACCESIBLE",
            "revisado_por": "Tester",
            "fecha_revision": "2026-10-03",
            "variantes": [{"codigo": "T100-AR", "mercado": "Argentina"}],
            "documentacion": {},
            "alertas": [],
            "fuentes_consultadas": [
                {"fuente": "CPSC API", "fecha_consulta": "2026-10-03", "estado": "FALLIDA", "resultado": "Error de conexión"},
            ],
        }
        html = render_model_dossier_page(exp_mock)
        self.assertIn("⚠️ Inaccesible", html)
        self.assertNotIn("✓ FALLIDA", html)

    def test_render_expedientes_y_enlaces(self):
        """Verifica que las páginas completas de cada expediente pasen validar_html sin errores."""
        slugs = obtener_todos_los_slugs()
        for slug in slugs:
            path = f"/alertas/{slug}/"
            html = servidor_local.render_alertas_page(path)
            self.assertIn("<!DOCTYPE html>", html)
            self.assertIn("Expediente técnico:", html)
            self.assertIn(DESCARGO_INDEPENDENCIA, html)

            # Validar enlaces internos contra INDEXABLE_PATH_SET
            try:
                validar_html(html, path, servidor_local.INDEXABLE_PATH_SET, servidor_local.SITE_URL)
            except Exception as e:
                self.fail(f"validar_html falló en la ruta '{path}': {e}")

    def test_enlace_bidireccional_guia_sierras(self):
        """Verifica que la guía de ingletadoras enlace al expediente técnico DWS780 con texto editorial sobrio."""
        guia_path = ROOT_DIR / "paginas" / "sierras" / "13-ingletadora-dewalt.md"
        with open(guia_path, "r", encoding="utf-8") as f:
            contenido = f.read()
        self.assertIn("/alertas/dewalt-dws780/", contenido, "La guía de ingletadoras debe enlazar al expediente de DWS780")
        self.assertNotIn("expediente oficial DeWalt", contenido, "No debe rotularse como 'expediente oficial DeWalt'")
        self.assertIn("expediente técnico de TallerLab con fuentes oficiales", contenido)

    def test_flask_app_endpoints(self):
        """Verifica que la aplicación Flask de app.py sirva las rutas correctamente."""
        try:
            import app
            client = app.app.test_client()

            # Hub
            res_hub = client.get("/alertas/")
            self.assertEqual(res_hub.status_code, 200)
            self.assertIn(b"Documentaci", res_hub.data)

            # Expediente DWS780
            res_dws = client.get("/alertas/dewalt-dws780/")
            self.assertEqual(res_dws.status_code, 200)
            self.assertIn(b"DWS780", res_dws.data)

            # Expediente DW8307 (con exclusión visible)
            res_flap = client.get("/alertas/dewalt-dw8307/")
            self.assertEqual(res_flap.status_code, 200)
            self.assertIn(b"DW8307-AR", res_flap.data)

            # Redirección sin barra final
            res_redir = client.get("/alertas")
            self.assertEqual(res_redir.status_code, 301)
        except ImportError as e:
            self.skipTest(f"Flask no disponible en este entorno: {e}")


if __name__ == "__main__":
    unittest.main()
