"""
Convert existing heat_map.tif to .npy format
"""
import rasterio
import numpy as np
from pathlib import Path
import sys
sys.path.append('.')
from src import config

print("="*80)
print("🔄 CONVERTING HEAT MAP: TIF → NPY")
print("="*80)

processed = Path(config.DATA_PROCESSED)

# Load existing TIF
heat_tif = processed / 'heat_map.tif'

if not heat_tif.exists():
    print(f"❌ File not found: {heat_tif}")
    sys.exit(1)

print(f"\n📂 Loading: {heat_tif}")

with rasterio.open(heat_tif) as src:
    print(f"   Shape: {src.shape}")
    print(f"   Bands: {src.count}")
    print(f"   CRS: {src.crs}")
    print(f"   Bounds: {src.bounds}")
    
    # Read the heat map (first band)
    heat_array = src.read(1)
    
    print(f"\n📊 Heat Map Statistics:")
    print(f"   Min: {heat_array.min():.2f}")
    print(f"   Max: {heat_array.max():.2f}")
    print(f"   Mean: {heat_array.mean():.2f}")
    print(f"   Std: {heat_array.std():.2f}")
    
    # Check data type
    print(f"   Data type: {heat_array.dtype}")
    
    # Ensure it's in 0-100 range
    if heat_array.max() > 100:
        print(f"\n⚠️  Values > 100 detected, normalizing to 0-100...")
        heat_array = np.clip(heat_array, 0, 100)
    
    if heat_array.min() < 0:
        print(f"\n⚠️  Negative values detected, clipping to 0...")
        heat_array = np.clip(heat_array, 0, 100)

# Save as .npy
output = processed / 'heat_map.npy'
np.save(output, heat_array)

print(f"\n✅ Saved: {output}")
print(f"   Size: {output.stat().st_size / (1024*1024):.2f} MB")

# Verify it loads correctly
verification = np.load(output)
print(f"\n🔍 Verification:")
print(f"   Shape matches: {verification.shape == heat_array.shape}")
print(f"   Data matches: {np.allclose(verification, heat_array)}")

print("\n" + "="*80)
print("✅ CONVERSION COMPLETE!")
print("="*80)