"""
Profil: Rodzina z dziećmi (FAMILY)

Priorytety:
- Bezpieczeństwo i cisza
- Dostęp do edukacji (szkoły, przedszkola)
- Zieleń i tereny rekreacyjne
- Służba zdrowia w pobliżu

Dealbreakers:
- Głośna okolica (Quiet Score < 40)
- Brak szkół/przedszkoli w zasięgu
"""
from .base import (
    PersonaConfig,
    PersonaType,
    QuietScoreConfig,
    VerdictThresholds,
    NarrativeTemplates,
)


FAMILY_PERSONA = PersonaConfig(
    type=PersonaType.FAMILY,
    name="Rodzina z dziećmi",
    description="Bezpieczeństwo, szkoły, parki, cisza",
    emoji="👨‍👩‍👧",
    
    # Wagi kategorii - edukacja i natura krytyczne
    category_weights={
        'shops': 15,       # Podstawowe zakupy
        'transport': 12,   # Mniej ważny (samochód)
        'education': 28,   # ⬆️ KRYTYCZNE - szkoły, przedszkola
        'health': 18,      # ⬆️ Ważne - pediatra, szpital
        'nature': 22,      # ⬆️ KRYTYCZNE - parki, place zabaw
        'leisure': 8,      # Sport dla dzieci
        'food': 5,         # Mniej istotne
        'finance': 2,      # Najmniej istotne
    },
    
    # Quiet Score - bardzo ważny dla rodzin
    quiet_score_config=QuietScoreConfig(
        weight=1.5,              # Cisza ma duży wpływ
        threshold=50,            # Minimum akceptowalne
        bonus_above_threshold=0.15,  # +15% za bardzo cichą okolicę
        penalty_below_threshold=0.25, # -25% za głośną
    ),
    
    # Progi werdyktu - wyższe wymagania
    verdict_thresholds=VerdictThresholds(
        recommended=72,   # Wysoki próg
        conditional=48,
    ),
    
    # Szablony narracji
    narrative_templates=NarrativeTemplates(
        # Pozytywne
        high_education="🎓 Doskonały dostęp do szkół i przedszkoli w zasięgu spaceru",
        high_transport="🚌 Dobra komunikacja - dzieci mogą samodzielnie dojeżdżać do szkoły",
        high_nature="🌳 Idealna okolica dla rodzin - parki i place zabaw w pobliżu",
        high_food="🍽️ Restauracje przyjazne rodzinom w okolicy",
        high_health="🏥 Blisko do pediatry i przychodni",
        high_quiet="🔇 Spokojna okolica - idealna dla dzieci",
        
        # Negatywne
        low_education="⚠️ Brak szkół i przedszkoli w zasięgu spaceru - wymaga dojazdów",
        low_transport="⚠️ Słaba komunikacja - konieczny samochód",
        low_nature="⚠️ Brak parków i terenów zielonych - mało miejsca do zabawy",
        low_quiet="🚨 Hałaśliwa okolica - może przeszkadzać dzieciom i naruszać sen",
        low_health="⚠️ Daleko do przychodni - w nagłych wypadkach problem",
        
        # Werdykty
        verdict_recommended="✅ Lokalizacja idealna dla rodzin z dziećmi. Dobra infrastruktura edukacyjna, zieleń i spokój.",
        verdict_conditional="⚠️ Lokalizacja akceptowalna dla rodzin, ale wymaga kompromisów. Sprawdź szczegóły.",
        verdict_not_recommended="❌ Lokalizacja nieodpowiednia dla rodzin z dziećmi. Brakuje kluczowej infrastruktury lub jest zbyt głośno.",
    ),
    
    # Kategorie krytyczne - brak = automatyczna degradacja
    critical_categories=['education', 'nature'],
    
    # Dealbreakers - poniżej tych wartości = automatycznie NIEPOLECANE
    dealbreaker_categories={
        'education': 25,  # Brak szkół = niepołecane
    },
)
