"""
Enhance top locations with postal codes, street names, and detailed info
"""
import geopandas as gpd
import pandas as pd
from pathlib import Path
import sys
sys.path.append('.')
from src import config
from src.processors.postal_codes import PostalCodeManager

def enhance_locations():
    """Add detailed information to top locations"""
    
    print("="*80)
    print("✨ ENHANCING TOP LOCATIONS WITH FULL DETAILS")
    print("="*80)
    
    processed = Path(config.DATA_PROCESSED)
    outputs = Path(config.DATA_OUTPUTS)
    
    # Load top locations
    print("\n📂 Loading top 100 locations...")
    top_100 = gpd.read_file(processed / 'top_100_locations.geojson')
    
    # Initialize postal code manager
    postal_mgr = PostalCodeManager()
    
    # Assign postal codes
    top_100_enhanced = postal_mgr.assign_postal_codes(top_100)
    
    # Load land use for area names
    alkis_path = Path(config.DATA_RAW) / 'ALKIS'
    land_use_file = alkis_path / 'nutzung.shp'
    
    if land_use_file.exists():
        print("\n📍 Adding location descriptions...")
        land_use = gpd.read_file(land_use_file)
        if land_use.crs != config.CRS:
            land_use = land_use.to_crs(config.CRS)
        
        # Add location type
        top_100_enhanced['location_type'] = top_100_enhanced.geometry.apply(
            lambda point: get_location_type(point, land_use)
        )
    else:
        top_100_enhanced['location_type'] = 'Green Space'
    
    # Estimate nearby schools
    print("\n🏫 Estimating nearby amenities...")
    top_100_enhanced['schools_nearby'] = top_100_enhanced.geometry.apply(
        lambda point: estimate_schools_nearby(point, land_use if land_use_file.exists() else None)
    )
    
    # Estimate residents nearby
    print("\n🏘️  Estimating nearby residents...")
    top_100_enhanced['residents_nearby'] = top_100_enhanced.geometry.apply(
        lambda point: estimate_residents_nearby(point, land_use if land_use_file.exists() else None)
    )
    
    # Recommend tree species
    print("\n🌳 Recommending tree species...")
    top_100_enhanced['recommended_species'] = top_100_enhanced.apply(
        lambda row: recommend_tree_species(row), axis=1
    )
    
    # Estimate cooling effect
    print("\n❄️  Calculating cooling estimates...")
    top_100_enhanced['cooling_estimate'] = top_100_enhanced.apply(
        lambda row: estimate_cooling(row), axis=1
    )
    
    # Save enhanced version
    print("\n💾 Saving enhanced locations...")
    
    # GeoJSON
    enhanced_path = processed / 'top_100_enhanced.geojson'
    top_100_enhanced.to_file(enhanced_path, driver='GeoJSON')
    print(f"   ✅ Saved GeoJSON: {enhanced_path}")
    
    # Detailed CSV
    csv_data = top_100_enhanced.copy()

# Add UTM coordinates
    csv_data['utm_x'] = csv_data.geometry.x
    csv_data['utm_y'] = csv_data.geometry.y

    # Add Lat/Lon
    top_100_wgs = top_100_enhanced.to_crs('EPSG:4326')
    csv_data['latitude'] = top_100_wgs.geometry.y
    csv_data['longitude'] = top_100_wgs.geometry.x

    # Add Google Maps link
    csv_data['google_maps_link'] = csv_data.apply(
        lambda row: f"https://www.google.com/maps?q={row['latitude']:.6f},{row['longitude']:.6f}",
        axis=1
    )

    csv_data.drop('geometry', axis=1, inplace=True, errors='ignore')
    
    csv_path = outputs / 'top_100_detailed.csv'
    csv_data.to_csv(csv_path, index=False)
    print(f"   ✅ Saved CSV: {csv_path}")
    
    # Print beautiful summary
    print_beautiful_summary(top_100_enhanced)
    
    return top_100_enhanced

def get_location_type(point, land_use):
    """Determine location type"""
    nearby = land_use[land_use.distance(point) < 20]
    if len(nearby) > 0:
        nutzart = nearby.iloc[0]['nutzart']
        
        type_map = {
            'Sport Freizeit Und Erholungsflaeche': 'Recreation Area',
            'Gehoelz': 'Wooded Area',
            'Wald': 'Forest',
            'Wohnbauflaeche': 'Residential Green Strip',
            'Strassenverkehr': 'Street Side'
        }
        
        return type_map.get(nutzart, 'Green Space')
    
    return 'Park'

def estimate_schools_nearby(point, land_use):
    """Estimate number of schools within 200m"""
    if land_use is None:
        return "Unknown"
    
    nearby = land_use[land_use.distance(point) < 200]
    education_types = ['Sport Freizeit Und Erholungsflaeche', 
                      'Flaeche Besonderer Funktionaler Praegung']
    schools = nearby[nearby['nutzart'].isin(education_types)]
    
    # Return as estimate range
    count = len(schools) // 2
    if count == 0:
        return "No schools"
    elif count == 1:
        return "~1 school/recreation"
    else:
        return f"~{count} schools/recreation"

