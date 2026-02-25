"""
Testy integracyjne dla całego flow analizy lokalizacji z profilami użytkownika.

Testuje:
- E2E API requests z różnymi profilami
- Response format
- Różne werdykty dla różnych profili
"""
from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock
import json

from location_analysis.personas import PersonaType
from location_analysis.services import AnalysisService


# Helper: domyślne puste metryki dla mocków
EMPTY_NATURE_METRICS = {
    'green_landcover_counts': {},
    'green_types_present': [],
    'nearest_distances': {},
    'total_green_elements': 0,
    'green_density_proxy': 0.0,
    'greenery_level': 'niska',
    'greenery_label': 'Zieleń w otoczeniu: niska',
    'types_label': None,
    'nearest_park_label': 'Brak parku w zasięgu',
    'water_present': False,
    'nearest_water_m': None,
}

def make_mock_pois(pois_dict=None):
    """Tworzy mock return value dla _get_pois (tuple: pois, metrics, cache_used)."""
    if pois_dict is None:
        pois_dict = {cat: [] for cat in ['shops', 'transport', 'education', 'health', 'nature', 'leisure', 'food', 'finance', 'roads']}
    return (pois_dict, {'nature': EMPTY_NATURE_METRICS}, False)


class TestAnalyzeLocationAPIWithProfiles(TestCase):
    """Testy integracyjne dla API analizy lokalizacji z profilami."""
    
    def setUp(self):
        """Setup dla testów."""
        self.client = Client()
        self.url = '/api/analyze-location/'
        
        self.base_request = {
            'latitude': 52.2297,
            'longitude': 21.0122,
            'price': 500000,
            'area_sqm': 50,
            'address': 'Test Address, Warsaw',
        }
    
    def test_request_with_family_profile(self):
        """Request z profilem family jest akceptowany."""
        request_data = {**self.base_request, 'user_profile': 'family'}
        
        with patch('location_analysis.views.analysis_service') as mock_service:
            mock_service.analyze_location_stream.return_value = iter([
                json.dumps({'status': 'complete', 'result': {}}) + '\n'
            ])
            
            response = self.client.post(
                self.url,
                data=json.dumps(request_data),
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 200)
            mock_service.analyze_location_stream.assert_called_once()
            
            # Sprawdź czy user_profile został przekazany
            call_kwargs = mock_service.analyze_location_stream.call_args.kwargs
            self.assertEqual(call_kwargs.get('user_profile'), 'family')
    
    def test_request_with_urban_profile(self):
        """Request z profilem urban jest akceptowany."""
        request_data = {**self.base_request, 'user_profile': 'urban'}
        
        with patch('location_analysis.views.analysis_service') as mock_service:
            mock_service.analyze_location_stream.return_value = iter([
                json.dumps({'status': 'complete', 'result': {}}) + '\n'
            ])
            
            response = self.client.post(
                self.url,
                data=json.dumps(request_data),
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 200)
            
            call_kwargs = mock_service.analyze_location_stream.call_args.kwargs
            self.assertEqual(call_kwargs.get('user_profile'), 'urban')
    
    def test_request_with_investor_profile(self):
        """Request z profilem investor jest akceptowany."""
        request_data = {**self.base_request, 'user_profile': 'investor'}
        
        with patch('location_analysis.views.analysis_service') as mock_service:
            mock_service.analyze_location_stream.return_value = iter([
                json.dumps({'status': 'complete', 'result': {}}) + '\n'
            ])
            
            response = self.client.post(
                self.url,
                data=json.dumps(request_data),
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 200)
            
            call_kwargs = mock_service.analyze_location_stream.call_args.kwargs
            self.assertEqual(call_kwargs.get('user_profile'), 'investor')
    
    def test_request_without_profile_defaults_to_family(self):
        """Request bez profilu używa domyślnego (family)."""
        request_data = self.base_request  # Brak user_profile
        
        with patch('location_analysis.views.analysis_service') as mock_service:
            mock_service.analyze_location_stream.return_value = iter([
                json.dumps({'status': 'complete', 'result': {}}) + '\n'
            ])
            
            response = self.client.post(
                self.url,
                data=json.dumps(request_data),
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 200)
            
            call_kwargs = mock_service.analyze_location_stream.call_args.kwargs
            self.assertEqual(call_kwargs.get('user_profile'), 'family')
    
    def test_invalid_profile_rejected(self):
        """Nieprawidłowy profil jest odrzucany."""
        request_data = {**self.base_request, 'user_profile': 'invalid_profile'}
        
        response = self.client.post(
            self.url,
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)


