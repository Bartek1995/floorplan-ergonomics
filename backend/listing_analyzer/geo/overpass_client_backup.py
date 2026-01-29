"""
Klient do Overpass API (OpenStreetMap).
"""
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

import requests

logger = logging.getLogger(__name__)


@dataclass
class POI:
    """Point of Interest z OSM."""
    osm_type: str  # node, way, relation
    osm_id: int
    name: str
    category: str
    subcategory: str
    lat: float
    lon: float
    distance_m: Optional[float] = None
    tags: Dict[str, str] = field(default_factory=dict)


class OverpassClient:
    """
    Klient do pobierania POI z Overpass API.
    Używa darmowego API, więc należy być ostrożnym z rate-limitami.
    """
    
    # Publiczne endpointy Overpass API
    ENDPOINTS = [
        "https://overpass-api.de/api/interpreter",
        "https://lz4.overpass-api.de/api/interpreter",
    ]
    
    # Timeout dla requestów
    TIMEOUT = 30
    
    # Kategorie POI do wyszukiwania
    POI_QUERIES = {
        'shops': {
            'query': '["shop"]',
            'name': 'Sklepy',
            'subcategories': {
                'supermarket': 'Supermarket',
                'convenience': 'Sklep spożywczy',
                'mall': 'Centrum handlowe',
                'bakery': 'Piekarnia',
                'clothes': 'Sklep odzieżowy',
                'hairdresser': 'Fryzjer',
                'beauty': 'Kosmetyczka',
                'kiosk': 'Kiosk',
                'alcohol': 'Sklep monopolowy',
                'florist': 'Kwiaciarnia',
                'greengrocer': 'Warzywniak',
                'butcher': 'Rzeźnik',
                'car_repair': 'Warsztat samochodowy',
                'doityourself': 'Sklep budowlany',
                'drugstore': 'Drogeria',
                'books': 'Księgarnia',
                'electronics': 'Elektronika',
                'shoes': 'Obuwie',
                'furniture': 'Meble',
                'jewelry': 'Jubiler',
                'optician': 'Optyk',
                'gift': 'Upominki',
            }
        },
        'transport': {
            'query': '["public_transport"="stop_position"]',
            'alt_queries': [
                '["highway"="bus_stop"]',
                '["railway"="tram_stop"]',
                '["railway"="station"]',
            ],
            'name': 'Transport publiczny',
            'subcategories': {
                'bus_stop': 'Przystanek autobusowy',
                'tram_stop': 'Przystanek tramwajowy',
                'station': 'Stacja kolejowa',
            }
        },
        'education': {
            'query': '["amenity"~"school|kindergarten|university"]',
            'name': 'Edukacja',
            'subcategories': {
                'school': 'Szkoła',
                'kindergarten': 'Przedszkole',
                'university': 'Uczelnia',
            }
        },
        'health': {
            'query': '["amenity"~"pharmacy|doctors|hospital|clinic"]',
            'name': 'Zdrowie',
            'subcategories': {
                'pharmacy': 'Apteka',
                'doctors': 'Lekarz',
                'hospital': 'Szpital',
                'clinic': 'Przychodnia',
            }
        },
        'nature': {
            'query': '["leisure"~"park|garden|nature_reserve"]',
            'alt_queries': [
                '["landuse"~"forest|meadow|grass|recreation_ground"]',
                '["natural"~"wood|water|beach"]',
            ],
            'name': 'Zieleń i Wypoczynek',
            'subcategories': {
                'park': 'Park',
                'garden': 'Ogród',
                'nature_reserve': 'Rezerwat przyrody',
                'forest': 'Las',
                'wood': 'Las',
                'meadow': 'Łąka',
                'water': 'Woda',
                'beach': 'Plaża',
                'grass': 'Trawnik',
                'recreation_ground': 'Teren rekreacyjny',
            }
        },
        'leisure': {
            'query': '["leisure"~"playground|fitness_centre|pitch|sports_centre|stadium|swimming_pool"]',
            'name': 'Sport i Rekreacja',
            'subcategories': {
                'playground': 'Plac zabaw',
                'fitness_centre': 'Siłownia',
                'pitch': 'Boisko',
                'sports_centre': 'Centrum sportowe',
                'stadium': 'Stadion',
                'swimming_pool': 'Basen',
            }
        },
        'food': {
            'query': '["amenity"~"restaurant|cafe|fast_food"]',
            'name': 'Gastronomia',
            'subcategories': {
                'restaurant': 'Restauracja',
                'cafe': 'Kawiarnia',
                'fast_food': 'Fast food',
            }
        },
        'finance': {
            'query': '["amenity"~"bank|atm"]',
            'name': 'Finanse',
            'subcategories': {
                'bank': 'Bank',
                'atm': 'Bankomat',
            }
        },
        'roads': {
            'query': '["highway"~"motorway|trunk|primary|secondary|tertiary"]',
            'alt_queries': [
                '["railway"~"tram|rail"]'
            ],
            'name': 'Ruch drogowy',
            'subcategories': {
                'motorway': 'Autostrada',
                'trunk': 'Droga ekspresowa',
                'primary': 'Droga główna',
                'secondary': 'Droga wojewódzka',
                'tertiary': 'Droga powiatowa',
                'tram': 'Tramwaj',
                'rail': 'Kolej',
            }
        },
    }
    
    def __init__(self):
        self._current_endpoint_idx = 0
    
    def _get_endpoint(self) -> str:
        return self.ENDPOINTS[self._current_endpoint_idx % len(self.ENDPOINTS)]
    
    def _rotate_endpoint(self):
        self._current_endpoint_idx += 1
    
    def get_pois_around(
        self,
        lat: float,
        lon: float,
        radius_m: int = 500
    ) -> Dict[str, List[POI]]:
        """
        Pobiera wszystkie POI w promieniu od punktu.
        
        Args:
            lat: Szerokość geograficzna
            lon: Długość geograficzna
            radius_m: Promień w metrach (domyślnie 500m)
        
        Returns:
            Słownik {kategoria: [lista POI]}
        """
        results: Dict[str, List[POI]] = {}
        
        for category, config in self.POI_QUERIES.items():
            try:
                pois = self._query_category(lat, lon, radius_m, category, config)
                if pois:
                    results[category] = pois
            except Exception as e:
                logger.warning(f"Błąd pobierania kategorii {category}: {e}")
                results[category] = []
        
        return results
    
    def _query_category(
        self,
        lat: float,
        lon: float,
        radius_m: int,
        category: str,
        config: dict
    ) -> List[POI]:
        """Wykonuje zapytanie dla jednej kategorii."""
        
        # Buduj zapytanie Overpass
        queries = [config['query']]
        if 'alt_queries' in config:
            queries.extend(config['alt_queries'])
        
        # Łączone zapytanie dla wszystkich wariantów
        union_parts = []
        for q in queries:
            union_parts.append(f'node{q}(around:{radius_m},{lat},{lon});')
            union_parts.append(f'way{q}(around:{radius_m},{lat},{lon});')
        
        overpass_query = f"""
        [out:json][timeout:25];
        (
            {' '.join(union_parts)}
        );
        out center;
        """
        
        # Wykonaj request
        # Wykonaj request z retry
        import time
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self._get_endpoint(),
                    data={'data': overpass_query},
                    timeout=self.TIMEOUT * (attempt + 1), # Zwiększaj timeout przy kolejnych próbach
                    headers={'Content-Type': 'application/x-www-form-urlencoded'}
                )
                response.raise_for_status()
                break # Sukces
            except requests.RequestException as e:
                print(f"WARN: Błąd endpointu {self._get_endpoint()} dla {category}: {e}")
                self._rotate_endpoint()
                time.sleep(1) # Odczekaj chwilę
                
                if attempt == max_retries - 1:
                    print(f"ERROR: Nie udało się pobrać kategorii {category} po {max_retries} próbach.")
                    return [] # Zwróć pustą listę zamiast wywalać całą analizę
        
        try:
            data = response.json()
        except ValueError:
             print(f"ERROR: Nieprawidłowy JSON z Overpass dla {category}")
             return []
        elements = data.get('elements', [])
        
        pois = []
        for elem in elements:
            poi = self._parse_element(elem, category, config, lat, lon)
            if poi:
                pois.append(poi)
        
        # Sortuj po odległości
        pois.sort(key=lambda p: p.distance_m or 999999)
        
        return pois
    
    def _parse_element(
        self,
        elem: dict,
        category: str,
        config: dict,
        ref_lat: float,
        ref_lon: float
    ) -> Optional[POI]:
        """Parsuje element OSM do POI."""
        tags = elem.get('tags', {})
        
        # Pobierz współrzędne (dla way/relation użyj center)
        if 'center' in elem:
            lat = elem['center']['lat']
            lon = elem['center']['lon']
        elif 'lat' in elem and 'lon' in elem:
            lat = elem['lat']
            lon = elem['lon']
        else:
            return None
        
        # Subkategoria
        subcategory = ''
        # Kolejność kluczy ma znaczenie dla priorytetu
        for key in ['amenity', 'shop', 'leisure', 'public_transport', 'highway', 'railway', 'landuse', 'natural']:
            if key in tags:
                subcategory = tags[key]
                break
        
        # Nazwa - fallback do subkategorii jeśli brak
        name = tags.get('name', tags.get('brand'))
        
        # Tłumaczenie subkategorii do wyświetlania
        subcategory_pl = config.get('subcategories', {}).get(subcategory)
        
        # Jeśli brak tłumaczenia, sformatuj ładnie angielską nazwę (np. "clothes_shop" -> "Clothes shop")
        if not subcategory_pl:
            subcategory_pl = subcategory.replace('_', ' ').capitalize()
        
        if not name:
            # DEBUG: Loguj obiekty bez nazwy (z pominięciem spamu przyrodniczego)
            is_spam = category == 'nature' and subcategory in ['grass', 'water', 'meadow', 'forest', 'wood', 'basin', 'garden']
            if not is_spam:
                print(f"DEBUG: Nameless POI found | Category: {category} | Type: {subcategory} | Tags: {tags}")
            
            # Użyj polskiej nazwy subkategorii jako nazwy własnej (np. "Plac zabaw" zamiast "Bez nazwy")
            if subcategory_pl:
                name = subcategory_pl.capitalize()
            else:
                name = "Obiekt bez nazwy"
        
        # Jeśli nazwa jest identyczna jak subkategoria (np. "Park"), to ok

        
        # Oblicz odległość
        distance = self._haversine_distance(ref_lat, ref_lon, lat, lon)
        
        return POI(
            osm_type=elem.get('type', 'node'),
            osm_id=elem.get('id', 0),
            name=name,
            category=category,
            subcategory=subcategory,
            lat=lat,
            lon=lon,
            distance_m=distance,
            tags=tags
        )
    
    @staticmethod
    def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Oblicza odległość w metrach między dwoma punktami (wzór Haversine)."""
        import math
        
        R = 6371000  # Promień Ziemi w metrach
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
