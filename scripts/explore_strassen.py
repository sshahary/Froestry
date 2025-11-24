"""
Explore Straßenkataster (Street Cadastre) dataset
"""
import geopandas as gpd
from pathlib import Path
import sys
sys.path.append('.')
from src import config

def explore_streets():
    """Explore street cadastre dataset"""
    
    print("🛣️  Exploring Straßenkataster Dataset...\n")
    print("=" * 70)
    
    streets_path = Path(config.DATA_RAW) / 'Strassenkataster'
    
    # Try alternative spellings
    if not streets_path.exists():
        streets_path = Path(config.DATA_RAW) / 'Straßenkataster'
    if not streets_path.exists():
        streets_path = Path(config.DATA_RAW) / 'Strassenkataster_Stand2015'
    
    if not streets_path.exists():
        print(f"❌ Folder not found!")
        print(f"   Tried: Strassenkataster, Straßenkataster, Strassenkataster_Stand2015")
        return
    
    print(f"📁 Found folder: {streets_path.name}\n")
    
    # List all shapefiles
    shapefiles = list(streets_path.glob('*.shp'))
    
    if not shapefiles:
        print("❌ No shapefiles found!")
        return
    
    print(f"Found {len(shapefiles)} shapefile(s):\n")
    
    for shp_file in shapefiles:
        print(f"{'='*70}")
        print(f"📂 File: {shp_file.name}")
        print(f"{'='*70}")
        
        try:
            gdf = gpd.read_file(shp_file)
            
            print(f"✅ Loaded successfully!")
            print(f"   Features: {len(gdf):,} streets")
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
            print(f"\n   🏷️  Important attributes:")
            
            # Street name
            name_cols = ['name', 'strasse', 'street', 'bezeichnung']
            for col in gdf.columns:
                col_lower = col.lower()
                if any(key in col_lower for key in name_cols):
                    print(f"      📛 {col}: Street name column")
                    print(f"         Sample: {gdf[col].head(3).tolist()}")
            
            # Street type/class
            type_cols = ['typ', 'klasse', 'art', 'kategorie', 'type', 'class']
            for col in gdf.columns:
                col_lower = col.lower()
                if any(key in col_lower for key in type_cols):
                    print(f"      🏷️  {col}: Street classification")
                    if gdf[col].notna().any():
                        print(f"         Values: {gdf[col].value_counts().head(5).to_dict()}")
            
            # Width
            width_cols = ['breite', 'width', 'fahrbahnbreite']
            for col in gdf.columns:
                col_lower = col.lower()
                if any(key in col_lower for key in width_cols):
                    print(f"      📏 {col}: Street width")
                    if gdf[col].notna().any():
                        print(f"         Mean: {gdf[col].mean():.2f}m")
                        print(f"         Range: {gdf[col].min():.1f}m - {gdf[col].max():.1f}m")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
    
    print("=" * 70)
    print("💡 Analysis:")
    print("=" * 70)
    print("   Straßenkataster can provide:")
    print("   • Street names for location identification")
    print("   • Street types (main roads vs. side streets)")
    print("   • Street widths (for tree spacing)")
    print("   • Pedestrian traffic areas")
    print("\n   We already have road exclusions from ALKIS nutzung.shp")
    print("   Straßenkataster adds METADATA for better scoring!")
    print("=" * 70)

if __name__ == "__main__":
    explore_streets()