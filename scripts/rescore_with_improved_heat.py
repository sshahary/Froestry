"""
Re-score all locations using improved heat map
"""
import geopandas as gpd
import numpy as np
import rasterio
from pathlib import Path
from tqdm import tqdm
import sys
sys.path.append('.')
from src import config

print("="*80)
print("🔄 RE-SCORING LOCATIONS WITH IMPROVED HEAT MAP")
print("="*80)

processed = Path(config.DATA_PROCESSED)

# Load improved heat map
print("\n📂 Loading improved heat map...")
improved_heat = np.load(processed / 'heat_map_improved.npy')
print(f"   Shape: {improved_heat.shape}")
print(f"   Mean heat: {improved_heat.mean():.2f}")

# Load heat map metadata for georeferencing
with rasterio.open(processed / 'heat_map_improved.tif') as src:
    transform = src.transform
    crs = src.crs

# Load ALL locations
print("\n📍 Loading all scored locations...")
all_locations = gpd.read_file(processed / 'scored_locations_all.geojson')
print(f"   Loaded {len(all_locations):,} locations")

# Ensure CRS matches
if str(all_locations.crs) != str(crs):
    all_locations = all_locations.to_crs(crs)

# Re-calculate heat scores
print("\n🔥 Re-calculating heat scores...")
new_heat_scores = []

for idx, row in tqdm(all_locations.iterrows(), total=len(all_locations)):
    point = row.geometry
    
    # Convert point to pixel coordinates
    col, row_idx = ~transform * (point.x, point.y)
    col, row_idx = int(col), int(row_idx)
    
    # Sample heat value (with bounds checking)
    if 0 <= row_idx < improved_heat.shape[0] and 0 <= col < improved_heat.shape[1]:
        heat_value = improved_heat[row_idx, col]
    else:
        heat_value = 0.0
    
    new_heat_scores.append(heat_value)

# Update heat scores
all_locations['heat_score'] = new_heat_scores

print(f"\n✅ Heat scores updated:")
print(f"   Min: {min(new_heat_scores):.2f}")
print(f"   Max: {max(new_heat_scores):.2f}")
print(f"   Mean: {np.mean(new_heat_scores):.2f}")

# Recalculate final scores with same weights
print("\n⚖️  Recalculating final scores...")

weights = {
    'heat': 0.40,
    'spatial': 0.30,
    'social': 0.20,
    'maintenance': 0.10
}

all_locations['final_score'] = (
    all_locations['heat_score'] * weights['heat'] +
    all_locations['spatial_score'] * weights['spatial'] +
    all_locations['social_score'] * weights['social'] +
    all_locations['maintenance_score'] * weights['maintenance']
)

# Re-rank
all_locations = all_locations.sort_values('final_score', ascending=False).reset_index(drop=True)
all_locations['rank'] = range(1, len(all_locations) + 1)

print(f"\n✅ Final scores recalculated:")
print(f"   Top score: {all_locations['final_score'].max():.2f}")
print(f"   Mean score: {all_locations['final_score'].mean():.2f}")

# Save updated locations
output = processed / 'scored_locations_all_improved.geojson'
all_locations.to_file(output, driver='GeoJSON')
print(f"\n💾 Saved: {output}")

# Also save top 100
top_100 = all_locations.head(100)
top_100_output = processed / 'top_100_improved.geojson'
top_100.to_file(top_100_output, driver='GeoJSON')
print(f"💾 Saved top 100: {top_100_output}")

# Compare with original
print("\n📊 COMPARISON WITH ORIGINAL SCORING:")
original = gpd.read_file(processed / 'scored_locations_all.geojson')

print(f"\n   Original top score: {original['final_score'].max():.2f}")
print(f"   Improved top score: {all_locations['final_score'].max():.2f}")
print(f"   Change: {all_locations['final_score'].max() - original['final_score'].max():+.2f}")

print(f"\n   Original mean: {original['final_score'].mean():.2f}")
print(f"   Improved mean: {all_locations['final_score'].mean():.2f}")
print(f"   Change: {all_locations['final_score'].mean() - original['final_score'].mean():+.2f}")

# Check if rankings changed significantly
original_top_10 = set(original.head(10)['rank'])
improved_top_10 = set(all_locations.head(10)['rank'])
changes = original_top_10.symmetric_difference(improved_top_10)

print(f"\n🔄 Top 10 changes: {len(changes)} locations")

print("\n" + "="*80)
print("✅ RE-SCORING COMPLETE!")
print("="*80)