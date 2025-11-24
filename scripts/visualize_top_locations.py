"""
Visualize top-ranked tree planting locations on the map
"""
import geopandas as gpd
import folium
from folium import plugins
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

def create_final_map():
    """Create final map with top-ranked tree locations"""
    
    print("🗺️  Creating FINAL MAP with ranked locations...\n")
    
    processed_path = Path(config.DATA_PROCESSED)
    
    # ============================================================================
    # LOAD DATA
    # ============================================================================
    print("📂 Loading data...")
    
    # Top locations
    top_100 = gpd.read_file(processed_path / 'top_100_locations.geojson')
    top_100_wgs = top_100.to_crs('EPSG:4326')
    
    # Base layers
    plantable = gpd.read_file(processed_path / 'plantable_area.geojson')
    green_spaces = gpd.read_file(processed_path / 'green_spaces.geojson')
    
    plantable_wgs = plantable.to_crs('EPSG:4326')
    green_spaces_wgs = green_spaces.to_crs('EPSG:4326')
    
    # Heat map
    heat_path = processed_path / 'heat_map.tif'
    has_heat = heat_path.exists()
    
    if has_heat:
        with rasterio.open(heat_path) as src:
            heat_data = src.read(1)
            heat_bounds = src.bounds
            heat_crs = src.crs if src.crs else 'EPSG:25832'
    
    # Calculate center
    center_point = plantable.dissolve().centroid.iloc[0]
    center_point_wgs = gpd.GeoSeries([center_point], crs=config.CRS).to_crs('EPSG:4326').iloc[0]
    center_lat = center_point_wgs.y
    center_lon = center_point_wgs.x
    
    print(f"   ✅ Loaded {len(top_100)} top locations")
    print(f"   📍 Map center: {center_lat:.4f}°N, {center_lon:.4f}°E")
    
    # Drop non-geometry columns for base layers
    for gdf in [plantable_wgs, green_spaces_wgs]:
        cols_to_drop = [col for col in gdf.columns if col != 'geometry']
        gdf.drop(columns=cols_to_drop, inplace=True, errors='ignore')
    
    # ============================================================================
    # CREATE MAP
    # ============================================================================
    print("\n🗺️  Building map...")
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=14,
        tiles='OpenStreetMap'
    )
    
    # ============================================================================
    # ADD HEAT MAP
    # ============================================================================
    if has_heat:
        print("   🔥 Adding heat map...")
        
        heat_display = heat_data[::10, ::10]
        heat_normalized = ((heat_display / 100.0) * 255).astype(np.uint8)
        
        rgba = np.zeros((heat_normalized.shape[0], heat_normalized.shape[1], 4), dtype=np.uint8)
        rgba[:, :, 0] = heat_normalized
        rgba[:, :, 1] = 255 - heat_normalized
        rgba[:, :, 2] = 0
        rgba[:, :, 3] = 120
        
        bounds_wgs84 = transform_bounds(heat_crs, 'EPSG:4326', *heat_bounds)
        
        img = Image.fromarray(rgba, mode='RGBA')
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.read()).decode()
        
        folium.raster_layers.ImageOverlay(
            image=f'data:image/png;base64,{img_base64}',
            bounds=[[bounds_wgs84[1], bounds_wgs84[0]], 
                    [bounds_wgs84[3], bounds_wgs84[2]]],
            name='🔥 Heat Priority Map',
            opacity=0.5,
            interactive=True,
            cross_origin=False,
            zindex=1
        ).add_to(m)
    
    # ============================================================================
    # ADD BASE LAYERS
    # ============================================================================
    print("   🌿 Adding base layers...")
    
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
    
    folium.GeoJson(
        plantable_wgs,
        name='✅ Plantable Areas',
        style_function=lambda x: {
            'fillColor': 'lime',
            'color': 'darkgreen',
            'weight': 2,
            'fillOpacity': 0.3
        }
    ).add_to(m)
    
    # ============================================================================
    # ADD TOP LOCATIONS
    # ============================================================================
    print("   🌟 Adding top-ranked locations...")
    
    # Create color scale based on score
    def get_color(score):
        """Get color based on score (red=bad, green=good)"""
        if score >= 90:
            return 'darkgreen'
        elif score >= 80:
            return 'green'
        elif score >= 70:
            return 'lightgreen'
        elif score >= 60:
            return 'yellow'
        else:
            return 'orange'
    
    def get_size(rank):
        """Get marker size based on rank"""
        if rank <= 10:
            return 12
        elif rank <= 50:
            return 8
        else:
            return 6
    
    # Top 10 - Special markers
    for idx, row in top_100_wgs.head(10).iterrows():
        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=get_size(row['rank']),
            popup=folium.Popup(
                f"""
                <b>🏆 Rank #{int(row['rank'])}</b><br>
                <b>Score: {row['final_score']:.2f}/100</b><br><br>
                🔥 Heat: {row['heat_score']:.1f}<br>
                📏 Spatial: {row['spatial_score']:.1f}<br>
                👥 Social: {row['social_score']:.1f}<br>
                🚜 Maintenance: {row['maintenance_score']:.1f}<br><br>
                📍 Coordinates:<br>
                X: {row.geometry.x:.2f}<br>
                Y: {row.geometry.y:.2f}
                """,
                max_width=250
            ),
            color='gold',
            fillColor=get_color(row['final_score']),
            fillOpacity=0.9,
            weight=3
        ).add_to(m)
    
    # Ranks 11-100
    for idx, row in top_100_wgs.iloc[10:].iterrows():
        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=get_size(row['rank']),
            popup=folium.Popup(
                f"""
                <b>Rank #{int(row['rank'])}</b><br>
                <b>Score: {row['final_score']:.2f}/100</b><br><br>
                🔥 Heat: {row['heat_score']:.1f}<br>
                📏 Spatial: {row['spatial_score']:.1f}<br>
                👥 Social: {row['social_score']:.1f}<br>
                🚜 Maintenance: {row['maintenance_score']:.1f}
                """,
                max_width=200
            ),
            color=get_color(row['final_score']),
            fillColor=get_color(row['final_score']),
            fillOpacity=0.7,
            weight=2
        ).add_to(m)
    
    # ============================================================================
    # ADD CONTROLS & LEGEND
    # ============================================================================
    folium.LayerControl(collapsed=False).add_to(m)
    
    # Add marker cluster option for all 100 points
    marker_cluster = plugins.MarkerCluster(name='📍 Clustered View').add_to(m)
    
    for idx, row in top_100_wgs.iterrows():
        folium.Marker(
            location=[row.geometry.y, row.geometry.x],
            popup=f"Rank #{int(row['rank'])} - Score: {row['final_score']:.2f}",
            icon=folium.Icon(color='green', icon='tree', prefix='fa')
        ).add_to(marker_cluster)
    
    # Legend
    legend_html = f'''
    <div style="position: fixed; 
                top: 10px; left: 60px; width: 450px; 
                background-color: white; border:3px solid darkgreen; 
                z-index:9999; font-size:13px; padding: 15px;
                border-radius: 10px; box-shadow: 0 0 15px rgba(0,0,0,0.2);">
    <h3 style="margin-top:0; color:darkgreen;">🌳 Top Tree Planting Locations</h3>
    <p style="margin: 10px 0; line-height: 1.6;">
       <b>🏆 Ranked by Score (0-100):</b><br>
       • Heat mitigation: 40%<br>
       • Spatial suitability: 30%<br>
       • Social impact: 20%<br>
       • Maintenance access: 10%<br><br>
       
       <b>🎯 Markers:</b><br>
       <span style="color:gold;">●</span> <b>Top 10</b> (Gold border)<br>
       <span style="color:darkgreen;">●</span> Dark green: Score 90+<br>
       <span style="color:green;">●</span> Green: Score 80-89<br>
       <span style="color:lightgreen;">●</span> Light green: Score 70-79<br>
       <span style="color:yellow;">●</span> Yellow: Score 60-69<br><br>
       
       <b>💡 Click markers for details!</b>
    </p>
    <p style="margin-top:15px; padding-top:10px; border-top:2px solid darkgreen; 
              font-size:12px; color:darkgreen; font-weight:bold;">
       🎮 LEVEL 3 COMPLETE!<br>
       📊 {len(top_100)} locations ranked & ready!<br>
       🌳 Avg score: {top_100['final_score'].mean():.1f}/100
    </p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # ============================================================================
    # SAVE
    # ============================================================================
    output_file = 'web/final_ranked_map.html'
    m.save(output_file)
    
    print(f"\n✅ Final map created!")
    print(f"   📁 Saved to: {output_file}")
    print(f"   🌟 Top 100 locations visualized")
    print(f"\n🌐 Open in browser:")
    print(f"   file://{Path(output_file).absolute()}")

if __name__ == "__main__":
    create_final_map()


