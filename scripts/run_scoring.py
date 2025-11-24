"""
Run complete Level 3 scoring pipeline
"""
import geopandas as gpd
from pathlib import Path
import sys
sys.path.append('.')
from src import config
from src.processors.scoring import TreeLocationScorer

def run_complete_scoring():
    """Run complete scoring and ranking pipeline"""
    
    print("="*80)
    print("🎮 LEVEL 3: COMPLETE SCORING & RANKING SYSTEM")
    print("="*80)
    
    # Initialize scorer
    scorer = TreeLocationScorer()
    
    # Generate candidate points
    candidates = scorer.generate_candidate_points(spacing=10)
    
    # Calculate scores
    scored_candidates = scorer.calculate_final_scores(candidates)
    
    # Sort by score (highest first)
    print("\n📊 Ranking locations...")
    scored_candidates = scored_candidates.sort_values('final_score', ascending=False).reset_index(drop=True)
    scored_candidates['rank'] = range(1, len(scored_candidates) + 1)
    
    # Save all scored locations
    print("\n💾 Saving results...")
    output_path = Path(config.DATA_PROCESSED) / 'scored_locations_all.geojson'
    scored_candidates.to_file(output_path, driver='GeoJSON')
    print(f"   ✅ Saved all {len(scored_candidates):,} locations")
    
    # Save top 100
    top_100 = scored_candidates.head(100)
    top_100_path = Path(config.DATA_PROCESSED) / 'top_100_locations.geojson'
    top_100.to_file(top_100_path, driver='GeoJSON')
    print(f"   ✅ Saved top 100 locations")
    
    # Save as CSV for easy viewing
    csv_path = Path(config.DATA_OUTPUTS) / 'top_100_tree_locations.csv'
    top_100_csv = top_100.copy()
    top_100_csv['x'] = top_100_csv.geometry.x
    top_100_csv['y'] = top_100_csv.geometry.y
    top_100_csv[['rank', 'final_score', 'heat_score', 'spatial_score', 
                  'social_score', 'maintenance_score', 'x', 'y']].to_csv(csv_path, index=False)
    print(f"   ✅ Saved CSV: {csv_path}")
    
    # Print summary
    print("\n" + "="*80)
    print("📊 SCORING SUMMARY")
    print("="*80)
    print(f"   Total candidates evaluated: {len(scored_candidates):,}")
    print(f"   Top score: {scored_candidates['final_score'].iloc[0]:.2f}")
    print(f"   Top 10 average: {scored_candidates.head(10)['final_score'].mean():.2f}")
    print(f"   Top 100 average: {top_100['final_score'].mean():.2f}")
    
    print("\n🏆 TOP 5 LOCATIONS:")
    for idx, row in top_100.head(5).iterrows():
        print(f"   #{row['rank']}: Score {row['final_score']:.2f} at ({row.geometry.x:.1f}, {row.geometry.y:.1f})")
    
    print("\n" + "="*80)
    print("✅ LEVEL 3 COMPLETE!")
    print("="*80)
    print("\n📁 Files created:")
    print(f"   • {output_path.name} - All scored locations")
    print(f"   • {top_100_path.name} - Top 100 locations")
    print(f"   • {csv_path.name} - CSV export")
    
    print("\n🎯 Next: Visualize top locations on map!")
    
    return scored_candidates, top_100

if __name__ == "__main__":
    scored_all, top_100 = run_complete_scoring()