"""
Generator werdyktu decyzyjnego.

Przekształca wynik scoringu w jednoznaczną rekomendację:
- ✅ Polecane
- ⚠️ Warunkowo polecane
- ❌ Niepolecane
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
import logging

from ..personas.base import PersonaConfig
from .engine import ScoringResult

logger = logging.getLogger(__name__)


class VerdictLevel(str, Enum):
    """Poziomy werdyktu."""
    RECOMMENDED = "recommended"
    CONDITIONAL = "conditional"
    NOT_RECOMMENDED = "not_recommended"


@dataclass
class Verdict:
    """
    Werdykt decyzyjny.
    
    Atrybuty:
        level: Poziom (RECOMMENDED, CONDITIONAL, NOT_RECOMMENDED)
        label: Etykieta tekstowa ("Polecane", etc.)
        emoji: Emoji dla UI
        explanation: Główne wyjaśnienie
        key_factors: Lista kluczowych czynników
        score: Końcowy score
        confidence: Pewność werdyktu (0-100%)
        persona_match: Jak dobrze lokalizacja pasuje do profilu
    """
    level: VerdictLevel
    label: str
    emoji: str
    explanation: str
    key_factors: List[str] = field(default_factory=list)
    score: float = 0.0
    confidence: int = 0  # 0-100%
    persona_match: str = ""  # "excellent", "good", "poor", "mismatch"
    
    def to_dict(self) -> dict:
        """Serializacja do słownika."""
        return {
            'level': self.level.value,
            'label': self.label,
            'emoji': self.emoji,
            'explanation': self.explanation,
            'key_factors': self.key_factors,
            'score': round(self.score, 1),
            'confidence': self.confidence,
            'persona_match': self.persona_match,
        }


class VerdictGenerator:
    """
    Generuje werdykt decyzyjny.
    
    Łączy wynik scoringu z profilem użytkownika, aby wydać
    jednoznaczną rekomendację z uzasadnieniem.
    """
    
    # Konfiguracja poziomów werdyktu
    VERDICT_CONFIG = {
        VerdictLevel.RECOMMENDED: {
            'label': 'Polecane',
            'emoji': '✅',
            'color': '#10B981',  # emerald-500
        },
        VerdictLevel.CONDITIONAL: {
            'label': 'Warunkowo polecane',
            'emoji': '⚠️',
            'color': '#F59E0B',  # amber-500
        },
        VerdictLevel.NOT_RECOMMENDED: {
            'label': 'Niepolecane',
            'emoji': '❌',
            'color': '#EF4444',  # red-500
        },
    }
    
    # Progi pewności (confidence)
    CONFIDENCE_THRESHOLDS = {
        'very_high': 90,   # Score bardzo daleko od progów
        'high': 75,        # Score wyraźnie w jednej strefie
        'medium': 60,      # Score blisko progu
        'low': 40,         # Score bardzo blisko progu
    }
    
    def generate(
        self,
        scoring_result: ScoringResult,
        persona: PersonaConfig,
    ) -> Verdict:
        """
        Generuje werdykt na podstawie wyniku scoringu.
        
        Args:
            scoring_result: Wynik z ScoringEngine
            persona: Profil użytkownika
        
        Returns:
            Verdict z pełnym uzasadnieniem
        """
        score = scoring_result.total_score
        thresholds = persona.verdict_thresholds
        
        # 1. Ustal poziom werdyktu
        if scoring_result.has_dealbreaker:
            # Dealbreaker = automatycznie niepolecane
            level = VerdictLevel.NOT_RECOMMENDED
        elif score >= thresholds.recommended:
            level = VerdictLevel.RECOMMENDED
        elif score >= thresholds.conditional:
            level = VerdictLevel.CONDITIONAL
        else:
            level = VerdictLevel.NOT_RECOMMENDED
        
        # 2. Pobierz konfigurację poziomu
        config = self.VERDICT_CONFIG[level]
        
        # 3. Oblicz pewność (confidence)
        confidence = self._calculate_confidence(score, thresholds, scoring_result.has_dealbreaker)
        
        # 4. Określ persona_match
        persona_match = self._determine_persona_match(score, thresholds)
        
        # 5. Generuj wyjaśnienie
        explanation = self._generate_explanation(
            level, 
            scoring_result, 
            persona,
            confidence,
        )
        
        # 6. Wybierz kluczowe czynniki
        key_factors = self._extract_key_factors(scoring_result, persona, level)
        
        return Verdict(
            level=level,
            label=config['label'],
            emoji=config['emoji'],
            explanation=explanation,
            key_factors=key_factors,
            score=score,
            confidence=confidence,
            persona_match=persona_match,
        )
    
    def _calculate_confidence(
        self,
        score: float,
        thresholds,
        has_dealbreaker: bool,
    ) -> int:
        """Oblicza pewność werdyktu."""
        if has_dealbreaker:
            return 95  # Dealbreaker = wysoka pewność
        
        # Odległość od najbliższego progu
        dist_to_recommended = abs(score - thresholds.recommended)
        dist_to_conditional = abs(score - thresholds.conditional)
        min_distance = min(dist_to_recommended, dist_to_conditional)
        
        # Większa odległość = większa pewność
        if min_distance >= 20:
            return 90
        elif min_distance >= 15:
            return 80
        elif min_distance >= 10:
            return 70
        elif min_distance >= 5:
            return 55
        else:
            return 45  # Bardzo blisko progu
    
    def _determine_persona_match(self, score: float, thresholds) -> str:
        """Określa jak dobrze lokalizacja pasuje do profilu."""
        if score >= thresholds.recommended + 10:
            return 'excellent'
        elif score >= thresholds.recommended:
            return 'good'
        elif score >= thresholds.conditional:
            return 'acceptable'
        elif score >= thresholds.conditional - 10:
            return 'poor'
        return 'mismatch'
    
    def _generate_explanation(
        self,
        level: VerdictLevel,
        scoring_result: ScoringResult,
        persona: PersonaConfig,
        confidence: int,
    ) -> str:
        """Generuje główne wyjaśnienie werdyktu."""
        templates = persona.narrative_templates
        
        # Użyj szablonu z persona jeśli dostępny
        template_key = f"verdict_{level.value}"
        template = getattr(templates, template_key, None)
        
        if template:
            return template
        
        # Fallback - generuj dynamicznie
        score = scoring_result.total_score
        
        if level == VerdictLevel.RECOMMENDED:
            return (
                f"Lokalizacja uzyskała {score:.0f}/100 punktów dla Twojego profilu "
                f"({persona.emoji} {persona.name}). Spełnia główne kryteria "
                f"i jest rekomendowana do dalszej analizy."
            )
        elif level == VerdictLevel.CONDITIONAL:
            return (
                f"Lokalizacja uzyskała {score:.0f}/100 punktów dla Twojego profilu "
                f"({persona.emoji} {persona.name}). Są pewne kompromisy do rozważenia - "
                f"sprawdź szczegóły poniżej."
            )
        else:
            if scoring_result.has_dealbreaker:
                return (
                    f"Lokalizacja zawiera elementy dyskwalifikujące dla Twojego profilu "
                    f"({persona.emoji} {persona.name}). Nie jest rekomendowana."
                )
            return (
                f"Lokalizacja uzyskała tylko {score:.0f}/100 punktów dla Twojego profilu "
                f"({persona.emoji} {persona.name}). Nie spełnia kluczowych kryteriów."
            )
    
    def _extract_key_factors(
        self,
        scoring_result: ScoringResult,
        persona: PersonaConfig,
        level: VerdictLevel,
    ) -> List[str]:
        """Ekstrahuje kluczowe czynniki decyzyjne."""
        factors = []
        
        # Dodaj ostrzeżenia (dealbreakers)
        for warning in scoring_result.warnings[:2]:
            factors.append(warning)
        
        # Dodaj główne mocne strony (dla polecanych)
        if level == VerdictLevel.RECOMMENDED:
            for strength in scoring_result.strengths[:3]:
                factors.append(f"➕ {strength}" if not strength.startswith(('✅', '🎓', '🚇', '🌳')) else strength)
        
        # Dodaj główne słabości (dla niepolecanych)
        if level == VerdictLevel.NOT_RECOMMENDED:
            for weakness in scoring_result.weaknesses[:3]:
                factors.append(f"➖ {weakness}" if not weakness.startswith(('⚠️', '🚨', '🚫')) else weakness)
        
        # Dodaj info o Quiet Score jeśli istotny
        quiet = scoring_result.quiet_score
        quiet_threshold = persona.quiet_score_config.threshold
        
        if quiet >= 70 and persona.quiet_score_config.weight >= 1.0:
            factors.append(f"🔇 Cicha okolica (Quiet Score: {quiet:.0f}/100)")
        elif quiet < quiet_threshold and persona.quiet_score_config.weight >= 1.0:
            factors.append(f"🔊 Głośna okolica (Quiet Score: {quiet:.0f}/100, min. {quiet_threshold})")
        
        # Deduplikacja i limit
        seen = set()
        unique_factors = []
        for f in factors:
            # Normalizuj do porównania
            normalized = f.lower().replace('✅', '').replace('⚠️', '').strip()[:30]
            if normalized not in seen:
                seen.add(normalized)
                unique_factors.append(f)
        
        return unique_factors[:5]  # Max 5 czynników


def generate_verdict_for_analysis(
    category_scores: Dict[str, float],
    quiet_score: float,
    persona: PersonaConfig,
) -> Verdict:
    """
    Convenience function - generuje werdykt od zera.
    
    Args:
        category_scores: Słownik {kategoria: score}
        quiet_score: Quiet Score
        persona: Profil użytkownika
    
    Returns:
        Verdict
    """
    from .engine import ScoringEngine
    
    engine = ScoringEngine(persona)
    scoring_result = engine.calculate(category_scores, quiet_score)
    
    generator = VerdictGenerator()
    return generator.generate(scoring_result, persona)
