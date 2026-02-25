"""
Testy dla centralnego modułu konfiguracji (app_config.py).
"""
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from location_analysis.app_config import AppConfig, get_config, reset_config


class TestAppConfigDefaults(TestCase):
    """Testy dla domyślnych wartości AppConfig."""

    def setUp(self):
        reset_config()

    def tearDown(self):
        reset_config()

    def test_default_overpass_url(self):
        """Domyślny URL overpass jest publicznym API."""
        config = AppConfig()
        self.assertEqual(config.overpass_url, "https://overpass-api.de/api/interpreter")

    def test_default_overpass_timeout(self):
        config = AppConfig()
        self.assertEqual(config.overpass_timeout, 60)

    def test_default_enrichment_disabled(self):
        """Enrichment domyślnie wyłączony (kosztowny)."""
        config = AppConfig()
        self.assertFalse(config.default_enrichment)

    def test_default_fallback_enabled(self):
        config = AppConfig()
        self.assertTrue(config.default_fallback)

    def test_default_poi_provider(self):
        config = AppConfig()
        self.assertEqual(config.default_poi_provider, "hybrid")

    def test_default_report_toggles(self):
        config = AppConfig()
        self.assertTrue(config.report_air_quality)
        self.assertTrue(config.report_ai_insights)
        self.assertTrue(config.report_nature_metrics)
        self.assertTrue(config.report_data_quality)
        self.assertFalse(config.report_noise_analysis)  # placeholder

    def test_overpass_endpoints_property(self):
        """overpass_endpoints łączy primary + fallback bez duplikatów."""
        config = AppConfig(
            overpass_url="http://localhost:12345/api/interpreter",
            overpass_fallback_urls=["https://overpass-api.de/api/interpreter"],
        )
        endpoints = config.overpass_endpoints
        self.assertEqual(endpoints[0], "http://localhost:12345/api/interpreter")
        self.assertIn("https://overpass-api.de/api/interpreter", endpoints)
        self.assertEqual(len(endpoints), 2)

    def test_overpass_endpoints_no_duplicates(self):
        """Nie duplikuje URL jeśli primary == fallback."""
        config = AppConfig(
            overpass_url="https://overpass-api.de/api/interpreter",
            overpass_fallback_urls=["https://overpass-api.de/api/interpreter", "https://lz4.overpass-api.de/api/interpreter"],
        )
        endpoints = config.overpass_endpoints
        # primary nie powinien się powtórzyć
        self.assertEqual(endpoints.count("https://overpass-api.de/api/interpreter"), 1)


class TestAppConfigPublicDict(TestCase):
    """Testy dla to_public_dict() — bezpieczeństwo API."""

    def test_no_api_key_in_public_dict(self):
        """API key NIE jest w public dict."""
        config = AppConfig(google_places_api_key="super-secret-key-123")
        public = config.to_public_dict()

        # Sprawdź że klucz nie wyciekł
        public_str = str(public)
        self.assertNotIn("super-secret-key-123", public_str)

    def test_has_api_key_flag(self):
        """Public dict zawiera flagę has_api_key."""
        config = AppConfig(google_places_api_key="test-key")
        public = config.to_public_dict()
        self.assertTrue(public['google_places']['has_api_key'])

    def test_no_api_key_flag_when_empty(self):
        config = AppConfig(google_places_api_key="")
        public = config.to_public_dict()
        self.assertFalse(public['google_places']['has_api_key'])

    def test_public_dict_structure(self):
        """Public dict ma oczekiwaną strukturę."""
        config = AppConfig()
        public = config.to_public_dict()

        expected_sections = [
            'overpass', 'google_places', 'defaults',
            'report_sections', 'air_quality', 'rate_limiting', 'cache_ttl',
        ]
        for section in expected_sections:
            self.assertIn(section, public, f"Brak sekcji: {section}")


class TestGetConfigSingleton(TestCase):
    """Testy dla singletona get_config()."""

    def setUp(self):
        reset_config()

    def tearDown(self):
        reset_config()

    def test_returns_same_instance(self):
        """get_config() zwraca ten sam obiekt."""
        config1 = get_config()
        config2 = get_config()
        self.assertIs(config1, config2)

    def test_reset_clears_singleton(self):
        """reset_config() czyści singleton."""
        config1 = get_config()
        reset_config()
        config2 = get_config()
        self.assertIsNot(config1, config2)

    @override_settings(LOKTIS_CONFIG={
        'OVERPASS_URL': 'http://localhost:12345/api/interpreter',
        'DEFAULT_ENRICHMENT': 'true',
        'RATE_LIMIT_PER_MINUTE': 100,
    })
    def test_reads_from_django_settings(self):
        """get_config() czyta wartości z settings.LOKTIS_CONFIG."""
        reset_config()
        config = get_config()
        self.assertEqual(config.overpass_url, 'http://localhost:12345/api/interpreter')
        self.assertTrue(config.default_enrichment)
        self.assertEqual(config.rate_limit_per_minute, 100)

    @override_settings(LOKTIS_CONFIG={
        'REPORT_AI_INSIGHTS': 'false',
        'REPORT_AIR_QUALITY': 'false',
    })
    def test_report_toggles_from_settings(self):
        """Report toggles z settings."""
        reset_config()
        config = get_config()
        self.assertFalse(config.report_ai_insights)
        self.assertFalse(config.report_air_quality)


class TestConfigAPIEndpoint(TestCase):
    """Testy dla GET /api/config/."""

    def setUp(self):
        reset_config()
        self.client = Client()

    def tearDown(self):
        reset_config()

    def test_config_endpoint_returns_200(self):
        response = self.client.get('/api/config/')
        self.assertEqual(response.status_code, 200)

    def test_config_endpoint_returns_json(self):
        response = self.client.get('/api/config/')
        data = response.json()
        self.assertIn('overpass', data)
        self.assertIn('defaults', data)
        self.assertIn('report_sections', data)

    def test_config_endpoint_no_secrets(self):
        """Endpoint nie wystawia sekretów."""
        response = self.client.get('/api/config/')
        data_str = str(response.json())
        # Nie powinien zawierać kluczy API
        self.assertNotIn('api_key', data_str.lower().replace('has_api_key', ''))
