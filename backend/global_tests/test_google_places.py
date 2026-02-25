"""
Test script for Google Places API (New).
Run with: python test_google_places.py
"""
import os
import sys
import requests

# Load .env
from pathlib import Path
env_file = Path('.env')
if env_file.exists():
    for line in env_file.read_text().splitlines():
        if '=' in line and not line.startswith('#'):
            key, val = line.split('=', 1)
            os.environ[key.strip()] = val.strip()

API_KEY = os.environ.get('GOOGLE_PLACES_API_KEY')
NEARBY_SEARCH_URL = "https://places.googleapis.com/v1/places:searchNearby"

print(f"API Key configured: {bool(API_KEY)}")
print(f"API Key prefix: {API_KEY[:20] if API_KEY else None}...")

# Test real location: Olawa, Poland
lat, lon = 50.9461808, 17.2778681
print(f"\nTesting location: ({lat}, {lon}) - Olawa, Poland")

# Nagłówki dla Places API (New)
headers = {
    'X-Goog-Api-Key': API_KEY,
    'X-Goog-FieldMask': 'places.id,places.displayName,places.location,places.types,places.rating,places.userRatingCount',
    'Content-Type': 'application/json',
}

# Try single type search
body = {
    'includedTypes': ['restaurant'],
    'maxResultCount': 10,
    'locationRestriction': {
        'circle': {
            'center': {'latitude': lat, 'longitude': lon},
            'radius': 500.0,
        }
    },
    'languageCode': 'pl',
}

print(f"\nRequest: restaurant search (POST)")
response = requests.post(NEARBY_SEARCH_URL, json=body, headers=headers, timeout=10)
print(f"HTTP Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    places = data.get('places', [])
    print(f"Results count: {len(places)}")
    
    for p in places[:5]:
        name = p.get('displayName', {}).get('text', 'Unknown')
        rating = p.get('rating', 'N/A')
        reviews = p.get('userRatingCount', 0)
        place_id = p.get('id', 'N/A')
        print(f"  - {name} (rating={rating}, reviews={reviews}, id={place_id[:20]}...)")
else:
    print(f"Error: {response.text[:300]}")

# Try batch types (key optimization!)
print("\n--- Batch types test (multiple types in one request) ---")
batch_types = ['supermarket', 'convenience_store', 'shopping_mall', 'store']
body['includedTypes'] = batch_types
body['maxResultCount'] = 20

response = requests.post(NEARBY_SEARCH_URL, json=body, headers=headers, timeout=10)
print(f"Types: {batch_types}")
print(f"HTTP Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    places = data.get('places', [])
    print(f"Results count: {len(places)}")
    for p in places[:5]:
        name = p.get('displayName', {}).get('text', 'Unknown')
        types = [t for t in p.get('types', []) if t in {'supermarket', 'convenience_store', 'shopping_mall', 'store'}]
        print(f"  - {name} (types={types})")

# Try other category batches
for label, types in [
    ('transport', ['bus_station', 'transit_station', 'train_station']),
    ('nature', ['park']),
    ('finance', ['bank', 'atm']),
]:
    body['includedTypes'] = types
    body['maxResultCount'] = 10
    response = requests.post(NEARBY_SEARCH_URL, json=body, headers=headers, timeout=10)
    if response.status_code == 200:
        count = len(response.json().get('places', []))
    else:
        count = f"ERROR {response.status_code}"
    print(f"\n{label} ({types}): {count} results")

# Test Place Details (New)
print("\n--- Place Details (New) test ---")
# Get first place_id from restaurant search
body['includedTypes'] = ['restaurant']
body['maxResultCount'] = 1
response = requests.post(NEARBY_SEARCH_URL, json=body, headers=headers, timeout=10)
if response.status_code == 200:
    places = response.json().get('places', [])
    if places:
        test_id = places[0].get('id')
        print(f"Testing details for: {test_id}")
        
        details_url = f"https://places.googleapis.com/v1/places/{test_id}"
        details_headers = {
            'X-Goog-Api-Key': API_KEY,
            'X-Goog-FieldMask': 'id,displayName,location,types,rating,userRatingCount',
        }
        det_response = requests.get(details_url, headers=details_headers, timeout=10)
        print(f"Details HTTP Status: {det_response.status_code}")
        if det_response.status_code == 200:
            d = det_response.json()
            print(f"  Name: {d.get('displayName', {}).get('text')}")
            print(f"  Rating: {d.get('rating')}")
            print(f"  Reviews: {d.get('userRatingCount')}")
            loc = d.get('location', {})
            print(f"  Location: ({loc.get('latitude')}, {loc.get('longitude')})")
