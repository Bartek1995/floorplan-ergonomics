"""
Bazowe klasy i typy dla systemu profili użytkownika (Personas).

System Personas pozwala na dynamiczne dostosowanie scoringu lokalizacji
do potrzeb różnych grup użytkowników (rodziny, single, inwestorzy).
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class PersonaType(str, Enum):
    """
    Typy dostępnych profili użytkownika.
    
    Każdy typ reprezentuje inny zestaw priorytetów przy ocenie lokalizacji:
    - FAMILY: Bezpieczeństwo, edukacja, zieleń, cisza
    - URBAN: Transport, gastronomia, życie nocne
    - INVESTOR: Płynność najmu, ROI, studenci
    """
    FAMILY = "family"
    URBAN = "urban"
    INVESTOR = "investor"
    
    @classmethod
    def from_string(cls, value: str) -> 'PersonaType':
        """Konwertuje string na PersonaType (case-insensitive)."""
        try:
            return cls(value.lower())
        except ValueError:
            return cls.FAMILY  # Default fallback


@dataclass
class CategoryWeight:
    """Waga kategorii z dodatkowymi metadanymi."""
    weight: int  # 0-100
    importance: str  # 'critical', 'high', 'medium', 'low'
    description: str


@dataclass
class VerdictThresholds:
    """Progi dla generowania werdyktu decyzyjnego."""
    recommended: int  # Score >= tego = POLECANE
    conditional: int  # Score >= tego = WARUNKOWO
    # Score < conditional = NIEPOLECANE
    
    def get_level(self, score: float) -> str:
        """Zwraca poziom werdyktu na podstawie score'u."""
        if score >= self.recommended:
            return 'recommended'
        elif score >= self.conditional:
            return 'conditional'
        return 'not_recommended'


@dataclass
class NarrativeTemplates:
    """Szablony narracji dla różnych sytuacji."""
    # Pozytywne
    high_education: str = ""
    high_transport: str = ""
    high_nature: str = ""
    high_food: str = ""
    high_health: str = ""
    high_quiet: str = ""
    
    # Negatywne
    low_education: str = ""
    low_transport: str = ""
    low_nature: str = ""
    low_quiet: str = ""
    low_health: str = ""
    
    # Werdykty
    verdict_recommended: str = ""
    verdict_conditional: str = ""
    verdict_not_recommended: str = ""


@dataclass
class QuietScoreConfig:
    """Konfiguracja Quiet Score dla profilu."""
    weight: float  # Multiplikator wpływu (0.0-2.0)
    threshold: int  # Minimalny akceptowalny Quiet Score
    bonus_above_threshold: float  # Bonus za przekroczenie progu
    penalty_below_threshold: float  # Kara za niedosięgnięcie progu


@dataclass
class PersonaConfig:
    """
    Pełna konfiguracja profilu użytkownika.
    
    Atrybuty:
        type: Typ profilu (FAMILY, URBAN, INVESTOR)
        name: Nazwa wyświetlana (np. "Rodzina z dziećmi")
        description: Krótki opis priorytetów
        emoji: Emoji do UI
        category_weights: Wagi kategorii POI (suma nie musi być 100)
        quiet_score_config: Konfiguracja wpływu Quiet Score
        verdict_thresholds: Progi dla werdyktu decyzyjnego
        narrative_templates: Szablony tekstów
        critical_categories: Kategorie które MUSZĄ mieć wysoki score
        dealbreaker_categories: Kategorie które przy niskim score = NIEPOLECANE
    """
    type: PersonaType
    name: str
    description: str
    emoji: str
    
    # Wagi kategorii (0-100)
    category_weights: Dict[str, int]
    
    # Quiet Score
    quiet_score_config: QuietScoreConfig
    
    # Werdykt
    verdict_thresholds: VerdictThresholds
    
    # Narracja
    narrative_templates: NarrativeTemplates
    
    # Krytyczne kategorie (brak = automatyczna degradacja werdyktu)
    critical_categories: List[str] = field(default_factory=list)
    
    # Dealbreakers (niski score = automatycznie NIEPOLECANE)
    dealbreaker_categories: Dict[str, int] = field(default_factory=dict)
    
    def get_normalized_weights(self) -> Dict[str, float]:
        """Zwraca wagi znormalizowane do sumy = 1.0"""
        total = sum(self.category_weights.values())
        if total == 0:
            return {k: 0.0 for k in self.category_weights}
        return {k: v / total for k, v in self.category_weights.items()}
    
    def is_critical_category(self, category: str) -> bool:
        """Sprawdza czy kategoria jest krytyczna dla tego profilu."""
        return category in self.critical_categories
    
    def is_dealbreaker(self, category: str, score: float) -> bool:
        """Sprawdza czy niski score w kategorii to dealbreaker."""
        threshold = self.dealbreaker_categories.get(category)
        if threshold is None:
            return False
        return score < threshold
    
    def to_dict(self) -> dict:
        """Serializacja do słownika (dla API response)."""
        return {
            'type': self.type.value,
            'name': self.name,
            'description': self.description,
            'emoji': self.emoji,
            'category_weights': self.category_weights,
            'quiet_score_weight': self.quiet_score_config.weight,
            'quiet_score_threshold': self.quiet_score_config.threshold,
            'verdict_thresholds': {
                'recommended': self.verdict_thresholds.recommended,
                'conditional': self.verdict_thresholds.conditional,
            },
            'critical_categories': self.critical_categories,
        }
