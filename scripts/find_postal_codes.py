"""
Find postal code data in our datasets
"""
import geopandas as gpd
from pathlib import Path
import sys
sys.path.append('.')
from src import config

def find_postal_codes():
    """Search for postal code data"""
    
    print("📮 Searching for postal code data...\n")
    print("="*70)
    
    # Check ALKIS parcels (flurstueck)
    alkis_path = Path(config.DATA_RAW) / 'ALKIS'
    parcels_file = alkis_path / 'flurstueck.shp'
    
    if parcels_file.exists():
        print("📂 Checking flurstueck.shp...")
        parcels = gpd.read_file(parcels_file)
        
        print(f"   Columns: {list(parcels.columns)}")
        
        # Look for postal code columns
        postal_cols = [col for col in parcels.columns 
                      if any(x in col.lower() for x in ['plz', 'postal', 'post'])]
        
        if postal_cols:
            print(f"   ✅ Found postal columns: {postal_cols}")
            for col in postal_cols:
                print(f"      Unique values: {parcels[col].unique()[:10]}")
        else:
            print("   ⚠️  No explicit postal column")
            
            # Check gemeinde column
            if 'gemeinde' in parcels.columns:
                print(f"   📍 gemeinde values: {parcels['gemeinde'].unique()[:5]}")
            
            # Check lagebeztxt (location description)
            if 'lagebeztxt' in parcels.columns:
                print(f"   📍 Sample locations: {parcels['lagebeztxt'].head(3).tolist()}")
    
    # Alternative: Use verwaltungseinheit
    admin_file = alkis_path / 'verwaltungseinheit.shp'
    if admin_file.exists():
        print("\n📂 Checking verwaltungseinheit.shp...")
        admin = gpd.read_file(admin_file)
        print(f"   Features: {len(admin)}")
        print(f"   Columns: {list(admin.columns)}")
        print(f"   Names: {admin['name'].tolist() if 'name' in admin.columns else 'N/A'}")
    
    # Alternative: Create synthetic postal zones based on location
    print("\n💡 SOLUTION:")
    print("="*70)
    print("   We'll create postal code zones based on coordinates!")
    print("   Heilbronn postal codes: 74072, 74074, 74076, 74078, 74080")
    print("   We'll divide the city geographically into these zones.")
    print("="*70)

if __name__ == "__main__":
    find_postal_codes()