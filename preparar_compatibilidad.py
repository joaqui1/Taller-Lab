"""Preparación local verificable; no autentica ni publica en Vercel."""
import unittest
from compatibilidad import catalog
from compatibilidad.cli import cmd_export
from preparar_assets_publicos import main as prepare_assets


def main():
    suite = unittest.defaultTestLoader.discover('tests', pattern='test_compatibilidad.py')
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)
    catalog.refresh_published_state()
    if not catalog.RELATIONS:
        raise SystemExit('No hay evidencia vigente: ejecutar mantenimiento antes de preparar el despliegue.')
    cmd_export(None)
    prepare_assets()
    print('Preparación local terminada. Publicación pendiente: seguir docs/OPERACION_COMPATIBILIDAD.md.')


if __name__ == '__main__':
    main()
