"""
Find nearest HIGH-SCORING tree planting locations to a given coordinate
"""
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from pathlib import Path
import sys
sys.path.append('.')
from src import config

def find_nearest_locations(lat, lon, n=5, min_score=95):
    """
    Find N nearest HIGH-SCORING tree planting locations to given coordinates
    
    Args:
        lat: Latitude (WGS84)
        lon: Longitude (WGS84)
        n: Number of nearest locations to find
        min_score: Minimum score threshold (default 95)
    """
    
    print("="*80)
    print("📍 FINDING NEAREST HIGH-SCORING TREE PLANTING LOCATIONS")
    print("="*80)
    
    # Your location
    print(f"\n📌 Your Location:")
    print(f"   Latitude:  {lat}")
    print(f"   Longitude: {lon}")
    
    # Create point in WGS84
    your_point_wgs = Point(lon, lat)
    your_gdf_wgs = gpd.GeoDataFrame([{'geometry': your_point_wgs}], crs='EPSG:4326')
    
    # Convert to UTM for accurate distance calculation
    your_gdf_utm = your_gdf_wgs.to_crs('EPSG:25832')
    your_point_utm = your_gdf_utm.geometry.iloc[0]
    
    print(f"   UTM: X={your_point_utm.x:.1f}, Y={your_point_utm.y:.1f}")
    
    # Load all enhanced locations
    print(f"\n📂 Loading tree locations...")
    web_data = Path('web/data')
    
    # Try to load the enhanced data
    data_file = web_data / 'all_locations.geojson'
    
    if not data_file.exists():
        # Try processed directory
        data_file = Path(config.DATA_PROCESSED) / 'scored_locations_all_enhanced.geojson'
        
    if not data_file.exists():
        # Try regular scored locations
        data_file = Path(config.DATA_PROCESSED) / 'scored_locations_all.geojson'
    
    if not data_file.exists():
        print("   ❌ No location data found!")
        print("   Please run: python scripts/enhance_ALL_locations.py")
        return
    
    locations = gpd.read_file(data_file)
    print(f"   ✅ Loaded {len(locations):,} total locations")
    
    # Filter by minimum score
    print(f"\n🎯 Filtering for score >= {min_score}...")
    high_score_locations = locations[locations['final_score'] >= min_score].copy()
    print(f"   ✅ Found {len(high_score_locations):,} locations with score >= {min_score}")
    
    if len(high_score_locations) == 0:
        print(f"\n   ⚠️  No locations found with score >= {min_score}")
        print(f"   Trying with lower threshold...")
        
        # Try progressively lower scores
        for threshold in [90, 85, 80, 75, 70]:
            high_score_locations = locations[locations['final_score'] >= threshold].copy()
            if len(high_score_locations) >= n:
                print(f"   ✅ Found {len(high_score_locations):,} locations with score >= {threshold}")
                min_score = threshold
                break
    
    # Convert to WGS84 if not already
    if high_score_locations.crs != 'EPSG:4326':
        locations_wgs = high_score_locations.to_crs('EPSG:4326')
    else:
        locations_wgs = high_score_locations
    
    # Also need UTM for distance calculation
    if high_score_locations.crs != 'EPSG:25832':
        locations_utm = high_score_locations.to_crs('EPSG:25832')
    else:
        locations_utm = high_score_locations
    
    # Calculate distances in UTM (meters)
    print(f"\n📏 Calculating distances...")
    distances = locations_utm.geometry.distance(your_point_utm)
    
    # Get nearest N
    nearest_indices = distances.nsmallest(n).index
    nearest_locations = high_score_locations.loc[nearest_indices].copy()
    nearest_locations_wgs = locations_wgs.loc[nearest_indices].copy()
    
    # Add distance column
    nearest_locations['distance_m'] = distances.loc[nearest_indices].values
    nearest_locations_wgs['distance_m'] = distances.loc[nearest_indices].values
    
    # Add lat/lon if not present
    if 'latitude' not in nearest_locations.columns:
        nearest_locations['latitude'] = nearest_locations_wgs.geometry.y
        nearest_locations['longitude'] = nearest_locations_wgs.geometry.x
    
    # Sort by distance
    nearest_locations = nearest_locations.sort_values('distance_m')
    nearest_locations_wgs = nearest_locations_wgs.sort_values('distance_m')
    
    # Display results
    print(f"\n🎯 Found {n} Nearest HIGH-SCORING Locations (score >= {min_score}):")
    print("="*80)
    
    for idx, (i, row) in enumerate(nearest_locations.iterrows(), 1):
        lat_loc = row.get('latitude', nearest_locations_wgs.loc[i, 'geometry'].y)
        lon_loc = row.get('longitude', nearest_locations_wgs.loc[i, 'geometry'].x)
        
        print(f"\n{'🥇' if idx == 1 else '🥈' if idx == 2 else '🥉' if idx == 3 else f'#{idx}'} LOCATION #{idx}")
        print(f"   Distance: {row['distance_m']:.0f} meters ({row['distance_m']/1000:.2f} km)")
        print(f"   ⭐ Score: {row.get('final_score', 0):.1f}/100 {'🔥' if row.get('final_score', 0) >= 95 else '✅'}")
        if 'rank' in row:
            print(f"   🏆 Overall Rank: #{int(row['rank'])} out of 114,982")
        
        # Scoring breakdown
        print(f"\n   📊 Scoring Breakdown:")
        print(f"      🔥 Heat Priority: {row.get('heat_score', 0):.1f}/100 (40% weight)")
        print(f"      📏 Spatial Quality: {row.get('spatial_score', 0):.1f}/100 (30% weight)")
        print(f"      👥 Social Impact: {row.get('social_score', 0):.1f}/100 (20% weight)")
        print(f"      🚜 Maintenance: {row.get('maintenance_score', 0):.1f}/100 (10% weight)")
        
        # Location details
        postal = row.get('postal_code', 'Unknown')
        area = row.get('area_name', 'Unknown')
        loc_type = row.get('location_type', 'Green Space')
        
        print(f"\n   📍 Location Details:")
        print(f"      Type: {loc_type}")
        print(f"      Area: {postal} - {area}")
        
        # Species recommendation
        if 'recommended_species' in row and pd.notna(row['recommended_species']):
            species = row['recommended_species']
            print(f"      🌳 Recommended: {species}")
        
        # Social impact
        if 'schools_nearby' in row and pd.notna(row['schools_nearby']):
            print(f"      🏫 Schools: {row['schools_nearby']}")
        if 'residents_nearby' in row and pd.notna(row['residents_nearby']):
            print(f"      👥 Residents: {row['residents_nearby']}")
        
        if 'cooling_estimate' in row and pd.notna(row['cooling_estimate']):
            print(f"      ❄️  Cooling: {row['cooling_estimate']}")
        
        # Coordinates
        print(f"\n   📐 Coordinates:")
        print(f"      Lat/Lon: {lat_loc:.6f}, {lon_loc:.6f}")
        if 'utm_x' in row:
            print(f"      UTM: X={row['utm_x']:.1f}, Y={row['utm_y']:.1f}")
        
        # Navigation
        google_maps = f"https://www.google.com/maps?q={lat_loc},{lon_loc}"
        apple_maps = f"http://maps.apple.com/?ll={lat_loc},{lon_loc}"
        
        print(f"\n   🗺️  Navigation:")
        print(f"      Google Maps: {google_maps}")
        print(f"      Apple Maps:  {apple_maps}")
        
        # Walking/driving time estimate
        walk_time_min = (row['distance_m'] / 1000) / 5 * 60
        drive_time_min = (row['distance_m'] / 1000) / 30 * 60
        
        print(f"\n   🚶 Estimated Travel Time:")
        print(f"      Walking (5 km/h): ~{walk_time_min:.0f} minutes")
        print(f"      Driving (30 km/h): ~{drive_time_min:.0f} minutes")
    
    # Save to CSV for easy reference
    print("\n" + "="*80)
    print("💾 Saving to CSV...")
    
    output_data = []
    for idx, (i, row) in enumerate(nearest_locations.iterrows(), 1):
        lat_loc = row.get('latitude', nearest_locations_wgs.loc[i, 'geometry'].y)
        lon_loc = row.get('longitude', nearest_locations_wgs.loc[i, 'geometry'].x)
        
        output_data.append({
            'Number': idx,
            'Distance_m': f"{row['distance_m']:.0f}",
            'Distance_km': f"{row['distance_m']/1000:.2f}",
            'Walking_Minutes': f"{(row['distance_m'] / 1000) / 5 * 60:.0f}",
            'Driving_Minutes': f"{(row['distance_m'] / 1000) / 30 * 60:.0f}",
            'Final_Score': f"{row.get('final_score', 0):.1f}",
            'Rank': int(row.get('rank', 0)) if 'rank' in row else 'N/A',
            'Heat_Score': f"{row.get('heat_score', 0):.1f}",
            'Spatial_Score': f"{row.get('spatial_score', 0):.1f}",
            'Social_Score': f"{row.get('social_score', 0):.1f}",
            'Maintenance_Score': f"{row.get('maintenance_score', 0):.1f}",
            'Location_Type': row.get('location_type', 'Green Space'),
            'Postal_Code': row.get('postal_code', 'Unknown'),
            'Area': row.get('area_name', 'Unknown'),
            'Recommended_Species': row.get('recommended_species', 'Oak or Linden'),
            'Schools_Nearby': row.get('schools_nearby', 'Unknown'),
            'Residents_Nearby': row.get('residents_nearby', 'Unknown'),
            'Cooling_Estimate': row.get('cooling_estimate', '-2.0°C'),
            'Latitude': f"{lat_loc:.6f}",
            'Longitude': f"{lon_loc:.6f}",
            'Google_Maps': f"https://www.google.com/maps?q={lat_loc},{lon_loc}",
            'Apple_Maps': f"http://maps.apple.com/?ll={lat_loc},{lon_loc}"
        })
    
    df = pd.DataFrame(output_data)
    csv_path = Path(config.DATA_OUTPUTS) / f'nearest_{n}_high_score_locations.csv'
    df.to_csv(csv_path, index=False)
    
    print(f"   ✅ Saved: {csv_path}")
    
    # Create quick HTML map
    print("\n🌐 Creating interactive map...")
    create_nearest_map(your_point_wgs, nearest_locations_wgs, lat, lon, min_score)
    
    print("\n" + "="*80)
    print("✅ NEAREST HIGH-SCORING LOCATIONS READY!")
    print("="*80)
    print(f"\n📱 Quick Actions:")
    print(f"   1. Open CSV: {csv_path}")
    print(f"   2. Open Map: web/nearest_locations.html")
    print(f"   3. Navigate to CLOSEST: #{1}, {nearest_locations.iloc[0]['distance_m']:.0f}m away")
    print(f"      Score: {nearest_locations.iloc[0]['final_score']:.1f}/100")
    
    print(f"\n📸 Photography Checklist for Location #1:")
    print(f"   ✓ Wide shot showing the area")
    print(f"   ✓ Close-up of bare/hot surface (proving heat score {nearest_locations.iloc[0].get('heat_score', 0):.0f}/100)")
    print(f"   ✓ Available space where tree could go")
    print(f"   ✓ Nearby buildings/context")
    print(f"   ✓ Your phone GPS showing coordinates")
    print(f"   ✓ Reference object for scale (yourself, car, etc.)")
    
    print(f"\n💡 Why This Location Is Perfect:")
    if nearest_locations.iloc[0].get('heat_score', 0) >= 95:
        print(f"   • EXTREME heat priority - visibly bare/hot surface")
    if nearest_locations.iloc[0].get('spatial_score', 0) >= 95:
        print(f"   • Perfect spacing and available area")
    if nearest_locations.iloc[0].get('social_score', 0) >= 80:
        print(f"   • High social impact - benefits many residents")
    
    return nearest_locations

