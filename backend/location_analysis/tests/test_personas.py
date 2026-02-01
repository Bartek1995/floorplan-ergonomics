"""
Testy dla modułu Personas (Profile użytkownika).

Testuje:
- Poprawność definicji profili
- Normalizację wag
- Registry i factory functions
"""
from django.test import TestCase

from location_analysis.personas import (
    PersonaType,
    PersonaConfig,
    get_persona,
    get_all_personas,
    get_persona_by_string,
    PERSONA_REGISTRY,
)
from location_analysis.personas.base import (
    VerdictThresholds,
    QuietScoreConfig,
    NarrativeTemplates,
)
from location_analysis.personas.family import FAMILY_PERSONA
from location_analysis.personas.urban import URBAN_PERSONA
from location_analysis.personas.investor import INVESTOR_PERSONA


class TestPersonaType(TestCase):
    """Testy dla PersonaType enum."""
    
    def test_persona_types_exist(self):
        """Wszystkie typy personas są zdefiniowane."""
        self.assertEqual(PersonaType.FAMILY.value, 'family')
        self.assertEqual(PersonaType.URBAN.value, 'urban')
        self.assertEqual(PersonaType.INVESTOR.value, 'investor')
    
    def test_from_string_valid(self):
        """from_string konwertuje poprawne stringi."""
        self.assertEqual(PersonaType.from_string('family'), PersonaType.FAMILY)
        self.assertEqual(PersonaType.from_string('FAMILY'), PersonaType.FAMILY)
        self.assertEqual(PersonaType.from_string('urban'), PersonaType.URBAN)
        self.assertEqual(PersonaType.from_string('investor'), PersonaType.INVESTOR)
    
    def test_from_string_invalid_returns_default(self):
        """from_string zwraca FAMILY dla nieprawidłowych wartości."""
        self.assertEqual(PersonaType.from_string('invalid'), PersonaType.FAMILY)
        self.assertEqual(PersonaType.from_string(''), PersonaType.FAMILY)
        self.assertEqual(PersonaType.from_string('random'), PersonaType.FAMILY)


class TestPersonaConfig(TestCase):
    """Testy dla PersonaConfig."""
    
    def test_family_persona_has_required_fields(self):
        """FAMILY_PERSONA ma wszystkie wymagane pola."""
        persona = FAMILY_PERSONA
        
        self.assertEqual(persona.type, PersonaType.FAMILY)
        self.assertIsNotNone(persona.name)
        self.assertIsNotNone(persona.description)
        self.assertIsNotNone(persona.emoji)
        self.assertIsInstance(persona.category_weights, dict)
        self.assertIsInstance(persona.quiet_score_config, QuietScoreConfig)
        self.assertIsInstance(persona.verdict_thresholds, VerdictThresholds)
        self.assertIsInstance(persona.narrative_templates, NarrativeTemplates)
    
    def test_urban_persona_has_required_fields(self):
        """URBAN_PERSONA ma wszystkie wymagane pola."""
        persona = URBAN_PERSONA
        
        self.assertEqual(persona.type, PersonaType.URBAN)
        self.assertIsNotNone(persona.name)
        self.assertIsNotNone(persona.category_weights)
    
    def test_investor_persona_has_required_fields(self):
        """INVESTOR_PERSONA ma wszystkie wymagane pola."""
        persona = INVESTOR_PERSONA
        
        self.assertEqual(persona.type, PersonaType.INVESTOR)
        self.assertIsNotNone(persona.name)
        self.assertIsNotNone(persona.category_weights)
    
    def test_category_weights_contain_all_categories(self):
        """Każdy profil ma wagi dla wszystkich kategorii POI."""
        expected_categories = {
            'shops', 'transport', 'education', 'health',
            'nature', 'leisure', 'food', 'finance'
        }
        
        for persona in [FAMILY_PERSONA, URBAN_PERSONA, INVESTOR_PERSONA]:
            with self.subTest(persona=persona.type.value):
                self.assertEqual(
                    set(persona.category_weights.keys()),
                    expected_categories,
                    f"Brakuje kategorii w profilu {persona.type.value}"
                )
    
    def test_category_weights_are_positive(self):
        """Wagi kategorii są dodatnie."""
        for persona in [FAMILY_PERSONA, URBAN_PERSONA, INVESTOR_PERSONA]:
            for category, weight in persona.category_weights.items():
                with self.subTest(persona=persona.type.value, category=category):
                    self.assertGreaterEqual(weight, 0)
    
    def test_normalized_weights_sum_to_one(self):
        """Znormalizowane wagi sumują się do 1.0 (z tolerancją)."""
        for persona in [FAMILY_PERSONA, URBAN_PERSONA, INVESTOR_PERSONA]:
            weights = persona.get_normalized_weights()
            total = sum(weights.values())
            
            with self.subTest(persona=persona.type.value):
                self.assertAlmostEqual(total, 1.0, places=5)


