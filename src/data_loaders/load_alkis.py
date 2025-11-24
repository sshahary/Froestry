"""
ALKIS data loader - Extract buildings, boundaries, land use
"""
import geopandas as gpd
from pathlib import Path
import sys
sys.path.append('.')
from src import config
import pandas as pd 

class ALKISLoader:
    """Load and process ALKIS data"""
    
    def __init__(self, alkis_folder=None):
        """Initialize ALKIS loader"""
        self.alkis_path = Path(alkis_folder) if alkis_folder else Path(config.DATA_RAW) / 'ALKIS'
        
        if not self.alkis_path.exists():
            raise FileNotFoundError(f"ALKIS folder not found: {self.alkis_path}")
        
        print(f"📂 ALKIS folder: {self.alkis_path}")
    
    def load_buildings(self):
        """
        Load building polygons from gebaeudeBauwerke.shp
        
        Returns:
            GeoDataFrame: Building polygons with attributes
        """
        print("\n🏢 Loading buildings...")
        
        buildings_file = self.alkis_path / 'gebaeudeBauwerke.shp'
        buildings = gpd.read_file(buildings_file)
        
        # Ensure correct CRS
        if buildings.crs != config.CRS:
            print(f"   🔄 Reprojecting from {buildings.crs} to {config.CRS}")
            buildings = buildings.to_crs(config.CRS)
        
        print(f"   ✅ Loaded {len(buildings):,} buildings")
        print(f"   📊 Building types: {buildings['gebnutzbez'].value_counts().head(5).to_dict()}")
        
        return buildings
    
    def filter_actual_buildings(self, buildings):
        """
        Filter to keep only actual buildings (not towers, storage, etc.)
        
        Args:
            buildings: GeoDataFrame of all buildings
            
        Returns:
            GeoDataFrame: Filtered buildings
        """
        print("\n🔍 Filtering to actual buildings...")
        
        # Keep only 'Gebaeude' (actual buildings)
        actual_buildings = buildings[buildings['gebnutzbez'] == 'Gebaeude'].copy()
        
        print(f"   ✅ Kept {len(actual_buildings):,} actual buildings")
        print(f"   ❌ Filtered out {len(buildings) - len(actual_buildings):,} other structures")
        
        return actual_buildings
    
    def load_land_use(self):
        """
        Load land use data from nutzung.shp
        
        Returns:
            GeoDataFrame: Land use polygons
        """
        print("\n🌳 Loading land use...")
        
        land_use_file = self.alkis_path / 'nutzung.shp'
        land_use = gpd.read_file(land_use_file)
        
        # Ensure correct CRS
        if land_use.crs != config.CRS:
            land_use = land_use.to_crs(config.CRS)
        
        print(f"   ✅ Loaded {len(land_use):,} land use polygons")
        print(f"   📊 Top land use types:")
        for nutzart, count in land_use['nutzart'].value_counts().head(10).items():
            print(f"      • {nutzart}: {count:,}")
        
        return land_use
    
    def extract_green_spaces(self, land_use):
        """
        Extract green spaces from land use data
        
        Args:
            land_use: GeoDataFrame of land use
            
        Returns:
            GeoDataFrame: Green space polygons
        """
        print("\n🌿 Extracting green spaces...")
        
        # Green space types
        green_types = [
            'Sport Freizeit Und Erholungsflaeche',
            'Gehoelz',
            'Wald'
        ]
        
        green_spaces = land_use[land_use['nutzart'].isin(green_types)].copy()
        
        print(f"   ✅ Found {len(green_spaces):,} green space polygons")
        for nutzart in green_types:
            count = len(green_spaces[green_spaces['nutzart'] == nutzart])
            if count > 0:
                print(f"      • {nutzart}: {count:,}")
        
        return green_spaces
    
    def extract_roads(self, land_use):
        """
        Extract roads from land use data
        
        Args:
            land_use: GeoDataFrame of land use
            
        Returns:
            GeoDataFrame: Road polygons
        """
        print("\n🛣️  Extracting roads...")
        
        road_types = ['Strassenverkehr', 'Weg']
        roads = land_use[land_use['nutzart'].isin(road_types)].copy()
        
        print(f"   ✅ Found {len(roads):,} road polygons")
        
        return roads
    
    def load_parcels(self):
        """
        Load property parcels from flurstueck.shp
        
        Returns:
            GeoDataFrame: Parcel polygons
        """
        print("\n📐 Loading parcels...")
        
        parcels_file = self.alkis_path / 'flurstueck.shp'
        parcels = gpd.read_file(parcels_file)
        
        # Ensure correct CRS
        if parcels.crs != config.CRS:
            parcels = parcels.to_crs(config.CRS)
        
        print(f"   ✅ Loaded {len(parcels):,} parcels")
        
        return parcels
    
    def create_exclusion_zone(self, gdf, buffer_distance, name="features"):
        """
        Create buffer around features for exclusion zone
        
        Args:
            gdf: GeoDataFrame of features
            buffer_distance: Buffer distance in meters
            name: Name of features (for logging)
        
        Returns:
            GeoDataFrame: Buffered features
        """
        print(f"\n🔵 Creating {buffer_distance}m buffer around {name}...")
        
        # Create buffer
        buffered = gdf.copy()
        buffered['geometry'] = gdf.geometry.buffer(buffer_distance)
        
        # Dissolve to create single exclusion zone
        exclusion_zone = buffered.dissolve()
        
        print(f"   ✅ Exclusion zone created")
        print(f"   📊 Original features: {len(gdf):,}")
        print(f"   📊 Exclusion zone area: {exclusion_zone.geometry.area.sum() / 1_000_000:.2f} km²")
        
        return exclusion_zone
    
    def save_geojson(self, gdf, filename):
        """
        Save GeoDataFrame as GeoJSON
        
        Args:
            gdf: GeoDataFrame to save
            filename: Output filename
        """
        output_path = Path(config.DATA_PROCESSED) / filename
        gdf.to_file(output_path, driver='GeoJSON')
        print(f"   💾 Saved to: {output_path}")
        
        return output_path

    def load_fire_routes(self):
        """
        Load fire access routes from Feuerwehrflaechen
        Combines all fire-related shapefiles
        
        Returns:
            GeoDataFrame: Combined fire route polygons/lines
        """
        print("\n🚒 Loading fire routes...")
        
        fire_folder = Path(config.DATA_RAW) / 'Feuerwehrflaechen'
        
        if not fire_folder.exists():
            print(f"   ⚠️  Folder not found: {fire_folder}")
            return None
        
        # Find all shapefiles
        shapefiles = list(fire_folder.glob('*.shp'))
        
        if not shapefiles:
            print(f"   ⚠️  No shapefiles found in {fire_folder}")
            return None
        
        print(f"   📂 Found {len(shapefiles)} fire-related files")
        
        # Load all fire route files
        fire_gdfs = []
        
        for shp_file in shapefiles:
            try:
                gdf = gpd.read_file(shp_file)
                
                # Ensure correct CRS
                if gdf.crs != config.CRS:
                    gdf = gdf.to_crs(config.CRS)
                
                # Get file type from BEMERKUNG field
                file_type = gdf['BEMERKUNG'].iloc[0] if 'BEMERKUNG' in gdf.columns else shp_file.stem
                
                print(f"      • {file_type}: {len(gdf)} features ({gdf.geometry.type.unique()[0]})")
                
                fire_gdfs.append(gdf)
                
            except Exception as e:
                print(f"      ⚠️  Error loading {shp_file.name}: {e}")
        
        if not fire_gdfs:
            print("   ⚠️  No fire data could be loaded")
            return None
        
        # Combine all fire routes into single GeoDataFrame
        fire_routes = gpd.GeoDataFrame(
            pd.concat(fire_gdfs, ignore_index=True),
            crs=config.CRS
        )
        
        print(f"   ✅ Combined {len(fire_routes):,} total fire access features")
        print(f"   📊 Geometry types: {fire_routes.geometry.type.unique()}")
        
        return fire_routes
    
    def load_existing_trees(self):
        """
        Load existing trees from Baumkataster
        
        Returns:
            GeoDataFrame: Existing tree points with crown diameter
        """
        print("\n🌳 Loading existing trees...")
        
        trees_folder = Path(config.DATA_RAW) / 'Baumkataster'
        
        if not trees_folder.exists():
            print(f"   ⚠️  Folder not found: {trees_folder}")
            return None
        
        # Find shapefile
        shapefiles = list(trees_folder.glob('*.shp'))
        
        if not shapefiles:
            print(f"   ⚠️  No shapefiles found in {trees_folder}")
            return None
        
        trees_file = shapefiles[0]
        print(f"   📂 Loading: {trees_file.name}")
        
        trees = gpd.read_file(trees_file)
        
        # Ensure correct CRS
        if trees.crs != config.CRS:
            trees = trees.to_crs(config.CRS)
        
        print(f"   ✅ Loaded {len(trees):,} existing trees")
        
        # Check crown diameter data
        if 'KRONE_DM' in trees.columns:
            valid_crowns = trees[trees['KRONE_DM'] > 0]
            print(f"   📊 Crown diameter (KRONE_DM):")
            print(f"      Trees with crown data: {len(valid_crowns):,}")
            print(f"      Average crown: {trees['KRONE_DM'].mean():.2f}m")
            print(f"      Range: {trees['KRONE_DM'].min():.1f}m - {trees['KRONE_DM'].max():.1f}m")
        
        # Top tree species
        if 'DEU_TEXT' in trees.columns:
            print(f"   🌲 Top 5 tree species:")
            for species, count in trees['DEU_TEXT'].value_counts().head(5).items():
                print(f"      • {species}: {count}")
        
        return trees
    
    def create_tree_exclusion_zone(self, trees):
        """
        Create buffers around existing trees based on crown diameter
        
        Args:
            trees: GeoDataFrame of existing trees with KRONE_DM column
        
        Returns:
            GeoDataFrame: Buffered tree exclusion zones
        """
        print(f"\n🔵 Creating dynamic buffers around existing trees...")
        
        trees_buffered = trees.copy()
        
        # Use crown diameter as buffer, but ensure minimum buffer
        # Buffer = crown_radius + safety margin (2m)
        if 'KRONE_DM' in trees.columns:
            # Crown radius + 2m safety = (KRONE_DM/2) + 2
            trees_buffered['buffer_distance'] = (trees['KRONE_DM'] / 2) + 2
            
            # Ensure minimum buffer of 6m (for trees with missing/small crown data)
            trees_buffered['buffer_distance'] = trees_buffered['buffer_distance'].fillna(6.0)
            trees_buffered.loc[trees_buffered['buffer_distance'] < 6.0, 'buffer_distance'] = 6.0
            
            # Apply individual buffers
            trees_buffered['geometry'] = trees_buffered.apply(
                lambda row: row.geometry.buffer(row['buffer_distance']), 
                axis=1
            )
            
            avg_buffer = trees_buffered['buffer_distance'].mean()
            print(f"   ✅ Applied dynamic buffers")
            print(f"   📊 Average buffer: {avg_buffer:.2f}m")
            print(f"   📊 Buffer range: {trees_buffered['buffer_distance'].min():.1f}m - {trees_buffered['buffer_distance'].max():.1f}m")
        else:
            # Fallback: use fixed buffer
            default_buffer = config.BUFFERS['existing_trees']
            trees_buffered['geometry'] = trees.geometry.buffer(default_buffer)
            print(f"   ✅ Applied fixed {default_buffer}m buffer (no crown data)")
        
        # Dissolve into single exclusion zone
        trees_exclusion = trees_buffered.dissolve()
        
        exclusion_area = trees_exclusion.geometry.area.sum() / 1_000_000
        print(f"   📊 Tree exclusion zone area: {exclusion_area:.2f} km²")
        
        return trees_exclusion
    
    def extract_water_bodies(self, land_use):
        """
        Extract water bodies from land use data
        
        Args:
            land_use: GeoDataFrame of land use
            
        Returns:
            GeoDataFrame: Water body polygons
        """
        print("\n🌊 Extracting water bodies...")
        
        # Water-related land use types
        water_types = ['Hafenbecken', 'Gewaesser', 'Fliessgewaesser', 
                      'Stehendes Gewaesser', 'Meer']
        
        # Check what water types exist in the data
        available_water = [wt for wt in water_types if wt in land_use['nutzart'].values]
        
        if not available_water:
            print("   ⚠️  No water bodies found in land use data")
            return None
        
        water_bodies = land_use[land_use['nutzart'].isin(available_water)].copy()
        
        print(f"   ✅ Found {len(water_bodies):,} water body polygons")
        for water_type in available_water:
            count = len(water_bodies[water_bodies['nutzart'] == water_type])
            if count > 0:
                print(f"      • {water_type}: {count:,}")
        
        return water_bodies