def create_nearest_map(your_point, nearest_locations, your_lat, your_lon, min_score):
    """Create interactive map showing nearest locations"""
    
    import folium
    
    # Create map centered on your location
    m = folium.Map(
        location=[your_lat, your_lon],
        zoom_start=14,
        tiles='OpenStreetMap'
    )
    
    # Add your location with bigger icon
    folium.Marker(
        location=[your_lat, your_lon],
        popup=folium.Popup('<h3>📍 Your Current Location</h3><p>Start here!</p>', max_width=200),
        icon=folium.Icon(color='red', icon='user', prefix='fa', icon_size=(40, 40)),
        tooltip='You are here!'
    ).add_to(m)
    
    # Add circle showing your position
    folium.Circle(
        location=[your_lat, your_lon],
        radius=50,
        color='red',
        fill=True,
        fillOpacity=0.2
    ).add_to(m)
    
    # Add nearest locations
    for idx, row in nearest_locations.iterrows():
        lat = row.geometry.y
        lon = row.geometry.x
        
        score = row.get('final_score', 0)
        rank_num = nearest_locations.index.get_loc(idx) + 1
        
        # Determine icon
        if rank_num == 1:
            icon_color = 'darkgreen'
            icon_icon = 'star'
        else:
            icon_color = 'green'
            icon_icon = 'tree'
        
        popup_html = f"""
        <div style="min-width: 280px;">
            <h3 style="color: darkgreen;">{'🥇' if rank_num == 1 else '🥈' if rank_num == 2 else '🥉' if rank_num == 3 else f'#{rank_num}'} Location #{rank_num}</h3>
            <p><strong>Distance:</strong> {row['distance_m']:.0f}m ({row['distance_m']/1000:.2f} km)</p>
            <p><strong>⭐ Score:</strong> {score:.1f}/100</p>
            <hr>
            <p><strong>🔥 Heat:</strong> {row.get('heat_score', 0):.1f}/100</p>
            <p><strong>📏 Spatial:</strong> {row.get('spatial_score', 0):.1f}/100</p>
            <p><strong>👥 Social:</strong> {row.get('social_score', 0):.1f}/100</p>
            <p><strong>🚜 Maintenance:</strong> {row.get('maintenance_score', 0):.1f}/100</p>
            <hr>
            <p><strong>Type:</strong> {row.get('location_type', 'Green Space')}</p>
            <p><strong>Area:</strong> {row.get('postal_code', 'Unknown')} - {row.get('area_name', 'Unknown')}</p>
            <a href="https://www.google.com/maps?q={lat},{lon}" target="_blank"
               style="display: inline-block; margin-top: 10px; padding: 8px 15px;
                      background: green; color: white; text-decoration: none; border-radius: 5px;">
                🗺️ Navigate Here
            </a>
        </div>
        """
        
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=320),
            icon=folium.Icon(color=icon_color, icon=icon_icon, prefix='fa'),
            tooltip=f'#{rank_num}: {row["distance_m"]:.0f}m - Score {score:.1f}'
        ).add_to(m)
        
        # Draw line from you to location
        folium.PolyLine(
            locations=[[your_lat, your_lon], [lat, lon]],
            color='darkgreen' if rank_num == 1 else 'green',
            weight=3 if rank_num == 1 else 2,
            opacity=0.7,
            dash_array='10, 5'
        ).add_to(m)
    
    # Add legend
    legend_html = f'''
    <div style="position: fixed; top: 10px; right: 10px; 
                background: white; padding: 15px; border-radius: 10px;
                box-shadow: 0 0 10px rgba(0,0,0,0.3); z-index: 1000;">
        <h4 style="margin: 0 0 10px 0; color: darkgreen;">High-Score Locations</h4>
        <p style="margin: 5px 0;"><strong>Min Score:</strong> {min_score}/100</p>
        <p style="margin: 5px 0;"><span style="color: red;">●</span> Your Location</p>
        <p style="margin: 5px 0;"><span style="color: darkgreen;">⭐</span> Closest Spot</p>
        <p style="margin: 5px 0;"><span style="color: green;">🌳</span> Other Spots</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Save
    output_file = 'web/nearest_locations.html'
    m.save(output_file)
    print(f"   ✅ Map saved: {output_file}")

if __name__ == "__main__":
    # Your current coordinates
    YOUR_LAT = 49.138
    YOUR_LON = 9.226
    
    # Find 5 nearest locations with score >= 95
    find_nearest_locations(YOUR_LAT, YOUR_LON, n=5, min_score=95)