class TestPersonaRegistry(TestCase):
    """Testy dla registry i factory functions."""
    
    def test_registry_contains_all_personas(self):
        """Registry zawiera wszystkie 3 profile."""
        self.assertEqual(len(PERSONA_REGISTRY), 3)
        self.assertIn(PersonaType.FAMILY, PERSONA_REGISTRY)
        self.assertIn(PersonaType.URBAN, PERSONA_REGISTRY)
        self.assertIn(PersonaType.INVESTOR, PERSONA_REGISTRY)
    
    def test_get_persona_returns_correct_type(self):
        """get_persona zwraca poprawny profil."""
        family = get_persona(PersonaType.FAMILY)
        self.assertEqual(family.type, PersonaType.FAMILY)
        
        urban = get_persona(PersonaType.URBAN)
        self.assertEqual(urban.type, PersonaType.URBAN)
        
        investor = get_persona(PersonaType.INVESTOR)
        self.assertEqual(investor.type, PersonaType.INVESTOR)
    
    def test_get_persona_by_string(self):
        """get_persona_by_string działa poprawnie."""
        self.assertEqual(get_persona_by_string('family').type, PersonaType.FAMILY)
        self.assertEqual(get_persona_by_string('urban').type, PersonaType.URBAN)
        self.assertEqual(get_persona_by_string('investor').type, PersonaType.INVESTOR)
    
    def test_get_persona_by_string_case_insensitive(self):
        """get_persona_by_string jest case-insensitive."""
        self.assertEqual(get_persona_by_string('FAMILY').type, PersonaType.FAMILY)
        self.assertEqual(get_persona_by_string('Family').type, PersonaType.FAMILY)
    
    def test_get_persona_by_string_invalid_returns_default(self):
        """get_persona_by_string zwraca FAMILY dla nieprawidłowych wartości."""
        self.assertEqual(get_persona_by_string('invalid').type, PersonaType.FAMILY)
    
    def test_get_all_personas(self):
        """get_all_personas zwraca listę wszystkich profili."""
        personas = get_all_personas()
        self.assertEqual(len(personas), 3)
        types = {p.type for p in personas}
        self.assertEqual(types, {PersonaType.FAMILY, PersonaType.URBAN, PersonaType.INVESTOR})


class TestFamilyPersonaWeights(TestCase):
    """Testy specyficzne dla profilu FAMILY."""
    
    def test_education_has_high_weight(self):
        """Edukacja ma wysoką wagę dla rodzin."""
        weights = FAMILY_PERSONA.get_normalized_weights()
        # Edukacja powinna być w top 3
        sorted_weights = sorted(weights.items(), key=lambda x: x[1], reverse=True)
        top_3_categories = [cat for cat, _ in sorted_weights[:3]]
        
        self.assertIn('education', top_3_categories)
    
    def test_nature_has_high_weight(self):
        """Zieleń ma wysoką wagę dla rodzin."""
        weights = FAMILY_PERSONA.get_normalized_weights()
        sorted_weights = sorted(weights.items(), key=lambda x: x[1], reverse=True)
        top_3_categories = [cat for cat, _ in sorted_weights[:3]]
        
        self.assertIn('nature', top_3_categories)
    
    def test_quiet_score_weight_is_high(self):
        """Quiet Score jest ważny dla rodzin."""
        self.assertGreaterEqual(FAMILY_PERSONA.quiet_score_config.weight, 1.0)
    
    def test_education_is_critical(self):
        """Edukacja jest kategorią krytyczną."""
        self.assertIn('education', FAMILY_PERSONA.critical_categories)
    
    def test_education_is_dealbreaker(self):
        """Niska edukacja jest dealbreaker."""
        self.assertIn('education', FAMILY_PERSONA.dealbreaker_categories)


