"""
Silnik Scoringu z dynamicznymi wagami na podstawie profilu użytkownika.

Ten moduł przelicza surowe score'y kategorii POI na końcowy wynik
uwzględniający specyficzne priorytety profilu (Persona).
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import logging

from ..personas.base import PersonaConfig

logger = logging.getLogger(__name__)


@dataclass
class CategoryAnalysis:
    """Analiza pojedynczej kategorii."""
    category: str
    raw_score: float        # Surowy score (0-100)
    weight: float           # Znormalizowana waga (0-1)
    weighted_score: float   # raw_score * weight
    is_critical: bool       # Czy kategoria krytyczna dla profilu
    is_dealbreaker: bool    # Czy score poniżej dealbreaker threshold
    rating: str             # 'excellent', 'good', 'poor', 'critical'


@dataclass
class ScoringResult:
    """
    Wynik scoringu z pełnym breakdown'em.
    
    Atrybuty:
        total_score: Końcowy score (0-100)
        base_score: Score przed modyfikatorami
        quiet_modifier: Modyfikator Quiet Score
        category_breakdown: Szczegóły per kategoria
        persona_type: Użyty profil
        warnings: Ostrzeżenia (np. dealbreakers)
        strengths: Mocne strony (score > 70)
        weaknesses: Słabe strony (score < 30)
    """
    total_score: float
    base_score: float
    quiet_modifier: float
    quiet_score: float
    category_breakdown: List[CategoryAnalysis] = field(default_factory=list)
    persona_type: str = ""
    warnings: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    has_dealbreaker: bool = False
    
    def to_dict(self) -> dict:
        """Serializacja do słownika."""
        return {
            'total_score': round(self.total_score, 1),
            'base_score': round(self.base_score, 1),
            'quiet_modifier': round(self.quiet_modifier, 3),
            'quiet_score': round(self.quiet_score, 1),
            'persona_type': self.persona_type,
            'has_dealbreaker': self.has_dealbreaker,
            'category_breakdown': [
                {
                    'category': c.category,
                    'raw_score': round(c.raw_score, 1),
                    'weight': round(c.weight, 3),
                    'weighted_score': round(c.weighted_score, 2),
                    'is_critical': c.is_critical,
                    'rating': c.rating,
                }
                for c in self.category_breakdown
            ],
            'warnings': self.warnings,
            'strengths': self.strengths,
            'weaknesses': self.weaknesses,
        }


class ScoringEngine:
    """
    Silnik scoringu z dynamicznymi wagami.
    
    Proces obliczania:
    1. Normalizacja wag profilu do sumy = 1.0
    2. Obliczenie base_score jako ważonej średniej
    3. Detekcja dealbreakers (automatyczna degradacja)
    4. Obliczenie modyfikatora Quiet Score
    5. Aplikacja modyfikatora: total_score = base_score * quiet_modifier
    6. Ekstrakcja mocnych/słabych stron
    """
    
    # Progi dla oceny kategorii
    RATING_THRESHOLDS = {
        'excellent': 75,
        'good': 50,
        'poor': 25,
        # < 25 = 'critical'
    }
    
    # Nazwy kategorii (do raportów)
    CATEGORY_NAMES = {
        'shops': 'Sklepy',
        'transport': 'Transport publiczny',
        'education': 'Edukacja',
        'health': 'Zdrowie',
        'nature': 'Zieleń i rekreacja',
        'leisure': 'Sport i rozrywka',
        'food': 'Gastronomia',
        'finance': 'Banki i finanse',
    }
    
    def __init__(self, persona: PersonaConfig):
        """
        Inicjalizuje silnik dla danego profilu.
        
        Args:
            persona: Konfiguracja profilu użytkownika
        """
        self.persona = persona
        self.weights = persona.get_normalized_weights()
        
        logger.debug(
            f"ScoringEngine initialized for {persona.type.value}: "
            f"weights={self.weights}"
        )
    
    def calculate(
        self,
        category_scores: Dict[str, float],
        quiet_score: float,
    ) -> ScoringResult:
        """
        Oblicza końcowy score na podstawie profilu.
        
        Args:
            category_scores: Słownik {kategoria: score 0-100}
            quiet_score: Wynik Quiet Score (0-100)
        
        Returns:
            ScoringResult z pełnym breakdown'em
        """
        # 1. Analiza kategorii
        breakdown = []
        dealbreakers = []
        
        for category, weight in self.weights.items():
            raw_score = category_scores.get(category, 0)
            is_critical = self.persona.is_critical_category(category)
            is_dealbreaker = self.persona.is_dealbreaker(category, raw_score)
            
            if is_dealbreaker:
                dealbreakers.append(category)
            
            rating = self._get_rating(raw_score)
            
            breakdown.append(CategoryAnalysis(
                category=category,
                raw_score=raw_score,
                weight=weight,
                weighted_score=raw_score * weight,
                is_critical=is_critical,
                is_dealbreaker=is_dealbreaker,
                rating=rating,
            ))
        
        # 2. Base score (ważona średnia)
        base_score = sum(c.weighted_score for c in breakdown)
        
        # 3. Quiet modifier
        quiet_modifier = self._calculate_quiet_modifier(quiet_score)
        
        # 4. Total score
        total_score = base_score * quiet_modifier
        
        # 5. Dealbreaker penalty
        has_dealbreaker = len(dealbreakers) > 0
        if has_dealbreaker:
            # Dealbreaker ogranicza max score do 40
            total_score = min(total_score, 40)
        
        # 6. Clamp to 0-100
        total_score = max(0, min(100, total_score))
        
        # 7. Extract strengths & weaknesses
        strengths, weaknesses = self._extract_highlights(breakdown, quiet_score)
        
        # 8. Generate warnings
        warnings = self._generate_warnings(breakdown, quiet_score, dealbreakers)
        
        return ScoringResult(
            total_score=total_score,
            base_score=base_score,
            quiet_modifier=quiet_modifier,
            quiet_score=quiet_score,
            category_breakdown=breakdown,
            persona_type=self.persona.type.value,
            warnings=warnings,
            strengths=strengths,
            weaknesses=weaknesses,
            has_dealbreaker=has_dealbreaker,
        )
    
    def recalculate_with_custom_weights(
        self,
        category_scores: Dict[str, float],
        quiet_score: float,
        custom_weights: Dict[str, int],
    ) -> ScoringResult:
        """
        Przelicza score z niestandardowymi wagami (dla suwaków UI).
        
        Args:
            category_scores: Słownik {kategoria: score 0-100}
            quiet_score: Wynik Quiet Score
            custom_weights: Niestandardowe wagi (0-100)
        
        Returns:
            ScoringResult z custom wagami
        """
        # Normalizacja custom wag
        total = sum(custom_weights.values())
        if total == 0:
            custom_normalized = {k: 0.0 for k in custom_weights}
        else:
            custom_normalized = {k: v / total for k, v in custom_weights.items()}
        
        # Tymczasowa podmiana wag
        original_weights = self.weights
        self.weights = custom_normalized
        
        try:
            result = self.calculate(category_scores, quiet_score)
            result.persona_type = f"{self.persona.type.value}_custom"
            return result
        finally:
            # Przywróć oryginalne wagi
            self.weights = original_weights
    
    def _calculate_quiet_modifier(self, quiet_score: float) -> float:
        """
        Oblicza modyfikator na podstawie Quiet Score i profilu.
        
        Returns:
            Modyfikator (0.7 - 1.15)
        """
        config = self.persona.quiet_score_config
        threshold = config.threshold
        
        if quiet_score >= threshold:
            # Bonus za ciszę powyżej progu
            excess = quiet_score - threshold
            bonus = (excess / 100) * config.bonus_above_threshold
            return min(1.15, 1.0 + bonus)
        else:
            # Kara za hałas poniżej progu
            deficit = threshold - quiet_score
            penalty = (deficit / 100) * config.penalty_below_threshold
            return max(0.7, 1.0 - penalty)
    
    def _get_rating(self, score: float) -> str:
        """Zwraca tekstową ocenę dla score'u."""
        if score >= self.RATING_THRESHOLDS['excellent']:
            return 'excellent'
        elif score >= self.RATING_THRESHOLDS['good']:
            return 'good'
        elif score >= self.RATING_THRESHOLDS['poor']:
            return 'poor'
        return 'critical'
    
    def _extract_highlights(
        self,
        breakdown: List[CategoryAnalysis],
        quiet_score: float,
    ) -> Tuple[List[str], List[str]]:
        """Ekstrahuje mocne i słabe strony."""
        strengths = []
        weaknesses = []
        
        templates = self.persona.narrative_templates
        
        # Kategorie
        for cat in breakdown:
            name = self.CATEGORY_NAMES.get(cat.category, cat.category)
            
            if cat.raw_score >= 70:
                # Sprawdź czy jest custom template
                template_key = f"high_{cat.category}"
                template = getattr(templates, template_key, None)
                if template:
                    strengths.append(template)
                else:
                    strengths.append(f"✅ {name}: doskonały dostęp")
            
            elif cat.raw_score <= 30 and cat.is_critical:
                template_key = f"low_{cat.category}"
                template = getattr(templates, template_key, None)
                if template:
                    weaknesses.append(template)
                else:
                    weaknesses.append(f"⚠️ {name}: słaby dostęp")
        
        # Quiet Score
        if quiet_score >= 70:
            if templates.high_quiet:
                strengths.append(templates.high_quiet)
        elif quiet_score <= 35:
            if templates.low_quiet:
                weaknesses.append(templates.low_quiet)
        
        return strengths[:4], weaknesses[:4]  # Max 4 każdy
    
    def _generate_warnings(
        self,
        breakdown: List[CategoryAnalysis],
        quiet_score: float,
        dealbreakers: List[str],
    ) -> List[str]:
        """Generuje ostrzeżenia."""
        warnings = []
        
        # Dealbreakers
        for cat in dealbreakers:
            name = self.CATEGORY_NAMES.get(cat, cat)
            warnings.append(
                f"🚨 DEALBREAKER: {name} poniżej akceptowalnego minimum dla Twojego profilu!"
            )
        
        # Quiet Score poniżej progu
        threshold = self.persona.quiet_score_config.threshold
        if quiet_score < threshold:
            warnings.append(
                f"⚠️ Quiet Score ({quiet_score:.0f}) poniżej progu ({threshold}) dla Twojego profilu."
            )
        
        # Krytyczne kategorie z niskim score
        for cat in breakdown:
            if cat.is_critical and cat.raw_score < 40 and cat.category not in dealbreakers:
                name = self.CATEGORY_NAMES.get(cat.category, cat.category)
                warnings.append(
                    f"⚠️ {name} jest krytyczne dla Twojego profilu, ale ma niski score ({cat.raw_score:.0f})."
                )
        
        return warnings
