"""
Explore all ALKIS shapefiles to understand structure
"""
import geopandas as gpd
from pathlib import Path
import sys

# Add src to path
sys.path.append('.')
from src import config

def explore_all_alkis_files():
    """Load and explore ALL ALKIS shapefiles"""
    
    print("🔍 Exploring ALL ALKIS Shapefiles...\n")
    
    alkis_path = Path(config.DATA_RAW) / 'ALKIS'
    
    if not alkis_path.exists():
        print("❌ ALKIS folder not found!")
        return
    
    # Get all shapefiles
    shapefiles = list(alkis_path.glob('*.shp'))
    
    print(f"Found {len(shapefiles)} shapefiles\n")
    print("=" * 80)
    
    for i, shp_file in enumerate(shapefiles, 1):
        print(f"\n{'='*80}")
        print(f"📂 FILE {i}/{len(shapefiles)}: {shp_file.name}")
        print(f"{'='*80}")
        
        try:
            gdf = gpd.read_file(shp_file)
            
            print(f"✅ Loaded successfully!")
            print(f"   Features: {len(gdf):,}")
            print(f"   Geometry: {gdf.geometry.type.unique().tolist()}")
            print(f"   CRS: {gdf.crs}")
            
            print(f"\n   📋 Columns: {list(gdf.columns)}")
            
            # Show first row (non-geometry columns only)
            print(f"\n   🔍 Sample data (first row):")
            for col in gdf.columns:
                if col != 'geometry':
                    val = gdf[col].iloc[0] if len(gdf) > 0 else 'N/A'
                    print(f"      {col}: {val}")
            
            # Check for important columns
            print(f"\n   🏷️  Key attributes:")
            key_cols = ['objart', 'art', 'typ', 'funktion', 'name', 'nutzung', 
                       'bezeichnung', 'flaeche', 'gebaeudefunktion']
            
            for col in gdf.columns:
                col_lower = col.lower()
                if any(key in col_lower for key in ['art', 'typ', 'funk', 'nutz', 'name']):
                    if gdf[col].notna().any():
                        unique_count = gdf[col].nunique()
                        print(f"      ▪ {col}: {unique_count} unique values")
                        if unique_count < 20:
                            print(f"        Values: {gdf[col].value_counts().head(10).to_dict()}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n{'='*80}")
    print("🎯 SUMMARY - What Each File Likely Contains:")
    print(f"{'='*80}")
    
    file_purposes = {
        'gebaeudeBauwerke.shp': '🏢 Buildings and structures',
        'flurstueck.shp': '📐 Property parcels/plots',
        'nutzung.shp': '🌳 Land use types',
        'nutzungFlurstueck.shp': '📊 Parcel-level land use',
        'verwaltungseinheit.shp': '🗺️  Administrative boundaries (postal codes!)',
        'katasterBezirk.shp': '📍 Cadastral districts',
        'grenzpunkt.shp': '📌 Boundary points',
        'praesentation.shp': '🎨 Presentation/cartographic data'
    }
    
    for file, purpose in file_purposes.items():
        if any(shp.name == file for shp in shapefiles):
            print(f"   ✅ {file:30s} → {purpose}")
    
    print(f"\n{'='*80}")
    print("💡 NEXT STEPS:")
    print(f"{'='*80}")
    print("   1. gebaeudeBauwerke.shp → Extract buildings for exclusion zones")
    print("   2. verwaltungseinheit.shp → Get postal code boundaries") 
    print("   3. nutzung.shp → Identify green spaces, sealed surfaces")
    print("   4. flurstueck.shp → Property boundaries (public vs private)")

if __name__ == "__main__":
    explore_all_alkis_files()