class TestUrbanPersonaWeights(TestCase):
    """Testy specyficzne dla profilu URBAN."""
    
    def test_transport_has_highest_weight(self):
        """Transport ma najwyższą wagę dla singli."""
        weights = URBAN_PERSONA.get_normalized_weights()
        max_category = max(weights.items(), key=lambda x: x[1])[0]
        
        self.assertEqual(max_category, 'transport')
    
    def test_food_has_high_weight(self):
        """Gastronomia ma wysoką wagę dla singli."""
        weights = URBAN_PERSONA.get_normalized_weights()
        sorted_weights = sorted(weights.items(), key=lambda x: x[1], reverse=True)
        top_3_categories = [cat for cat, _ in sorted_weights[:3]]
        
        self.assertIn('food', top_3_categories)
    
    def test_quiet_score_weight_is_low(self):
        """Quiet Score jest mniej ważny dla singli."""
        self.assertLess(URBAN_PERSONA.quiet_score_config.weight, 1.0)
    
    def test_education_has_low_weight(self):
        """Edukacja ma niską wagę dla singli."""
        urban_edu = URBAN_PERSONA.category_weights['education']
        family_edu = FAMILY_PERSONA.category_weights['education']
        
        self.assertLess(urban_edu, family_edu)


class TestInvestorPersonaWeights(TestCase):
    """Testy specyficzne dla profilu INVESTOR."""
    
    def test_transport_has_high_weight(self):
        """Transport ma wysoką wagę dla inwestorów (płynność)."""
        weights = INVESTOR_PERSONA.get_normalized_weights()
        sorted_weights = sorted(weights.items(), key=lambda x: x[1], reverse=True)
        top_2_categories = [cat for cat, _ in sorted_weights[:2]]
        
        self.assertIn('transport', top_2_categories)
    
    def test_education_higher_than_urban(self):
        """Edukacja ważniejsza dla inwestora niż dla singla (studenci)."""
        investor_edu = INVESTOR_PERSONA.category_weights['education']
        urban_edu = URBAN_PERSONA.category_weights['education']
        
        self.assertGreater(investor_edu, urban_edu)
    
    def test_verdict_thresholds_are_pragmatic(self):
        """Progi werdyktu są pragmatyczne (niższe niż dla rodzin)."""
        investor_recommended = INVESTOR_PERSONA.verdict_thresholds.recommended
        family_recommended = FAMILY_PERSONA.verdict_thresholds.recommended
        
        self.assertLess(investor_recommended, family_recommended)


class TestPersonaConfigSerialization(TestCase):
    """Testy serializacji PersonaConfig."""
    
    def test_to_dict_returns_dict(self):
        """to_dict zwraca słownik."""
        result = FAMILY_PERSONA.to_dict()
        self.assertIsInstance(result, dict)
    
    def test_to_dict_contains_required_keys(self):
        """to_dict zawiera wymagane klucze."""
        result = FAMILY_PERSONA.to_dict()
        
        required_keys = [
            'type', 'name', 'description', 'emoji',
            'category_weights', 'quiet_score_weight',
            'quiet_score_threshold', 'verdict_thresholds',
            'critical_categories'
        ]
        
        for key in required_keys:
            self.assertIn(key, result)
    
    def test_to_dict_type_is_string(self):
        """to_dict zwraca type jako string (nie enum)."""
        result = FAMILY_PERSONA.to_dict()
        self.assertIsInstance(result['type'], str)
        self.assertEqual(result['type'], 'family')
