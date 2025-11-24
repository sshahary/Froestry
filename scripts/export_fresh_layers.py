"""
Export fresh data layers for complete map visualization
"""
import geopandas as gpd
from pathlib import Path
import sys
sys.path.append('.')
from src import config

print("="*80)
print("🗺️  EXPORTING FRESH LAYERS FOR COMPLETE MAP")
print("="*80)

alkis_path = Path(config.DATA_RAW) / 'ALKIS'
processed = Path(config.DATA_PROCESSED)
web_data = Path('web/data')
web_data.mkdir(exist_ok=True)

# 1. Fresh Buildings
print("\n🏢 Exporting fresh buildings...")
buildings = gpd.read_file(alkis_path / 'gebaeudeBauwerke.shp')

if 'aktualit' in buildings.columns:
    fresh_buildings = buildings[buildings['aktualit'] >= '2020-01-01'].copy()
    print(f"   Found {len(fresh_buildings):,} fresh buildings")
    
    # Convert to WGS84 for web
    if fresh_buildings.crs != 'EPSG:4326':
        fresh_buildings = fresh_buildings.to_crs('EPSG:4326')
    
    # Save to processed
    output = processed / 'exclusion_buildings_fresh.geojson'
    fresh_buildings.to_file(output, driver='GeoJSON')
    print(f"   ✅ Saved: {output}")
    
    # Copy to web for easy access
    web_output = web_data / 'exclusion_buildings_fresh.geojson'
    fresh_buildings.to_file(web_output, driver='GeoJSON')
    print(f"   ✅ Saved web copy: {web_output}")
else:
    print("   ⚠️  No aktualit column found")

# 2. Fresh Roads
print("\n🛣️  Exporting fresh roads...")
land_use = gpd.read_file(alkis_path / 'nutzung.shp')

if 'aktualit' in land_use.columns:
    fresh_roads = land_use[
        (land_use['aktualit'] >= '2020-01-01') & 
        (land_use['nutzart'] == 'Strassenverkehr')
    ].copy()
    print(f"   Found {len(fresh_roads):,} fresh roads")
    
    # Convert to WGS84 for web
    if fresh_roads.crs != 'EPSG:4326':
        fresh_roads = fresh_roads.to_crs('EPSG:4326')
    
    # Save to processed
    output = processed / 'exclusion_roads_fresh.geojson'
    fresh_roads.to_file(output, driver='GeoJSON')
    print(f"   ✅ Saved: {output}")
    
    # Copy to web
    web_output = web_data / 'exclusion_roads_fresh.geojson'
    fresh_roads.to_file(web_output, driver='GeoJSON')
    print(f"   ✅ Saved web copy: {web_output}")
else:
    print("   ⚠️  No aktualit column found")

# 3. Copy existing exclusions to web (if not already there)
print("\n📦 Copying other exclusions to web...")

other_files = [
    'exclusion_trees.geojson',
    'water_bodies.geojson'
]

for filename in other_files:
    source = processed / filename
    if source.exists():
        # Load and convert to WGS84
        data = gpd.read_file(source)
        if data.crs != 'EPSG:4326':
            data = data.to_crs('EPSG:4326')
        
        dest = web_data / filename
        data.to_file(dest, driver='GeoJSON')
        print(f"   ✅ Copied: {filename}")
    else:
        print(f"   ⚠️  Not found: {filename}")
# Add this at the end of the script (before the final print):

# 4. Copy fire safety routes
print("\n🔥 Exporting fire safety routes...")
fire_source = processed / 'exclusion_fire.geojson'
if fire_source.exists():
    fire_data = gpd.read_file(fire_source)
    
    # Convert to WGS84 for web
    if fire_data.crs != 'EPSG:4326':
        fire_data = fire_data.to_crs('EPSG:4326')
    
    fire_dest = web_data / 'exclusion_fire.geojson'
    fire_data.to_file(fire_dest, driver='GeoJSON')
    print(f"   ✅ Copied fire routes: {fire_dest}")
else:
    print("   ⚠️  Fire routes not found")

print("\n" + "="*80)
print("✅ FRESH LAYERS EXPORTED!")
print("="*80)
print("\nFiles exported to:")
print("   • data/processed/")
print("   • web/data/")