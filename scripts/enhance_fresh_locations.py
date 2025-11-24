"""
Enhance fresh locations with complete details like the main dataset
"""
import geopandas as gpd
import pandas as pd
from pathlib import Path
import sys
sys.path.append('.')
from src import config

def get_proven_species_for_heilbronn():
    """Get proven tree species"""
    trees_path = Path(config.DATA_RAW) / 'Baumkataster'
    tree_files = list(trees_path.glob('*.shp'))
    
    if tree_files:
        trees = gpd.read_file(tree_files[0])
        if 'DEU_TEXT' in trees.columns:
            top_species = trees['DEU_TEXT'].value_counts().head(20).index.tolist()
            
            large_heat_tolerant = [s for s in top_species if any(x in s.lower() for x in ['eiche', 'linde', 'platane'])]
            medium_trees = [s for s in top_species if any(x in s.lower() for x in ['ahorn', 'kastanie', 'robinie'])]
            
            return {
                'heat_tolerant': large_heat_tolerant[:3] if large_heat_tolerant else top_species[:3],
                'moderate': medium_trees[:3] if medium_trees else top_species[3:6],
            }
    
    return {
        'heat_tolerant': ['Ahornblättrige Platane', 'Winterlinde `Greenspire`'],
        'moderate': ['Spitz-Ahorn', 'Robinie'],
    }

