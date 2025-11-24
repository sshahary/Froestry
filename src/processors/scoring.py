"""
Complete scoring system for tree planting locations
"""
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.features import rasterize
from shapely.geometry import Point
from pathlib import Path
from tqdm import tqdm
import sys
import pandas as pd
sys.path.append('.')
from src import config

class TreeLocationScorer:
    """Score potential tree planting locations"""
    
    def __init__(self):
        """Initialize scorer with all necessary data"""
        self.processed_path = Path(config.DATA_PROCESSED)
        self.raw_path = Path(config.DATA_RAW)
        
        print("🎯 Initializing Tree Location Scorer...")
        
        # Load all required datasets
        self._load_data()
    
    def _load_data(self):
        """Load all required datasets"""
        print("\n📂 Loading datasets...")
        
        # Essential data
        self.plantable = gpd.read_file(self.processed_path / 'plantable_area.geojson')
        self.green_spaces = gpd.read_file(self.processed_path / 'green_spaces.geojson')
        
        # Buildings (from ALKIS)
        buildings_file = self.processed_path / 'exclusion_buildings.geojson'
        if buildings_file.exists():
            self.buildings = gpd.read_file(buildings_file)
            print("   ✅ Buildings loaded")
        else:
            self.buildings = None
            print("   ⚠️  Buildings not found")
        
        # Existing trees (from Baumkataster)
        trees_folder = self.raw_path / 'Baumkataster'
        tree_files = list(trees_folder.glob('*.shp')) if trees_folder.exists() else []
        if tree_files:
            self.existing_trees = gpd.read_file(tree_files[0])
            if self.existing_trees.crs != config.CRS:
                self.existing_trees = self.existing_trees.to_crs(config.CRS)
            print(f"   ✅ Existing trees loaded: {len(self.existing_trees):,}")
        else:
            self.existing_trees = None
            print("   ⚠️  Existing trees not found")
        
        # Roads (for maintenance access)
        roads_file = self.processed_path / 'exclusion_roads.geojson'
        if roads_file.exists():
            self.roads = gpd.read_file(roads_file)
            print("   ✅ Roads loaded")
        else:
            self.roads = None
            print("   ⚠️  Roads not found")
        
        # Land use (for residential, schools, etc.)
        alkis_path = self.raw_path / 'ALKIS'
        land_use_file = alkis_path / 'nutzung.shp'
        if land_use_file.exists():
            self.land_use = gpd.read_file(land_use_file)
            if self.land_use.crs != config.CRS:
                self.land_use = self.land_use.to_crs(config.CRS)
            print("   ✅ Land use loaded")
        else:
            self.land_use = None
            print("   ⚠️  Land use not found")
        
        # Heat map
        heat_file = self.processed_path / 'heat_map.tif'
        if heat_file.exists():
            self.heat_map = rasterio.open(heat_file)
            print("   ✅ Heat map loaded")
        else:
            self.heat_map = None
            print("   ⚠️  Heat map not found")
        
        print("   ✅ Data loading complete!")
    
    def generate_candidate_points(self, spacing=10):
        """
        Generate candidate tree planting points in a grid
        
        Args:
            spacing: Distance between points in meters
            
        Returns:
            GeoDataFrame: Candidate points
        """
        print(f"\n🔵 Generating candidate points ({spacing}m spacing)...")
        
        # Get bounds of plantable area
        bounds = self.plantable.total_bounds
        minx, miny, maxx, maxy = bounds
        
        # Create grid
        x_coords = np.arange(minx, maxx, spacing)
        y_coords = np.arange(miny, maxy, spacing)
        
        xx, yy = np.meshgrid(x_coords, y_coords)
        points = [Point(x, y) for x, y in zip(xx.ravel(), yy.ravel())]
        
        print(f"   📊 Generated {len(points):,} grid points")
        
        # Create GeoDataFrame
        candidates = gpd.GeoDataFrame(geometry=points, crs=config.CRS)
        
        # Keep only points within plantable areas
        print("   ✂️  Filtering to plantable areas...")
        candidates = gpd.sjoin(candidates, self.plantable, predicate='within', how='inner')
        candidates = candidates[['geometry']].reset_index(drop=True)
        
        print(f"   ✅ {len(candidates):,} candidate points in plantable areas")
        
        return candidates
    
    def score_heat_mitigation(self, candidates):
        """
        Score based on heat priority (40% weight)
        
        Args:
            candidates: GeoDataFrame of candidate points
            
        Returns:
            numpy array: Heat scores (0-100)
        """
        print("\n🔥 Scoring: Heat Mitigation Need (40% weight)...")
        
        if self.heat_map is None:
            print("   ⚠️  No heat map - using default score 50")
            return np.full(len(candidates), 50.0)
        
        # Sample heat map at each point
        coords = [(point.x, point.y) for point in candidates.geometry]
        
        heat_scores = []
        for x, y in tqdm(coords, desc="   Sampling heat map"):
            try:
                row, col = self.heat_map.index(x, y)
                value = self.heat_map.read(1, window=((row, row+1), (col, col+1)))[0, 0]
                heat_scores.append(float(value))
            except:
                heat_scores.append(50.0)  # Default if outside bounds
        
        heat_scores = np.array(heat_scores)
        
        print(f"   ✅ Heat scores: mean={heat_scores.mean():.1f}, range={heat_scores.min():.1f}-{heat_scores.max():.1f}")
        
        return heat_scores
    
    def score_spatial_suitability(self, candidates):
        """
        Score based on spatial factors (30% weight)
        
        Args:
            candidates: GeoDataFrame of candidate points
            
        Returns:
            numpy array: Spatial scores (0-100)
        """
        print("\n📏 Scoring: Spatial Suitability (30% weight)...")
        
        spatial_scores = np.zeros(len(candidates))
        
        # Sub-score 1: Distance from buildings (10 points max)
        if self.buildings is not None:
            print("   📐 Distance from buildings...")
            dist_to_buildings = candidates.geometry.apply(
                lambda point: self.buildings.distance(point).min()
            )
            
            # 3-8m = 10 pts (optimal shade), >15m = 5 pts
            building_scores = np.where(
                (dist_to_buildings >= 3) & (dist_to_buildings <= 8), 10,
                np.where(dist_to_buildings > 15, 5, 7)
            )
            spatial_scores += building_scores
            print(f"      Mean: {building_scores.mean():.1f}/10")
        else:
            spatial_scores += 7  # Default
        
        # Sub-score 2: Distance from existing trees (10 points max)
        if self.existing_trees is not None:
            print("   🌳 Distance from existing trees...")
            dist_to_trees = candidates.geometry.apply(
                lambda point: self.existing_trees.distance(point).min()
            )
            
            # >10m = 10 pts, 6-10m = 5 pts
            tree_scores = np.where(dist_to_trees > 10, 10, 5)
            spatial_scores += tree_scores
            print(f"      Mean: {tree_scores.mean():.1f}/10")
        else:
            spatial_scores += 8  # Default
        
        # Sub-score 3: Available space (10 points max)
        # Check size of green space polygon containing each point
        print("   📦 Available space size...")
        
        # Join with green spaces to get polygon info
        joined = gpd.sjoin(candidates, self.green_spaces, predicate='within', how='left')
        
        space_scores = []
        for idx, row in joined.iterrows():
            if pd.notna(row.get('index_right')):
                # Get the green space polygon
                polygon = self.green_spaces.iloc[int(row['index_right'])].geometry
                area = polygon.area
                
                # >25m² = 10 pts, 10-25m² = 7 pts, <10m² = 4 pts
                if area > 25:
                    space_scores.append(10)
                elif area >= 10:
                    space_scores.append(7)
                else:
                    space_scores.append(4)
            else:
                space_scores.append(7)  # Default
        
        spatial_scores += np.array(space_scores)
        print(f"      Mean: {np.mean(space_scores):.1f}/10")
        
        # Normalize to 0-100
        spatial_scores = (spatial_scores / 30) * 100
        
        print(f"   ✅ Spatial scores: mean={spatial_scores.mean():.1f}")
        
        return spatial_scores
    
    def score_social_impact(self, candidates):
        """
        Score based on social benefit (20% weight)
        
        Args:
            candidates: GeoDataFrame of candidate points
            
        Returns:
            numpy array: Social scores (0-100)
        """
        print("\n👥 Scoring: Social Impact (20% weight)...")
        
        social_scores = np.zeros(len(candidates))
        
        if self.land_use is None:
            print("   ⚠️  No land use data - using default score 50")
            return np.full(len(candidates), 50.0)
        
        # Extract different land use types
        residential = self.land_use[self.land_use['nutzart'] == 'Wohnbauflaeche']
        
        # Sub-score 1: Near residential (7 points max)
        if len(residential) > 0:
            print("   🏠 Proximity to residential areas...")
            candidates['temp_geom'] = candidates.geometry.buffer(100)
            temp_gdf = gpd.GeoDataFrame(candidates[['temp_geom']], geometry='temp_geom', crs=config.CRS)
            
            intersects_residential = temp_gdf.intersects(residential.unary_union)
            residential_scores = np.where(intersects_residential, 7, 0)
            social_scores += residential_scores
            
            candidates.drop('temp_geom', axis=1, inplace=True)
            print(f"      {np.sum(intersects_residential)} points near residential")
        
        # Sub-score 2: Near schools/education (7 points max)
        # Look for education-related land use
        education_types = ['Sport Freizeit Und Erholungsflaeche', 'Flaeche Besonderer Funktionaler Praegung']
        education = self.land_use[self.land_use['nutzart'].isin(education_types)]
        
        if len(education) > 0:
            print("   🏫 Proximity to schools/recreation...")
            candidates['temp_geom'] = candidates.geometry.buffer(150)
            temp_gdf = gpd.GeoDataFrame(candidates[['temp_geom']], geometry='temp_geom', crs=config.CRS)
            
            intersects_education = temp_gdf.intersects(education.unary_union)
            education_scores = np.where(intersects_education, 7, 0)
            social_scores += education_scores
            
            candidates.drop('temp_geom', axis=1, inplace=True)
            print(f"      {np.sum(intersects_education)} points near schools/recreation")
        
        # Sub-score 3: General accessibility (6 points - default for public green spaces)
        social_scores += 6
        
        # Normalize to 0-100
        social_scores = (social_scores / 20) * 100
        
        print(f"   ✅ Social scores: mean={social_scores.mean():.1f}")
        
        return social_scores
    
    def score_maintenance_access(self, candidates):
        """
        Score based on maintenance ease (10% weight)
        
        Args:
            candidates: GeoDataFrame of candidate points
            
        Returns:
            numpy array: Maintenance scores (0-100)
        """
        print("\n🚜 Scoring: Maintenance & Access (10% weight)...")
        
        maintenance_scores = np.zeros(len(candidates))
        
        # Sub-score 1: Distance to road access (10 points max)
        if self.roads is not None:
            print("   🛣️  Distance to vehicle access...")
            dist_to_roads = candidates.geometry.apply(
                lambda point: self.roads.distance(point).min()
            )
            
            # <5m = 10 pts, 5-10m = 7 pts, >10m = 3 pts
            road_scores = np.where(
                dist_to_roads < 5, 10,
                np.where(dist_to_roads < 10, 7, 3)
            )
            maintenance_scores += road_scores
            print(f"      Mean: {road_scores.mean():.1f}/10")
        else:
            maintenance_scores += 7  # Default
        
        # Sub-score 2: Within maintained green space (5 points)
        # All candidates are in green spaces by definition
        maintenance_scores += 5
        
        # Normalize to 0-100
        maintenance_scores = (maintenance_scores / 15) * 100
        
        print(f"   ✅ Maintenance scores: mean={maintenance_scores.mean():.1f}")
        
        return maintenance_scores
    
    def calculate_final_scores(self, candidates):
        """
        Calculate final weighted scores for all candidates
        
        Args:
            candidates: GeoDataFrame of candidate points
            
        Returns:
            GeoDataFrame: Candidates with scores
        """
        print("\n" + "="*80)
        print("🧮 CALCULATING FINAL SCORES")
        print("="*80)
        
        # Calculate all component scores
        heat_scores = self.score_heat_mitigation(candidates)
        spatial_scores = self.score_spatial_suitability(candidates)
        social_scores = self.score_social_impact(candidates)
        maintenance_scores = self.score_maintenance_access(candidates)
        
        # Apply weights and calculate final score
        print("\n⚖️  Applying weights...")
        print(f"   Heat: 40%")
        print(f"   Spatial: 30%")
        print(f"   Social: 20%")
        print(f"   Maintenance: 10%")
        
        final_scores = (
            heat_scores * config.WEIGHTS['heat'] +
            spatial_scores * config.WEIGHTS['spatial'] +
            social_scores * config.WEIGHTS['social'] +
            maintenance_scores * config.WEIGHTS['maintenance']
        )
        
        # Add scores to candidates
        candidates['heat_score'] = heat_scores
        candidates['spatial_score'] = spatial_scores
        candidates['social_score'] = social_scores
        candidates['maintenance_score'] = maintenance_scores
        candidates['final_score'] = final_scores
        
        print(f"\n✅ Final scores calculated!")
        print(f"   Mean: {final_scores.mean():.2f}")
        print(f"   Range: {final_scores.min():.2f} - {final_scores.max():.2f}")
        print(f"   Std: {final_scores.std():.2f}")
        
        return candidates


