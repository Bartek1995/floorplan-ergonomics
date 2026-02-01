"""
Testy dla VerdictGenerator.

Testuje:
- Generowanie werdyktu na podstawie score'u
- Progi werdyktu per profil
- Generowanie wyjaśnień i kluczowych czynników
- Obliczanie confidence
"""
from django.test import TestCase

from location_analysis.scoring import ScoringEngine, VerdictGenerator, Verdict, VerdictLevel
from location_analysis.personas import get_persona, PersonaType
from location_analysis.personas.family import FAMILY_PERSONA
from location_analysis.personas.urban import URBAN_PERSONA
from location_analysis.personas.investor import INVESTOR_PERSONA


class TestVerdictLevel(TestCase):
    """Testy dla VerdictLevel enum."""
    
    def test_verdict_levels_exist(self):
        """Wszystkie poziomy werdyktu istnieją."""
        self.assertEqual(VerdictLevel.RECOMMENDED.value, 'recommended')
        self.assertEqual(VerdictLevel.CONDITIONAL.value, 'conditional')
        self.assertEqual(VerdictLevel.NOT_RECOMMENDED.value, 'not_recommended')


class TestVerdictGeneratorBasic(TestCase):
    """Podstawowe testy VerdictGenerator."""
    
    def setUp(self):
        """Setup dla testów."""
        self.generator = VerdictGenerator()
        
        self.high_scores = {
            'shops': 80, 'transport': 85, 'education': 90,
            'health': 75, 'nature': 88, 'leisure': 70,
            'food': 65, 'finance': 60,
        }
        
        self.low_scores = {
            'shops': 25, 'transport': 20, 'education': 15,
            'health': 30, 'nature': 20, 'leisure': 35,
            'food': 30, 'finance': 25,
        }
        
        self.medium_scores = {
            'shops': 55, 'transport': 50, 'education': 45,
            'health': 50, 'nature': 55, 'leisure': 50,
            'food': 50, 'finance': 45,
        }
    
    def test_generate_returns_verdict(self):
        """generate zwraca obiekt Verdict."""
        engine = ScoringEngine(FAMILY_PERSONA)
        scoring_result = engine.calculate(self.high_scores, quiet_score=75)
        
        verdict = self.generator.generate(scoring_result, FAMILY_PERSONA)
        
        self.assertIsInstance(verdict, Verdict)
    
    def test_verdict_has_required_fields(self):
        """Verdict ma wszystkie wymagane pola."""
        engine = ScoringEngine(FAMILY_PERSONA)
        scoring_result = engine.calculate(self.high_scores, quiet_score=75)
        
        verdict = self.generator.generate(scoring_result, FAMILY_PERSONA)
        
        self.assertIsNotNone(verdict.level)
        self.assertIsNotNone(verdict.label)
        self.assertIsNotNone(verdict.emoji)
        self.assertIsNotNone(verdict.explanation)
        self.assertIsInstance(verdict.key_factors, list)
        self.assertIsInstance(verdict.score, float)
        self.assertIsInstance(verdict.confidence, int)


class TestVerdictGeneratorLevels(TestCase):
    """Testy dla progów werdyktu."""
    
    def setUp(self):
        """Setup dla testów."""
        self.generator = VerdictGenerator()
    
    def test_high_score_gives_recommended(self):
        """Wysoki score daje RECOMMENDED."""
        engine = ScoringEngine(FAMILY_PERSONA)
        
        scores = {
            'shops': 85, 'transport': 80, 'education': 95,
            'health': 80, 'nature': 90, 'leisure': 75,
            'food': 70, 'finance': 65,
        }
        scoring_result = engine.calculate(scores, quiet_score=85)
        
        verdict = self.generator.generate(scoring_result, FAMILY_PERSONA)
        
        self.assertEqual(verdict.level, VerdictLevel.RECOMMENDED)
    
    def test_low_score_gives_not_recommended(self):
        """Niski score daje NOT_RECOMMENDED."""
        engine = ScoringEngine(FAMILY_PERSONA)
        
        scores = {
            'shops': 20, 'transport': 15, 'education': 10,
            'health': 25, 'nature': 15, 'leisure': 30,
            'food': 20, 'finance': 15,
        }
        scoring_result = engine.calculate(scores, quiet_score=25)
        
        verdict = self.generator.generate(scoring_result, FAMILY_PERSONA)
        
        self.assertEqual(verdict.level, VerdictLevel.NOT_RECOMMENDED)
    
    def test_medium_score_gives_conditional(self):
        """Średni score daje CONDITIONAL."""
        engine = ScoringEngine(FAMILY_PERSONA)
        
        scores = {
            'shops': 55, 'transport': 50, 'education': 55,
            'health': 50, 'nature': 55, 'leisure': 50,
            'food': 50, 'finance': 45,
        }
        scoring_result = engine.calculate(scores, quiet_score=55)
        
        verdict = self.generator.generate(scoring_result, FAMILY_PERSONA)
        
        self.assertEqual(verdict.level, VerdictLevel.CONDITIONAL)
    
    def test_dealbreaker_gives_not_recommended(self):
        """Dealbreaker daje NOT_RECOMMENDED nawet przy dobrym score."""
        engine = ScoringEngine(FAMILY_PERSONA)
        
        # Dobre score'y ale edukacja = dealbreaker
        scores = {
            'shops': 80, 'transport': 80, 'education': 10,  # Dealbreaker!
            'health': 80, 'nature': 80, 'leisure': 80,
            'food': 80, 'finance': 80,
        }
        scoring_result = engine.calculate(scores, quiet_score=80)
        
        verdict = self.generator.generate(scoring_result, FAMILY_PERSONA)
        
        self.assertEqual(verdict.level, VerdictLevel.NOT_RECOMMENDED)