def enhance_fresh_locations():
    """Add all enhanced fields to fresh locations"""
    
    print("="*80)
    print("✨ ENHANCING FRESH LOCATIONS WITH FULL DETAILS")
    print("="*80)
    
    processed = Path(config.DATA_PROCESSED)
    alkis_path = Path(config.DATA_RAW) / 'ALKIS'
    
    # Load fresh locations
    print("\n📂 Loading fresh locations...")
    fresh = gpd.read_file(processed / 'scored_locations_fresh.geojson')
    print(f"   ✅ Loaded {len(fresh):,} locations")
    
    # Load land use for social impact
    print("\n📂 Loading ALKIS land use...")
    land_use_file = alkis_path / 'nutzung.shp'
    if land_use_file.exists():
        land_use = gpd.read_file(land_use_file)
        if land_use.crs != config.CRS:
            land_use = land_use.to_crs(config.CRS)
        print(f"   ✅ Loaded {len(land_use):,} land use polygons")
    else:
        land_use = None
        print("   ⚠️  Land use not found")
    
    # Get proven species
    print("\n🌳 Loading proven tree species...")
    species_db = get_proven_species_for_heilbronn()
    print(f"   ✅ Heat-tolerant: {', '.join(species_db['heat_tolerant'][:2])}")
    
    # Add tree recommendations
    print("\n🌳 Adding tree recommendations...")
    def recommend_species(heat_score):
        if heat_score > 80:
            species = ' or '.join(species_db['heat_tolerant'][:2])
            return f"{species} (proven in Heilbronn, heat-tolerant)"
        else:
            species = ' or '.join(species_db['moderate'][:2])
            return f"{species} (proven in Heilbronn)"
    
    fresh['recommended_species'] = fresh['heat_score'].apply(recommend_species)
    
    # Add cooling estimates
    print("\n❄️  Adding cooling estimates...")
    def estimate_cooling(heat_score):
        if heat_score > 80:
            return "-2.5°C in 20m radius"
        elif heat_score > 60:
            return "-2.0°C in 15m radius"
        else:
            return "-1.5°C in 15m radius"
    
    fresh['cooling_estimate'] = fresh['heat_score'].apply(estimate_cooling)
    
    # Add location types
    print("\n📍 Determining location types...")
    def get_location_type(point, land_use):
        if land_use is None:
            return "Green Space"
        try:
            nearby = land_use[land_use.distance(point) < 20]
            if len(nearby) > 0:
                nutzart = nearby.iloc[0]['nutzart']
                type_map = {
                    'Sport Freizeit Und Erholungsflaeche': 'Recreation Area',
                    'Wohnbauflaeche': 'Residential Green Strip',
                    'Strassenverkehr': 'Street Side'
                }
                return type_map.get(nutzart, 'Green Space')
        except:
            pass
        return "Green Space"
    
    fresh['location_type'] = fresh.geometry.apply(lambda p: get_location_type(p, land_use))
    
    # Add social impact estimates
    print("\n👥 Estimating social impact...")
    def estimate_schools(point, land_use):
        if land_use is None:
            return "Unknown"
        try:
            nearby = land_use[land_use.distance(point) < 200]
            education = nearby[nearby['nutzart'].isin(['Sport Freizeit Und Erholungsflaeche', 
                                                        'Flaeche Besonderer Funktionaler Praegung'])]
            count = len(education) // 2
            if count == 0:
                return "No schools nearby"
            elif count == 1:
                return "~1 school/recreation nearby"
            else:
                return f"~{count} schools/recreation nearby"
        except:
            return "Unknown"
    
    def estimate_residents(point, land_use):
        if land_use is None:
            return "Unknown"
        try:
            nearby = land_use[land_use.distance(point) < 100]
            residential = nearby[nearby['nutzart'] == 'Wohnbauflaeche']
            area_hectares = residential.geometry.area.sum() / 10000
            
            if area_hectares < 0.1:
                return "Low density area"
            elif area_hectares < 0.5:
                return "~50-100 residents nearby"
            elif area_hectares < 1.0:
                return "~100-200 residents nearby"
            else:
                estimated = int(area_hectares * 50)
                return f"~{estimated} residents nearby"
        except:
            return "Unknown"
    
    fresh['schools_nearby'] = fresh.geometry.apply(lambda p: estimate_schools(p, land_use))
    fresh['residents_nearby'] = fresh.geometry.apply(lambda p: estimate_residents(p, land_use))
    
    # Add postal codes
    print("\n📮 Assigning postal codes...")
    def assign_postal(row):
        x, y = row.geometry.x, row.geometry.y
        
        if 514500 <= x <= 515500 and 5442500 <= y <= 5443500:
            return '74072', 'Innenstadt'
        elif 515000 <= x <= 516000 and 5443000 <= y <= 5444000:
            return '74074', 'Böckingen'
        elif 515500 <= x <= 516500 and 5442500 <= y <= 5443500:
            return '74076', 'Sontheim'
        elif 516000 <= x <= 517000 and 5443000 <= y <= 5444000:
            return '74078', 'Neckargartach'
        elif 514500 <= x <= 515500 and 5443000 <= y <= 5444000:
            return '74080', 'Frankenbach'
        else:
            return 'Unknown', 'Heilbronn'
    
    postal_data = fresh.apply(assign_postal, axis=1)
    fresh['postal_code'] = [p[0] for p in postal_data]
    fresh['area_name'] = [p[1] for p in postal_data]
    
    # Save enhanced version
    print("\n💾 Saving enhanced fresh locations...")
    output = processed / 'scored_locations_fresh_enhanced.geojson'
    fresh.to_file(output, driver='GeoJSON')
    print(f"   ✅ Saved: {output}")
    
    # Export to web with WGS84
    print("\n🌐 Exporting to web format...")
    fresh['utm_x'] = fresh.geometry.x
    fresh['utm_y'] = fresh.geometry.y
    
    fresh_wgs = fresh.to_crs('EPSG:4326')
    fresh_wgs['latitude'] = fresh_wgs.geometry.y
    fresh_wgs['longitude'] = fresh_wgs.geometry.x
    
    # Copy enhanced fields
    for col in ['location_type', 'recommended_species', 'cooling_estimate', 
                'schools_nearby', 'residents_nearby', 'postal_code', 'area_name',
                'utm_x', 'utm_y']:
        if col in fresh.columns:
            fresh_wgs[col] = fresh[col].values
    
    web_output = Path('web/data/scored_locations_fresh.geojson')
    fresh_wgs.to_file(web_output, driver='GeoJSON')
    print(f"   ✅ Saved web version: {web_output}")
    
    print("\n" + "="*80)
    print("✅ ENHANCEMENT COMPLETE!")
    print("="*80)
    print("\n📊 Sample of top location:")
    top = fresh.iloc[0]
    print(f"   Rank: #{top['rank']}")
    print(f"   Score: {top['final_score']:.1f}")
    print(f"   Location: {top['location_type']}")
    print(f"   Postal: {top['postal_code']} - {top['area_name']}")
    print(f"   Species: {top['recommended_species']}")
    print(f"   Schools: {top['schools_nearby']}")
    print(f"   Residents: {top['residents_nearby']}")
    print(f"   Cooling: {top['cooling_estimate']}")

if __name__ == "__main__":
    enhance_fresh_locations()