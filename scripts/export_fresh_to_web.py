"""
Export fresh locations to web-friendly WGS84 format
"""
import geopandas as gpd
from pathlib import Path
import sys
sys.path.append('.')
from src import config

print("="*80)
print("🌐 EXPORTING FRESH DATA TO WEB FORMAT (WGS84)")
print("="*80)

processed = Path(config.DATA_PROCESSED)
web_data = Path('web/data')
web_data.mkdir(exist_ok=True)

# Load fresh locations
print("\n📂 Loading fresh locations...")
fresh = gpd.read_file(processed / 'scored_locations_fresh.geojson')
print(f"   ✅ Loaded {len(fresh):,} locations")
print(f"   Current CRS: {fresh.crs}")

# Add UTM coordinates as attributes
print("\n📐 Adding coordinate fields...")
fresh['utm_x'] = fresh.geometry.x
fresh['utm_y'] = fresh.geometry.y

# Convert to WGS84
print("\n🌐 Converting to WGS84...")
if fresh.crs != 'EPSG:4326':
    fresh_wgs = fresh.to_crs('EPSG:4326')
else:
    fresh_wgs = fresh

# Add lat/lon as attributes
fresh_wgs['latitude'] = fresh_wgs.geometry.y
fresh_wgs['longitude'] = fresh_wgs.geometry.x

print(f"   ✅ Converted to WGS84")
print(f"   Lat range: {fresh_wgs.geometry.y.min():.6f} to {fresh_wgs.geometry.y.max():.6f}")
print(f"   Lon range: {fresh_wgs.geometry.x.min():.6f} to {fresh_wgs.geometry.x.max():.6f}")

# Copy UTM attributes to WGS84 dataframe
for col in ['utm_x', 'utm_y']:
    if col in fresh.columns:
        fresh_wgs[col] = fresh[col].values

# Save to web directory
print("\n💾 Saving to web directory...")
output = web_data / 'scored_locations_fresh.geojson'
fresh_wgs.to_file(output, driver='GeoJSON')

file_size = output.stat().st_size / (1024 * 1024)
print(f"   ✅ Saved: {output}")
print(f"   📦 File size: {file_size:.2f} MB")

# Also save top 100
top_100 = fresh_wgs.head(100)
top_100_output = web_data / 'top_100_fresh.geojson'
top_100.to_file(top_100_output, driver='GeoJSON')
print(f"   ✅ Saved top 100: {top_100_output}")

print("\n" + "="*80)
print("✅ EXPORT COMPLETE!")
print("="*80)
print("\nRefresh the browser: http://localhost:8000/fresh_data_map.html")