class TestVerdictGeneratorLabels(TestCase):
    """Testy dla etykiet werdyktu."""
    
    def setUp(self):
        """Setup dla testów."""
        self.generator = VerdictGenerator()
    
    def test_recommended_label(self):
        """RECOMMENDED ma poprawną etykietę."""
        engine = ScoringEngine(FAMILY_PERSONA)
        scores = {
            'shops': 85, 'transport': 80, 'education': 90,
            'health': 80, 'nature': 85, 'leisure': 75,
            'food': 70, 'finance': 65,
        }
        scoring_result = engine.calculate(scores, quiet_score=85)
        
        verdict = self.generator.generate(scoring_result, FAMILY_PERSONA)
        
        self.assertEqual(verdict.label, 'Polecane')
        self.assertEqual(verdict.emoji, '✅')
    
    def test_conditional_label(self):
        """CONDITIONAL ma poprawną etykietę."""
        engine = ScoringEngine(URBAN_PERSONA)
        scores = {
            'shops': 50, 'transport': 55, 'education': 40,
            'health': 45, 'nature': 45, 'leisure': 55,
            'food': 60, 'finance': 40,
        }
        scoring_result = engine.calculate(scores, quiet_score=50)
        
        verdict = self.generator.generate(scoring_result, URBAN_PERSONA)
        
        self.assertEqual(verdict.label, 'Warunkowo polecane')
        self.assertEqual(verdict.emoji, '⚠️')
    
    def test_not_recommended_label(self):
        """NOT_RECOMMENDED ma poprawną etykietę."""
        engine = ScoringEngine(FAMILY_PERSONA)
        scores = {
            'shops': 20, 'transport': 15, 'education': 10,
            'health': 25, 'nature': 15, 'leisure': 30,
            'food': 20, 'finance': 15,
        }
        scoring_result = engine.calculate(scores, quiet_score=20)
        
        verdict = self.generator.generate(scoring_result, FAMILY_PERSONA)
        
        self.assertEqual(verdict.label, 'Niepolecane')
        self.assertEqual(verdict.emoji, '❌')


class TestVerdictGeneratorConfidence(TestCase):
    """Testy dla obliczania confidence."""
    
    def setUp(self):
        """Setup dla testów."""
        self.generator = VerdictGenerator()
    
    def test_confidence_in_range(self):
        """Confidence jest w zakresie 0-100."""
        engine = ScoringEngine(FAMILY_PERSONA)
        
        # Różne score'y
        for scores_dict, quiet in [
            ({'shops': 90, 'transport': 90, 'education': 90, 'health': 90,
              'nature': 90, 'leisure': 90, 'food': 90, 'finance': 90}, 90),
            ({'shops': 10, 'transport': 10, 'education': 10, 'health': 10,
              'nature': 10, 'leisure': 10, 'food': 10, 'finance': 10}, 10),
            ({'shops': 50, 'transport': 50, 'education': 50, 'health': 50,
              'nature': 50, 'leisure': 50, 'food': 50, 'finance': 50}, 50),
        ]:
            scoring_result = engine.calculate(scores_dict, quiet_score=quiet)
            verdict = self.generator.generate(scoring_result, FAMILY_PERSONA)
            
            self.assertGreaterEqual(verdict.confidence, 0)
            self.assertLessEqual(verdict.confidence, 100)
    
    def test_dealbreaker_high_confidence(self):
        """Dealbreaker daje wysoką pewność."""
        engine = ScoringEngine(FAMILY_PERSONA)
        
        scores = {
            'shops': 80, 'transport': 80, 'education': 5,  # Dealbreaker
            'health': 80, 'nature': 80, 'leisure': 80,
            'food': 80, 'finance': 80,
        }
        scoring_result = engine.calculate(scores, quiet_score=80)
        
        verdict = self.generator.generate(scoring_result, FAMILY_PERSONA)
        
        self.assertGreater(verdict.confidence, 90)


