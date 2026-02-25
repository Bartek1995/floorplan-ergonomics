import os, json, glob

logs_dir = r"C:\Projects\floorplan-ergonomics\backend\global_tests\test_logs"
json_files = sorted(glob.glob(os.path.join(logs_dir, "profiles_*.json")))[-10:]

print(f"Analyzing {len(json_files)} recent test runs for URBAN profile...")
for f in json_files:
    try:
        with open(f, "r", encoding="utf-8") as file:
            data = json.load(file)
            loc = data.get("location", {})
            coords = loc.get("coordinates", {})
            all_runs = data.get("all_runs", [])
            results = all_runs[0] if all_runs and isinstance(all_runs[0], list) else []
            urban_profile = next((p for p in results if isinstance(p, dict) and p.get("profile") == "urban"), None)
            
            if urban_profile:
                print(f"--- File: {os.path.basename(f)} | Coords: {coords.get('lat')}, {coords.get('lon')} ---")
                print(f"  Urban Score: {urban_profile.get('score')} | Verdict: {urban_profile.get('verdict')}")
                scores = urban_profile.get("category_scores", {})
                print(f"  Scores: Transport={scores.get('transport')}, Food={scores.get('food')}, Nature={scores.get('nature_background', scores.get('nature_place'))}, Shops={scores.get('shops')}")
                caps = urban_profile.get("critical_caps_applied", [])
                if caps:
                    print(f"  Caps Applied: {caps}")
                scores = urban_profile.get("category_scores", {})
                print(f"  Scores: [Transport: {scores.get('transport')}, Food: {scores.get('food')}, Nature: {scores.get('nature_background', scores.get('nature_place'))}, Shops: {scores.get('shops')}]")
    except Exception as e:
        print(f"Error reading {f}: {e}")
