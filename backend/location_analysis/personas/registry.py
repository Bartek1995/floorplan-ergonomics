"""
Rejestr i fabryka profili użytkownika (Personas).

Centralny punkt dostępu do wszystkich zdefiniowanych profili.
"""
from typing import Dict, List, Optional

from .base import PersonaConfig, PersonaType
from .family import FAMILY_PERSONA
from .urban import URBAN_PERSONA
from .investor import INVESTOR_PERSONA


# Rejestr wszystkich dostępnych profili
PERSONA_REGISTRY: Dict[PersonaType, PersonaConfig] = {
    PersonaType.FAMILY: FAMILY_PERSONA,
    PersonaType.URBAN: URBAN_PERSONA,
    PersonaType.INVESTOR: INVESTOR_PERSONA,
}

# Domyślny profil
DEFAULT_PERSONA = PersonaType.FAMILY


def get_persona(persona_type: PersonaType) -> PersonaConfig:
    """
    Pobiera konfigurację profilu na podstawie typu.
    
    Args:
        persona_type: Typ profilu (PersonaType enum)
    
    Returns:
        PersonaConfig dla danego typu
    
    Raises:
        KeyError: Jeśli profil nie istnieje (nie powinno się zdarzyć)
    """
    return PERSONA_REGISTRY[persona_type]


def get_persona_by_string(persona_str: str) -> PersonaConfig:
    """
    Pobiera profil na podstawie stringa (case-insensitive).
    
    Args:
        persona_str: String z nazwą profilu ('family', 'urban', 'investor')
    
    Returns:
        PersonaConfig (domyślnie FAMILY jeśli nieznany)
    """
    try:
        persona_type = PersonaType(persona_str.lower())
    except ValueError:
        persona_type = DEFAULT_PERSONA
    
    return PERSONA_REGISTRY[persona_type]


def get_all_personas() -> List[PersonaConfig]:
    """
    Zwraca listę wszystkich dostępnych profili.
    
    Returns:
        Lista PersonaConfig
    """
    return list(PERSONA_REGISTRY.values())


def get_persona_choices() -> List[tuple]:
    """
    Zwraca choices dla Django/DRF ChoiceField.
    
    Returns:
        Lista tuple (value, label)
    """
    return [
        (p.type.value, f"{p.emoji} {p.name}")
        for p in PERSONA_REGISTRY.values()
    ]


def get_personas_summary() -> List[dict]:
    """
    Zwraca podsumowanie wszystkich profili (dla API).
    
    Returns:
        Lista słowników z podstawowymi info o profilach
    """
    return [
        {
            'type': p.type.value,
            'name': p.name,
            'description': p.description,
            'emoji': p.emoji,
        }
        for p in PERSONA_REGISTRY.values()
    ]
