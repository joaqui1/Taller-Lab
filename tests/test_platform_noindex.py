"""Las plataformas sin modelos verificados no se indexan; las que tienen modelos sí."""
import unittest
from tests.compatibility_fixtures import use_fresh_compatibility_catalog

from compatibilidad.views import get_compatibility_meta


class PlatformNoindexTests(unittest.TestCase):
    def setUp(self):
        use_fresh_compatibility_catalog(self)

    def test_platform_without_published_models_is_noindex(self):
        _, _, extra = get_compatibility_meta("/plataformas/einhell-power-x-change/", "https://example.test")
        self.assertIn('content="noindex, follow"', extra)
        self.assertNotIn("CollectionPage", extra)

    def test_platform_with_published_models_keeps_collection_schema(self):
        _, _, extra = get_compatibility_meta("/plataformas/bosch-professional-18v/", "https://example.test")
        self.assertNotIn("noindex", extra)
        self.assertIn("CollectionPage", extra)


if __name__ == "__main__":
    unittest.main()
