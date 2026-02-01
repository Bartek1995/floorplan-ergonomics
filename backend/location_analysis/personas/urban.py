"""
Profil: Singiel / City Life (URBAN)

Priorytety:
- Doskonała komunikacja (metro, tramwaj, autobusy)
- Życie nocne i gastronomia
- Bliskość centrum
- Siłownie i sport

Dealbreakers:
- Brak transportu publicznego
- Odcięcie od centrum
"""
from .base import (
    PersonaConfig,
    PersonaType,
    QuietScoreConfig,
    VerdictThresholds,
    NarrativeTemplates,
)


URBAN_PERSONA = PersonaConfig(
    type=PersonaType.URBAN,
    name="Singiel / City Life",
    description="Transport, gastronomia, życie nocne, centrum",
    emoji="💼",
    
    # Wagi kategorii - transport i gastro krytyczne
    category_weights={
        'shops': 18,       # Sklepy convenience
        'transport': 32,   # ⬆️ KRYTYCZNE - metro, tramwaj
        'education': 5,    # Mniej istotne
        'health': 8,       # Podstawowe
        'nature': 8,       # Park do joggingu
        'leisure': 15,     # ⬆️ Siłownie, kluby
        'food': 22,        # ⬆️ WAŻNE - restauracje, kawiarnie
        'finance': 7,      # Bankomaty, fintech
    },
    
    # Quiet Score - mniej ważny (miasto = szum)
    quiet_score_config=QuietScoreConfig(
        weight=0.5,              # Cisza mniej istotna
        threshold=25,            # Niski próg akceptacji
        bonus_above_threshold=0.05,
        penalty_below_threshold=0.1,
    ),
    
    # Progi werdyktu - umiarkowane
    verdict_thresholds=VerdictThresholds(
        recommended=65,
        conditional=42,
    ),
    
    # Szablony narracji
    narrative_templates=NarrativeTemplates(
        # Pozytywne
        high_education="📚 Blisko bibliotek i przestrzeni coworkingowych",
        high_transport="🚇 Świetna komunikacja - wszędzie szybko dojedziesz. Idealne bez samochodu.",
        high_nature="🌳 Park w pobliżu - dobre miejsce na jogging",
        high_food="🍕 Mnóstwo restauracji i kawiarni - nie musisz gotować!",
        high_health="💊 Apteki i przychodnie w zasięgu",
        high_quiet="🔇 Zaskakująco cicho jak na centrum - bonus!",
        
        # Negatywne
        low_education="",  # Nie istotne dla tego profilu
        low_transport="🚫 Słaba komunikacja - rozważ samochód lub rower. To duży minus!",
        low_nature="🏙️ Brak parków - typowo miejska okolica",
        low_quiet="🎉 Głośna okolica - idealne dla imprezowiczów, minus dla light-sleepers",
        low_health="⚠️ Daleko do apteki",
        
        # Werdykty
        verdict_recommended="✅ Idealna lokalizacja dla aktywnego singla. Życie nocne, transport i wszystko na wyciągnięcie ręki!",
        verdict_conditional="⚠️ Dobra lokalizacja miejska, ale nie idealna. Sprawdź komunikację.",
        verdict_not_recommended="❌ Słaba lokalizacja dla miejskiego stylu życia. Transport i usługi poniżej oczekiwań.",
    ),
    
    # Kategorie krytyczne
    critical_categories=['transport', 'food'],
    
    # Dealbreakers
    dealbreaker_categories={
        'transport': 20,  # Brak transportu = niepolecane
    },
)
