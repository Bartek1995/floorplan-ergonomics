"""
Testy dla ScoringEngine.

Testuje:
- Obliczanie score'u z dynamicznymi wagami
- Modyfikatory Quiet Score
- Detekcję dealbreakers
- Ekstrakcję mocnych/słabych stron
"""
from django.test import TestCase

from location_analysis.scoring import ScoringEngine, ScoringResult
from location_analysis.personas import get_persona, PersonaType
from location_analysis.personas.family import FAMILY_PERSONA
from location_analysis.personas.urban import URBAN_PERSONA
from location_analysis.personas.investor import INVESTOR_PERSONA


class TestScoringEngineInit(TestCase):
    """Testy inicjalizacji ScoringEngine."""
    
    def test_init_with_family_persona(self):
        """Inicjalizacja z profilem FAMILY."""
        engine = ScoringEngine(FAMILY_PERSONA)
        
        self.assertEqual(engine.persona, FAMILY_PERSONA)
        self.assertIsNotNone(engine.weights)
    
    def test_init_normalizes_weights(self):
        """Wagi są normalizowane do sumy = 1.0."""
        engine = ScoringEngine(FAMILY_PERSONA)
        
        total = sum(engine.weights.values())
        self.assertAlmostEqual(total, 1.0, places=5)


class TestScoringEngineCalculate(TestCase):
    """Testy dla metody calculate."""
    
    def setUp(self):
        """Setup dla testów."""
        # Przykładowe score'y kategorii
        self.good_scores = {
            'shops': 80,
            'transport': 75,
            'education': 85,
            'health': 70,
            'nature': 90,
            'leisure': 60,
            'food': 65,
            'finance': 50,
        }
        
        self.poor_scores = {
            'shops': 20,
            'transport': 15,
            'education': 10,
            'health': 25,
            'nature': 20,
            'leisure': 30,
            'food': 25,
            'finance': 20,
        }
        
        self.mixed_scores = {
            'shops': 60,
            'transport': 90,   # Bardzo dobry
            'education': 20,   # Słaby
            'health': 50,
            'nature': 30,
            'leisure': 70,
            'food': 85,        # Bardzo dobry
            'finance': 40,
        }
    
    def test_calculate_returns_scoring_result(self):
        """calculate zwraca ScoringResult."""
        engine = ScoringEngine(FAMILY_PERSONA)
        result = engine.calculate(self.good_scores, quiet_score=70)
        
        self.assertIsInstance(result, ScoringResult)
    
    def test_calculate_total_score_in_range(self):
        """total_score jest w zakresie 0-100."""
        engine = ScoringEngine(FAMILY_PERSONA)
        
        # Dobre score'y
        result = engine.calculate(self.good_scores, quiet_score=80)
        self.assertGreaterEqual(result.total_score, 0)
        self.assertLessEqual(result.total_score, 100)
        
        # Słabe score'y
        result = engine.calculate(self.poor_scores, quiet_score=20)
        self.assertGreaterEqual(result.total_score, 0)
        self.assertLessEqual(result.total_score, 100)
    
    def test_good_scores_give_high_total(self):
        """Dobre score'y dają wysoki wynik końcowy."""
        engine = ScoringEngine(FAMILY_PERSONA)
        result = engine.calculate(self.good_scores, quiet_score=80)
        
        self.assertGreater(result.total_score, 60)
    
    def test_poor_scores_give_low_total(self):
        """Słabe score'y dają niski wynik końcowy."""
        engine = ScoringEngine(FAMILY_PERSONA)
        result = engine.calculate(self.poor_scores, quiet_score=20)
        
        self.assertLess(result.total_score, 40)
    
    def test_persona_type_in_result(self):
        """persona_type jest w wyniku."""
        engine = ScoringEngine(FAMILY_PERSONA)
        result = engine.calculate(self.good_scores, quiet_score=70)
        
        self.assertEqual(result.persona_type, 'family')
    
    def test_category_breakdown_present(self):
        """category_breakdown jest w wyniku."""
        engine = ScoringEngine(FAMILY_PERSONA)
        result = engine.calculate(self.good_scores, quiet_score=70)
        
        self.assertIsInstance(result.category_breakdown, list)
        self.assertEqual(len(result.category_breakdown), 8)  # 8 kategorii


