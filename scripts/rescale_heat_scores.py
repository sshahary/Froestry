"""
Rescale heat scores to proper 0-100 range
"""
import geopandas as gpd
import numpy as np
from pathlib import Path
import sys
sys.path.append('.')
from src import config

print("="*80)
print("🔧 RESCALING HEAT SCORES TO 0-100")
print("="*80)

processed = Path(config.DATA_PROCESSED)

# Load improved locations
print("\n📂 Loading improved locations...")
locations = gpd.read_file(processed / 'scored_locations_all_improved.geojson')

print(f"   Loaded {len(locations):,} locations")
print(f"\n📊 Current heat score range:")
print(f"   Min: {locations['heat_score'].min():.2f}")
print(f"   Max: {locations['heat_score'].max():.2f}")
print(f"   Mean: {locations['heat_score'].mean():.2f}")

# Rescale to 0-100
old_min = locations['heat_score'].min()
old_max = locations['heat_score'].max()

# Linear rescaling to 0-100
locations['heat_score'] = (
    (locations['heat_score'] - old_min) / (old_max - old_min) * 100
)

print(f"\n✅ Rescaled heat scores:")
print(f"   Min: {locations['heat_score'].min():.2f}")
print(f"   Max: {locations['heat_score'].max():.2f}")
print(f"   Mean: {locations['heat_score'].mean():.2f}")

# Recalculate final scores
weights = {
    'heat': 0.40,
    'spatial': 0.30,
    'social': 0.20,
    'maintenance': 0.10
}

locations['final_score'] = (
    locations['heat_score'] * weights['heat'] +
    locations['spatial_score'] * weights['spatial'] +
    locations['social_score'] * weights['social'] +
    locations['maintenance_score'] * weights['maintenance']
)

# Re-rank
locations = locations.sort_values('final_score', ascending=False).reset_index(drop=True)
locations['rank'] = range(1, len(locations) + 1)

print(f"\n✅ Final scores recalculated:")
print(f"   Top score: {locations['final_score'].max():.2f}")
print(f"   Mean score: {locations['final_score'].mean():.2f}")

# Show heat distribution
print(f"\n🔥 Heat Score Distribution:")
print(f"   ≥90 (EXTREME): {(locations['heat_score'] >= 90).sum():,}")
print(f"   ≥80 (VERY HIGH): {(locations['heat_score'] >= 80).sum():,}")
print(f"   ≥70 (HIGH): {(locations['heat_score'] >= 70).sum():,}")
print(f"   ≥60 (MODERATE): {(locations['heat_score'] >= 60).sum():,}")

# Save
output = processed / 'scored_locations_all_improved.geojson'
locations.to_file(output, driver='GeoJSON')
print(f"\n💾 Saved: {output}")

# Also update top 100
top_100 = locations.head(100)
top_100_output = processed / 'top_100_improved.geojson'
top_100.to_file(top_100_output, driver='GeoJSON')
print(f"💾 Saved top 100: {top_100_output}")

print("\n" + "="*80)
print("✅ RESCALING COMPLETE!")
print("="*80)