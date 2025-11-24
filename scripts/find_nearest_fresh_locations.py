"""
Find nearest locations using FRESH data only
"""
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from pathlib import Path
import sys
sys.path.append('.')
from src import config

def find_nearest_fresh_locations(lat, lon, n=5, min_score=90):
    """Find nearest HIGH-SCORING locations from FRESH data"""
    
    print("="*80)
    print("🆕 FINDING NEAREST FRESH DATA LOCATIONS")
    print("="*80)
    
    print(f"\n📌 Your Location:")
    print(f"   Latitude:  {lat}")
    print(f"   Longitude: {lon}")
    
    # Create point
    your_point_wgs = Point(lon, lat)
    your_gdf_wgs = gpd.GeoDataFrame([{'geometry': your_point_wgs}], crs='EPSG:4326')
    your_gdf_utm = your_gdf_wgs.to_crs('EPSG:25832')
    your_point_utm = your_gdf_utm.geometry.iloc[0]
    
    # Load fresh locations
    print(f"\n📂 Loading FRESH locations...")
    fresh_file = Path(config.DATA_PROCESSED) / 'scored_locations_fresh.geojson'
    
    if not fresh_file.exists():
        print("   ❌ Fresh locations not found!")
        print("   Please run: python scripts/create_fresh_data_locations.py")
        return
    
    locations = gpd.read_file(fresh_file)
    print(f"   ✅ Loaded {len(locations):,} fresh locations")
    print(f"   🆕 Data Quality: VERIFIED 2020+")
    
    # Filter by score
    high_score = locations[locations['final_score'] >= min_score].copy()
    print(f"   ✅ {len(high_score):,} locations with score >= {min_score}")
    
    # Convert coordinates
    if high_score.crs != 'EPSG:25832':
        locations_utm = high_score.to_crs('EPSG:25832')
    else:
        locations_utm = high_score
    
    locations_wgs = locations_utm.to_crs('EPSG:4326')
    
    # Calculate distances
    distances = locations_utm.geometry.distance(your_point_utm)
    
    # Get nearest
    nearest_indices = distances.nsmallest(n).index
    nearest = high_score.loc[nearest_indices].copy()
    nearest_wgs = locations_wgs.loc[nearest_indices].copy()
    
    nearest['distance_m'] = distances.loc[nearest_indices].values
    nearest_wgs['distance_m'] = distances.loc[nearest_indices].values
    
    # Add lat/lon
    nearest['latitude'] = nearest_wgs.geometry.y
    nearest['longitude'] = nearest_wgs.geometry.x
    
    # Sort by distance
    nearest = nearest.sort_values('distance_m')
    nearest_wgs = nearest_wgs.sort_values('distance_m')
    
    # Display
    print(f"\n🎯 NEAREST {n} FRESH DATA LOCATIONS:")
    print("="*80)
    
    for idx, (i, row) in enumerate(nearest.iterrows(), 1):
        lat_loc = row['latitude']
        lon_loc = row['longitude']
        
        print(f"\n{'🥇' if idx == 1 else '🥈' if idx == 2 else '🥉' if idx == 3 else f'#{idx}'} FRESH LOCATION #{idx}")
        print(f"   🆕 DATA QUALITY: VERIFIED CURRENT (2020+)")
        print(f"   📏 Distance: {row['distance_m']:.0f}m ({row['distance_m']/1000:.2f} km)")
        print(f"   ⭐ Score: {row['final_score']:.1f}/100")
        print(f"   🏆 Rank: #{int(row['rank'])} (in fresh dataset)")
        
        print(f"\n   📊 Breakdown:")
        print(f"      🔥 Heat: {row.get('heat_score', 0):.1f}/100")
        print(f"      📏 Spatial: {row.get('spatial_score', 0):.1f}/100")
        print(f"      👥 Social: {row.get('social_score', 0):.1f}/100")
        print(f"      🚜 Maintenance: {row.get('maintenance_score', 0):.1f}/100")
        
        print(f"\n   📐 Coordinates:")
        print(f"      Lat/Lon: {lat_loc:.6f}, {lon_loc:.6f}")
        print(f"      UTM: X={row.geometry.x:.1f}, Y={row.geometry.y:.1f}")
        
        print(f"\n   🗺️  Navigation:")
        print(f"      Google: https://www.google.com/maps?q={lat_loc},{lon_loc}")
        print(f"      Apple:  http://maps.apple.com/?ll={lat_loc},{lon_loc}")
        
        walk_time = (row['distance_m'] / 1000) / 5 * 60
        print(f"\n   🚶 Walking time: ~{walk_time:.0f} minutes")
    
    # Save CSV
    output_data = []
    for idx, (i, row) in enumerate(nearest.iterrows(), 1):
        output_data.append({
            'Number': idx,
            'Data_Quality': 'VERIFIED FRESH (2020+)',
            'Distance_m': f"{row['distance_m']:.0f}",
            'Score': f"{row['final_score']:.1f}",
            'Rank': int(row['rank']),
            'Latitude': f"{row['latitude']:.6f}",
            'Longitude': f"{row['longitude']:.6f}",
            'Google_Maps': f"https://www.google.com/maps?q={row['latitude']},{row['longitude']}",
        })
    
    df = pd.DataFrame(output_data)
    csv_path = Path(config.DATA_OUTPUTS) / 'nearest_fresh_locations.csv'
    df.to_csv(csv_path, index=False)
    
    print(f"\n💾 Saved: {csv_path}")
    print("\n✅ These locations use ONLY fresh data - high accuracy expected!")
    
    return nearest

if __name__ == "__main__":
    YOUR_LAT = 49.152363551254254
    YOUR_LON = 9.215867312497755
    
    find_nearest_fresh_locations(YOUR_LAT, YOUR_LON, n=5, min_score=90)