class TestScoringEngineQuietModifier(TestCase):
    """Testy dla modyfikatora Quiet Score."""
    
    def test_high_quiet_score_gives_bonus(self):
        """Wysoki Quiet Score daje bonus."""
        engine = ScoringEngine(FAMILY_PERSONA)
        
        # Ten sam base score, różny quiet score
        result_high = engine.calculate({'shops': 50, 'transport': 50, 'education': 50,
                                         'health': 50, 'nature': 50, 'leisure': 50,
                                         'food': 50, 'finance': 50}, quiet_score=90)
        result_low = engine.calculate({'shops': 50, 'transport': 50, 'education': 50,
                                        'health': 50, 'nature': 50, 'leisure': 50,
                                        'food': 50, 'finance': 50}, quiet_score=30)
        
        self.assertGreater(result_high.total_score, result_low.total_score)
    
    def test_quiet_modifier_in_range(self):
        """quiet_modifier jest w zakresie 0.7-1.15."""
        engine = ScoringEngine(FAMILY_PERSONA)
        
        # Ekstremalnie wysoki quiet
        result = engine.calculate({'shops': 50, 'transport': 50, 'education': 50,
                                   'health': 50, 'nature': 50, 'leisure': 50,
                                   'food': 50, 'finance': 50}, quiet_score=100)
        self.assertLessEqual(result.quiet_modifier, 1.15)
        self.assertGreaterEqual(result.quiet_modifier, 0.7)
        
        # Ekstremalnie niski quiet
        result = engine.calculate({'shops': 50, 'transport': 50, 'education': 50,
                                   'health': 50, 'nature': 50, 'leisure': 50,
                                   'food': 50, 'finance': 50}, quiet_score=0)
        self.assertLessEqual(result.quiet_modifier, 1.15)
        self.assertGreaterEqual(result.quiet_modifier, 0.7)
    
    def test_urban_less_affected_by_low_quiet(self):
        """Profil URBAN jest mniej dotknięty niskim Quiet Score."""
        scores = {'shops': 50, 'transport': 80, 'education': 30,
                  'health': 50, 'nature': 40, 'leisure': 60,
                  'food': 80, 'finance': 40}
        
        family_engine = ScoringEngine(FAMILY_PERSONA)
        urban_engine = ScoringEngine(URBAN_PERSONA)
        
        # Niska cisza
        family_result = family_engine.calculate(scores, quiet_score=25)
        urban_result = urban_engine.calculate(scores, quiet_score=25)
        
        # Różnica modyfikatora powinna być mniejsza dla urban
        # (quiet ma mniejszą wagę)
        self.assertLess(
            abs(1.0 - urban_result.quiet_modifier),
            abs(1.0 - family_result.quiet_modifier)
        )


class TestScoringEngineDealbreakers(TestCase):
    """Testy dla dealbreakers."""
    
    def test_dealbreaker_detected(self):
        """Dealbreaker jest wykrywany."""
        engine = ScoringEngine(FAMILY_PERSONA)
        
        # Edukacja poniżej progu (dealbreaker dla rodzin)
        scores = {'shops': 60, 'transport': 60, 'education': 10,  # < 25
                  'health': 60, 'nature': 60, 'leisure': 60,
                  'food': 60, 'finance': 60}
        
        result = engine.calculate(scores, quiet_score=70)
        
        self.assertTrue(result.has_dealbreaker)
    
    def test_dealbreaker_limits_max_score(self):
        """Dealbreaker ogranicza max score do 40."""
        engine = ScoringEngine(FAMILY_PERSONA)
        
        # Dobre score'y ale edukacja = dealbreaker
        scores = {'shops': 80, 'transport': 80, 'education': 10,
                  'health': 80, 'nature': 80, 'leisure': 80,
                  'food': 80, 'finance': 80}
        
        result = engine.calculate(scores, quiet_score=80)
        
        self.assertLessEqual(result.total_score, 40)
    
    def test_no_dealbreaker_when_above_threshold(self):
        """Brak dealbreakera gdy powyżej progu."""
        engine = ScoringEngine(FAMILY_PERSONA)
        
        scores = {'shops': 60, 'transport': 60, 'education': 50,  # > 25
                  'health': 60, 'nature': 60, 'leisure': 60,
                  'food': 60, 'finance': 60}
        
        result = engine.calculate(scores, quiet_score=70)
        
        self.assertFalse(result.has_dealbreaker)
    
    def test_urban_transport_dealbreaker(self):
        """Transport jest dealbreaker dla URBAN."""
        engine = ScoringEngine(URBAN_PERSONA)
        
        scores = {'shops': 70, 'transport': 10,  # < 20
                  'education': 50, 'health': 60, 'nature': 60,
                  'leisure': 70, 'food': 80, 'finance': 50}
        
        result = engine.calculate(scores, quiet_score=60)
        
        self.assertTrue(result.has_dealbreaker)


class TestScoringEngineStrengthsWeaknesses(TestCase):
    """Testy dla ekstrakcji mocnych/słabych stron."""
    
    def test_strengths_extracted(self):
        """Mocne strony są ekstrahowane."""
        engine = ScoringEngine(FAMILY_PERSONA)
        
        scores = {'shops': 80, 'transport': 40, 'education': 90,
                  'health': 50, 'nature': 85, 'leisure': 45,
                  'food': 60, 'finance': 35}
        
        result = engine.calculate(scores, quiet_score=75)
        
        self.assertIsInstance(result.strengths, list)
        self.assertGreater(len(result.strengths), 0)
    
    def test_weaknesses_extracted(self):
        """Słabe strony są ekstrahowane."""
        engine = ScoringEngine(FAMILY_PERSONA)
        
        scores = {'shops': 50, 'transport': 50, 'education': 20,  # Słabe (krytyczne)
                  'health': 50, 'nature': 15,  # Słabe (krytyczne)
                  'leisure': 50, 'food': 50, 'finance': 50}
        
        result = engine.calculate(scores, quiet_score=50)
        
        self.assertIsInstance(result.weaknesses, list)
        self.assertGreater(len(result.weaknesses), 0)


