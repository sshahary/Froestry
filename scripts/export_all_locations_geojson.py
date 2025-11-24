"""
Enhance ALL scored locations with full details
"""
import geopandas as gpd
import pandas as pd
from pathlib import Path
import sys
sys.path.append('.')
from src import config

def get_proven_species_for_heilbronn():
    """Get list of proven tree species from Baumkataster"""
    trees_path = Path(config.DATA_RAW) / 'Baumkataster'
    tree_files = list(trees_path.glob('*.shp'))
    
    if not tree_files:
        return {
            'heat_tolerant': ['Oak', 'Linden'],
            'moderate': ['Maple', 'Plane tree'],
            'small': ['Birch', 'Cherry']
        }
    
    trees = gpd.read_file(tree_files[0])
    
    if 'DEU_TEXT' not in trees.columns:
        return {
            'heat_tolerant': ['Oak', 'Linden'],
            'moderate': ['Maple', 'Plane tree'],
            'small': ['Birch', 'Cherry']
        }
    
    # Get top species
    top_species = trees['DEU_TEXT'].value_counts().head(20).index.tolist()
    
    # Categorize
    large_heat_tolerant = [s for s in top_species if any(x in s.lower() for x in ['eiche', 'linde', 'platane'])]
    medium_trees = [s for s in top_species if any(x in s.lower() for x in ['ahorn', 'kastanie', 'robinie'])]
    small_trees = [s for s in top_species if any(x in s.lower() for x in ['birke', 'kirsche', 'apfel'])]
    
    return {
        'heat_tolerant': large_heat_tolerant[:3] if large_heat_tolerant else top_species[:3],
        'moderate': medium_trees[:3] if medium_trees else top_species[3:6],
        'small': small_trees[:2] if small_trees else top_species[6:8]
    }

def recommend_tree_species(heat_score, species_db):
    """Recommend tree species based on heat"""
    if heat_score > 80:
        species = ' or '.join(species_db['heat_tolerant'][:2])
        return f"{species} (proven in Heilbronn, heat-tolerant)"
    elif heat_score > 60:
        species = ' or '.join(species_db['moderate'][:2])
        return f"{species} (proven in Heilbronn)"
    else:
        species = ' or '.join(species_db['small'][:2])
        return f"{species} (proven in Heilbronn)"

def estimate_cooling(heat_score):
    """Estimate cooling effect"""
    if heat_score > 80:
        return "-2.5°C in 20m radius"
    elif heat_score > 60:
        return "-2.0°C in 15m radius"
    else:
        return "-1.5°C in 15m radius"

def estimate_schools_nearby(point, land_use):
    """Estimate schools within 200m"""
    if land_use is None or len(land_use) == 0:
        return "Unknown"
    
    try:
        nearby = land_use[land_use.distance(point) < 200]
        education_types = ['Sport Freizeit Und Erholungsflaeche', 
                          'Flaeche Besonderer Funktionaler Praegung']
        schools = nearby[nearby['nutzart'].isin(education_types)]
        
        count = len(schools) // 2
        if count == 0:
            return "No schools/recreation nearby"
        elif count == 1:
            return "~1 school/recreation nearby"
        else:
            return f"~{count} schools/recreation nearby"
    except:
        return "Unknown"

def estimate_residents_nearby(point, land_use):
    """Estimate residents within 100m"""
    if land_use is None or len(land_use) == 0:
        return "Unknown"
    
    try:
        nearby = land_use[land_use.distance(point) < 100]
        residential = nearby[nearby['nutzart'] == 'Wohnbauflaeche']
        
        total_area_hectares = residential.geometry.area.sum() / 10000
        
        if total_area_hectares < 0.1:
            return "Low density area"
        elif total_area_hectares < 0.5:
            return "~50-100 residents nearby"
        elif total_area_hectares < 1.0:
            return "~100-200 residents nearby"
        else:
            estimated = int(total_area_hectares * 50)
            return f"~{estimated} residents nearby"
    except:
        return "Unknown"

def get_location_type(point, land_use):
    """Determine location type"""
    if land_use is None or len(land_use) == 0:
        return "Green Space"
    
    try:
        nearby = land_use[land_use.distance(point) < 20]
        if len(nearby) > 0:
            nutzart = nearby.iloc[0]['nutzart']
            
            type_map = {
                'Sport Freizeit Und Erholungsflaeche': 'Recreation Area',
                'Gehoelz': 'Wooded Area',
                'Wald': 'Forest Edge',
                'Wohnbauflaeche': 'Residential Green Strip',
                'Strassenverkehr': 'Street Side'
            }
            
            return type_map.get(nutzart, 'Green Space')
    except:
        pass
    
    return "Green Space"