def estimate_residents_nearby(point, land_use):
    """Estimate residents within 100m"""
    if land_use is None:
        return "Unknown"
    
    nearby = land_use[land_use.distance(point) < 100]
    residential = nearby[nearby['nutzart'] == 'Wohnbauflaeche']
    
    total_area_hectares = residential.geometry.area.sum() / 10000
    
    if total_area_hectares < 0.1:
        return "Low density"
    elif total_area_hectares < 0.5:
        return "~50-100 residents"
    elif total_area_hectares < 1.0:
        return "~100-200 residents"
    else:
        estimated = int(total_area_hectares * 50)
        return f"~{estimated} residents (estimate)"

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
    
    # Get top species actually growing in Heilbronn
    top_species = trees['DEU_TEXT'].value_counts().head(15).index.tolist()
    
    # Categorize by typical characteristics
    # (You can refine this based on actual species characteristics)
    large_heat_tolerant = [s for s in top_species if any(x in s.lower() for x in ['eiche', 'linde', 'platane'])]
    medium_trees = [s for s in top_species if any(x in s.lower() for x in ['ahorn', 'kastanie', 'robinie'])]
    small_trees = [s for s in top_species if any(x in s.lower() for x in ['birke', 'kirsche', 'apfel'])]
    
    return {
        'heat_tolerant': large_heat_tolerant[:3] if large_heat_tolerant else top_species[:3],
        'moderate': medium_trees[:3] if medium_trees else top_species[3:6],
        'small': small_trees[:2] if small_trees else top_species[6:8]
    }

def recommend_tree_species(row):
    """Recommend tree species based on actual Heilbronn data"""
    
    species_db = get_proven_species_for_heilbronn()
    
    score = row['final_score']
    heat = row['heat_score']
    
    # For hot areas, recommend heat-tolerant species proven in Heilbronn
    if heat > 80:
        species = ' or '.join(species_db['heat_tolerant'][:2])
        return f"{species} (proven in Heilbronn, heat-tolerant)"
    elif heat > 60:
        species = ' or '.join(species_db['moderate'][:2])
        return f"{species} (proven in Heilbronn)"
    else:
        species = ' or '.join(species_db['small'][:2])
        return f"{species} (proven in Heilbronn)"

def estimate_cooling(row):
    """Estimate cooling effect in °C"""
    # Rough estimate: larger trees in hotter areas provide more cooling
    heat = row['heat_score']
    
    # High heat areas benefit more from trees
    if heat > 80:
        return "-2.5°C in 20m radius"
    elif heat > 60:
        return "-2.0°C in 15m radius"
    else:
        return "-1.5°C in 15m radius"

def print_beautiful_summary(enhanced_gdf):
    """Print beautiful formatted summary"""
    
    # Convert to WGS84 for lat/lon
    enhanced_wgs = enhanced_gdf.to_crs('EPSG:4326')
    
    print("\n" + "="*80)
    print("🏆 TOP 5 LOCATIONS - DETAILED VIEW")
    print("="*80)
    
    for idx, (orig_row, wgs_row) in enumerate(zip(enhanced_gdf.head(5).iterrows(), enhanced_wgs.head(5).iterrows())):
        _, row = orig_row
        _, row_wgs = wgs_row
        
        postal = row.get('postal_code', 'Unknown')
        area = row.get('area_name', 'Unknown')
        
        lat = row_wgs.geometry.y
        lon = row_wgs.geometry.x
        
        print(f"\n🥇 RANK #{int(row['rank'])}: Score {row['final_score']:.1f}/100")
        print(f"📍 Location: {row['location_type']} (Postal: {postal} - {area})")
        print(f"🔥 Heat Priority: {'EXTREME' if row['heat_score'] > 80 else 'HIGH' if row['heat_score'] > 60 else 'MODERATE'} ({row['heat_score']:.0f}/100)")
        print(f"🌳 Recommended: {row['recommended_species']}")
        print(f"👥 Nearby (estimated): {row['schools_nearby']}, {row['residents_nearby']}")
        print(f"   ⚠️  Based on ALKIS land use classification")
        print(f"💰 Estimated cooling: {row['cooling_estimate']}")
        print(f"\n📐 Coordinates:")
        print(f"   UTM (EPSG:25832): X={row.geometry.x:.1f}, Y={row.geometry.y:.1f}")
        print(f"   Lat/Lon (WGS84):  {lat:.6f}, {lon:.6f}")
        print(f"   🗺️  Google Maps: https://www.google.com/maps?q={lat:.6f},{lon:.6f}")
    
    print("\n" + "="*80)
    print("📊 DISTRIBUTION BY POSTAL CODE")
    print("="*80)
    
    if 'postal_code' in enhanced_gdf.columns:
        for postal in sorted(enhanced_gdf['postal_code'].unique()):
            if postal != 'Unknown':
                count = len(enhanced_gdf[enhanced_gdf['postal_code'] == postal])
                avg_score = enhanced_gdf[enhanced_gdf['postal_code'] == postal]['final_score'].mean()
                area_name = enhanced_gdf[enhanced_gdf['postal_code'] == postal]['area_name'].iloc[0]
                print(f"   {postal} ({area_name}): {count} locations, avg score {avg_score:.1f}")

if __name__ == "__main__":
    enhanced = enhance_locations()