def test_alkis_pipeline():
    """
    Complete ALKIS pipeline with all Level 1 exclusions
    """
    print("="*80)
    print("🎮 LEVEL 1: COMPLETE EXCLUSION ZONE PIPELINE")
    print("="*80)
    
    loader = ALKISLoader()
    
    # 1. Buildings
    print("\n" + "="*80)
    print("STEP 1: BUILDINGS")
    print("="*80)
    all_buildings = loader.load_buildings()
    buildings = loader.filter_actual_buildings(all_buildings)
    buildings_exclusion = loader.create_exclusion_zone(
        buildings, 
        config.BUFFERS['buildings'],
        "buildings"
    )
    loader.save_geojson(buildings_exclusion, 'exclusion_buildings.geojson')
    
    # 2. Land use (roads, green spaces, water)
    print("\n" + "="*80)
    print("STEP 2: LAND USE")
    print("="*80)
    land_use = loader.load_land_use()
    
    green_spaces = loader.extract_green_spaces(land_use)
    loader.save_geojson(green_spaces, 'green_spaces.geojson')
    
    roads = loader.extract_roads(land_use)
    roads_exclusion = loader.create_exclusion_zone(
        roads,
        config.BUFFERS['roads'],
        "roads"
    )
    loader.save_geojson(roads_exclusion, 'exclusion_roads.geojson')
    
    # Extract water bodies
    water_bodies = loader.extract_water_bodies(land_use)
    if water_bodies is not None and len(water_bodies) > 0:
        loader.save_geojson(water_bodies, 'water_bodies.geojson')
        has_water = True
    else:
        has_water = False
    
    # 3. Fire routes
    print("\n" + "="*80)
    print("STEP 3: FIRE ROUTES 🚒")
    print("="*80)
    fire_routes = loader.load_fire_routes()
    
    if fire_routes is not None and len(fire_routes) > 0:
        fire_exclusion = loader.create_exclusion_zone(
            fire_routes,
            config.BUFFERS['fire_access'],
            "fire routes"
        )
        loader.save_geojson(fire_exclusion, 'exclusion_fire.geojson')
        has_fire = True
    else:
        print("   ⚠️  No fire route data - skipping")
        has_fire = False
    
    # 4. Existing trees
    print("\n" + "="*80)
    print("STEP 4: EXISTING TREES 🌳")
    print("="*80)
    existing_trees = loader.load_existing_trees()
    
    if existing_trees is not None and len(existing_trees) > 0:
        trees_exclusion = loader.create_tree_exclusion_zone(existing_trees)
        loader.save_geojson(trees_exclusion, 'exclusion_trees.geojson')
        has_trees = True
    else:
        print("   ⚠️  No tree data - skipping")
        has_trees = False
    
    # 5. Combine all exclusion zones
    print("\n" + "="*80)
    print("STEP 5: COMBINED EXCLUSION ZONE")
    print("="*80)
    print("🔴 Combining ALL exclusion zones...")
    
    exclusion_geoms = [
        buildings_exclusion.geometry.iloc[0],
        roads_exclusion.geometry.iloc[0]
    ]
    
    if has_fire:
        exclusion_geoms.append(fire_exclusion.geometry.iloc[0])
    if has_trees:
        exclusion_geoms.append(trees_exclusion.geometry.iloc[0])
    if has_water:
        # Water bodies are direct exclusions (no buffer needed)
        water_dissolved = water_bodies.dissolve()
        exclusion_geoms.append(water_dissolved.geometry.iloc[0])
    
    combined_exclusion = gpd.GeoDataFrame(
        geometry=exclusion_geoms,
        crs=config.CRS
    ).dissolve()
    
    loader.save_geojson(combined_exclusion, 'exclusion_combined.geojson')
    
    total_area = combined_exclusion.geometry.area.sum() / 1_000_000
    print(f"   ✅ Combined exclusion zone: {total_area:.2f} km²")
    
    # 6. Calculate plantable area
    print("\n" + "="*80)
    print("STEP 6: FINAL PLANTABLE AREA")
    print("="*80)
    print("🟢 Calculating plantable area...")
    
    green_spaces_dissolved = green_spaces.dissolve()
    plantable = gpd.GeoDataFrame(
        geometry=[green_spaces_dissolved.geometry.iloc[0]],
        crs=config.CRS
    )
    plantable['geometry'] = plantable.geometry.difference(combined_exclusion.geometry.iloc[0])
    
    plantable_area = plantable.geometry.area.sum() / 1_000_000
    print(f"   ✅ Plantable area: {plantable_area:.2f} km²")
    
    loader.save_geojson(plantable, 'plantable_area.geojson')
    
    # 7. Summary
    print("\n" + "="*80)
    print("📊 LEVEL 1 SUMMARY")
    print("="*80)
    print(f"   Buildings excluded: {len(buildings):,} (3m buffer)")
    print(f"   Roads excluded: {len(roads):,} (2.5m buffer)")
    if has_fire:
        print(f"   Fire routes excluded: {len(fire_routes):,} (5m buffer)")
    if has_trees:
        print(f"   Existing trees excluded: {len(existing_trees):,} (dynamic buffer)")
    if has_water:
        print(f"   Water bodies excluded: {len(water_bodies):,}")
    print(f"   Green spaces available: {len(green_spaces):,}")
    print(f"\n   Total exclusion area: {total_area:.2f} km²")
    print(f"   Final plantable area: {plantable_area:.2f} km²")
    
    print("\n" + "="*80)
    print("✅ LEVEL 1 COMPLETE!")
    print("="*80)
    print("\n📁 Files saved:")
    print("   • exclusion_buildings.geojson")
    print("   • exclusion_roads.geojson")
    if has_fire:
        print("   • exclusion_fire.geojson")
    if has_trees:
        print("   • exclusion_trees.geojson")
    if has_water:
        print("   • water_bodies.geojson")
    print("   • exclusion_combined.geojson")
    print("   • green_spaces.geojson")
    print("   • plantable_area.geojson")
    
    print("\n🎯 Next: Level 2 - Heat Map (DOP + DGM)")
    
    return buildings, green_spaces, plantable


if __name__ == "__main__":
    test_alkis_pipeline()
