"""
Explore Baumkataster (Existing Trees) dataset
"""
import geopandas as gpd
from pathlib import Path
import sys
sys.path.append('.')
from src import config

def explore_trees():
    """Explore existing trees dataset"""
    
    print("🌳 Exploring Baumkataster Dataset...\n")
    print("=" * 70)
    
    trees_path = Path(config.DATA_RAW) / 'Baumkataster'
    
    if not trees_path.exists():
        print(f"❌ Folder not found: {trees_path}")
        return
    
    # List all shapefiles
    shapefiles = list(trees_path.glob('*.shp'))
    
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
            print(f"   Features: {len(gdf):,} trees")
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
            
            # Check for crown diameter or similar attributes
            print(f"\n   🏷️  Important attributes:")
            crown_cols = ['kronendurchmesser', 'krone', 'durchmesser', 'radius', 
                         'crown', 'diameter', 'breite', 'width']
            
            for col in gdf.columns:
                col_lower = col.lower()
                if any(key in col_lower for key in crown_cols):
                    print(f"      ⭐ {col}: Found crown/diameter column!")
                    if gdf[col].notna().any():
                        print(f"         Min: {gdf[col].min()}")
                        print(f"         Max: {gdf[col].max()}")
                        print(f"         Mean: {gdf[col].mean():.2f}")
                        print(f"         Sample values: {gdf[col].head(5).tolist()}")
            
            # Check for tree species
            species_cols = ['art', 'baumart', 'species', 'gattung']
            for col in gdf.columns:
                col_lower = col.lower()
                if any(key in col_lower for key in species_cols):
                    print(f"      🌲 {col}: Tree species column")
                    print(f"         Top 5 species: {gdf[col].value_counts().head(5).to_dict()}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
    
    print("=" * 70)
    print("💡 Next: Add load_existing_trees() to load_alkis.py")
    print("=" * 70)

if __name__ == "__main__":
    explore_trees()