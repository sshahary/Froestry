"""
Configuration file for tree planting algorithm
"""

# Coordinate Reference System (EPSG:25832 for Heilbronn)
CRS = "EPSG:25832"

# Buffer distances (meters)
BUFFERS = {
    'buildings': 3.0,
    'existing_trees': 6.0,
    'fire_access': 5.0,
    'roads': 2.5,
}

# Slope thresholds (degrees)
SLOPE_MAX = 15.0
SLOPE_IDEAL = 5.0

# Scoring weights
WEIGHTS = {
    'heat': 0.40,
    'spatial': 0.30,
    'social': 0.20,
    'maintenance': 0.10,
}

# Tree spacing (meters)
TREE_SPACING_MIN = 8.0
TREE_SPACING_MAX = 12.0

# NDVI thresholds
NDVI_THRESHOLDS = {
    'bare': 0.2,
    'sparse': 0.4,
    'moderate': 0.6,
    'dense': 0.8,
}

# Postal codes
POSTAL_CODES = ['74072', '74074', '74076', '74078']

# Output settings
TOP_N_LOCATIONS = 100
GRID_SIZE = 5.0

# File paths
DATA_RAW = 'data/raw/'
DATA_PROCESSED = 'data/processed/'
DATA_OUTPUTS = 'data/outputs/'