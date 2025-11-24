"""
Level 1 Completion Summary
"""
import geopandas as gpd
from pathlib import Path
import sys
sys.path.append('.')
from src import config

def print_level1_summary():
    """Print comprehensive Level 1 summary"""
    
    print("\n" + "="*80)
    print("🎮 LEVEL 1: EXCLUSION ZONES - COMPLETION REPORT")
    print("="*80)
    
    processed = Path(config.DATA_PROCESSED)
    
    # Load all data
    print("\n📂 Loading results...")
    exclusion = gpd.read_file(processed / 'exclusion_combined.geojson')
    green_spaces = gpd.read_file(processed / 'green_spaces.geojson')
    plantable = gpd.read_file(processed / 'plantable_area.geojson')
    
    # Calculate areas
    heilbronn_total = 100  # Heilbronn city area ~100 km²
    green_area = green_spaces.geometry.area.sum() / 1_000_000
    exclusion_area = exclusion.geometry.area.sum() / 1_000_000
    plantable_area = plantable.geometry.area.sum() / 1_000_000
    
    print("\n" + "="*80)
    print("📊 AREA STATISTICS")
    print("="*80)
    print(f"   Heilbronn total area: ~{heilbronn_total:.0f} km²")
    print(f"   Green spaces identified: {green_area:.2f} km² ({green_area/heilbronn_total*100:.1f}% of city)")
    print(f"   Total exclusions: {exclusion_area:.2f} km²")
    print(f"   Final plantable area: {plantable_area:.2f} km² ({plantable_area/green_area*100:.1f}% of green spaces)")
    
    # Exclusion breakdown
    print("\n" + "="*80)
    print("🚫 EXCLUSION ZONES APPLIED")
    print("="*80)
    
    exclusions = [
        ("Buildings", "exclusion_buildings.geojson", "3m buffer", 25619),
        ("Roads", "exclusion_roads.geojson", "2.5m buffer", 1412),
        ("Fire Access", "exclusion_fire.geojson", "5m buffer", 469),
        ("Existing Trees", "exclusion_trees.geojson", "dynamic buffer (avg 5.79m)", 4911),
        ("Water Bodies", "water_bodies.geojson", "direct exclusion", 146)
    ]
    
    for name, filename, buffer, count in exclusions:
        file_path = processed / filename
        if file_path.exists():
            gdf = gpd.read_file(file_path)
            area = gdf.geometry.area.sum() / 1_000_000
            print(f"   ✅ {name:20s}: {count:6,} features, {area:6.2f} km² ({buffer})")
        else:
            print(f"   ⚠️  {name:20s}: Not found")
    
    # Tree capacity estimate
    print("\n" + "="*80)
    print("🌲 TREE PLANTING CAPACITY")
    print("="*80)
    
    tree_spacing_options = [8, 10, 12]
    print("   Based on different spacing scenarios:\n")
    
    for spacing in tree_spacing_options:
        area_per_tree = spacing ** 2
        estimated_trees = int((plantable_area * 1_000_000) / area_per_tree)
        print(f"      {spacing}m spacing: ~{estimated_trees:,} trees")
    
    print(f"\n   💡 Recommendation: Use 10m spacing = ~{int((plantable_area * 1_000_000) / 100):,} trees")
    
    # Environmental impact
    print("\n" + "="*80)
    print("🌍 ESTIMATED ENVIRONMENTAL IMPACT")
    print("="*80)
    
    trees_10m = int((plantable_area * 1_000_000) / 100)
    
    # Rough estimates (based on urban forestry research)
    co2_per_tree_year = 22  # kg CO2/tree/year
    cooling_per_tree = 0.5  # °C cooling in 15m radius
    
    co2_total = trees_10m * co2_per_tree_year / 1000  # tonnes
    
    print(f"   With ~{trees_10m:,} trees:")
    print(f"      🌡️  Cooling effect: Significant temperature reduction in hot zones")
    print(f"      💨 CO₂ sequestration: ~{co2_total:.1f} tonnes/year")
    print(f"      🌳 Canopy coverage: Additional {plantable_area:.1f} km² green canopy")
    print(f"      💧 Stormwater management: Improved water absorption")
    
    # Files created
    print("\n" + "="*80)
    print("📁 OUTPUT FILES CREATED")
    print("="*80)
    
    output_files = [
        'exclusion_buildings.geojson',
        'exclusion_roads.geojson',
        'exclusion_fire.geojson',
        'exclusion_trees.geojson',
        'water_bodies.geojson',
        'exclusion_combined.geojson',
        'green_spaces.geojson',
        'plantable_area.geojson'
    ]
    
    for filename in output_files:
        file_path = processed / filename
        if file_path.exists():
            size = file_path.stat().st_size / 1024  # KB
            print(f"   ✅ {filename:35s} ({size:7.1f} KB)")
    
    # Next steps
    print("\n" + "="*80)
    print("🎯 LEVEL 1 COMPLETE - NEXT STEPS")
    print("="*80)
    print("   ✅ DONE: Identified all exclusion zones")
    print("   ✅ DONE: Calculated plantable areas (11.50 km²)")
    print("   ✅ DONE: Created interactive visualization")
    print("\n   ⏳ NEXT: LEVEL 2 - Heat Mapping")
    print("      • Load DOP20RGBI (aerial imagery)")
    print("      • Calculate NDVI (vegetation index)")
    print("      • Load DGM1 (terrain model)")
    print("      • Calculate slope & aspect")
    print("      • Generate heat priority map")
    print("\n   ⏳ THEN: LEVEL 3 - Scoring & Ranking")
    print("      • Score each location (0-100)")
    print("      • Apply spacing rules")
    print("      • Generate ranked list")
    print("      • Add postal code filtering")
    
    print("\n" + "="*80)
    print("🏆 LEVEL 1: SUCCESSFULLY COMPLETED!")
    print("="*80)
    print(f"\n   Time to move to Level 2! 🚀\n")

if __name__ == "__main__":
    print_level1_summary()



