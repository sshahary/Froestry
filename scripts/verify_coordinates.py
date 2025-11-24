"""
Verify coordinate accuracy - check a sample of high-scoring locations
"""
import geopandas as gpd
from pathlib import Path
import sys
sys.path.append('.')
from src import config

def verify_coordinate_accuracy():
    """Check if coordinates make sense"""
    
    print("="*80)
    print("🎯 VERIFYING COORDINATE ACCURACY")
    print("="*80)
    
    # Load top locations
    top_file = Path(config.DATA_PROCESSED) / 'top_100_enhanced.geojson'
    if not top_file.exists():
        top_file = Path(config.DATA_PROCESSED) / 'top_100_locations.geojson'
    
    if not top_file.exists():
        print("❌ Top locations file not found!")
        return
    
    top_100 = gpd.read_file(top_file)
    
    print(f"\n📊 Loaded {len(top_100)} locations")
    print(f"   CRS: {top_100.crs}")
    
    # Check CRS
    if top_100.crs != 'EPSG:25832':
        print(f"\n⚠️  WARNING: Data is in {top_100.crs}, not EPSG:25832 (UTM32N)")
        print(f"   Converting to EPSG:25832...")
        top_100_utm = top_100.to_crs('EPSG:25832')
    else:
        top_100_utm = top_100
    
    # Convert to WGS84
    top_100_wgs = top_100_utm.to_crs('EPSG:4326')
    
    print(f"\n📐 COORDINATE RANGES:")
    print(f"   UTM X: {top_100_utm.geometry.x.min():.1f} to {top_100_utm.geometry.x.max():.1f}")
    print(f"   UTM Y: {top_100_utm.geometry.y.min():.1f} to {top_100_utm.geometry.y.max():.1f}")
    print(f"   Latitude: {top_100_wgs.geometry.y.min():.6f} to {top_100_wgs.geometry.y.max():.6f}")
    print(f"   Longitude: {top_100_wgs.geometry.x.min():.6f} to {top_100_wgs.geometry.x.max():.6f}")
    
    # Expected ranges for Heilbronn
    print(f"\n✅ EXPECTED RANGES FOR HEILBRONN:")
    print(f"   UTM X: ~514,000 to ~517,000")
    print(f"   UTM Y: ~5,442,000 to ~5,446,000")
    print(f"   Latitude: ~49.12° to ~49.16°N")
    print(f"   Longitude: ~9.19° to ~9.24°E")
    
    # Check if coordinates are within expected range
    utm_x_ok = (514000 <= top_100_utm.geometry.x.min() <= 517000 and 
                514000 <= top_100_utm.geometry.x.max() <= 517000)
    utm_y_ok = (5442000 <= top_100_utm.geometry.y.min() <= 5446000 and 
                5442000 <= top_100_utm.geometry.y.max() <= 5446000)
    
    lat_ok = (49.10 <= top_100_wgs.geometry.y.min() <= 49.18 and 
              49.10 <= top_100_wgs.geometry.y.max() <= 49.18)
    lon_ok = (9.18 <= top_100_wgs.geometry.x.min() <= 9.26 and 
              9.18 <= top_100_wgs.geometry.x.max() <= 9.26)
    
    print(f"\n🔍 COORDINATE VALIDATION:")
    print(f"   UTM X range: {'✅ OK' if utm_x_ok else '❌ OUT OF RANGE'}")
    print(f"   UTM Y range: {'✅ OK' if utm_y_ok else '❌ OUT OF RANGE'}")
    print(f"   Latitude range: {'✅ OK' if lat_ok else '❌ OUT OF RANGE'}")
    print(f"   Longitude range: {'✅ OK' if lon_ok else '❌ OUT OF RANGE'}")
    
    # Show sample of top 5 locations
    print(f"\n📍 TOP 5 LOCATIONS FOR MANUAL VERIFICATION:")
    print("-" * 80)
    
    for idx, row in top_100.head(5).iterrows():
        rank = row.get('rank', idx + 1)
        score = row.get('final_score', 0)
        
        # Get both coordinate systems
        geom_utm = top_100_utm.loc[idx].geometry
        geom_wgs = top_100_wgs.loc[idx].geometry
        
        print(f"\n🏆 Rank #{int(rank)} (Score: {score:.1f}/100)")
        print(f"   UTM32N:  X={geom_utm.x:.2f}, Y={geom_utm.y:.2f}")
        print(f"   WGS84:   Lat={geom_wgs.y:.6f}, Lon={geom_wgs.x:.6f}")
        print(f"   Google:  https://www.google.com/maps?q={geom_wgs.y:.6f},{geom_wgs.x:.6f}")
        print(f"   Verify:  Open this in Google Maps and check if it's in Heilbronn green space")
    
    print("\n" + "="*80)
    print("✅ VERIFICATION COMPLETE")
    print("="*80)
    
    if utm_x_ok and utm_y_ok and lat_ok and lon_ok:
        print("\n✅ Coordinates appear correct - all within expected Heilbronn ranges")
    else:
        print("\n⚠️  COORDINATE MISMATCH DETECTED!")
        print("   Possible issues:")
        print("   • Wrong CRS transformation")
        print("   • Data from different region")
        print("   • X/Y coordinates swapped")

if __name__ == "__main__":
    verify_coordinate_accuracy()