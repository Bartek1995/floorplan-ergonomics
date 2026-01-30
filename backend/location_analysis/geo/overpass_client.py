"""
Klient do Overpass API (OpenStreetMap).
Wersja zoptymalizowana: Single Batch Request (jedno zapytanie zamiast 8).
"""
import requests
import time
import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

@dataclass
class POI:
    lat: float
    lon: float
    name: str
    category: str
    subcategory: str
    distance_m: float
    tags: dict

class OverpassClient:
    """Klient do pobierania danych z OSM."""
    
    # Lista publicznych instancji Overpass API (Load Balancer)
    ENDPOINTS = [
        "https://overpass-api.de/api/interpreter",
        "https://lz4.overpass-api.de/api/interpreter",
        "https://z.overpass-api.de/api/interpreter",
        "https://maps.mail.ru/osm/tools/overpass/api/interpreter", 
    ]
    
    TIMEOUT = 60 # Zwiększony timeout dla dużego zapytania
    
    # Konfiguracja kategorii (zachowujemy strukturę dla subkategorii i nazw)
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
        Pobiera punkty POI w okolicy (Single Batch Request).
        Wysyła jedno duże zapytanie zamiast wielu małych.
        """
        
        # 1. Zbuduj wielkie Query (Union)
        union_parts = []
        
        for config in self.POI_QUERIES.values():
            q = config['query']
            # Używamy node i way (relation pomijamy dla wydajności, chyba że krytyczne)
            union_parts.append(f'node{q}(around:{radius_m},{lat},{lon});')
            union_parts.append(f'way{q}(around:{radius_m},{lat},{lon});')
            
            for alt_q in config.get('alt_queries', []):
                union_parts.append(f'node{alt_q}(around:{radius_m},{lat},{lon});')
                union_parts.append(f'way{alt_q}(around:{radius_m},{lat},{lon});')
        
        overpass_query = f"""
        [out:json][timeout:{self.TIMEOUT}];
        (
            {' '.join(union_parts)}
        );
        out center;
        """
        
        # 2. Wyślij request (z Retry Logic)
        elements = []
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                # print(f"DEBUG: Wysyłam Batch Request do {self._get_endpoint()} (próba {attempt+1})")
                response = requests.post(
                    self._get_endpoint(),
                    data={'data': overpass_query},
                    timeout=self.TIMEOUT * (attempt + 1),
                    headers={'Content-Type': 'application/x-www-form-urlencoded'}
                )
                response.raise_for_status()
                
                data = response.json()
                elements = data.get('elements', [])
                break # Sukces
                
            except (requests.RequestException, ValueError) as e:
                print(f"WARN: Batch Request failed on {self._get_endpoint()}: {e}")
                self._rotate_endpoint()
                time.sleep(1)
                
                if attempt == max_retries - 1:
                    print("ERROR: Wszystkie próby pobrania danych nie powiodły się.")
                    # Zwracamy puste wyniki (fail gracefully)
                    return {cat: [] for cat in self.POI_QUERIES}

        # 3. Klasyfikuj i Parsuj wyniki lokalnie
        pois_by_category = {cat: [] for cat in self.POI_QUERIES}
        
        # Cache przetworzonych id, żeby nie dublować (node może być częścią way, ale tu dostajemy node i way osobno z query)
        # Overpass 'out center' zwraca geometrię way jako center, więc jest ok.
        
        for elem in elements:
            tags = elem.get('tags', {})
            if not tags: continue
            
            # Pobierz koordynaty raz
            elem_lat = elem.get('lat') or elem.get('center', {}).get('lat')
            elem_lon = elem.get('lon') or elem.get('center', {}).get('lon')
            if not elem_lat: continue
            
            # Dopasuj kategorie
            matched_cats = self._match_categories(tags)
            
            for cat in matched_cats:
                poi = self._create_poi(elem, tags, cat, elem_lat, elem_lon, lat, lon)
                if poi:
                    pois_by_category[cat].append(poi)
        
        # 4. Sortuj wynikowe listy
        for cat in pois_by_category:
            pois_by_category[cat].sort(key=lambda p: p.distance_m)
            
        return pois_by_category

    def _match_categories(self, tags: dict) -> List[str]:
        """Sprawdza, do jakich kategorii pasuje dany obiekt na podstawie tagów."""
        matches = []
        
        # Shops
        if 'shop' in tags:
            matches.append('shops')
            
        # Transport (public_transport=stop_position OR highway=bus_stop OR railway=tram_stop/station)
        if (tags.get('public_transport') == 'stop_position' or 
            tags.get('highway') == 'bus_stop' or 
            tags.get('railway') in ['tram_stop', 'station']):
            matches.append('transport')
            
        # Education (amenity ~ school|kindergarten|university)
        amenity = tags.get('amenity', '')
        if amenity in ['school', 'kindergarten', 'university']:
            matches.append('education')
            
        # Health (amenity ~ pharmacy|doctors|hospital|clinic)
        if amenity in ['pharmacy', 'doctors', 'hospital', 'clinic']:
            matches.append('health')
            
        # Nature (leisure ~ park|garden|nature_reserve OR landuse ~ ...)
        leisure = tags.get('leisure', '')
        landuse = tags.get('landuse', '')
        natural = tags.get('natural', '')
        
        if (leisure in ['park', 'garden', 'nature_reserve'] or
            landuse in ['forest', 'meadow', 'grass', 'recreation_ground'] or
            natural in ['wood', 'water', 'beach']):
            matches.append('nature')
            
        # Leisure (playground, fitness, pitch, etc)
        if leisure in ['playground', 'fitness_centre', 'pitch', 'sports_centre', 'stadium', 'swimming_pool']:
            matches.append('leisure')
            
        # Food
        if amenity in ['restaurant', 'cafe', 'fast_food']:
            matches.append('food')
            
        # Finance
        if amenity in ['bank', 'atm']:
            matches.append('finance')
            
        # Roads (highway ~ motorway... OR railway ~ tram|rail)
        highway = tags.get('highway', '')
        railway = tags.get('railway', '')
        if (highway in ['motorway', 'trunk', 'primary', 'secondary', 'tertiary'] or
            railway in ['tram', 'rail']):
            matches.append('roads')
            
        return matches

    def _create_poi(self, elem: dict, tags: dict, category: str, 
                    lat: float, lon: float, ref_lat: float, ref_lon: float) -> Optional[POI]:
        """Tworzy obiekt POI dla danej kategorii."""
        config = self.POI_QUERIES.get(category, {})
        
        # Nazwa
        name = tags.get('name', tags.get('brand'))
        
        # Subkategoria dla tej konkretnej kategorii
        subcategory = ''
        
        # Logika wyboru subkategorii specyficzna dla kategorii
        if category == 'shops':
            subcategory = tags.get('shop', '')
        elif category == 'transport':
            if tags.get('highway') == 'bus_stop': subcategory = 'bus_stop'
            elif tags.get('railway') == 'tram_stop': subcategory = 'tram_stop'
            elif tags.get('railway') == 'station': subcategory = 'station'
            else: subcategory = tags.get('public_transport', '')
        elif category == 'education':
            subcategory = tags.get('amenity', '')
        elif category == 'health':
            subcategory = tags.get('amenity', '')
        elif category == 'nature':
            # Priorytet: leisure > landuse > natural
            subcategory = tags.get('leisure') or tags.get('landuse') or tags.get('natural', '')
        elif category == 'leisure':
            subcategory = tags.get('leisure', '')
        elif category == 'food':
            subcategory = tags.get('amenity', '')
        elif category == 'finance':
            subcategory = tags.get('amenity', '')
        elif category == 'roads':
            subcategory = tags.get('highway') or tags.get('railway', '')
            
        # Tłumaczenie subkategorii
        subcategory_pl = config.get('subcategories', {}).get(subcategory)
        
        # Fallback formatowania
        if not subcategory_pl:
            subcategory_pl = subcategory.replace('_', ' ').capitalize()
        
        # Fallback nazwy
        if not name:
            # DEBUG: Loguj (z filtrem spamu)
            is_spam = (category == 'nature' and subcategory in ['grass', 'water', 'meadow', 'forest', 'wood', 'basin', 'garden']) or \
                      (category == 'roads' and subcategory in ['tram', 'rail'])
            if not is_spam:
                print(f"DEBUG: Nameless POI found | Category: {category} | Type: {subcategory} | Tags: {tags}")
            
            if subcategory_pl:
                name = subcategory_pl.capitalize()
            else:
                name = "Obiekt bez nazwy"

        distance = self._haversine_distance(ref_lat, ref_lon, lat, lon)
        
        return POI(
            lat=lat,
            lon=lon,
            name=name,
            category=category,
            subcategory=subcategory,
            distance_m=round(distance),
            tags=tags
        )

    def _haversine_distance(self, lat1, lon1, lat2, lon2):
        R = 6371000
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
