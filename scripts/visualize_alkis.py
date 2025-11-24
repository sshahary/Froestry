"""
Complete unified visualization with all layers including heat map
"""
import geopandas as gpd
import folium
from folium import raster_layers
import rasterio
from rasterio.warp import transform_bounds
import numpy as np
from PIL import Image
import io
import base64
from pathlib import Path
import sys
sys.path.append('.')
from src import config

def create_complete_map():
    """Create comprehensive interactive map with ALL layers"""
    
    print("🗺️  Creating COMPLETE unified visualization...\n")
    
    processed_path = Path(config.DATA_PROCESSED)
    
    # ============================================================================
    # LOAD ALL DATA
    # ============================================================================
    print("📂 Loading all data layers...")
    
    # Required layers
    exclusion = gpd.read_file(processed_path / 'exclusion_combined.geojson')
    green_spaces = gpd.read_file(processed_path / 'green_spaces.geojson')
    plantable = gpd.read_file(processed_path / 'plantable_area.geojson')
    
    # Optional vector layers
    optional_layers = {}
    optional_files = {
        'fire': 'exclusion_fire.geojson',
        'trees': 'exclusion_trees.geojson',
        'water': 'water_bodies.geojson',
        'buildings': 'exclusion_buildings.geojson',
        'roads': 'exclusion_roads.geojson'
    }
    
    for name, filename in optional_files.items():
        file_path = processed_path / filename
        if file_path.exists():
            optional_layers[name] = gpd.read_file(file_path)
            print(f"   ✅ {name.title()}")
    
    # Heat map (raster)
    heat_path = processed_path / 'heat_map.tif'
    has_heat_map = heat_path.exists()
    
    if has_heat_map:
        with rasterio.open(heat_path) as src:
            heat_data = src.read(1)
            heat_bounds = src.bounds
            heat_crs = src.crs if src.crs else 'EPSG:25832'
        print(f"   ✅ Heat Map")
    
    # ============================================================================
    # CONVERT TO WGS84
    # ============================================================================
    print("\n   🔄 Converting to WGS84...")
    
    exclusion_wgs = exclusion.to_crs('EPSG:4326')
    green_spaces_wgs = green_spaces.to_crs('EPSG:4326')
    plantable_wgs = plantable.to_crs('EPSG:4326')
    
    for name in optional_layers:
        optional_layers[name] = optional_layers[name].to_crs('EPSG:4326')
    
    # Calculate center
    center_point = plantable.dissolve().centroid.iloc[0]
    center_point_wgs = gpd.GeoSeries([center_point], crs=config.CRS).to_crs('EPSG:4326').iloc[0]
    center_lat = center_point_wgs.y
    center_lon = center_point_wgs.x
    
    print(f"   📍 Map center: {center_lat:.4f}°N, {center_lon:.4f}°E")
    
    # Drop non-geometry columns
    for gdf in [exclusion_wgs, green_spaces_wgs, plantable_wgs] + list(optional_layers.values()):
        cols_to_drop = [col for col in gdf.columns if col != 'geometry']
        gdf.drop(columns=cols_to_drop, inplace=True, errors='ignore')
    
    # ============================================================================
    # CREATE MAP
    # ============================================================================
    print("\n🗺️  Building comprehensive map...")
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=13,
        tiles='OpenStreetMap'
    )
    
    # ============================================================================
    # ADD HEAT MAP LAYER (if available)
    # ============================================================================
    if has_heat_map:
        print("   🔥 Adding heat priority layer...")
        
        # Downsample for web display
        heat_display = heat_data[::10, ::10]
        
        # Normalize to 0-255
        heat_normalized = ((heat_display / 100.0) * 255).astype(np.uint8)
        
        # Create RGBA (Red-Yellow-Green colormap)
        rgba = np.zeros((heat_normalized.shape[0], heat_normalized.shape[1], 4), dtype=np.uint8)
        
        # Red for hot (high priority)
        rgba[:, :, 0] = heat_normalized
        # Green for cool (low priority)  
        rgba[:, :, 1] = 255 - heat_normalized
        # Blue stays low
        rgba[:, :, 2] = 0
        # Alpha
        rgba[:, :, 3] = 150
        
        # Convert bounds to WGS84
        bounds_wgs84 = transform_bounds(heat_crs, 'EPSG:4326', *heat_bounds)
        
        # Create PIL Image and convert to base64
        img = Image.fromarray(rgba, mode='RGBA')
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.read()).decode()
        
        # Add to map
        folium.raster_layers.ImageOverlay(
            image=f'data:image/png;base64,{img_base64}',
            bounds=[[bounds_wgs84[1], bounds_wgs84[0]], 
                    [bounds_wgs84[3], bounds_wgs84[2]]],
            name='🔥 Heat Priority Map (NDVI)',
            opacity=0.6,
            interactive=True,
            cross_origin=False,
            zindex=1
        ).add_to(m)
    
    # ============================================================================
    # ADD VECTOR LAYERS
    # ============================================================================
    
    # Layer 1: Buildings
    if 'buildings' in optional_layers:
        print("   🏢 Adding buildings...")
        folium.GeoJson(
            optional_layers['buildings'],
            name='🏢 Buildings (3m buffer)',
            style_function=lambda x: {
                'fillColor': '#ffcccc',
                'color': '#cc0000',
                'weight': 1,
                'fillOpacity': 0.3
            },
            show=False  # Hidden by default
        ).add_to(m)
    
    # Layer 2: Roads
    if 'roads' in optional_layers:
        print("   🛣️  Adding roads...")
        folium.GeoJson(
            optional_layers['roads'],
            name='🛣️ Roads (2.5m buffer)',
            style_function=lambda x: {
                'fillColor': '#999999',
                'color': '#666666',
                'weight': 1,
                'fillOpacity': 0.3
            },
            show=False
        ).add_to(m)
    
    # Layer 3: Fire routes
    if 'fire' in optional_layers:
        print("   🚒 Adding fire access...")
        folium.GeoJson(
            optional_layers['fire'],
            name='🚒 Fire Access (5m buffer)',
            style_function=lambda x: {
                'fillColor': 'orange',
                'color': 'darkorange',
                'weight': 2,
                'fillOpacity': 0.4,
                'dashArray': '5, 5'
            },
            show=False
        ).add_to(m)
    
    # Layer 4: Existing trees
    if 'trees' in optional_layers:
        print("   🌳 Adding existing trees...")
        folium.GeoJson(
            optional_layers['trees'],
            name='🌳 Existing Trees (dynamic buffer)',
            style_function=lambda x: {
                'fillColor': '#8B4513',
                'color': '#654321',
                'weight': 2,
                'fillOpacity': 0.3
            },
            show=False
        ).add_to(m)
    
    # Layer 5: Water bodies
    if 'water' in optional_layers:
        print("   🌊 Adding water bodies...")
        folium.GeoJson(
            optional_layers['water'],
            name='🌊 Water Bodies',
            style_function=lambda x: {
                'fillColor': '#0066cc',
                'color': '#004499',
                'weight': 2,
                'fillOpacity': 0.5
            }
        ).add_to(m)
    
    # Layer 6: Combined exclusions
    print("   🔴 Adding combined exclusions...")
    folium.GeoJson(
        exclusion_wgs,
        name='🚫 ALL Exclusions (Combined)',
        style_function=lambda x: {
            'fillColor': 'red',
            'color': 'darkred',
            'weight': 2,
            'fillOpacity': 0.2
        },
        show=False
    ).add_to(m)
    
    # Layer 7: Green spaces
    print("   🌿 Adding green spaces...")
    folium.GeoJson(
        green_spaces_wgs,
        name='🌳 Green Spaces',
        style_function=lambda x: {
            'fillColor': 'lightgreen',
            'color': 'green',
            'weight': 1,
            'fillOpacity': 0.4
        }
    ).add_to(m)
    
    # Layer 8: Plantable areas (MOST IMPORTANT!)
    print("   ✅ Adding plantable areas...")
    folium.GeoJson(
        plantable_wgs,
        name='✅ PLANTABLE AREA',
        style_function=lambda x: {
            'fillColor': 'lime',
            'color': 'darkgreen',
            'weight': 3,
            'fillOpacity': 0.6
        }
    ).add_to(m)
    
    # ============================================================================
    # ADD CONTROLS
    # ============================================================================
    folium.LayerControl(collapsed=False).add_to(m)
    
    # ============================================================================
    # ADD LEGEND
    # ============================================================================
    
    # Build dynamic legend
    legend_items = []
    
    if has_heat_map:
        legend_items.append('''
        <b>🔥 Heat Priority (NDVI):</b><br>
        <span style="display:inline-block; width:20px; height:20px; background:red;"></span> 
        Hot/Bare (100) - URGENT!<br>
        <span style="display:inline-block; width:20px; height:20px; background:orange;"></span> 
        Sparse veg (70)<br>
        <span style="display:inline-block; width:20px; height:20px; background:yellow;"></span> 
        Moderate veg (40)<br>
        <span style="display:inline-block; width:20px; height:20px; background:lightgreen;"></span> 
        Dense veg (10)<br><br>
        ''')
    
    if 'buildings' in optional_layers:
        legend_items.append('<span style="color:#cc0000;">●</span> Buildings (3m)')
    if 'roads' in optional_layers:
        legend_items.append('<span style="color:#666;">●</span> Roads (2.5m)')
    if 'fire' in optional_layers:
        legend_items.append('<span style="color:orange;">●</span> Fire Access (5m)')
    if 'trees' in optional_layers:
        legend_items.append('<span style="color:#8B4513;">●</span> Existing Trees')
    if 'water' in optional_layers:
        legend_items.append('<span style="color:#0066cc;">●</span> Water Bodies')
    
    exclusion_legend = '<br>'.join([f'&nbsp;&nbsp;&nbsp;&nbsp;{item}' for item in legend_items])
    
    title_html = f'''
    <div style="position: fixed; 
                top: 10px; left: 60px; width: 450px; 
                background-color: white; border:3px solid #2e7d32; 
                z-index:9999; font-size:13px; padding: 15px;
                border-radius: 10px; box-shadow: 0 0 15px rgba(0,0,0,0.2);">
    <h3 style="margin-top:0; color:#2e7d32;">🌳 Heilbronn Tree Planting System</h3>
    <p style="margin: 10px 0; line-height: 1.6;">
       {exclusion_legend if exclusion_legend else ''}
       <br>
       <span style="color:lime; font-size:16px;">●</span> <b>PLANTABLE AREA</b><br>
       &nbsp;&nbsp;&nbsp;&nbsp;<b>11.50 km² ready for trees!</b><br>
       &nbsp;&nbsp;&nbsp;&nbsp;~115,000 tree capacity
    </p>
    <p style="margin-top:15px; padding-top:10px; border-top:2px solid #2e7d32; 
              font-size:12px; color:#2e7d32; font-weight:bold;">
       🎮 LEVEL 1 ✅ Exclusions mapped<br>
       🎮 LEVEL 2 ✅ Heat map generated<br>
       {'📊 79.7% of area is HOT!' if has_heat_map else ''}
    </p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    # ============================================================================
    # SAVE
    # ============================================================================
    output_file = 'web/complete_map.html'
    m.save(output_file)
    
    print(f"\n✅ Complete map created!")
    print(f"   📁 Saved to: {output_file}")
    
    layer_count = 3  # Base: exclusion, green, plantable
    layer_count += len(optional_layers)
    layer_count += 1 if has_heat_map else 0
    
    print(f"   📊 Total layers: {layer_count}")
    print(f"\n🌐 Open in browser:")
    print(f"   file://{Path(output_file).absolute()}")
    
    print(f"\n💡 Tip: Use layer control to toggle different views!")

if __name__ == "__main__":
    create_complete_map()