class TestVerdictGeneratorExplanation(TestCase):
    """Testy dla generowania wyjaśnień."""
    
    def setUp(self):
        """Setup dla testów."""
        self.generator = VerdictGenerator()
    
    def test_explanation_not_empty(self):
        """Wyjaśnienie nie jest puste."""
        engine = ScoringEngine(FAMILY_PERSONA)
        scores = {
            'shops': 60, 'transport': 60, 'education': 60,
            'health': 60, 'nature': 60, 'leisure': 60,
            'food': 60, 'finance': 60,
        }
        scoring_result = engine.calculate(scores, quiet_score=60)
        
        verdict = self.generator.generate(scoring_result, FAMILY_PERSONA)
        
        self.assertIsNotNone(verdict.explanation)
        self.assertGreater(len(verdict.explanation), 10)
    
    def test_explanation_contains_persona_name(self):
        """Wyjaśnienie zawiera nawiązanie do profilu."""
        engine = ScoringEngine(FAMILY_PERSONA)
        scores = {
            'shops': 60, 'transport': 60, 'education': 60,
            'health': 60, 'nature': 60, 'leisure': 60,
            'food': 60, 'finance': 60,
        }
        scoring_result = engine.calculate(scores, quiet_score=60)
        
        verdict = self.generator.generate(scoring_result, FAMILY_PERSONA)
        
        # Wyjaśnienie powinno zawierać emoji LUB słowo kluczowe z nazwy profilu
        # ("rodzin" jako część "rodzina", "Rodzina z dziećmi" itp.)
        explanation_lower = verdict.explanation.lower()
        self.assertTrue(
            FAMILY_PERSONA.emoji in verdict.explanation or
            'rodzin' in explanation_lower or
            'family' in explanation_lower or
            FAMILY_PERSONA.name.lower() in explanation_lower
        )


class TestVerdictGeneratorKeyFactors(TestCase):
    """Testy dla kluczowych czynników."""
    
    def setUp(self):
        """Setup dla testów."""
        self.generator = VerdictGenerator()
    
    def test_key_factors_not_empty_for_extreme_scores(self):
        """Kluczowe czynniki nie są puste dla ekstremalnych score'ów."""
        engine = ScoringEngine(FAMILY_PERSONA)
        
        # Bardzo dobre score'y
        scores = {
            'shops': 90, 'transport': 85, 'education': 95,
            'health': 80, 'nature': 92, 'leisure': 75,
            'food': 70, 'finance': 65,
        }
        scoring_result = engine.calculate(scores, quiet_score=85)
        
        verdict = self.generator.generate(scoring_result, FAMILY_PERSONA)
        
        self.assertGreater(len(verdict.key_factors), 0)
    
    def test_key_factors_limited_to_5(self):
        """Kluczowe czynniki są ograniczone do 5."""
        engine = ScoringEngine(FAMILY_PERSONA)
        
        scores = {
            'shops': 90, 'transport': 85, 'education': 10,  # Dealbreaker
            'health': 80, 'nature': 92, 'leisure': 75,
            'food': 70, 'finance': 65,
        }
        scoring_result = engine.calculate(scores, quiet_score=85)
        
        verdict = self.generator.generate(scoring_result, FAMILY_PERSONA)
        
        self.assertLessEqual(len(verdict.key_factors), 5)


