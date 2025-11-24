"""
Create and manage postal code zones for Heilbronn
"""
import geopandas as gpd
from shapely.geometry import Polygon, Point
import pandas as pd
from pathlib import Path
import sys
sys.path.append('.')
from src import config

class PostalCodeManager:
    """Manage postal code zones"""
    
    # Heilbronn postal code zones (approximate boundaries in UTM32N)
    POSTAL_ZONES = {
        '74072': {'name': 'Innenstadt', 'xmin': 514500, 'xmax': 515500, 'ymin': 5442500, 'ymax': 5443500},
        '74074': {'name': 'Böckingen', 'xmin': 515000, 'xmax': 516000, 'ymin': 5443000, 'ymax': 5444000},
        '74076': {'name': 'Sontheim', 'xmin': 515500, 'xmax': 516500, 'ymin': 5442500, 'ymax': 5443500},
        '74078': {'name': 'Neckargartach', 'xmin': 516000, 'xmax': 517000, 'ymin': 5443000, 'ymax': 5444000},
        '74080': {'name': 'Frankenbach', 'xmin': 514500, 'xmax': 515500, 'ymin': 5443000, 'ymax': 5444000}
    }
    
    def __init__(self):
        """Initialize postal code manager"""
        print("📮 Initializing Postal Code Manager...")
    
    def create_postal_zones(self):
        """
        Create postal code zone polygons
        
        Returns:
            GeoDataFrame: Postal code zones
        """
        print("\n📮 Creating postal code zones...")
        
        zones = []
        for postal_code, bounds in self.POSTAL_ZONES.items():
            # Create polygon from bounds
            polygon = Polygon([
                (bounds['xmin'], bounds['ymin']),
                (bounds['xmax'], bounds['ymin']),
                (bounds['xmax'], bounds['ymax']),
                (bounds['xmin'], bounds['ymax']),
                (bounds['xmin'], bounds['ymin'])
            ])
            
            zones.append({
                'postal_code': postal_code,
                'name': bounds['name'],
                'geometry': polygon
            })
        
        postal_gdf = gpd.GeoDataFrame(zones, crs=config.CRS)
        
        print(f"   ✅ Created {len(postal_gdf)} postal zones")
        for idx, row in postal_gdf.iterrows():
            print(f"      {row['postal_code']} - {row['name']}")
        
        return postal_gdf
    
    def assign_postal_codes(self, locations_gdf):
        """
        Assign postal codes to locations based on spatial join
        
        Args:
            locations_gdf: GeoDataFrame of locations
            
        Returns:
            GeoDataFrame: Locations with postal codes
        """
        print("\n📮 Assigning postal codes to locations...")
        
        # Create postal zones
        postal_zones = self.create_postal_zones()
        
        # Spatial join
        locations_with_postal = gpd.sjoin(
            locations_gdf, 
            postal_zones[['postal_code', 'name', 'geometry']], 
            how='left', 
            predicate='within'
        )
        
        # Rename columns
        if 'postal_code' in locations_with_postal.columns:
            locations_with_postal['postal_code'] = locations_with_postal['postal_code'].fillna('Unknown')
            locations_with_postal['area_name'] = locations_with_postal['name'].fillna('Unknown')
            locations_with_postal.drop('name', axis=1, inplace=True, errors='ignore')
        
        # Count by postal code
        if 'postal_code' in locations_with_postal.columns:
            print(f"\n   📊 Distribution by postal code:")
            counts = locations_with_postal['postal_code'].value_counts()
            for postal, count in counts.items():
                print(f"      {postal}: {count:,} locations")
        
        return locations_with_postal
    
    def get_street_name(self, point, land_use_gdf=None):
        """
        Try to get street name from nearby land use data
        
        Args:
            point: Point geometry
            land_use_gdf: Land use GeoDataFrame with name info
            
        Returns:
            str: Street name or area description
        """
        if land_use_gdf is None or 'name' not in land_use_gdf.columns:
            return "Green Space"
        
        # Find nearest named feature within 50m
        nearby = land_use_gdf[land_use_gdf.distance(point) < 50]
        if len(nearby) > 0 and nearby['name'].notna().any():
            return nearby[nearby['name'].notna()].iloc[0]['name']
        
        return "Public Green Area"
    
    def save_postal_zones(self, postal_gdf, filename='postal_zones.geojson'):
        """Save postal zones to file"""
        output_path = Path(config.DATA_PROCESSED) / filename
        postal_gdf.to_file(output_path, driver='GeoJSON')
        print(f"   💾 Saved to: {output_path}")
        return output_path