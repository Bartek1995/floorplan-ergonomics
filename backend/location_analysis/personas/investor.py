"""
Profil: Inwestor / ROI (INVESTOR)

Priorytety:
- Płynność najmu (łatwo wynająć)
- Bliskość uczelni (studenci = stały popyt)
- Węzły komunikacyjne
- Biurowce i centra biznesowe

Dealbreakers:
- Brak transportu (niska płynność)
- Bardzo głośna okolica (narzekania najemców)
"""
from .base import (
    PersonaConfig,
    PersonaType,
    QuietScoreConfig,
    VerdictThresholds,
    NarrativeTemplates,
)


INVESTOR_PERSONA = PersonaConfig(
    type=PersonaType.INVESTOR,
    name="Inwestor / ROI",
    description="Płynność najmu, studenci, biurowce, transport",
    emoji="📈",
    
    # Wagi kategorii - transport i edukacja (uczelnie) krytyczne
    category_weights={
        'shops': 12,       # Podstawowe
        'transport': 30,   # ⬆️ KRYTYCZNE - płynność!
        'education': 25,   # ⬆️ WAŻNE - uczelnie = studenci
        'health': 8,       # Podstawowe
        'nature': 8,       # Miłe bonus
        'leisure': 12,     # Siłownie, rozrywka
        'food': 15,        # Restauracje dla najemców
        'finance': 5,      # Banki blisko
    },
    
    # Quiet Score - umiarkowanie ważny
    quiet_score_config=QuietScoreConfig(
        weight=0.8,
        threshold=35,
        bonus_above_threshold=0.08,
        penalty_below_threshold=0.15,
    ),
    
    # Progi werdyktu - pragmatyczne
    verdict_thresholds=VerdictThresholds(
        recommended=62,
        conditional=38,
    ),
    
    # Szablony narracji
    narrative_templates=NarrativeTemplates(
        # Pozytywne
        high_education="🎓 Blisko uczelni - doskonały potencjał najmu dla studentów!",
        high_transport="🚇 Węzeł komunikacyjny - bardzo wysoka płynność najmu. Szybko znajdziesz najemcę.",
        high_nature="🌳 Zieleń podnosi atrakcyjność dla najemców premium",
        high_food="🍽️ Dużo restauracji - atrakcyjne dla młodych profesjonalistów",
        high_health="🏥 Blisko przychodni - plus dla długoterminowych najemców",
        high_quiet="🔇 Cicha okolica - możesz liczyć na mniejszą rotację najemców",
        
        # Negatywne
        low_education="📉 Daleko od uczelni - mniejszy popyt ze strony studentów",
        low_transport="🚫 Słaba komunikacja = niska płynność najmu. DUŻE RYZYKO pustostanu!",
        low_nature="🏙️ Brak zieleni może obniżyć czynsz",
        low_quiet="🔊 Głośna okolica - spodziewaj się narzekań i wyższej rotacji",
        low_health="",
        
        # Werdykty
        verdict_recommended="✅ Doskonała lokalizacja inwestycyjna! Wysoka płynność najmu i stabilny popyt.",
        verdict_conditional="⚠️ Akceptowalna inwestycja, ale nie premium. Sprawdź ceny najmu w okolicy.",
        verdict_not_recommended="❌ Słaba lokalizacja pod wynajem. Ryzyko pustostanu i niskiego czynszu.",
    ),
    
    # Kategorie krytyczne
    critical_categories=['transport'],
    
    # Dealbreakers
    dealbreaker_categories={
        'transport': 18,  # Brak transportu = wysoka ryzyko
    },
)
