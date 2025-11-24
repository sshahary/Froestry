"""
Calculate actual plantable area from fresh locations
"""
import geopandas as gpd
from pathlib import Path
import sys
sys.path.append('.')
from src import config

print("="*80)
print("📐 CALCULATING ACTUAL FRESH PLANTABLE AREA")
print("="*80)

processed = Path(config.DATA_PROCESSED)

# Load fresh locations
print("\n📂 Loading fresh locations...")
fresh = gpd.read_file(processed / 'scored_locations_fresh.geojson')
print(f"   ✅ Loaded {len(fresh):,} locations")

# Method 1: Sum of individual location areas (10m radius assumption)
print("\n📏 Method 1: Individual Location Areas")
# Each location represents potential planting area
# Assume ~10m spacing for trees = ~100m² per location
area_per_location = 100  # m²
total_area_m2 = len(fresh) * area_per_location
total_area_km2 = total_area_m2 / 1_000_000

print(f"   Locations: {len(fresh):,}")
print(f"   Area per location: {area_per_location} m² (10m radius)")
print(f"   Total area: {total_area_m2:,.0f} m²")
print(f"   Total area: {total_area_km2:.2f} km²")

# Method 2: Create buffers and measure actual coverage
print("\n📏 Method 2: Buffer-Based Coverage")
fresh_buffered = fresh.copy()
fresh_buffered['geometry'] = fresh.buffer(10)  # 10m radius around each point
dissolved = fresh_buffered.dissolve()
actual_area_m2 = dissolved.geometry.area.sum()
actual_area_km2 = actual_area_m2 / 1_000_000

print(f"   Buffer size: 10m radius")
print(f"   Actual coverage (dissolved): {actual_area_m2:,.0f} m²")
print(f"   Actual coverage: {actual_area_km2:.2f} km²")

# Method 3: Compare with original dataset
print("\n📊 Comparison with Original Dataset:")
all_locations = gpd.read_file(processed / 'scored_locations_all.geojson')
print(f"   Original locations: {len(all_locations):,}")
print(f"   Fresh locations: {len(fresh):,}")
print(f"   Percentage: {len(fresh)/len(all_locations)*100:.1f}%")

# Calculate proportional area
original_area_km2 = 11.50  # From original stats
proportional_area_km2 = original_area_km2 * (len(fresh) / len(all_locations))
print(f"\n   Original area: {original_area_km2:.2f} km²")
print(f"   Proportional fresh area: {proportional_area_km2:.2f} km²")

# Summary
print("\n" + "="*80)
print("📊 RECOMMENDED VALUES FOR DASHBOARD")
print("="*80)
print(f"\n✅ Fresh Locations: {len(fresh):,}")
print(f"✅ Fresh Plantable Area: {proportional_area_km2:.2f} km²")
print(f"   (Proportional to original 11.50 km²)")
print(f"\nAlternatively:")
print(f"   Buffer-based: {actual_area_km2:.2f} km²")
print(f"   Per-location: {total_area_km2:.2f} km²")

print("\n💡 Recommended: Use {:.2f} km²".format(proportional_area_km2))
print("   (Most conservative and logical estimate)")

print("\n" + "="*80)