class TestVerdictGeneratorDifferentPersonas(TestCase):
    """Testy porównujące werdykty dla różnych profili."""
    
    def setUp(self):
        """Setup dla testów."""
        self.generator = VerdictGenerator()
    
    def test_same_location_different_verdicts(self):
        """Ta sama lokalizacja może mieć różne werdykty dla różnych profili."""
        # Lokalizacja idealna dla singla, słaba dla rodziny
        scores = {
            'shops': 70, 'transport': 95, 'education': 25,  # Słaba edukacja
            'health': 50, 'nature': 30,  # Mało zieleni
            'leisure': 85, 'food': 90,
            'finance': 60,
        }
        quiet = 35  # Głośno
        
        family_engine = ScoringEngine(FAMILY_PERSONA)
        urban_engine = ScoringEngine(URBAN_PERSONA)
        
        family_result = family_engine.calculate(scores, quiet)
        urban_result = urban_engine.calculate(scores, quiet)
        
        family_verdict = self.generator.generate(family_result, FAMILY_PERSONA)
        urban_verdict = self.generator.generate(urban_result, URBAN_PERSONA)
        
        # Urban powinien być bardziej pozytywny
        self.assertNotEqual(family_verdict.level, urban_verdict.level)
        # Family prawdopodobnie NOT_RECOMMENDED (dealbreaker edukacja)
        # Urban prawdopodobnie RECOMMENDED lub CONDITIONAL
    
    def test_family_location_good_for_family(self):
        """Lokalizacja rodzinna jest polecana dla rodzin."""
        # Lokalizacja idealna dla rodziny
        scores = {
            'shops': 60, 'transport': 50, 'education': 95,  # Świetna edukacja
            'health': 75, 'nature': 90,  # Dużo zieleni
            'leisure': 60, 'food': 40,
            'finance': 30,
        }
        quiet = 85  # Cicho
        
        family_engine = ScoringEngine(FAMILY_PERSONA)
        family_result = family_engine.calculate(scores, quiet)
        family_verdict = self.generator.generate(family_result, FAMILY_PERSONA)
        
        self.assertEqual(family_verdict.level, VerdictLevel.RECOMMENDED)


class TestVerdictGeneratorPersonaMatch(TestCase):
    """Testy dla persona_match."""
    
    def setUp(self):
        """Setup dla testów."""
        self.generator = VerdictGenerator()
    
    def test_persona_match_values(self):
        """persona_match zwraca poprawne wartości."""
        valid_matches = {'excellent', 'good', 'acceptable', 'poor', 'mismatch'}
        
        engine = ScoringEngine(FAMILY_PERSONA)
        
        for score_level in [90, 70, 50, 30, 10]:
            scores = {cat: score_level for cat in 
                     ['shops', 'transport', 'education', 'health',
                      'nature', 'leisure', 'food', 'finance']}
            
            scoring_result = engine.calculate(scores, quiet_score=score_level)
            verdict = self.generator.generate(scoring_result, FAMILY_PERSONA)
            
            self.assertIn(verdict.persona_match, valid_matches)


class TestVerdictSerialization(TestCase):
    """Testy serializacji Verdict."""
    
    def setUp(self):
        """Setup dla testów."""
        self.generator = VerdictGenerator()
    
    def test_to_dict_returns_dict(self):
        """to_dict zwraca słownik."""
        engine = ScoringEngine(FAMILY_PERSONA)
        scores = {
            'shops': 60, 'transport': 60, 'education': 60,
            'health': 60, 'nature': 60, 'leisure': 60,
            'food': 60, 'finance': 60,
        }
        scoring_result = engine.calculate(scores, quiet_score=60)
        
        verdict = self.generator.generate(scoring_result, FAMILY_PERSONA)
        dict_result = verdict.to_dict()
        
        self.assertIsInstance(dict_result, dict)
    
    def test_to_dict_contains_required_keys(self):
        """to_dict zawiera wymagane klucze."""
        engine = ScoringEngine(FAMILY_PERSONA)
        scores = {
            'shops': 60, 'transport': 60, 'education': 60,
            'health': 60, 'nature': 60, 'leisure': 60,
            'food': 60, 'finance': 60,
        }
        scoring_result = engine.calculate(scores, quiet_score=60)
        
        verdict = self.generator.generate(scoring_result, FAMILY_PERSONA)
        dict_result = verdict.to_dict()
        
        required_keys = [
            'level', 'label', 'emoji', 'explanation',
            'key_factors', 'score', 'confidence', 'persona_match'
        ]
        
        for key in required_keys:
            self.assertIn(key, dict_result)
    
    def test_to_dict_level_is_string(self):
        """to_dict zwraca level jako string."""
        engine = ScoringEngine(FAMILY_PERSONA)
        scores = {
            'shops': 60, 'transport': 60, 'education': 60,
            'health': 60, 'nature': 60, 'leisure': 60,
            'food': 60, 'finance': 60,
        }
        scoring_result = engine.calculate(scores, quiet_score=60)
        
        verdict = self.generator.generate(scoring_result, FAMILY_PERSONA)
        dict_result = verdict.to_dict()
        
        self.assertIsInstance(dict_result['level'], str)