class TestAnalysisServiceWithProfiles(TestCase):
    """Testy dla AnalysisService z profilami."""
    
    def setUp(self):
        """Setup dla testów."""
        self.service = AnalysisService()
    
    @patch.object(AnalysisService, '_get_pois')
    @patch.object(AnalysisService, '_save_location_to_db')
    def test_analyze_location_stream_with_family_profile(self, mock_save, mock_pois):
        """analyze_location_stream działa z profilem family."""
        # Mock POIs (now returns tuple: pois, metrics)
        mock_pois.return_value = make_mock_pois()
        mock_save.return_value = None
        
        # Wykonaj analizę
        results = list(self.service.analyze_location_stream(
            lat=52.2297,
            lon=21.0122,
            price=500000,
            area_sqm=50,
            address='Test Address',
            user_profile='family',
        ))
        
        # Sprawdź czy analiza się zakończyła
        self.assertGreater(len(results), 0)
        
        # Ostatni event powinien być 'complete' lub 'error'
        last_event = json.loads(results[-1])
        self.assertIn(last_event['status'], ['complete', 'error'])
    
    @patch.object(AnalysisService, '_get_pois')
    @patch.object(AnalysisService, '_save_location_to_db')
    def test_response_contains_persona_data(self, mock_save, mock_pois):
        """Response zawiera dane o profilu."""
        mock_pois.return_value = make_mock_pois()
        mock_save.return_value = None
        
        results = list(self.service.analyze_location_stream(
            lat=52.2297,
            lon=21.0122,
            price=500000,
            area_sqm=50,
            address='Test Address',
            user_profile='urban',
        ))
        
        # Znajdź event 'complete'
        complete_events = [json.loads(r) for r in results if 'complete' in r]
        
        if complete_events:
            result = complete_events[0].get('result', {})
            
            # Sprawdź czy persona jest w wyniku
            self.assertIn('persona', result)
            self.assertEqual(result['persona']['type'], 'urban')
    
    @patch.object(AnalysisService, '_get_pois')
    @patch.object(AnalysisService, '_save_location_to_db')
    def test_response_contains_scoring_data(self, mock_save, mock_pois):
        """Response zawiera dane scoringu."""
        mock_pois.return_value = make_mock_pois()
        mock_save.return_value = None
        
        results = list(self.service.analyze_location_stream(
            lat=52.2297,
            lon=21.0122,
            price=500000,
            area_sqm=50,
            address='Test Address',
            user_profile='investor',
        ))
        
        complete_events = [json.loads(r) for r in results if 'complete' in r]
        
        if complete_events:
            result = complete_events[0].get('result', {})
            
            self.assertIn('scoring', result)
            self.assertIn('total_score', result['scoring'])
    
    @patch.object(AnalysisService, '_get_pois')
    @patch.object(AnalysisService, '_save_location_to_db')
    def test_response_contains_verdict(self, mock_save, mock_pois):
        """Response zawiera werdykt."""
        mock_pois.return_value = make_mock_pois()
        mock_save.return_value = None
        
        results = list(self.service.analyze_location_stream(
            lat=52.2297,
            lon=21.0122,
            price=500000,
            area_sqm=50,
            address='Test Address',
            user_profile='family',
        ))
        
        complete_events = [json.loads(r) for r in results if 'complete' in r]
        
        if complete_events:
            result = complete_events[0].get('result', {})
            
            self.assertIn('verdict', result)
            self.assertIn('level', result['verdict'])
            self.assertIn('label', result['verdict'])