def enhance_all_locations():
    """Enhance all locations with detailed information"""
    
    print("="*80)
    print("✨ ENHANCING ALL LOCATIONS WITH DETAILED INFORMATION")
    print("="*80)
    
    processed = Path(config.DATA_PROCESSED)
    
    # Load all scored locations
    print("\n📂 Loading all scored locations...")
    all_locations = gpd.read_file(processed / 'scored_locations_all.geojson')
    print(f"   ✅ Loaded {len(all_locations):,} locations")
    
    # Load land use data
    print("\n📂 Loading ALKIS land use data...")
    alkis_path = Path(config.DATA_RAW) / 'ALKIS'
    land_use_file = alkis_path / 'nutzung.shp'
    
    if land_use_file.exists():
        land_use = gpd.read_file(land_use_file)
        if land_use.crs != config.CRS:
            land_use = land_use.to_crs(config.CRS)
        print(f"   ✅ Loaded {len(land_use):,} land use polygons")
    else:
        land_use = None
        print("   ⚠️  Land use data not found - using defaults")
    
    # Get proven species
    print("\n🌳 Loading proven tree species from Baumkataster...")
    species_db = get_proven_species_for_heilbronn()
    print(f"   ✅ Heat-tolerant: {', '.join(species_db['heat_tolerant'][:2])}")
    
    # Add location types
    print("\n📍 Determining location types...")
    all_locations['location_type'] = all_locations.geometry.apply(
        lambda point: get_location_type(point, land_use)
    )
    
    # Add tree recommendations
    print("\n🌳 Recommending tree species based on Heilbronn data...")
    all_locations['recommended_species'] = all_locations['heat_score'].apply(
        lambda heat: recommend_tree_species(heat, species_db)
    )
    
    # Add cooling estimates
    print("\n❄️  Calculating cooling estimates...")
    all_locations['cooling_estimate'] = all_locations['heat_score'].apply(
        lambda heat: estimate_cooling(heat)
    )
    
    # Add social impact data (this takes time - process in batches)
    print("\n👥 Estimating social impact (this may take a few minutes)...")
    print("   Processing in batches of 10,000...")
    
    schools_list = []
    residents_list = []
    
    batch_size = 10000
    total_batches = (len(all_locations) + batch_size - 1) // batch_size
    
    for i in range(0, len(all_locations), batch_size):
        batch = all_locations.iloc[i:i+batch_size]
        batch_num = i // batch_size + 1
        
        print(f"   Batch {batch_num}/{total_batches}...")
        
        for _, row in batch.iterrows():
            schools = estimate_schools_nearby(row.geometry, land_use)
            residents = estimate_residents_nearby(row.geometry, land_use)
            
            schools_list.append(schools)
            residents_list.append(residents)
    
    all_locations['schools_nearby'] = schools_list
    all_locations['residents_nearby'] = residents_list
    
    # Postal codes - use simplified assignment
    print("\n📮 Assigning postal codes...")
    
    # Simple postal code assignment based on coordinates
    def assign_postal(row):
        x, y = row.geometry.x, row.geometry.y
        
        # Innenstadt (74072)
        if 514500 <= x <= 515500 and 5442500 <= y <= 5443500:
            return '74072', 'Innenstadt'
        # Böckingen (74074)
        elif 515000 <= x <= 516000 and 5443000 <= y <= 5444000:
            return '74074', 'Böckingen'
        # Sontheim (74076)
        elif 515500 <= x <= 516500 and 5442500 <= y <= 5443500:
            return '74076', 'Sontheim'
        # Neckargartach (74078)
        elif 516000 <= x <= 517000 and 5443000 <= y <= 5444000:
            return '74078', 'Neckargartach'
        # Frankenbach (74080)
        elif 514500 <= x <= 515500 and 5443000 <= y <= 5444000:
            return '74080', 'Frankenbach'
        else:
            return 'Unknown', 'Heilbronn'
    
    postal_data = all_locations.apply(assign_postal, axis=1)
    all_locations['postal_code'] = [p[0] for p in postal_data]
    all_locations['area_name'] = [p[1] for p in postal_data]
    
    # Save enhanced version
    print("\n💾 Saving enhanced locations...")
    output_file = processed / 'scored_locations_all_enhanced.geojson'
    all_locations.to_file(output_file, driver='GeoJSON')
    print(f"   ✅ Saved: {output_file}")
    
    # Export to web
    print("\n🌐 Exporting to web format...")
    
    # Add UTM and Lat/Lon
    all_locations['utm_x'] = all_locations.geometry.x
    all_locations['utm_y'] = all_locations.geometry.y
    
    locations_wgs = all_locations.to_crs('EPSG:4326')
    locations_wgs['latitude'] = locations_wgs.geometry.y
    locations_wgs['longitude'] = locations_wgs.geometry.x
    
    # Copy enhanced fields
    for col in ['location_type', 'recommended_species', 'cooling_estimate', 
                'schools_nearby', 'residents_nearby', 'postal_code', 'area_name',
                'utm_x', 'utm_y']:
        if col in all_locations.columns:
            locations_wgs[col] = all_locations[col].values
    
    web_output = Path('web/data/all_locations.geojson')
    locations_wgs.to_file(web_output, driver='GeoJSON')
    print(f"   ✅ Saved web version: {web_output}")
    print(f"   📦 File size: {web_output.stat().st_size / 1024 / 1024:.2f} MB")
    
    # Print summary
    print("\n" + "="*80)
    print("📊 ENHANCEMENT SUMMARY")
    print("="*80)
    print(f"   Total locations: {len(all_locations):,}")
    print(f"   Avg score: {all_locations['final_score'].mean():.2f}")
    print(f"\n   By Postal Code:")
    for postal in sorted(all_locations['postal_code'].unique()):
        if postal != 'Unknown':
            count = len(all_locations[all_locations['postal_code'] == postal])
            avg = all_locations[all_locations['postal_code'] == postal]['final_score'].mean()
            area = all_locations[all_locations['postal_code'] == postal]['area_name'].iloc[0]
            print(f"      {postal} ({area}): {count:,} locations, avg {avg:.1f}")
    
    print("\n✅ ALL LOCATIONS ENHANCED!")
    print("="*80)
    
    return all_locations

if __name__ == "__main__":
    enhance_all_locations()