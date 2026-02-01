"""
Personas package - Profile użytkownika dla dynamicznego scoringu.
"""
from .base import PersonaType, PersonaConfig
from .registry import get_persona, get_persona_by_string, get_all_personas, PERSONA_REGISTRY

__all__ = [
    'PersonaType',
    'PersonaConfig', 
    'get_persona',
    'get_persona_by_string',
    'get_all_personas',
    'PERSONA_REGISTRY',
]

