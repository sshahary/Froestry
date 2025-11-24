"""
Convert coordinates to Lat/Lon (No external API needed)
"""
import geopandas as gpd
import pandas as pd
from pathlib import Path
import sys
sys.path.append('.')
from src import config

def convert_to_latlon():
    """Convert top locations to lat/lon for navigation"""
    
    print("="*80)
    print("📍 CONVERTING COORDINATES TO LAT/LON FOR NAVIGATION")
    print("="*80)
    
    processed = Path(config.DATA_PROCESSED)
    outputs = Path(config.DATA_OUTPUTS)
    
    # Load enhanced locations
    print("\n📂 Loading top 100 locations...")
    top_100 = gpd.read_file(processed / 'top_100_enhanced.geojson')
    
    # Convert to WGS84 (Lat/Lon)
    print("🌐 Converting to WGS84 (Lat/Lon)...")
    top_100_wgs = top_100.to_crs('EPSG:4326')
    
    # Add lat/lon columns
    top_100['latitude'] = top_100_wgs.geometry.y
    top_100['longitude'] = top_100_wgs.geometry.x
    
    # Create readable location description from postal code + area
    top_100['location_description'] = top_100.apply(
        lambda row: f"{row.get('location_type', 'Green Space')} in {row.get('area_name', 'Heilbronn')} ({row.get('postal_code', 'Unknown')})",
        axis=1
    )
    
    print(f"   ✅ Coordinates converted!")
    
    # Save updated version
    print("\n💾 Saving with lat/lon...")
    
    output_path = processed / 'top_100_with_coordinates.geojson'
    top_100.to_file(output_path, driver='GeoJSON')
    print(f"   ✅ Saved: {output_path}")
    
    # Create navigation-ready CSV
    print("\n📊 Creating navigation CSV...")
    
    nav_data = []
    for idx, row in top_100.head(20).iterrows():
        nav_data.append({
            'Rank': int(row['rank']),
            'Score': round(row['final_score'], 1),
            'Latitude': round(row['latitude'], 6),
            'Longitude': round(row['longitude'], 6),
            'Postal_Code': row.get('postal_code', 'Unknown'),
            'Area': row.get('area_name', 'Unknown'),
            'Location_Type': row.get('location_type', 'Green Space'),
            'Heat_Score': round(row['heat_score'], 1),
            'Recommended_Species': row.get('recommended_species', 'Oak or Linden'),
            'Cooling_Effect': row.get('cooling_estimate', '-2.0°C'),
            'Google_Maps_Link': f"https://www.google.com/maps?q={row['latitude']:.6f},{row['longitude']:.6f}",
            'Apple_Maps_Link': f"http://maps.apple.com/?ll={row['latitude']:.6f},{row['longitude']:.6f}",
            'Coordinates_UTM': f"{row.geometry.x:.1f}, {row.geometry.y:.1f}"
        })
    
    nav_df = pd.DataFrame(nav_data)
    
    csv_path = outputs / 'top_100_detailed.csv'
    nav_df.to_csv(csv_path, index=False)
    print(f"   ✅ Saved: {csv_path}")
    
    # Print top 5 with navigation info
    print("\n" + "="*80)
    print("🗺️  TOP 5 LOCATIONS - READY FOR FIELD VERIFICATION")
    print("="*80)
    
    for idx, row in nav_df.head(5).iterrows():
        print(f"\n🏆 RANK #{row['Rank']}: Score {row['Score']}/100")
        print(f"   📍 Location: {row['Location_Type']} in {row['Area']}")
        print(f"   📮 Postal Code: {row['Postal_Code']}")
        print(f"   🔥 Heat Priority: {row['Heat_Score']}/100")
        print(f"   🌳 Recommended: {row['Recommended_Species']}")
        print(f"   ❄️  Cooling: {row['Cooling_Effect']}")
        print(f"\n   📱 NAVIGATION:")
        print(f"   Latitude:  {row['Latitude']}")
        print(f"   Longitude: {row['Longitude']}")
        print(f"   Google Maps: {row['Google_Maps_Link']}")
        print(f"   Apple Maps:  {row['Apple_Maps_Link']}")
    
    # Create verification guide
    print("\n" + "="*80)
    print("📸 FIELD VERIFICATION GUIDE")
    print("="*80)
    print("""
    HOW TO VERIFY THE MODEL:
    
    1. Open: data/outputs/TOP_20_NAVIGATION.csv
    
    2. Choose a location (Rank #1 recommended!)
    
    3. NAVIGATE:
       • Copy the Google_Maps_Link or Apple_Maps_Link
       • Or enter Latitude/Longitude directly in maps app
       • Drive/walk to the location
    
    4. AT THE LOCATION, TAKE PHOTOS OF:
       ✓ The ground surface (should be bare/paved if heat score is high)
       ✓ The surrounding area (should have space for a tree)
       ✓ Nearby buildings (proving residential proximity)
       ✓ Any schools/recreation areas (proving social impact)
       ✓ Road access (proving maintenance access)
    
    5. COMPARE WITH MODEL:
       • Open: web/final_ranked_map.html
       • Find the location on the map
       • Check if heat map shows RED at this spot
       • Verify the scoring makes sense
    
    6. FOR DEMO:
       • Show photos side-by-side with map
       • "The model predicted this was hot and bare - and it is!"
       • "Perfect spot for a tree that will cool this area"
    
    🎯 This proves your AI works in the real world!
    """)
    
    # Create a simple HTML navigation page
    print("\n🌐 Creating navigation webpage...")
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Heilbronn Tree Planting - Navigation</title>
        <meta charset="utf-8"> <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: #f5f5f5;
            }}
            .header {{
                background: linear-gradient(135deg, #2e7d32 0%, #66bb6a 100%);
                color: white;
                padding: 30px;
                border-radius: 10px;
                margin-bottom: 20px;
            }}
            .location {{
                background: white;
                padding: 20px;
                margin: 10px 0;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .rank {{
                background: gold;
                color: black;
                padding: 5px 15px;
                border-radius: 20px;
                font-weight: bold;
                display: inline-block;
            }}
            .score {{
                font-size: 24px;
                font-weight: bold;
                color: #2e7d32;
            }}
            .nav-button {{
                display: inline-block;
                padding: 10px 20px;
                margin: 5px;
                background: #2e7d32;
                color: white;
                text-decoration: none;
                border-radius: 5px;
            }}
            .nav-button:hover {{
                background: #1b5e20;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🌳 Heilbronn Tree Planting Navigation</h1>
            <p>Top 20 locations - Ready for field verification</p>
        </div>
    """
    
    for idx, row in nav_df.head(20).iterrows():
        html_content += f"""
        <div class="location">
            <span class="rank">#{row['Rank']}</span>
            <span class="score">{row['Score']}/100</span>
            <h3>📍 {row['Location_Type']} in {row['Area']}</h3>
            <p>
                <strong>Postal Code:</strong> {row['Postal_Code']}<br>
                <strong>Heat Priority:</strong> {row['Heat_Score']}/100 🔥<br>
                <strong>Recommended:</strong> {row['Recommended_Species']}<br>
                <strong>Cooling Effect:</strong> {row['Cooling_Effect']}
            </p>
            <p>
                <strong>📱 Navigate:</strong><br>
                Lat: {row['Latitude']} | Lon: {row['Longitude']}<br>
                <a href="{row['Google_Maps_Link']}" target="_blank" class="nav-button">🗺️ Google Maps</a>
                <a href="{row['Apple_Maps_Link']}" target="_blank" class="nav-button">🍎 Apple Maps</a>
            </p>
        </div>
        """
    
    html_content += """
    </body>
    </html>
    """
    
    html_path = Path('web') / 'navigation.html'
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"   ✅ Saved: {html_path}")
    print(f"\n🌐 Open in browser: file://{html_path.absolute()}")
    
    print("\n" + "="*80)
    print("✅ NAVIGATION READY!")
    print("="*80)
    print(f"\n📁 Files created:")
    print(f"   • {csv_path.name} - CSV with all navigation data")
    print(f"   • {html_path.name} - Click to open navigation page")
    print(f"\n🎯 Choose any location and go verify the model!")
    
    return top_100

if __name__ == "__main__":
    convert_to_latlon()