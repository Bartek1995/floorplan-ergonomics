"""Detailed diagnostic for a single profile to understand POI data."""
import requests
import json

profile = 'remote_work'
print(f'=== DETAILED DIAGNOSTIC: {profile.upper()} ===', flush=True)
body = {
    'latitude': 51.277,
    'longitude': 17.235,
    'price': None,
    'area_sqm': None,
    'address': '1 Maja 11, Wiazow',
    'radius': 500,
    'profile_key': profile,
    'poi_provider': 'hybrid',
}

resp = requests.post('http://localhost:8000/api/analyze-location/', json=body, stream=True, timeout=120)
report = None
for line in resp.iter_lines():
    if not line:
        continue
    event = json.loads(line)
    if event.get('status') == 'complete':
        report = event.get('result')
        break
    elif event.get('status') == 'analyzing':
        print(f'  Status: {event.get("message", "")}', flush=True)

if not report:
    print('  FAILED')
    exit(1)

# Print full verdict
v = report.get('verdict', {})
scoring = report.get('scoring', {})
gen_params = report.get('generation_params', {})

print(f'\nScore: {v.get("score")}/100')
print(f'Level: {v.get("level")}')
print(f'Explanation: {v.get("explanation")}')

print(f'\nTotal score: {scoring.get("total_score")}')
print(f'Base score: {scoring.get("base_score")}')
print(f'Noise penalty: {scoring.get("noise_penalty")}')
print(f'Roads penalty: {scoring.get("roads_penalty")}')
print(f'Quiet score: {scoring.get("quiet_score")}')
print(f'Critical caps: {scoring.get("critical_caps_applied")}')
print(f'Strengths: {scoring.get("strengths")}')
print(f'Weaknesses: {scoring.get("weaknesses")}')
print(f'Warnings: {scoring.get("warnings")}')

print(f'\nRadii used: {gen_params.get("radii", {})}')
print(f'Fetch radius: {gen_params.get("fetch_radius")}')

cats = scoring.get('category_scores', {})
print(f'\nCategory breakdown:')
for cat, data in sorted(cats.items(), key=lambda x: x[1].get('score', 0), reverse=True):
    print(f'  {cat}:')
    print(f'    score={data.get("score")}, pois={data.get("poi_count")}, nearest={data.get("nearest_distance_m")}')
    print(f'    utility_score={data.get("utility_score")}, coverage_bonus={data.get("coverage_bonus")}')
    print(f'    radius_used={data.get("radius_used")}, is_critical={data.get("is_critical")}')
    top_pois = data.get('top_pois', [])
    for poi in top_pois[:3]:
        print(f'      -> {poi.get("name")} ({poi.get("distance_m")}m, score={poi.get("score")})')

# POI stats
print(f'\nPOI categories:')
poi_cats = report.get('poi_categories', {})
for cat, stats in poi_cats.items():
    print(f'  {cat}: count={stats.get("count")}, nearest={stats.get("nearest")}')
