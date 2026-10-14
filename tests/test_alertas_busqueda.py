"""Búsqueda normalizada del buscador de alertas."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import alertas_datos
import app as flask_app
import servidor_local
from compatibilidad.storage import StateStore
from compatibilidad import telemetry
from render_alertas import render_alerts_hub_page


class AlertSearchTests(unittest.TestCase):
    def test_home_search_is_a_get_form_to_alertas(self):
        html = servidor_local.render_home_page()
        self.assertIn("¿Tu herramienta tiene un aviso de seguridad?", html)
        self.assertIn('action="/alertas/" method="get"', html)
        self.assertIn('name="q" type="search"', html)
        self.assertIn('href="/alertas/" class="nav-btn">Alertas</a>', html)

    def test_normaliza_mayusculas_guiones_y_espacios(self):
        self.assertEqual(alertas_datos.normalizar_codigo_modelo("DWS 780"), "dws780")
        self.assertEqual(alertas_datos.normalizar_codigo_modelo("dws780"), "dws780")
        self.assertEqual(alertas_datos.normalizar_codigo_modelo("DWS780-AR"), "dws780ar")

    def test_modelo_y_variante_encuentran_el_mismo_expediente(self):
        expediente = alertas_datos.obtener_expediente("dewalt-dws780")
        with patch.object(alertas_datos, "cargar_expedientes", return_value=[expediente]):
            for query in ("DWS 780", "dws780", "DWS780-AR"):
                with self.subTest(query=query):
                    encontrados = alertas_datos.buscar_expedientes(query)
                    self.assertEqual([item["slug"] for item in encontrados], ["dewalt-dws780"])

    def test_resultados_y_sin_resultado_son_utilizables_sin_javascript(self):
        expediente = alertas_datos.obtener_expediente("dewalt-dws780")
        with patch("render_alertas.cargar_expedientes", return_value=[expediente]):
            html_resultado = render_alerts_hub_page("DWS780-AR")
            self.assertIn('action="/alertas/" method="get"', html_resultado)
            self.assertIn('name="q" value="DWS780-AR"', html_resultado)
            self.assertIn("DeWalt DWS780", html_resultado)
            self.assertIn("Alerta oficial confirmada", html_resultado)
            self.assertIn('href="/alertas/dewalt-dws780/"', html_resultado)

            html_vacio = render_alerts_hub_page("MODELO-INEXISTENTE")
            self.assertIn("No encontramos avisos para ese modelo en nuestra base", html_vacio)
            self.assertIn("no certifica la seguridad del producto", html_vacio)
            self.assertIn('href="/alertas/metodologia/"', html_vacio)

    def test_ruta_sin_resultados_registra_solo_la_consulta(self):
        with patch.object(servidor_local, "track_event") as track:
            html = servidor_local.render_alertas_page("/alertas/", "MODELO-INEXISTENTE")
        track.assert_called_once_with(event_type="alert_search_no_result", query_text="MODELO-INEXISTENTE")
        self.assertIn("No encontramos avisos para ese modelo en nuestra base", html)

    def test_evento_no_puede_enviarse_desde_el_endpoint_publico(self):
        with patch.object(flask_app, "track_event") as track:
            response = flask_app.app.test_client().post(
                "/api/compatibilidad/evento",
                json={"event_type": "alert_search_no_result", "query_text": "MODELO XYZ"},
            )
        self.assertEqual(response.status_code, 400)
        track.assert_not_called()

    def test_consultas_sin_resultado_guardan_solo_el_texto(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd(), prefix=".qa-alert-search-") as temp:
            store = StateStore(path=Path(temp) / "telemetry.sqlite3", database_url="")
            with patch.object(telemetry, "_store", return_value=store):
                telemetry.track_event("alert_search_no_result", query_text="  MODELO   XYZ  ")
                telemetry.track_event("alert_search_no_result", query_text="MODELO XYZ")
                telemetry.track_event("alert_search_no_result", query_text="")
                self.assertEqual(telemetry.get_alert_search_no_results(), [
                    {"query_text": "MODELO XYZ", "searches": 2}
                ])


if __name__ == "__main__":
    unittest.main()
