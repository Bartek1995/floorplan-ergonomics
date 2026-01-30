"""
Moduł parserów ogłoszeń nieruchomości.
Każdy provider obsługuje jeden serwis (Otodom, OLX, itp.).
"""
from .base import BaseProvider, PropertyData, ListingData
from .otodom import OtodomProvider
from .olx import OlxProvider
from .registry import ProviderRegistry, get_provider_for_url

__all__ = [
    'BaseProvider',
    'PropertyData',
    'ListingData',  # Alias for backward compatibility
    'OtodomProvider',
    'OlxProvider',
    'ProviderRegistry',
    'get_provider_for_url',
]