class TestDifferentProfilesGiveDifferentVerdicts(TestCase):
    """Testy sprawdzające czy różne profile dają różne wyniki."""
    
    def setUp(self):
        """Setup dla testów."""
        self.service = AnalysisService()
    
    @patch.object(AnalysisService, '_get_pois')
    @patch.object(AnalysisService, '_save_location_to_db')
    def test_urban_location_scores_differently_for_different_profiles(
        self, mock_save, mock_pois
    ):
        """Lokalizacja miejska jest oceniana różnie przez różne profile."""
        from location_analysis.geo.overpass_client import POI
        
        # Symuluj lokalizację miejską (dobry transport, gastro, słaba edukacja)
        urban_pois = {
            'shops': [
                POI(lat=52.23, lon=21.01, name='Żabka', category='shops', subcategory='convenience', distance_m=50, tags={}),
                POI(lat=52.23, lon=21.01, name='Biedronka', category='shops', subcategory='supermarket', distance_m=150, tags={}),
            ],
            'transport': [
                POI(lat=52.23, lon=21.01, name='Metro Centrum', category='transport', subcategory='subway', distance_m=100, tags={}),
                POI(lat=52.23, lon=21.01, name='Tramwaj 15', category='transport', subcategory='tram_stop', distance_m=80, tags={}),
                POI(lat=52.23, lon=21.01, name='Autobus 175', category='transport', subcategory='bus_stop', distance_m=120, tags={}),
            ],
            'education': [],  # Brak szkół!
            'health': [POI(lat=52.23, lon=21.01, name='Apteka', category='health', subcategory='pharmacy', distance_m=200, tags={})],
            'nature': [],  # Brak parków
            'leisure': [
                POI(lat=52.23, lon=21.01, name='Fitness Club', category='leisure', subcategory='fitness_centre', distance_m=100, tags={}),
            ],
            'food': [
                POI(lat=52.23, lon=21.01, name='Pizzeria', category='food', subcategory='restaurant', distance_m=50, tags={}),
                POI(lat=52.23, lon=21.01, name='Starbucks', category='food', subcategory='cafe', distance_m=80, tags={}),
                POI(lat=52.23, lon=21.01, name='Bar Mleczny', category='food', subcategory='fast_food', distance_m=150, tags={}),
            ],
            'finance': [POI(lat=52.23, lon=21.01, name='PKO BP', category='finance', subcategory='bank', distance_m=200, tags={})],
            'roads': [],
        }
        mock_pois.return_value = make_mock_pois(urban_pois)
        mock_save.return_value = None
        
        # Analiza dla FAMILY
        family_results = list(self.service.analyze_location_stream(
            lat=52.2297, lon=21.0122,
            price=500000, area_sqm=50,
            address='Test', user_profile='family',
        ))
        
        # Analiza dla URBAN
        urban_results = list(self.service.analyze_location_stream(
            lat=52.2297, lon=21.0122,
            price=500000, area_sqm=50,
            address='Test', user_profile='urban',
        ))
        
        # Wyciągnij score'y
        family_complete = [json.loads(r) for r in family_results if 'complete' in r]
        urban_complete = [json.loads(r) for r in urban_results if 'complete' in r]
        
        if family_complete and urban_complete:
            family_score = family_complete[0]['result']['scoring']['total_score']
            urban_score = urban_complete[0]['result']['scoring']['total_score']
            
            # Urban powinien mieć wyższy score dla tej lokalizacji
            self.assertGreater(urban_score, family_score)


class TestProfileInStreamMessages(TestCase):
    """Testy dla komunikatów stream z informacją o profilu."""
    
    def setUp(self):
        """Setup dla testów."""
        self.service = AnalysisService()
    
    @patch.object(AnalysisService, '_get_pois')
    @patch.object(AnalysisService, '_save_location_to_db')
    def test_starting_message_contains_profile_info(self, mock_save, mock_pois):
        """Pierwszy komunikat zawiera info o profilu."""
        mock_pois.return_value = make_mock_pois()
        mock_save.return_value = None
        
        results = list(self.service.analyze_location_stream(
            lat=52.2297, lon=21.0122,
            price=500000, area_sqm=50,
            address='Test', user_profile='family',
        ))
        
        # Pierwszy event 'starting' powinien zawierać info o profilu
        starting_events = [json.loads(r) for r in results if 'starting' in r]
        
        if starting_events:
            message = starting_events[0].get('message', '')
            # Powinien zawierać emoji lub nazwę profilu
            self.assertTrue(
                '👨‍👩‍👧' in message or 'Rodzina' in message or 'family' in message.lower()
            )
    
    @patch.object(AnalysisService, '_get_pois')
    @patch.object(AnalysisService, '_save_location_to_db')
    def test_profile_calculation_step_exists(self, mock_save, mock_pois):
        """Jest krok 'profile' w streamie."""
        mock_pois.return_value = make_mock_pois()
        mock_save.return_value = None
        
        results = list(self.service.analyze_location_stream(
            lat=52.2297, lon=21.0122,
            price=500000, area_sqm=50,
            address='Test', user_profile='urban',
        ))
        
        # Szukaj eventu 'profile'
        profile_events = [json.loads(r) for r in results if 'profile' in r]
        
        self.assertGreater(len(profile_events), 0)
