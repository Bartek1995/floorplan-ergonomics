"""
Scoring package - Silnik scoringu z dynamicznymi wagami.
"""
from .engine import ScoringEngine, ScoringResult
from .verdict import VerdictGenerator, Verdict, VerdictLevel

__all__ = [
    'ScoringEngine',
    'ScoringResult',
    'VerdictGenerator',
    'Verdict',
    'VerdictLevel',
]
