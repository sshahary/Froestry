"""
Explore Feuerwehrflächen (Fire Routes) dataset
"""
import geopandas as gpd
from pathlib import Path
import sys
sys.path.append('.')
from src import config

def explore_fire_routes():
    """Explore fire routes dataset"""
    
    print("🚒 Exploring Feuerwehrflächen Dataset...\n")
    print("=" * 70)
    
    fire_path = Path(config.DATA_RAW) / 'Feuerwehrflaechen'
    
    if not fire_path.exists():
        print(f"❌ Folder not found: {fire_path}")
        return
    
    # List all shapefiles
    shapefiles = list(fire_path.glob('*.shp'))
    
    if not shapefiles:
        print("❌ No shapefiles found!")
        return
    
    print(f"📁 Found {len(shapefiles)} shapefile(s):\n")
    
    for shp_file in shapefiles:
        print(f"{'='*70}")
        print(f"📂 File: {shp_file.name}")
        print(f"{'='*70}")
        
        try:
            gdf = gpd.read_file(shp_file)
            
            print(f"✅ Loaded successfully!")
            print(f"   Features: {len(gdf):,}")
            print(f"   Geometry types: {gdf.geometry.type.unique()}")
            print(f"   CRS: {gdf.crs}")
            print(f"   Bounds: {gdf.total_bounds}")
            
            print(f"\n   📋 Columns: {list(gdf.columns)}")
            
            # Show sample data
            print(f"\n   🔍 Sample data (first row):")
            for col in gdf.columns:
                if col != 'geometry':
                    val = gdf[col].iloc[0] if len(gdf) > 0 else 'N/A'
                    print(f"      {col}: {val}")
            
            # Check for useful attributes
            print(f"\n   🏷️  Attributes with values:")
            for col in gdf.columns:
                if col != 'geometry' and gdf[col].notna().any():
                    unique_count = gdf[col].nunique()
                    print(f"      ▪ {col}: {unique_count} unique values")
                    if unique_count < 20:
                        print(f"        Values: {gdf[col].value_counts().to_dict()}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
    
    print("=" * 70)
    print("💡 Next: Add this to load_alkis.py as load_fire_routes()")
    print("=" * 70)

if __name__ == "__main__":
    explore_fire_routes()