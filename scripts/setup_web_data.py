#!/usr/bin/env python3
"""
Setup script to copy processed GeoJSON files to web public directory
"""

import os
import shutil
from pathlib import Path

def setup_web_data():
    """Copy GeoJSON files from data/processed to web/public/data"""
    
    # Define paths
    source_dir = Path("data/processed")
    target_dir = Path("web/public/data")
    
    # Create target directory if it doesn't exist
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # List of GeoJSON files to copy
    geojson_files = [
        "exclusion_buildings.geojson",
        "exclusion_buildings_fresh.geojson", 
        "exclusion_roads.geojson",
        "exclusion_roads_fresh.geojson",
        "exclusion_trees.geojson",
        "exclusion_fire.geojson",
        "water_bodies.geojson",
        "plantable_area.geojson",
        "plantable_area_fresh.geojson",
        "exclusion_combined.geojson",
        "exclusion_combined_fresh.geojson",
        "green_spaces.geojson",
        "top_100_locations.geojson",
        "top_100_fresh.geojson",
        "top_100_enhanced.geojson",
        "scored_locations_all.geojson",
        "scored_locations_all_enhanced.geojson",
        "scored_locations_fresh.geojson",
        "scored_locations_fresh_enhanced.geojson",
        "top_100_with_coordinates.geojson",
    ]
    
    # Copy CSV files too
    csv_files = [
        "../outputs/top_100_detailed.csv",
        "../outputs/nearest_fresh_locations.csv",
    ]
    
    copied_files = []
    
    # Copy GeoJSON files
    for filename in geojson_files:
        source_file = source_dir / filename
        target_file = target_dir / filename
        
        if source_file.exists():
            shutil.copy2(source_file, target_file)
            copied_files.append(filename)
            print(f"✅ Copied {filename}")
        else:
            print(f"⚠️  File not found: {filename}")
    
    # Copy CSV files
    for filename in csv_files:
        source_file = Path("data") / filename
        target_file = target_dir / Path(filename).name
        
        if source_file.exists():
            shutil.copy2(source_file, target_file)
            copied_files.append(Path(filename).name)
            print(f"✅ Copied {Path(filename).name}")
        else:
            print(f"⚠️  File not found: {filename}")
    
    print(f"\n🎉 Setup complete! Copied {len(copied_files)} files to {target_dir}")
    print(f"Files available for web app: {', '.join(copied_files)}")
    
    return copied_files

if __name__ == "__main__":
    setup_web_data()