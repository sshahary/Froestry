#!/usr/bin/env python3
"""
Create a web-compatible heat map overlay from the TIF file
"""

import rasterio
import numpy as np
from PIL import Image
import json
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.colors as colors

def create_web_heat_map():
    """Convert heat map TIF to PNG with bounds for web overlay"""
    
    processed_dir = Path("data/processed")
    web_data_dir = Path("web/public/data")
    
    # Ensure web data directory exists
    web_data_dir.mkdir(parents=True, exist_ok=True)
    
    # Load the heat map TIF
    heat_tif = processed_dir / "heat_map_improved.tif"
    if not heat_tif.exists():
        heat_tif = processed_dir / "heat_map.tif"
    
    if not heat_tif.exists():
        print("❌ No heat map TIF file found")
        return
    
    print(f"📂 Loading heat map: {heat_tif}")
    
    with rasterio.open(heat_tif) as src:
        # Read the data
        heat_data = src.read(1)
        
        # Get bounds in lat/lng (assuming the TIF is in WGS84 or can be converted)
        bounds = src.bounds
        transform = src.transform
        crs = src.crs
        
        print(f"   Shape: {heat_data.shape}")
        print(f"   CRS: {crs}")
        print(f"   Bounds: {bounds}")
        print(f"   Data range: {heat_data.min():.2f} - {heat_data.max():.2f}")
        
        # Normalize to 0-100 if needed
        if heat_data.max() > 100:
            heat_data = np.clip(heat_data * 100 / heat_data.max(), 0, 100)
        
        # Create a colormap for the heat map
        # Red = hot (high values), Green = cool (low values)
        cmap = plt.cm.RdYlGn_r  # Reversed Red-Yellow-Green
        norm = colors.Normalize(vmin=0, vmax=100)
        
        # Apply colormap
        colored_data = cmap(norm(heat_data))
        
        # Convert to 8-bit RGBA
        rgba_data = (colored_data * 255).astype(np.uint8)
        
        # Make low values (cool areas) more transparent
        alpha_channel = np.where(heat_data < 30, 
                                heat_data * 255 / 100 * 0.3,  # Very transparent for cool areas
                                heat_data * 255 / 100 * 0.8)  # More opaque for hot areas
        rgba_data[:, :, 3] = alpha_channel.astype(np.uint8)
        
        # Create PIL image
        img = Image.fromarray(rgba_data, 'RGBA')
        
        # Save as PNG
        output_png = web_data_dir / "heat_map_overlay.png"
        img.save(output_png)
        
        print(f"✅ Saved heat map overlay: {output_png}")
        
        # Save bounds information for Leaflet
        # Convert bounds to lat/lng if needed
        if crs != 'EPSG:4326':
            # Transform bounds to WGS84
            from rasterio.warp import transform_bounds
            bounds_wgs84 = transform_bounds(crs, 'EPSG:4326', *bounds)
        else:
            bounds_wgs84 = bounds
        
        bounds_info = {
            "bounds": [
                [bounds_wgs84[1], bounds_wgs84[0]],  # Southwest [lat, lng]
                [bounds_wgs84[3], bounds_wgs84[2]]   # Northeast [lat, lng]
            ],
            "url": "/data/heat_map_overlay.png",
            "opacity": 0.7,
            "attribution": "Heat Priority Map (NDVI Analysis)"
        }
        
        # Save bounds info
        bounds_file = web_data_dir / "heat_map_bounds.json"
        with open(bounds_file, 'w') as f:
            json.dump(bounds_info, f, indent=2)
        
        print(f"✅ Saved bounds info: {bounds_file}")
        print(f"   Bounds (WGS84): {bounds_wgs84}")
        
        return bounds_info

if __name__ == "__main__":
    create_web_heat_map()