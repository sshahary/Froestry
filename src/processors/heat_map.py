"""
Heat map generation using NDVI from DOP20RGBI imagery
"""
import numpy as np
import rasterio
from rasterio.merge import merge
from rasterio.mask import mask
import geopandas as gpd
from pathlib import Path
import sys
sys.path.append('.')
from src import config

class HeatMapGenerator:
    """Generate heat priority maps using NDVI"""
    
    def __init__(self, dop_folder=None):
        """Initialize heat map generator"""
        self.dop_path = Path(dop_folder) if dop_folder else Path(config.DATA_RAW) / 'DOP20RGBI'
        
        if not self.dop_path.exists():
            raise FileNotFoundError(f"DOP folder not found: {self.dop_path}")
        
        print(f"📂 DOP folder: {self.dop_path}")
    
    def load_dop_tiles(self):
        """
        Load all DOP20RGBI tiles
        
        Returns:
            list: List of opened rasterio datasets
        """
        print("\n🛰️  Loading DOP tiles...")
        
        tif_files = list(self.dop_path.glob('*.tif'))
        
        if not tif_files:
            raise FileNotFoundError(f"No .tif files found in {self.dop_path}")
        
        print(f"   Found {len(tif_files)} tiles")
        
        datasets = []
        for tif_file in tif_files:
            src = rasterio.open(tif_file)
            datasets.append(src)
            print(f"      ✅ {tif_file.name}")
        
        return datasets
    
    def merge_tiles(self, datasets):
        """
        Merge multiple DOP tiles into single mosaic
        
        Args:
            datasets: List of rasterio datasets
            
        Returns:
            tuple: (merged_array, transform)
        """
        print("\n🔗 Merging tiles into mosaic...")
        
        # Merge all tiles
        mosaic, out_transform = merge(datasets)
        
        print(f"   ✅ Mosaic created: {mosaic.shape}")
        print(f"   📊 Bands: {mosaic.shape[0]}")
        print(f"   📐 Size: {mosaic.shape[2]} x {mosaic.shape[1]} pixels")
        
        return mosaic, out_transform
    
    def calculate_ndvi(self, red_band, nir_band):
        """
        Calculate NDVI from red and near-infrared bands
        
        NDVI = (NIR - Red) / (NIR + Red)
        
        Args:
            red_band: Red band array
            nir_band: Near-infrared band array
            
        Returns:
            numpy array: NDVI values (-1 to 1)
        """
        print("\n🧮 Calculating NDVI...")
        
        # Convert to float to avoid division issues
        red = red_band.astype(float)
        nir = nir_band.astype(float)
        
        # Avoid division by zero
        denominator = nir + red
        denominator[denominator == 0] = 0.0001
        
        # Calculate NDVI
        ndvi = (nir - red) / denominator
        
        # Clip to valid range
        ndvi = np.clip(ndvi, -1, 1)
        
        print(f"   ✅ NDVI calculated")
        print(f"   📊 Range: {ndvi.min():.3f} to {ndvi.max():.3f}")
        print(f"   📊 Mean: {ndvi.mean():.3f}")
        
        return ndvi
    
    def ndvi_to_heat_score(self, ndvi):
        """
        Convert NDVI to heat priority score (0-100)
        
        Low NDVI = Hot/bare surface = High priority
        High NDVI = Cool/vegetated = Low priority
        
        Args:
            ndvi: NDVI array (-1 to 1)
            
        Returns:
            numpy array: Heat scores (0-100)
        """
        print("\n🔥 Converting NDVI to heat scores...")
        
        heat_score = np.zeros_like(ndvi, dtype=float)
        
        # Bare/hot surfaces (NDVI < 0.2) → Score 100 (URGENT!)
        mask_bare = ndvi < 0.2
        heat_score[mask_bare] = 100
        
        # Sparse vegetation (NDVI 0.2-0.4) → Score 70
        mask_sparse = (ndvi >= 0.2) & (ndvi < 0.4)
        heat_score[mask_sparse] = 70
        
        # Moderate vegetation (NDVI 0.4-0.6) → Score 40
        mask_moderate = (ndvi >= 0.4) & (ndvi < 0.6)
        heat_score[mask_moderate] = 40
        
        # Dense vegetation (NDVI >= 0.6) → Score 10 (low priority)
        mask_dense = ndvi >= 0.6
        heat_score[mask_dense] = 10
        
        print(f"   ✅ Heat scores calculated")
        print(f"   🔴 Bare surfaces (score 100): {np.sum(mask_bare):,} pixels")
        print(f"   🟠 Sparse vegetation (score 70): {np.sum(mask_sparse):,} pixels")
        print(f"   🟡 Moderate vegetation (score 40): {np.sum(mask_moderate):,} pixels")
        print(f"   🟢 Dense vegetation (score 10): {np.sum(mask_dense):,} pixels")
        
        return heat_score
    
    def clip_to_plantable_area(self, heat_score, transform, plantable_gdf):
        """
        Clip heat map to plantable areas only
        
        Args:
            heat_score: Heat score array
            transform: Raster transform
            plantable_gdf: Plantable area GeoDataFrame
            
        Returns:
            tuple: (clipped_array, clipped_transform)
        """
        print("\n✂️  Clipping to plantable areas...")
        
        # Create temporary raster
        temp_path = Path(config.DATA_PROCESSED) / 'temp_heat_full.tif'
        
        # Get proper CRS from plantable areas
        crs = plantable_gdf.crs
        
        with rasterio.open(
            temp_path,
            'w',
            driver='GTiff',
            height=heat_score.shape[0],
            width=heat_score.shape[1],
            count=1,
            dtype=heat_score.dtype,
            crs=crs,
            transform=transform,
        ) as dst:
            dst.write(heat_score, 1)
        
        # Clip to plantable areas
        with rasterio.open(temp_path) as src:
            clipped, clipped_transform = mask(
                src, 
                plantable_gdf.geometry, 
                crop=True,
                filled=True,
                nodata=0
            )
        
        # Clean up temp file
        temp_path.unlink()
        
        print(f"   ✅ Clipped to plantable areas")
        print(f"   📐 New size: {clipped.shape[2]} x {clipped.shape[1]} pixels")
        
        return clipped[0], clipped_transform
    
    def save_heat_map(self, heat_score, transform, crs, filename='heat_map.tif'):
        """
        Save heat map as GeoTIFF
        
        Args:
            heat_score: Heat score array
            transform: Raster transform
            crs: Coordinate reference system
            filename: Output filename
        """
        output_path = Path(config.DATA_PROCESSED) / filename
        
        with rasterio.open(
            output_path,
            'w',
            driver='GTiff',
            height=heat_score.shape[0],
            width=heat_score.shape[1],
            count=1,
            dtype=heat_score.dtype,
            crs=crs,
            transform=transform,
            compress='lzw'
        ) as dst:
            dst.write(heat_score, 1)
        
        print(f"   💾 Saved to: {output_path}")
        
        return output_path


