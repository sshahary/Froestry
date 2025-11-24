"""
Check metadata and dates of all datasets
"""
import geopandas as gpd
import rasterio
from pathlib import Path
import os
from datetime import datetime
import sys
sys.path.append('.')
from src import config

def check_all_metadata():
    """Check metadata for all datasets"""
    
    print("="*80)
    print("📅 CHECKING DATA FRESHNESS & METADATA")
    print("="*80)
    
    alkis_path = Path(config.DATA_RAW) / 'ALKIS'
    
    # Check ALKIS files
    print("\n🏢 ALKIS DATA:")
    print("-" * 80)
    
    alkis_files = {
        'Buildings': 'gebaeudeBauwerke.shp',
        'Land Use': 'nutzung.shp',
        'Parcels': 'flurstueck.shp',
        'Admin Units': 'verwaltungseinheit.shp'
    }
    
    for name, filename in alkis_files.items():
        filepath = alkis_path / filename
        if filepath.exists():
            print(f"\n📂 {name} ({filename}):")
            
            # File modification date
            mod_time = os.path.getmtime(filepath)
            mod_date = datetime.fromtimestamp(mod_time)
            print(f"   📆 File last modified: {mod_date.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # File size
            file_size = os.path.getsize(filepath) / (1024 * 1024)
            print(f"   📦 File size: {file_size:.2f} MB")
            
            # Read shapefile metadata
            try:
                gdf = gpd.read_file(filepath)
                print(f"   📊 Features: {len(gdf):,}")
                print(f"   🗺️  CRS: {gdf.crs}")
                print(f"   📋 Columns: {list(gdf.columns)}")
                
                # Check for date/timestamp columns
                date_columns = [col for col in gdf.columns 
                               if any(x in col.lower() for x in ['date', 'datum', 'zeit', 'time', 'aktual', 'update'])]
                
                if date_columns:
                    print(f"   📅 Date columns found: {date_columns}")
                    for date_col in date_columns:
                        sample_dates = gdf[date_col].dropna().unique()[:5]
                        print(f"      {date_col}: {sample_dates}")
                else:
                    print(f"   ⚠️  No date columns found in data")
                
                # Check aktualit column specifically (common in ALKIS)
                if 'aktualit' in gdf.columns:
                    print(f"\n   📅 AKTUALIT (Data Currency):")
                    aktualit_values = gdf['aktualit'].value_counts()
                    for val, count in aktualit_values.head(5).items():
                        print(f"      {val}: {count:,} features")
                
            except Exception as e:
                print(f"   ❌ Error reading file: {e}")
    
    # Check Baumkataster
    print("\n\n🌳 BAUMKATASTER (Tree Cadastre):")
    print("-" * 80)
    
    trees_path = Path(config.DATA_RAW) / 'Baumkataster'
    tree_files = list(trees_path.glob('*.shp')) if trees_path.exists() else []
    
    if tree_files:
        for tree_file in tree_files:
            print(f"\n📂 {tree_file.name}:")
            
            mod_time = os.path.getmtime(tree_file)
            mod_date = datetime.fromtimestamp(mod_time)
            print(f"   📆 File last modified: {mod_date.strftime('%Y-%m-%d %H:%M:%S')}")
            
            file_size = os.path.getsize(tree_file) / (1024 * 1024)
            print(f"   📦 File size: {file_size:.2f} MB")
            
            try:
                trees = gpd.read_file(tree_file)
                print(f"   📊 Trees: {len(trees):,}")
                print(f"   📋 Columns: {list(trees.columns)}")
                
                # Check for date columns
                date_columns = [col for col in trees.columns 
                               if any(x in col.lower() for x in ['date', 'datum', 'pflanz', 'erfass', 'update', 'jahr'])]
                
                if date_columns:
                    print(f"   📅 Date-related columns: {date_columns}")
                    for date_col in date_columns:
                        if trees[date_col].notna().any():
                            sample = trees[date_col].dropna().unique()[:5]
                            print(f"      {date_col}: {sample}")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
    else:
        print("   ⚠️  No Baumkataster files found")
    
    # Check DOP (Aerial Imagery)
    print("\n\n📸 DOP AERIAL IMAGERY:")
    print("-" * 80)
    
    dop_path = Path(config.DATA_RAW) / 'DOP20RGBI'
    dop_files = list(dop_path.glob('*.tif')) if dop_path.exists() else []
    
    if dop_files:
        for dop_file in dop_files[:3]:  # Check first 3 files
            print(f"\n📂 {dop_file.name}:")
            
            # Check filename for date (often in format: dop20rgbi_32_514_5443_1_bw_2024.tif)
            if '2024' in dop_file.name or '2023' in dop_file.name or '2022' in dop_file.name:
                year = '2024' if '2024' in dop_file.name else '2023' if '2023' in dop_file.name else '2022'
                print(f"   📅 Year from filename: {year}")
            
            mod_time = os.path.getmtime(dop_file)
            mod_date = datetime.fromtimestamp(mod_time)
            print(f"   📆 File last modified: {mod_date.strftime('%Y-%m-%d %H:%M:%S')}")
            
            file_size = os.path.getsize(dop_file) / (1024 * 1024)
            print(f"   📦 File size: {file_size:.2f} MB")
            
            # Read raster metadata
            try:
                with rasterio.open(dop_file) as src:
                    print(f"   📐 Dimensions: {src.width} x {src.height}")
                    print(f"   📊 Bands: {src.count}")
                    print(f"   🗺️  CRS: {src.crs}")
                    
                    # Check for date in metadata tags
                    if src.tags():
                        print(f"   📋 Metadata tags:")
                        for key, value in src.tags().items():
                            if any(x in key.lower() for x in ['date', 'time', 'year', 'acquisition']):
                                print(f"      {key}: {value}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        if len(dop_files) > 3:
            print(f"\n   ... and {len(dop_files) - 3} more DOP files")
    else:
        print("   ⚠️  No DOP files found")
    
    # Check Green Spaces
    print("\n\n🌿 GREEN SPACES:")
    print("-" * 80)
    
    green_files = list(Path(config.DATA_RAW).rglob('*gruenflaeche*.shp'))
    green_files.extend(list(Path(config.DATA_RAW).rglob('*green*.shp')))
    
    if green_files:
        for green_file in green_files[:2]:
            print(f"\n📂 {green_file.name}:")
            
            mod_time = os.path.getmtime(green_file)
            mod_date = datetime.fromtimestamp(mod_time)
            print(f"   📆 File last modified: {mod_date.strftime('%Y-%m-%d %H:%M:%S')}")
            
            try:
                green = gpd.read_file(green_file)
                print(f"   📊 Features: {len(green):,}")
                print(f"   📋 Columns: {list(green.columns)}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    # Summary
    print("\n\n" + "="*80)
    print("📊 DATA FRESHNESS SUMMARY")
    print("="*80)
    
    print("\n🔍 Key Findings:")
    
    # Check if we found any date information
    has_date_info = False
    
    # Summarize what we found
    print("\n✅ Recommendations:")
    print("   1. Check 'aktualit' column in ALKIS - this is the official currency date")
    print("   2. DOP filename suggests 2024 data (if '2024' in name)")
    print("   3. File modification dates show when data was downloaded, not collected")
    print("   4. ALKIS data in Germany is typically updated quarterly")
    
    print("\n⚠️  IMPORTANT:")
    print("   If your on-site verification doesn't match:")
    print("   • Data might be from earlier in 2024 (Q1 or Q2)")
    print("   • Construction could have happened after data collection")
    print("   • Coordinates could be in different reference system")
    print("   • Need to verify CRS transformation is correct")

if __name__ == "__main__":
    check_all_metadata()