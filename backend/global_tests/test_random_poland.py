import re
import subprocess
import time
import requests
import sys
import os

def fetch_random_locations(count=2):
    url = f"https://www.generatormix.com/random-address-in-poland?number={count}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    print(f"Pobieram {count} losowych lokalizacji z {url}...")
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    html = response.text
    # Regex aby wyciągnąć lat i lon z linków Google Street View (cbll=lat,lon)
    pattern = r"cbll=([0-9.-]+),([0-9.-]+)"
    matches = re.findall(pattern, html)
    
    unique_locations = []
    seen = set()
    for lat_str, lon_str in matches:
        coord = (float(lat_str), float(lon_str))
        if coord not in seen:
            seen.add(coord)
            unique_locations.append(coord)
            if len(unique_locations) >= count:
                break
                
    return unique_locations

def main():
    try:
        locations = fetch_random_locations(2)
    except Exception as e:
        print(f"Nie udało się pobrać lokalizacji: {e}")
        return

    print(f"Znaleziono {len(locations)} unikalnych lokalizacji:")
    for idx, (lat, lon) in enumerate(locations, 1):
        print(f" {idx}. {lat}, {lon}")
    
    for i, (lat, lon) in enumerate(locations, 1):
        print(f"\n{'='*80}")
        print(f"  TESTOWANIE LOKALIZACJI {i}/{len(locations)}: lat={lat}, lon={lon}")
        print(f"{'='*80}\n")
        
        script_path = os.path.join(os.path.dirname(__file__), "test_all_profiles_full.py")
        cmd = [
            sys.executable, script_path,
            "--lat", str(lat),
            "--lon", str(lon),
            "--address", f"Random_Location_{i}",
            "--poi-provider", "overpass",
        ]
        
        try:
            # Używamy sys.stdout.flush by widzieć output test_all_profiles_full na bieżąco
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Błąd podczas testowania lokalizacji {i}: {e}")
            
        # Krótka pauza żeby nie przeciążyć gwałtownie serwera/Overpass API
        print("\nOczekiwanie 5 sekund przed kolejną lokalizacją...")
        time.sleep(5)

if __name__ == "__main__":
    main()
