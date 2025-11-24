"""
Create heat priority zones - KEEP SEPARATE (don't dissolve too much)
"""
import geopandas as gpd
import numpy as np
from pathlib import Path
import sys
sys.path.append('.')
from src import config
import pandas as pd

print("="*80)
print("🔥 CREATING HEAT PRIORITY ZONES (IMPROVED - SEPARATE)")
print("="*80)

processed = Path(config.DATA_PROCESSED)
web_data = Path('web/data')

# Load improved scored locations
print("\n📂 Loading locations...")
scored_paths = [
    processed / 'scored_locations_all_improved.geojson',
    processed / 'scored_locations_all.geojson'
]

locations = None
for path in scored_paths:
    if path.exists():
        locations = gpd.read_file(path)
        print(f"   ✅ Loaded from: {path.name}")
        break

if locations is None:
    print("❌ No locations found!")
    sys.exit(1)

print(f"   Total locations: {len(locations):,}")
print(f"   Heat score range: {locations['heat_score'].min():.1f} - {locations['heat_score'].max():.1f}")

# Filter by heat categories
print("\n🔥 Filtering by heat categories...")

categories = {
    'EXTREME': locations['heat_score'] >= 90,
    'VERY_HIGH': (locations['heat_score'] >= 80) & (locations['heat_score'] < 90),
    'HIGH': (locations['heat_score'] >= 70) & (locations['heat_score'] < 80),
    'MODERATE': (locations['heat_score'] >= 60) & (locations['heat_score'] < 70)
}

all_zones = []

for category, mask in categories.items():
    filtered = locations[mask].copy()
    count = len(filtered)
    
    if count == 0:
        print(f"   ⚠️  {category}: 0 locations - skipping")
        continue
    
    print(f"   ✅ {category}: {count:,} locations")
    
    # Add category label
    filtered['heat_category'] = category
    
    # Create small buffers (10m) to make zones visible but not too large
    filtered['geometry'] = filtered.geometry.buffer(10)
    
    # Group nearby zones (within 50m) to avoid too many tiny polygons
    # But DON'T dissolve everything into one!
    filtered['cluster_id'] = range(len(filtered))
    
    # Only dissolve very close neighbors (within 30m)
    from shapely.ops import unary_union
    
    # Take every 10th point to create representative zones
    sample_size = max(10, count // 100)  # At least 10, or 1% of locations
    sampled = filtered.sample(n=min(sample_size, count), random_state=42)
    
    # Buffer sampled points to create visible zones
    sampled['geometry'] = sampled.geometry.buffer(50)  # Larger buffer for visibility
    
    all_zones.append(sampled)

# Combine all categories
if len(all_zones) == 0:
    print("\n❌ No heat zones created!")
    sys.exit(1)

heat_zones = gpd.GeoDataFrame(pd.concat(all_zones, ignore_index=True))

print(f"\n✅ Created {len(heat_zones)} heat zone polygons")
print(f"   Distribution:")
for cat in ['EXTREME', 'VERY_HIGH', 'HIGH', 'MODERATE']:
    count = (heat_zones['heat_category'] == cat).sum()
    if count > 0:
        print(f"      {cat}: {count} zones")

# Keep only essential columns
heat_zones = heat_zones[['heat_category', 'heat_score', 'geometry']]

# Convert to WGS84
if heat_zones.crs != 'EPSG:4326':
    print(f"\n🌐 Converting to WGS84...")
    heat_zones = heat_zones.to_crs('EPSG:4326')

# Save
output = web_data / 'heat_priority_zones.geojson'
heat_zones.to_file(output, driver='GeoJSON')

print(f"\n✅ Saved: {output}")
print(f"   File size: {output.stat().st_size / 1024:.1f} KB")
print(f"   Features: {len(heat_zones)}")

# Verify
verify = gpd.read_file(output)
print(f"\n🔍 Verification:")
for cat in verify['heat_category'].unique():
    count = (verify['heat_category'] == cat).sum()
    print(f"   {cat}: {count} polygons")

print("\n" + "="*80)
print("✅ HEAT ZONES READY!")
print("="*80)
print("\n💡 Tip: Toggle heat layer on/off to see the zones")