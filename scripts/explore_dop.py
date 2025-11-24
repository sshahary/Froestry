"""
Explore DOP20RGBI (Digital Orthophoto with Infrared) dataset
"""
import rasterio
from pathlib import Path
import numpy as np
import sys
sys.path.append('.')
from src import config

def explore_dop():
    """Explore DOP20RGBI aerial imagery files"""
    
    print("🛰️  Exploring DOP20RGBI Dataset...\n")
    print("=" * 70)
    
    dop_path = Path(config.DATA_RAW) / 'DOP20RGBI'
    
    if not dop_path.exists():
        print(f"❌ Folder not found: {dop_path}")
        return
    
    # Find all .tif files (DOP are usually GeoTIFF)
    tif_files = list(dop_path.glob('*.tif')) + list(dop_path.glob('*.tiff'))
    
    if not tif_files:
        print("❌ No .tif files found!")
        print("   Looking for other image formats...")
        
        # Try other formats
        other_files = (list(dop_path.glob('*.jp2')) + 
                      list(dop_path.glob('*.jpg')) + 
                      list(dop_path.glob('*.png')))
        
        if other_files:
            print(f"   Found {len(other_files)} files in other formats")
            tif_files = other_files
        else:
            print("   No image files found!")
            return
    
    print(f"📁 Found {len(tif_files)} imagery file(s)\n")
    
    for i, tif_file in enumerate(tif_files[:5], 1):  # Check first 5 files
        print(f"{'='*70}")
        print(f"📂 File {i}: {tif_file.name}")
        print(f"{'='*70}")
        
        try:
            with rasterio.open(tif_file) as src:
                print(f"✅ Opened successfully!")
                print(f"   Driver: {src.driver}")
                print(f"   Size: {src.width} x {src.height} pixels")
                print(f"   Bands: {src.count}")
                print(f"   Data type: {src.dtypes[0]}")
                print(f"   CRS: {src.crs}")
                print(f"   Bounds: {src.bounds}")
                print(f"   Resolution: {src.res[0]:.2f}m x {src.res[1]:.2f}m")
                
                # Check band descriptions
                print(f"\n   📊 Band Information:")
                for band_idx in range(1, src.count + 1):
                    band_desc = src.descriptions[band_idx - 1] or f"Band {band_idx}"
                    print(f"      Band {band_idx}: {band_desc}")
                
                # Sample some pixel values
                print(f"\n   🔍 Sample pixel values (center of image):")
                center_x, center_y = src.width // 2, src.height // 2
                window = rasterio.windows.Window(center_x, center_y, 1, 1)
                
                for band_idx in range(1, min(src.count + 1, 5)):  # First 4 bands
                    data = src.read(band_idx, window=window)
                    print(f"      Band {band_idx}: {data[0, 0]}")
                
                # File size
                file_size_mb = tif_file.stat().st_size / (1024 * 1024)
                print(f"\n   💾 File size: {file_size_mb:.2f} MB")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
    
    if len(tif_files) > 5:
        print(f"... and {len(tif_files) - 5} more files")
    
    print("=" * 70)
    print("💡 EXPECTED STRUCTURE:")
    print("=" * 70)
    print("   DOP20RGBI should have 4 bands:")
    print("   • Band 1: Red (R)")
    print("   • Band 2: Green (G)")
    print("   • Band 3: Blue (B)")
    print("   • Band 4: Infrared (I)")
    print("\n   For NDVI calculation we need:")
    print("   • Red band (Band 1)")
    print("   • Infrared band (Band 4)")
    print("\n   Formula: NDVI = (Infrared - Red) / (Infrared + Red)")
    print("=" * 70)
    
    print("\n💡 NEXT STEPS:")
    print("   1. Confirm band order (especially Infrared)")
    print("   2. Check if multiple tiles cover Heilbronn")
    print("   3. Merge tiles if needed")
    print("   4. Calculate NDVI for plantable areas")
    print("=" * 70)

if __name__ == "__main__":
    explore_dop()