def generate_heat_map():
    """
    Main function to generate heat priority map
    """
    print("="*80)
    print("🔥 LEVEL 2: HEAT MAP GENERATION (NDVI-BASED)")
    print("="*80)
    
    generator = HeatMapGenerator()
    
    # Load plantable areas
    print("\n📂 Loading plantable areas...")
    plantable = gpd.read_file(Path(config.DATA_PROCESSED) / 'plantable_area.geojson')
    print(f"   ✅ Loaded plantable areas: {plantable.geometry.area.sum() / 1_000_000:.2f} km²")
    
    # Load DOP tiles
    datasets = generator.load_dop_tiles()
    
    # Merge tiles
    mosaic, transform = generator.merge_tiles(datasets)
    
    # Extract bands (assuming RGBI order)
    red_band = mosaic[0]    # Band 1: Red
    nir_band = mosaic[3]    # Band 4: Infrared
    
    print(f"\n   📊 Red band range: {red_band.min()} - {red_band.max()}")
    print(f"   📊 NIR band range: {nir_band.min()} - {nir_band.max()}")
    
    # Calculate NDVI
    ndvi = generator.calculate_ndvi(red_band, nir_band)
    
    # Convert to heat scores
    heat_score = generator.ndvi_to_heat_score(ndvi)
    
    # Clip to plantable areas
    heat_clipped, heat_transform = generator.clip_to_plantable_area(
        heat_score, 
        transform, 
        plantable
    )
    
    # Save results
    print("\n💾 Saving heat map...")
    generator.save_heat_map(heat_clipped, heat_transform, plantable.crs, 'heat_map.tif')
    
    # Close datasets
    for ds in datasets:
        ds.close()
    
    print("\n" + "="*80)
    print("✅ LEVEL 2 COMPLETE - HEAT MAP GENERATED!")
    print("="*80)
    print("\n📁 Output:")
    print("   • heat_map.tif - Heat priority scores (0-100)")
    print("\n🎯 Next: Use this heat map for scoring tree locations!")
    
    return heat_clipped, heat_transform

if __name__ == "__main__":
    generate_heat_map()