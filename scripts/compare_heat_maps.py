"""
Compare original vs improved heat maps
"""
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import sys
sys.path.append('.')
from src import config

processed = Path(config.DATA_PROCESSED)

# Load both
original = np.load(processed / 'heat_map.npy')
improved = np.load(processed / 'heat_map_improved.npy')

# Calculate difference
difference = improved - original

print("="*80)
print("📊 HEAT MAP COMPARISON")
print("="*80)

print(f"\n📈 Statistics:")
print(f"   Original Mean: {original.mean():.2f}")
print(f"   Improved Mean: {improved.mean():.2f}")
print(f"   Change: {improved.mean() - original.mean():+.2f}")

print(f"\n🔥 Hot Areas (>80):")
print(f"   Original: {(original > 80).sum():,} pixels")
print(f"   Improved: {(improved > 80).sum():,} pixels")
print(f"   Increase: {(improved > 80).sum() - (original > 80).sum():+,} pixels")

print(f"\n❄️  Cool Areas (<40):")
print(f"   Original: {(original < 40).sum():,} pixels")
print(f"   Improved: {(improved < 40).sum():,} pixels")
print(f"   Change: {(improved < 40).sum() - (original < 40).sum():+,} pixels")

# Create visualization
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

# Original
im1 = axes[0].imshow(original, cmap='RdYlGn_r', vmin=0, vmax=100)
axes[0].set_title('Original Heat Map\n(Vegetation-based)', fontsize=14, fontweight='bold')
axes[0].axis('off')
plt.colorbar(im1, ax=axes[0], label='Heat Score')

# Improved
im2 = axes[1].imshow(improved, cmap='RdYlGn_r', vmin=0, vmax=100)
axes[1].set_title('Improved Heat Map\n(Multi-factor)', fontsize=14, fontweight='bold')
axes[1].axis('off')
plt.colorbar(im2, ax=axes[1], label='Heat Score')

# Difference
im3 = axes[2].imshow(difference, cmap='RdBu_r', vmin=-50, vmax=50)
axes[2].set_title('Difference\n(Improved - Original)', fontsize=14, fontweight='bold')
axes[2].axis('off')
plt.colorbar(im3, ax=axes[2], label='Change in Heat Score')

plt.tight_layout()
output = Path(config.DATA_OUTPUTS) / 'heat_map_comparison.png'
plt.savefig(output, dpi=300, bbox_inches='tight')
print(f"\n💾 Saved visualization: {output}")

plt.close()

print("\n" + "="*80)
print("✅ COMPARISON COMPLETE!")
print("="*80)