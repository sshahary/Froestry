"""
Improved heat model combining multiple factors
Based on Heilbronn Climate Adaptation Strategy methodology
"""
import geopandas as gpd
import rasterio
import numpy as np
from pathlib import Path
from rasterio.features import rasterize
from rasterio.warp import reproject, Resampling
from shapely.geometry import mapping
import sys
sys.path.append('.')
from src import config

print("="*80)
print("🔥 IMPROVED HEAT MODEL - MULTI-FACTOR APPROACH")
print("="*80)

processed = Path(config.DATA_PROCESSED)
alkis_path = Path(config.DATA_RAW) / 'ALKIS'

# =========================================================================
# LOAD REFERENCE: Use existing heat map for dimensions
# =========================================================================
print("\n📐 Loading reference heat map...")
reference_heat_path = processed / 'heat_map.tif'

with rasterio.open(reference_heat_path) as src:
    reference_shape = src.shape
    reference_transform = src.transform
    reference_crs = src.crs or 'EPSG:25832'
    reference_bounds = src.bounds
    
    print(f"   Reference dimensions: {reference_shape[0]} x {reference_shape[1]}")
    print(f"   CRS: {reference_crs}")
    print(f"   Bounds: {reference_bounds}")

height, width = reference_shape

# =========================================================================
# FACTOR 1: Building Density (40% weight) - FROM OFFICIAL STRATEGY
# =========================================================================
print("\n🏢 FACTOR 1: Building Density (40% weight)")
print("   Based on: Dense buildings = HIGH heat storage")

buildings = gpd.read_file(alkis_path / 'gebaeudeBauwerke.shp')
if str(buildings.crs) != str(reference_crs):
    buildings = buildings.to_crs(reference_crs)

print(f"   Loaded {len(buildings):,} buildings")

# Create building density raster
building_shapes = [(mapping(geom), 1) for geom in buildings.geometry if geom.is_valid]
building_raster = rasterize(
    building_shapes,
    out_shape=(height, width),
    transform=reference_transform,
    fill=0,
    dtype='float32'
)

# Calculate density with a moving window
from scipy.ndimage import uniform_filter
density_radius = 3  # pixels (60m at 20m resolution)
building_density = uniform_filter(building_raster.astype(float), size=int(density_radius*2))

# Normalize to 0-100
if building_density.max() > 0:
    building_heat = (building_density / building_density.max()) * 100
else:
    building_heat = building_density

print(f"   ✅ Building density: max={building_heat.max():.1f}, mean={building_heat.mean():.1f}")

# =========================================================================
# FACTOR 2: Surface Sealing / Impervious Surfaces (30% weight)
# =========================================================================
print("\n🛣️  FACTOR 2: Surface Sealing (30% weight)")
print("   Based on: Roads, parking, sealed = heat storage")

land_use = gpd.read_file(alkis_path / 'nutzung.shp')
if str(land_use.crs) != str(reference_crs):
    land_use = land_use.to_crs(reference_crs)

# Identify sealed surfaces
sealed_types = ['Strassenverkehr', 'Platz', 'Flaechegemischternutzung']
sealed_surfaces = land_use[land_use['nutzart'].isin(sealed_types)]

print(f"   Found {len(sealed_surfaces):,} sealed surface polygons")

if len(sealed_surfaces) > 0:
    sealed_shapes = [(mapping(geom), 1) for geom in sealed_surfaces.geometry if geom.is_valid]
    sealed_raster = rasterize(
        sealed_shapes,
        out_shape=(height, width),
        transform=reference_transform,
        fill=0,
        dtype='float32'
    )
    sealed_heat = sealed_raster * 100
else:
    sealed_heat = np.zeros((height, width), dtype='float32')

print(f"   ✅ Sealed surfaces: max={sealed_heat.max():.1f}, coverage={sealed_raster.mean()*100:.1f}%")

# =========================================================================
# FACTOR 3: Vegetation Deficit (20% weight) - Load existing
# =========================================================================
print("\n🌿 FACTOR 3: Vegetation Deficit (20% weight)")
print("   Based on: Lack of trees/vegetation = less cooling")

# Load existing heat map (already at correct dimensions)
vegetation_deficit = np.load(processed / 'heat_map.npy')

# Ensure it matches reference shape
if vegetation_deficit.shape != (height, width):
    print(f"   ⚠️  Shape mismatch: {vegetation_deficit.shape} != {(height, width)}")
    print(f"   Resampling to match reference...")
    
    # Create temporary raster with vegetation data
    temp_profile = {
        'driver': 'GTiff',
        'height': vegetation_deficit.shape[0],
        'width': vegetation_deficit.shape[1],
        'count': 1,
        'dtype': 'float32',
        'crs': reference_crs,
        'transform': reference_transform
    }
    
    # Resample to match reference
    resampled = np.empty((height, width), dtype='float32')
    
    reproject(
        source=vegetation_deficit,
        destination=resampled,
        src_transform=reference_transform,
        src_crs=reference_crs,
        dst_transform=reference_transform,
        dst_crs=reference_crs,
        resampling=Resampling.bilinear
    )
    
    vegetation_deficit = resampled
    print(f"   ✅ Resampled to {vegetation_deficit.shape}")

print(f"   ✅ Vegetation deficit: max={vegetation_deficit.max():.1f}, mean={vegetation_deficit.mean():.1f}")

# =========================================================================
# FACTOR 4: Urban Canyon Effect (10% weight)
# =========================================================================
print("\n🏙️  FACTOR 4: Urban Canyon Effect (10% weight)")
print("   Based on: Tall buildings trap heat")

# Approximate building height from number of floors
if 'anzahlgs' in buildings.columns:
    buildings['height'] = buildings['anzahlgs'].fillna(2) * 3  # 3m per floor
