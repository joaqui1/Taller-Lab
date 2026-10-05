"""El filtro argentino descarta recalls de vehículos sin perder herramientas."""
import unittest

import sincronizador_alertas as s

COLS = {"fecha": 0, "marca": 1, "producto": 2, "defecto": 3}


class FiltroAutomotorTests(unittest.TestCase):
    def fila(self, marca, producto, defecto="Falla en la batería y la manguera"):
        return ["2025-01-01", marca, producto, defecto]

    def test_descarta_vehiculos(self):
        for marca, producto in [("VOLKSWAGEN ARGENTINA SA", "Fox, Gol y Saveiro"), ("FORD", "Ranger"),
                                ("Mercedes Benz Argentina SAU", "Clase C"), ("FIAT, JEEP, RAM", "Doblo")]:
            self.assertTrue(s._es_aviso_automotor(self.fila(marca, producto), COLS), marca)

    def test_conserva_herramientas(self):
        for marca, producto in [("Honda Motor de Argentina S.A.", "Generador Modelo EU22i"), ("Dewalt", "FS 85 y KA 85R"),
                                ("Makita Herramientas de Argentina S.A", "Pistola de grasa recargable DGP180"),
                                ("Ford", "Compresor portátil 12 V")]:
            self.assertFalse(s._es_aviso_automotor(self.fila(marca, producto), COLS), marca)

    def test_no_confunde_palabras_parciales(self):
        self.assertFalse(s._es_aviso_automotor(self.fila("Programas SA", "Cargador"), COLS))


if __name__ == "__main__":
    unittest.main()
