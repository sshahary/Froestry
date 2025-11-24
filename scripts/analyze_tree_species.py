"""
Analyze existing tree species in Baumkataster to inform recommendations
"""
import geopandas as gpd
from pathlib import Path
import sys
sys.path.append('.')
from src import config

def analyze_existing_trees():
    """Analyze what trees grow well in Heilbronn"""
    
    print("🌳 Analyzing Existing Tree Species in Heilbronn...\n")
    print("="*80)
    
    # Load Baumkataster
    trees_path = Path(config.DATA_RAW) / 'Baumkataster'
    tree_files = list(trees_path.glob('*.shp'))
    
    if not tree_files:
        print("❌ Baumkataster not found!")
        return None
    
    trees = gpd.read_file(tree_files[0])
    
    print(f"📊 Total trees in database: {len(trees):,}")
    print(f"\n📋 Available columns: {list(trees.columns)}")
    
    # Analyze by species (DEU_TEXT = German name, WIS_TEXT = Scientific name)
    if 'DEU_TEXT' in trees.columns:
        print("\n🌲 TOP 10 TREE SPECIES IN HEILBRONN:")
        print("="*80)
        
        species_counts = trees['DEU_TEXT'].value_counts().head(10)
        
        for i, (species, count) in enumerate(species_counts.items(), 1):
            percentage = (count / len(trees)) * 100
            
            # Get scientific name if available
            sci_name = ""
            if 'WIS_TEXT' in trees.columns:
                match = trees[trees['DEU_TEXT'] == species]['WIS_TEXT'].iloc[0]
                sci_name = f" ({match})" if match else ""
            
            print(f"   {i:2d}. {species}{sci_name}")
            print(f"       Count: {count:,} ({percentage:.1f}%)")
    
    # Analyze by tree type
    if 'TYP' in trees.columns:
        print("\n🌿 TREE TYPES:")
        print("="*80)
        type_counts = trees['TYP'].value_counts()
        for typ, count in type_counts.items():
            print(f"   {typ}: {count:,} ({count/len(trees)*100:.1f}%)")
    
    # Analyze by crown diameter
    if 'KRONE_DM' in trees.columns:
        print("\n👑 CROWN DIAMETER ANALYSIS:")
        print("="*80)
        crowns = trees[trees['KRONE_DM'] > 0]['KRONE_DM']
        print(f"   Average crown: {crowns.mean():.2f}m")
        print(f"   Small trees (<5m): {len(crowns[crowns < 5]):,}")
        print(f"   Medium trees (5-10m): {len(crowns[(crowns >= 5) & (crowns < 10)]):,}")
        print(f"   Large trees (>10m): {len(crowns[crowns >= 10]):,}")
    
    # Analyze by location type (stadtteile)
    if 'STADTTEIL' in trees.columns:
        print("\n🏘️  DISTRIBUTION BY DISTRICT:")
        print("="*80)
        districts = trees['STADTTEIL'].value_counts().head(5)
        for district, count in districts.items():
            print(f"   {district}: {count:,}")
    
    print("\n" + "="*80)
    print("💡 RECOMMENDATIONS BASED ON DATA:")
    print("="*80)
    
    if 'DEU_TEXT' in trees.columns:
        top_5_species = species_counts.head(5).index.tolist()
        print("   These species are proven to thrive in Heilbronn:")
        for i, species in enumerate(top_5_species, 1):
            print(f"   {i}. {species}")
    
    return trees

if __name__ == "__main__":
    analyze_existing_trees()