else:
    buildings['height'] = 9  # Assume 3 floors

# Weight by height
height_shapes = [(mapping(geom), float(h)) for geom, h in zip(buildings.geometry, buildings['height']) 
                 if geom.is_valid and not np.isnan(h)]

if len(height_shapes) > 0:
    height_raster = rasterize(
        height_shapes,
        out_shape=(height, width),
        transform=reference_transform,
        fill=0,
        dtype='float32'
    )
    
    # Apply density filter
    canyon_effect = uniform_filter(height_raster, size=int(density_radius*2))
    
    if canyon_effect.max() > 0:
        canyon_heat = (canyon_effect / canyon_effect.max()) * 100
    else:
        canyon_heat = canyon_effect
else:
    canyon_heat = np.zeros((height, width), dtype='float32')

print(f"   ✅ Canyon effect: max={canyon_heat.max():.1f}, mean={canyon_heat.mean():.1f}")

# =========================================================================
# VERIFY ALL ARRAYS HAVE SAME SHAPE
# =========================================================================
print("\n🔍 Verifying array shapes...")
shapes = {
    'building_heat': building_heat.shape,
    'sealed_heat': sealed_heat.shape,
    'vegetation_deficit': vegetation_deficit.shape,
    'canyon_heat': canyon_heat.shape
}

all_match = all(s == (height, width) for s in shapes.values())

if not all_match:
    print("   ❌ SHAPE MISMATCH DETECTED:")
    for name, shape in shapes.items():
        status = "✅" if shape == (height, width) else "❌"
        print(f"      {status} {name}: {shape}")
    sys.exit(1)
else:
    print(f"   ✅ All arrays match: {height} x {width}")

# =========================================================================
# COMBINE ALL FACTORS
# =========================================================================
print("\n⚖️  COMBINING FACTORS (Weighted)")

weights = {
    'building_density': 0.40,   # Most important per official strategy
    'sealed_surfaces': 0.30,
    'vegetation_deficit': 0.20,
    'canyon_effect': 0.10
}

print(f"   Weights: {weights}")

improved_heat_map = (
    building_heat * weights['building_density'] +
    sealed_heat * weights['sealed_surfaces'] +
    vegetation_deficit * weights['vegetation_deficit'] +
    canyon_heat * weights['canyon_effect']
)

# Clip to 0-100
improved_heat_map = np.clip(improved_heat_map, 0, 100)

print(f"\n✅ IMPROVED HEAT MAP CREATED")
print(f"   Shape: {improved_heat_map.shape}")
print(f"   Min: {improved_heat_map.min():.1f}")
print(f"   Max: {improved_heat_map.max():.1f}")
print(f"   Mean: {improved_heat_map.mean():.1f}")
print(f"   Std: {improved_heat_map.std():.1f}")

# Save
output_npy = processed / 'heat_map_improved.npy'
np.save(output_npy, improved_heat_map)
print(f"\n💾 Saved: {output_npy}")

# Also save as GeoTIFF for visualization
output_tif = processed / 'heat_map_improved.tif'
with rasterio.open(
    output_tif,
    'w',
    driver='GTiff',
    height=height,
    width=width,
    count=1,
    dtype='float32',
    crs=reference_crs,
    transform=reference_transform,
    compress='lzw'
) as dst:
    dst.write(improved_heat_map.astype('float32'), 1)

print(f"💾 Saved: {output_tif}")

# Compare with original
original_heat = np.load(processed / 'heat_map.npy')

# Ensure same shape for comparison
if original_heat.shape != improved_heat_map.shape:
    print(f"\n⚠️  Original shape {original_heat.shape} doesn't match, resampling for comparison...")
    original_resampled = np.empty((height, width), dtype='float32')
    reproject(
        source=original_heat,
        destination=original_resampled,
        src_transform=reference_transform,
        src_crs=reference_crs,
        dst_transform=reference_transform,
        dst_crs=reference_crs,
        resampling=Resampling.bilinear
    )
    original_heat = original_resampled

print("\n📊 COMPARISON WITH ORIGINAL:")
print(f"   Original mean: {original_heat.mean():.1f}")
print(f"   Improved mean: {improved_heat_map.mean():.1f}")
print(f"   Difference: {improved_heat_map.mean() - original_heat.mean():+.1f}")

# Analyze hot spots (>80)
original_hot = (original_heat > 80).sum()
improved_hot = (improved_heat_map > 80).sum()
print(f"\n🔥 Hot Spots (>80):")
print(f"   Original: {original_hot:,} pixels ({original_hot/(height*width)*100:.1f}%)")
print(f"   Improved: {improved_hot:,} pixels ({improved_hot/(height*width)*100:.1f}%)")
print(f"   Change: {improved_hot - original_hot:+,} pixels")

# Check approximate city center (middle of image)
center_y, center_x = height // 2, width // 2
radius = 100  # pixels

try:
    center_original = original_heat[center_y-radius:center_y+radius, center_x-radius:center_x+radius].mean()
    center_improved = improved_heat_map[center_y-radius:center_y+radius, center_x-radius:center_x+radius].mean()
    
    print(f"\n🏙️  APPROXIMATE CITY CENTER:")
    print(f"   Original method: {center_original:.1f}")
    print(f"   Improved method: {center_improved:.1f}")
    print(f"   Increase: {center_improved - center_original:+.1f} points")
except:
    print("\n⚠️  Could not analyze city center (radius too large)")

print("\n" + "="*80)
print("✅ HEAT MODEL IMPROVED!")
print("="*80)
print("\n💡 Key improvements:")
print("   • Buildings and sealed surfaces now contribute to heat")
print("   • Urban canyon effect included")
print("   • Multi-factor approach matches official climate strategy")
print("   • City center should now show higher heat values")