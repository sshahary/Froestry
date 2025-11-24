"""
Quick test to verify setup is correct
"""

import sys
import rasterio
import folium
from pathlib import Path
import geopandas as gpd

def test_imports():
    """Test if all packages imported successfully"""
    print("✅ All packages imported successfully!")
    print(f"   GeoPandas version: {gpd.__version__}")
    print(f"   Rasterio version: {rasterio.__version__}")
    print(f"   Folium version: {folium.__version__}")

def test_folders():
    """Test if folder structure exists"""
    required_folders = [
        'data/raw',
        'data/processed',
        'data/outputs',
        'src/data_loaders',
        'src/processors',
    ]
    
    all_exist = True
    for folder in required_folders:
        if Path(folder).exists():
            print(f"✅ {folder}")
        else:
            print(f"❌ {folder} - MISSING!")
            all_exist = False
    
    if all_exist:
        print("\n🎉 Folder structure is perfect!")
    else:
        print("\n⚠️ Some folders are missing!")

if __name__ == "__main__":
    print("🔍 Testing Setup...\n")
    print("=" * 50)
    print("Testing Imports:")
    print("=" * 50)
    test_imports()
    
    print("\n" + "=" * 50)
    print("Testing Folder Structure:")
    print("=" * 50)
    test_folders()
    
    print("\n✅ Setup complete! Ready to start coding! 🚀")