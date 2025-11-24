"""
Verify all exclusion files exist
"""
import geopandas as gpd
from pathlib import Path
import sys
sys.path.append('.')
from src import config

print("="*80)
print("🔍 VERIFYING EXCLUSION FILES")
print("="*80)

processed = Path(config.DATA_PROCESSED)

required_exclusions = {
    'Buildings': 'exclusion_buildings.geojson',
    'Roads': 'exclusion_roads.geojson',
    'Trees': 'exclusion_trees.geojson',
    'Fire Routes': 'exclusion_fire.geojson',
    'Water Bodies': 'water_bodies.geojson',
}

print("\n📂 Checking exclusion files:")

all_exist = True
for name, filename in required_exclusions.items():
    filepath = processed / filename
    if filepath.exists():
        try:
            data = gpd.read_file(filepath)
            size_mb = filepath.stat().st_size / (1024 * 1024)
            print(f"   ✅ {name:20} {len(data):>6,} features  ({size_mb:.2f} MB)")
        except Exception as e:
            print(f"   ❌ {name:20} EXISTS but ERROR: {e}")
            all_exist = False
    else:
        print(f"   ❌ {name:20} MISSING!")
        all_exist = False

print("\n" + "="*80)
if all_exist:
    print("✅ ALL EXCLUSIONS PRESENT!")
else:
    print("⚠️  SOME EXCLUSIONS MISSING - NEED TO REGENERATE!")
print("="*80)