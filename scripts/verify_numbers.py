"""
Verify all numbers in the data explorer are accurate
"""
import geopandas as gpd
from pathlib import Path
import sys
sys.path.append('.')
from src import config

def verify_all_numbers():
    """Verify every single number we claim"""
    
    print("="*80)
    print("🔍 VERIFYING ALL NUMBERS - FACT CHECK")
    print("="*80)
    
    alkis_path = Path(config.DATA_RAW) / 'ALKIS'
    processed_path = Path(config.DATA_PROCESSED)
    
    # 1. BUILDINGS
    print("\n🏢 BUILDINGS (gebaeudeBauwerke.shp):")
    buildings = gpd.read_file(alkis_path / 'gebaeudeBauwerke.shp')
    total_buildings = len(buildings)
    print(f"   Total buildings: {total_buildings:,}")
    
    if 'funktion' in buildings.columns:
        functions = buildings['funktion'].value_counts()
        
        residential = len(buildings[buildings['funktion'] == 'Wohnhaus'])
        print(f"   ✅ Residential (Wohnhaus): {residential:,}")
        
        garages = len(buildings[buildings['funktion'] == 'Garage'])
        print(f"   ✅ Garages: {garages:,}")
        
        tiefgarage = len(buildings[buildings['funktion'] == 'Tiefgarage'])
        print(f"   ✅ Underground garages (Tiefgarage): {tiefgarage:,}")
        
        parkhaus = len(buildings[buildings['funktion'] == 'Parkhaus'])
        print(f"   ✅ Multi-story parking (Parkhaus): {parkhaus:,}")
        
        tankstelle = len(buildings[buildings['funktion'] == 'Tankstelle'])
        print(f"   ✅ Gas stations (Tankstelle): {tankstelle:,}")
        
        # Total parking structures
        total_parking = garages + tiefgarage + parkhaus
        print(f"   ✅ Total parking structures: {total_parking:,}")
        
        # Commercial buildings (everything that's not residential, parking, or utility)
        residential_types = ['Wohnhaus', 'Wohn- und Geschäftsgebäude', 'Wohn- und Bürogebäude', 
                            'Wohn- und Betriebsgebäude', 'Gartenhaus']
        parking_types = ['Garage', 'Tiefgarage', 'Parkhaus']
        utility_types = ['Garage', 'Schuppen', 'Überdachung', 'Umformer']
        
        commercial = buildings[~buildings['funktion'].isin(residential_types + parking_types + utility_types)]
        print(f"   ✅ Commercial/other buildings: {len(commercial):,}")
        
        print(f"\n   📊 Top 10 building types:")
        for func, count in functions.head(10).items():
            print(f"      {func}: {count:,}")
    
    # 2. ROADS & SURFACE PARKING
    print("\n🛣️  ROADS & LAND USE (nutzung.shp):")
    nutzung = gpd.read_file(alkis_path / 'nutzung.shp')
    total_nutzung = len(nutzung)
    print(f"   Total land use polygons: {total_nutzung:,}")
    
    if 'nutzart' in nutzung.columns:
        nutzart_counts = nutzung['nutzart'].value_counts()
        
        strassenverkehr = len(nutzung[nutzung['nutzart'] == 'Strassenverkehr'])
        print(f"   ✅ Road/traffic areas (Strassenverkehr): {strassenverkehr:,}")
        print(f"      (Includes surface parking)")
        
        water = len(nutzung[nutzung['nutzart'].isin(['Fliessgewaesser', 'Stehendes Gewaesser', 'Hafenbecken'])])
        fliess = len(nutzung[nutzung['nutzart'] == 'Fliessgewaesser'])
        stehend = len(nutzung[nutzung['nutzart'] == 'Stehendes Gewaesser'])
        hafen = len(nutzung[nutzung['nutzart'] == 'Hafenbecken'])
        print(f"   ✅ Water bodies total: {water:,}")
        print(f"      Rivers (Fliessgewaesser): {fliess:,}")
        print(f"      Lakes (Stehendes Gewaesser): {stehend:,}")
        print(f"      Harbor (Hafenbecken): {hafen:,}")
    
    # 3. EXISTING TREES
    print("\n🌳 EXISTING TREES (Baumkataster):")
    trees_path = Path(config.DATA_RAW) / 'Baumkataster'
    tree_files = list(trees_path.glob('*.shp'))
    if tree_files:
        trees = gpd.read_file(tree_files[0])
        print(f"   ✅ Total existing trees: {len(trees):,}")
        
        if 'DEU_TEXT' in trees.columns:
            top_species = trees['DEU_TEXT'].value_counts().head(5)
            print(f"\n   📊 Top 5 tree species:")
            for species, count in top_species.items():
                print(f"      {species}: {count:,}")
    
    # 4. GREEN SPACES
    print("\n🌿 GREEN SPACES:")
    green_file = processed_path / 'green_spaces.geojson'
    if green_file.exists():
        green_spaces = gpd.read_file(green_file)
        print(f"   ✅ Green space polygons: {len(green_spaces):,}")
        total_area = green_spaces.geometry.area.sum() / 1_000_000
        print(f"   ✅ Total green area: {total_area:.2f} km²")
    
    # 5. PLANTABLE AREA
    print("\n✅ PLANTABLE AREA:")
    plantable_file = processed_path / 'plantable_area.geojson'
    if plantable_file.exists():
        plantable = gpd.read_file(plantable_file)
        plantable_area = plantable.geometry.area.sum() / 1_000_000
        print(f"   ✅ Plantable area: {plantable_area:.2f} km²")
    
    # 6. EXCLUSIONS
    print("\n🚫 EXCLUSIONS:")
    exclusion_file = processed_path / 'exclusion_combined.geojson'
    if exclusion_file.exists():
        exclusions = gpd.read_file(exclusion_file)
        print(f"   ✅ Total exclusion features: {len(exclusions):,}")
    
    # 7. SCORED LOCATIONS
    print("\n🎯 SCORED LOCATIONS:")
    scored_file = processed_path / 'scored_locations_all.geojson'
    if scored_file.exists():
        scored = gpd.read_file(scored_file)
        print(f"   ✅ Total candidates analyzed: {len(scored):,}")
        print(f"   ✅ Average score: {scored['final_score'].mean():.2f}")
        print(f"   ✅ Top score: {scored['final_score'].max():.2f}")
    
    # SUMMARY TABLE
    print("\n" + "="*80)
    print("📊 SUMMARY - VERIFY THESE NUMBERS MATCH YOUR CLAIMS")
    print("="*80)
    print(f"\n{'Category':<30} {'Our Claim':<20} {'Actual Data':<20} {'Match?':<10}")
    print("-" * 80)
    
    claims = [
        ("Residential Buildings", "11,746", f"{residential:,}", residential == 11746),
        ("Parking Garages", "8,527", f"{garages + tiefgarage:,}", garages + tiefgarage == 8527),
        ("Multi-story Parking", "35", f"{parkhaus:,}", parkhaus == 35),
        ("Gas Stations", "10", f"{tankstelle:,}", tankstelle == 10),
        ("Surface Parking Areas", "688", f"{strassenverkehr:,}", strassenverkehr == 688),
        ("Water Bodies", "144", f"{water:,}", water == 144),
        ("Total Buildings", "27,018", f"{total_buildings:,}", total_buildings == 27018),
    ]
    
    all_match = True
    for category, claim, actual, match in claims:
        status = "✅" if match else "❌"
        print(f"{category:<30} {claim:<20} {actual:<20} {status:<10}")
        if not match:
            all_match = False
    
    print("\n" + "="*80)
    if all_match:
        print("✅ ALL NUMBERS VERIFIED - 100% ACCURATE!")
    else:
        print("⚠️  SOME NUMBERS DON'T MATCH - UPDATE REQUIRED!")
    print("="*80)

if __name__ == "__main__":
    verify_all_numbers()