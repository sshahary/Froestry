"""
Visualize heat map on interactive map
"""
import rasterio
from rasterio.warp import reproject, Resampling
import geopandas as gpd
import folium
from folium import raster_layers
import numpy as np
from pathlib import Path
import sys
sys.path.append('.')
from src import config

def create_heat_map_visualization():
    """Create interactive map with heat layer"""
    
    print("🗺️  Creating heat map visualization...\n")
    
    processed_path = Path(config.DATA_PROCESSED)
    
    # Load heat map
    print("📂 Loading heat map...")
    heat_path = processed_path / 'heat_map.tif'
    
    with rasterio.open(heat_path) as src:
        heat_data = src.read(1)
        heat_transform = src.transform
        heat_crs = src.crs if src.crs else 'EPSG:25832'
        bounds = src.bounds
        
        print(f"   ✅ Heat map loaded")
        print(f"   📊 Size: {heat_data.shape}")
        print(f"   📊 Value range: {heat_data.min():.1f} - {heat_data.max():.1f}")
    
    # Load other layers
    print("\n📂 Loading other layers...")
    plantable = gpd.read_file(processed_path / 'plantable_area.geojson')
    green_spaces = gpd.read_file(processed_path / 'green_spaces.geojson')
    
    # Convert to WGS84
    plantable_wgs = plantable.to_crs('EPSG:4326')
    green_spaces_wgs = green_spaces.to_crs('EPSG:4326')
    
    # Calculate center
    center_point = plantable.dissolve().centroid.iloc[0]
    center_point_wgs = gpd.GeoSeries([center_point], crs='EPSG:25832').to_crs('EPSG:4326').iloc[0]
    center_lat = center_point_wgs.y
    center_lon = center_point_wgs.x
    
    # Drop non-geometry columns
    for gdf in [plantable_wgs, green_spaces_wgs]:
        cols_to_drop = [col for col in gdf.columns if col != 'geometry']
        gdf.drop(columns=cols_to_drop, inplace=True, errors='ignore')
    
    print(f"   📍 Map center: {center_lat:.4f}°N, {center_lon:.4f}°E")
    
    # Create map
    print("\n🗺️  Building map...")
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=13,
        tiles='OpenStreetMap'
    )
    
    # Add green spaces (reference)
    folium.GeoJson(
        green_spaces_wgs,
        name='🌳 Green Spaces',
        style_function=lambda x: {
            'fillColor': 'lightgreen',
            'color': 'green',
            'weight': 1,
            'fillOpacity': 0.3
        }
    ).add_to(m)
    
    # Add plantable areas
    folium.GeoJson(
        plantable_wgs,
        name='✅ Plantable Areas',
        style_function=lambda x: {
            'fillColor': 'lime',
            'color': 'darkgreen',
            'weight': 2,
            'fillOpacity': 0.4
        }
    ).add_to(m)
    
    # Sample heat map for display (too large otherwise)
    print("   🔥 Processing heat map for display...")
    
    # Downsample for web display (every 10th pixel)
    heat_display = heat_data[::10, ::10]
    
    # Create colormap overlay
    # We'll create a simpler approach - save a georeferenced PNG
    print("   🎨 Creating heat overlay...")
    
    # Normalize to 0-255 for display
    heat_normalized = ((heat_display / 100.0) * 255).astype(np.uint8)
    
    # Create RGBA (Red-Yellow colormap for heat)
    rgba = np.zeros((heat_normalized.shape[0], heat_normalized.shape[1], 4), dtype=np.uint8)
    
    # Red channel increases with heat
    rgba[:, :, 0] = heat_normalized
    # Green channel for yellow (hot areas)
    rgba[:, :, 1] = np.maximum(0, 255 - heat_normalized)
    # Blue stays low
    rgba[:, :, 2] = 0
    # Alpha - make visible
    rgba[:, :, 3] = 150  # Semi-transparent
    
    # Convert bounds to WGS84
    from rasterio.warp import transform_bounds
    bounds_wgs84 = transform_bounds(heat_crs, 'EPSG:4326', *bounds)
    
    # Add as ImageOverlay
    from PIL import Image
    import io
    import base64
    
    # Create PIL Image
    img = Image.fromarray(rgba, mode='RGBA')
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.read()).decode()
    
    # Add to map
    folium.raster_layers.ImageOverlay(
        image=f'data:image/png;base64,{img_base64}',
        bounds=[[bounds_wgs84[1], bounds_wgs84[0]], 
                [bounds_wgs84[3], bounds_wgs84[2]]],
        name='🔥 Heat Priority Map',
        opacity=0.6,
        interactive=True,
        cross_origin=False,
        zindex=1
    ).add_to(m)
    
    # Add layer control
    folium.LayerControl(collapsed=False).add_to(m)
    
    # Add legend
    legend_html = '''
    <div style="position: fixed; 
                top: 10px; left: 60px; width: 400px; 
                background-color: white; border:3px solid #ff5722; 
                z-index:9999; font-size:14px; padding: 15px;
                border-radius: 10px; box-shadow: 0 0 15px rgba(0,0,0,0.2);">
    <h3 style="margin-top:0; color:#ff5722;">🔥 Heat Priority Map</h3>
    <p style="margin: 10px 0; line-height: 1.8;">
       <b>🌡️ Heat Priority Scores:</b><br>
       <span style="display:inline-block; width:20px; height:20px; background:red; border:1px solid black;"></span> 
       <b>Red (100)</b>: Bare/Hot - URGENT! 🔥<br>
       <span style="display:inline-block; width:20px; height:20px; background:orange; border:1px solid black;"></span> 
       <b>Orange (70)</b>: Sparse vegetation<br>
       <span style="display:inline-block; width:20px; height:20px; background:yellow; border:1px solid black;"></span> 
       <b>Yellow (40)</b>: Moderate vegetation<br>
       <span style="display:inline-block; width:20px; height:20px; background:lightgreen; border:1px solid black;"></span> 
       <b>Green (10)</b>: Dense vegetation<br><br>
       
       <span style="color:lime; font-size:16px;">●</span> <b>Plantable Areas</b><br>
       &nbsp;&nbsp;&nbsp;&nbsp;Where we can plant trees
    </p>
    <p style="margin-top:15px; padding-top:10px; border-top:2px solid #ff5722; 
              font-size:13px; color:#ff5722; font-weight:bold;">
       🎮 LEVEL 2 COMPLETE!<br>
       📊 79.7% of area is HOT!
    </p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Save
    output_file = 'web/heat_map.html'
    m.save(output_file)
    
    print(f"\n✅ Heat map visualization created!")
    print(f"   📁 Saved to: {output_file}")
    print(f"\n🌐 Open in browser:")
    print(f"   file://{Path(output_file).absolute()}")

if __name__ == "__main__":
    create_heat_map_visualization()