class TestScoringEngineWarnings(TestCase):
    """Testy dla generowania ostrzeżeń."""
    
    def test_dealbreaker_warning_generated(self):
        """Ostrzeżenie o dealbreaker jest generowane."""
        engine = ScoringEngine(FAMILY_PERSONA)
        
        scores = {'shops': 60, 'transport': 60, 'education': 10,
                  'health': 60, 'nature': 60, 'leisure': 60,
                  'food': 60, 'finance': 60}
        
        result = engine.calculate(scores, quiet_score=70)
        
        self.assertGreater(len(result.warnings), 0)
        self.assertTrue(any('DEALBREAKER' in w for w in result.warnings))
    
    def test_quiet_score_warning_generated(self):
        """Ostrzeżenie o niskim Quiet Score jest generowane."""
        engine = ScoringEngine(FAMILY_PERSONA)
        
        scores = {'shops': 60, 'transport': 60, 'education': 60,
                  'health': 60, 'nature': 60, 'leisure': 60,
                  'food': 60, 'finance': 60}
        
        result = engine.calculate(scores, quiet_score=30)  # < threshold 50
        
        self.assertTrue(any('Quiet Score' in w for w in result.warnings))


class TestScoringEngineDifferentPersonas(TestCase):
    """Testy porównujące różne profile."""
    
    def test_same_scores_different_results_for_different_personas(self):
        """Te same score'y dają różne wyniki dla różnych profili."""
        scores = {'shops': 60, 'transport': 85, 'education': 30,
                  'health': 50, 'nature': 40, 'leisure': 70,
                  'food': 90, 'finance': 45}
        quiet = 60
        
        family_engine = ScoringEngine(FAMILY_PERSONA)
        urban_engine = ScoringEngine(URBAN_PERSONA)
        investor_engine = ScoringEngine(INVESTOR_PERSONA)
        
        family_result = family_engine.calculate(scores, quiet)
        urban_result = urban_engine.calculate(scores, quiet)
        investor_result = investor_engine.calculate(scores, quiet)
        
        # Wyniki powinny być różne
        self.assertNotAlmostEqual(family_result.total_score, urban_result.total_score, places=0)
    
    def test_urban_scores_higher_for_transport_heavy_location(self):
        """URBAN daje wyższy score dla lokalizacji z dobrym transportem."""
        scores = {'shops': 50, 'transport': 95, 'education': 20,
                  'health': 40, 'nature': 30, 'leisure': 80,
                  'food': 90, 'finance': 50}
        quiet = 40  # Głośna miejscówka
        
        family_engine = ScoringEngine(FAMILY_PERSONA)
        urban_engine = ScoringEngine(URBAN_PERSONA)
        
        family_result = family_engine.calculate(scores, quiet)
        urban_result = urban_engine.calculate(scores, quiet)
        
        self.assertGreater(urban_result.total_score, family_result.total_score)
    
    def test_family_scores_higher_for_education_heavy_location(self):
        """FAMILY daje wyższy score dla lokalizacji z dobrą edukacją."""
        scores = {'shops': 50, 'transport': 40, 'education': 95,
                  'health': 60, 'nature': 85, 'leisure': 50,
                  'food': 40, 'finance': 30}
        quiet = 80  # Cicha okolica
        
        family_engine = ScoringEngine(FAMILY_PERSONA)
        urban_engine = ScoringEngine(URBAN_PERSONA)
        
        family_result = family_engine.calculate(scores, quiet)
        urban_result = urban_engine.calculate(scores, quiet)
        
        self.assertGreater(family_result.total_score, urban_result.total_score)


class TestScoringResultSerialization(TestCase):
    """Testy serializacji ScoringResult."""
    
    def test_to_dict_returns_dict(self):
        """to_dict zwraca słownik."""
        engine = ScoringEngine(FAMILY_PERSONA)
        scores = {'shops': 60, 'transport': 60, 'education': 60,
                  'health': 60, 'nature': 60, 'leisure': 60,
                  'food': 60, 'finance': 60}
        
        result = engine.calculate(scores, quiet_score=60)
        dict_result = result.to_dict()
        
        self.assertIsInstance(dict_result, dict)
    
    def test_to_dict_contains_required_keys(self):
        """to_dict zawiera wymagane klucze."""
        engine = ScoringEngine(FAMILY_PERSONA)
        scores = {'shops': 60, 'transport': 60, 'education': 60,
                  'health': 60, 'nature': 60, 'leisure': 60,
                  'food': 60, 'finance': 60}
        
        result = engine.calculate(scores, quiet_score=60)
        dict_result = result.to_dict()
        
        required_keys = [
            'total_score', 'base_score', 'quiet_modifier', 'quiet_score',
            'persona_type', 'has_dealbreaker', 'category_breakdown',
            'warnings', 'strengths', 'weaknesses'
        ]
        
        for key in required_keys:
            self.assertIn(key, dict_result)
