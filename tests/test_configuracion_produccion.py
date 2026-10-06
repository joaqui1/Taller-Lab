"""Configuración de persistencia sin leer credenciales reales."""
import os
import unittest
from unittest.mock import patch

from compatibilidad.storage import StateStore


class ProductionDatabaseConfigurationTests(unittest.TestCase):
    def test_existing_neon_integration_is_used_without_copying_secrets(self):
        with patch.dict(os.environ, {'VERCEL': '1', 'COMPATIBILITY_DATABASE_URL': '',
                                    'DATABASE_URL': '', 'ALERTAS_DATABASE_DATABASE_URL': 'postgresql://fixture'}):
            self.assertEqual(StateStore().url, 'postgresql://fixture')
        with patch.dict(os.environ, {'VERCEL': '1', 'COMPATIBILITY_DATABASE_URL': 'postgresql://dedicated',
                                    'ALERTAS_DATABASE_DATABASE_URL': 'postgresql://fixture'}):
            self.assertEqual(StateStore().url, 'postgresql://dedicated')

    def test_missing_production_database_is_rejected(self):
        with patch.dict(os.environ, {'VERCEL': '1', 'COMPATIBILITY_DATABASE_URL': '',
                                    'DATABASE_URL': '', 'ALERTAS_DATABASE_DATABASE_URL': ''}):
            with self.assertRaises(RuntimeError):
                StateStore()
