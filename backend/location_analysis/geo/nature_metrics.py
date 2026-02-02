"""
Metryki pokrycia zielenią dla location intelligence.

Zamiast listy POI dla elementów landcover (grass, forest, meadow),
zbieramy metryki statystyczne używane do oceny "zieloności" lokalizacji.
"""
from dataclasses import dataclass, field
from typing import Dict, Set, Optional
import math


@dataclass
class NatureMetrics:
    """Metryki pokrycia zielenią w okolicy."""
    
    # Zliczenia per typ landcover
    green_landcover_counts: Dict[str, int] = field(default_factory=dict)
    
    # Typy zieleni które występują w okolicy
    green_types_present: Set[str] = field(default_factory=set)
    
    # Najbliższy element per typ (w metrach)
    nearest_distances: Dict[str, float] = field(default_factory=dict)
    
    # Łączna liczba elementów zieleni (land cover)
    total_green_elements: int = 0
    
    # Proxy gęstości (elementy / km²)
    green_density_proxy: float = 0.0
    
    # Woda
    water_present: bool = False
    nearest_water_m: Optional[float] = None
    water_types_present: Set[str] = field(default_factory=set)
    water_type_distances: Dict[str, float] = field(default_factory=dict)
    
    def add_landcover(self, landcover_type: str, distance_m: float) -> None:
        """Dodaje element landcover do metryk."""
        # Zlicz
        self.green_landcover_counts[landcover_type] = \
            self.green_landcover_counts.get(landcover_type, 0) + 1
        
        # Dodaj do typów obecnych
        self.green_types_present.add(landcover_type)
        
        # Inkrementuj łączną liczbę
        self.total_green_elements += 1
        
        # Aktualizuj nearest distance
        current_nearest = self.nearest_distances.get(landcover_type)
        if current_nearest is None or distance_m < current_nearest:
            self.nearest_distances[landcover_type] = round(distance_m)
    
    def add_water(self, distance_m: float, water_type: str = 'water') -> None:
        """Dodaje element wodny do metryk."""
        self.water_present = True
        self.water_types_present.add(water_type)
        
        # Aktualizuj najbliższą wodę ogólnie
        if self.nearest_water_m is None or distance_m < self.nearest_water_m:
            self.nearest_water_m = round(distance_m)
        
        # Aktualizuj per typ wody
        current = self.water_type_distances.get(water_type)
        if current is None or distance_m < current:
            self.water_type_distances[water_type] = round(distance_m)
    
    def add_park(self, distance_m: float) -> None:
        """Aktualizuje dystans do najbliższego parku."""
        current = self.nearest_distances.get('park')
        if current is None or distance_m < current:
            self.nearest_distances['park'] = round(distance_m)
    
    def calculate_density(self, radius_m: int) -> None:
        """Oblicza proxy gęstości na podstawie promienia."""
        area_km2 = math.pi * (radius_m / 1000) ** 2
        if area_km2 > 0:
            self.green_density_proxy = self.total_green_elements / area_km2
    
    def get_greenery_level(self) -> str:
        """Zwraca poziom zieleni: wysoka/średnia/niska."""
        if self.green_density_proxy >= 15:
            return 'wysoka'
        elif self.green_density_proxy >= 5:
            return 'średnia'
        else:
            return 'niska'
    
    def get_greenery_label_pl(self) -> str:
        """Zwraca polską etykietę poziomu zieleni."""
        level = self.get_greenery_level()
        return f"Zieleń w otoczeniu: {level}"
    
    def get_types_label_pl(self) -> Optional[str]:
        """Zwraca polską listę typów zieleni."""
        if not self.green_types_present:
            return None
        
        type_names = {
            'forest': 'las',
            'wood': 'las',
            'meadow': 'łąka',
            'grass': 'trawniki',
            'recreation_ground': 'teren rekreacyjny',
        }
        
        # Deduplikacja (forest i wood = las)
        polish_names = set()
        for t in self.green_types_present:
            polish_names.add(type_names.get(t, t))
        
        return f"Typy zieleni: {', '.join(sorted(polish_names))}"
    
    def get_nearest_park_label_pl(self) -> str:
        """Zwraca etykietę najbliższego parku."""
        nearest_park = self.nearest_distances.get('park')
        if nearest_park:
            return f"Najbliższy park: {round(nearest_park)}m"
        return "Brak parku w zasięgu"
    
    def get_water_label_pl(self) -> Optional[str]:
        """Zwraca polską etykietę wody."""
        if not self.water_present:
            return None
        
        water_names = {
            'river': 'rzeka',
            'stream': 'strumień',
            'canal': 'kanał',
            'lake': 'jezioro',
            'pond': 'staw',
            'water': 'zbiornik wodny',
            'beach': 'plaża',
            'reservoir': 'zbiornik',
        }
        
        # Znajdź najbliższy typ wody
        if self.water_type_distances:
            nearest_type = min(self.water_type_distances, key=self.water_type_distances.get)
            name = water_names.get(nearest_type, nearest_type)
            dist = self.water_type_distances[nearest_type]
            return f"Najbliższa {name}: {dist}m"
        elif self.nearest_water_m:
            return f"Woda w odległości: {self.nearest_water_m}m"
        
        return "Woda w okolicy"
    
    def to_dict(self) -> dict:
        """Serializacja do słownika."""
        return {
            'green_landcover_counts': self.green_landcover_counts,
            'green_types_present': list(self.green_types_present),
            'nearest_distances': self.nearest_distances,
            'total_green_elements': self.total_green_elements,
            'green_density_proxy': round(self.green_density_proxy, 2),
            'greenery_level': self.get_greenery_level(),
            'greenery_label': self.get_greenery_label_pl(),
            'types_label': self.get_types_label_pl(),
            'nearest_park_label': self.get_nearest_park_label_pl(),
            'water_present': self.water_present,
            'nearest_water_m': self.nearest_water_m,
            'water_types_present': list(self.water_types_present),
            'water_type_distances': self.water_type_distances,
            'water_label': self.get_water_label_pl(),
        }
