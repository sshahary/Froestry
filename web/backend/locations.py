from enum import Enum
import json
import pandas as pd
from scipy.spatial import cKDTree
from pydantic import BaseModel

class GeoLocator:
    def __init__(self, geojson_path):
        # --- Constants for Heilbronn Area ---
        self.KM_PER_LAT = 111.32
        self.KM_PER_LON = 73.0

        # Load data once when class is initialized
        with open(geojson_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        # Convert features to a Pandas DataFrame for easier handling/sorting later
        self.features_df = pd.DataFrame(self.data['features'])
        self.features = self.data['features']
        
        # Extract coordinates and scale them to "Kilometer Space"
        # We scale BEFORE building the tree so the tree measures distance in km, not degrees.
        # GeoJSON coordinates are [Longitude, Latitude]
        self.coords = [
            (f['geometry']['coordinates'][1], f['geometry']['coordinates'][0]) 
            for f in self.features
        ]

        self.coords_tree = cKDTree(self.coords)

        self.coords_km = [
            (
                f['geometry']['coordinates'][1] * self.KM_PER_LAT, # Latitude -> km
                f['geometry']['coordinates'][0] * self.KM_PER_LON  # Longitude -> km
            ) 
            for f in self.data['features']
        ]
        
        # Create the Tree (Spatial Index) using the scaled coordinates
        self.km_tree = cKDTree(self.coords_km)

    def find_closest(self, target_lat, target_lon):
        # query() returns tuple: (distance, index)
        # k=1 means return only the single closest point
        dist, idx = self.coords_tree.query((target_lat, target_lon), k=1)
        
        # Retrieve the feature using the index
        closest_feature = self.features[idx]
        
        # Note: The 'dist' returned here is Euclidean distance in degrees.
        # If you need precise meters, you should calculate Haversine 
        # on the result after finding it.
        return closest_feature
    
    def get_nearest_locations(self, target_lat, target_lon, radius_km):
        target_point = (target_lat * self.KM_PER_LAT, target_lon * self.KM_PER_LON)

        # query_ball_point returns indices of all points within the radius
        # r=radius_km works directly because our tree is in km units
        indices = self.km_tree.query_ball_point(target_point, r=radius_km)

        # Retrieve the matching rows using the indices
        nearby_df = self.features_df.iloc[indices].copy()

        # --- NEW: Calculate Distance ---
        # We use the pre-calculated 'self.coords_km' to save re-doing the math
        nearby_df['distance_from_search_point'] = [
            ((self.coords_km[i][0] - target_point[0])**2 + 
             (self.coords_km[i][1] - target_point[1])**2)**0.5 
            for i in indices
        ]

        return nearby_df
    
    # properties: heat_score, final_score, distance

    def sort_by_distance(self, nearby_df):
        # nearby, not furthest
        top_df = nearby_df.sort_values(by='distance_from_search_point', ascending=True)

        return top_df

    def sort_by_final_score(self, nearby_df):
        """
        Finds locations within radius_km, sorts them by final_score, and returns the top N.
        """
        # Scale the target coordinate to the same "Kilometer Space"

        # Retrieve the matching rows using the indices

        # Extract score for sorting (handling missing scores safely)
        # We create a temporary column for sorting to avoid modifying the actual properties
        nearby_df['_temp_score'] = nearby_df['properties'].apply(lambda x: x.get('final_score', 0))

        # Sort by score descending
        top_df = nearby_df.sort_values(by='_temp_score', ascending=False)

        return top_df.drop(columns=['_temp_score'])

    def sort_by_heat_score(self, nearby_df):
        """
        Finds locations within radius_km, sorts them by final_score, and returns the top N.
        """
        # Scale the target coordinate to the same "Kilometer Space"

        # Retrieve the matching rows using the indices

        # Extract score for sorting (handling missing scores safely)
        # We create a temporary column for sorting to avoid modifying the actual properties
        nearby_df['_temp_score'] = nearby_df['properties'].apply(lambda x: x.get('heat_score', 0))

        # Sort by score descending
        top_df = nearby_df.sort_values(by='_temp_score', ascending=False)

        return top_df.drop(columns=['_temp_score'])

    def select_top_n(self, nearby_df, n):
        return nearby_df.head(n).to_dict('records')


class SortBy(Enum):
    DISTANCE = "distance"
    FINAL_SCORE = "final_score"
    HEAT_SCORE = "heat_score"

class Location(BaseModel):
    lat: float
    lon: float

class SearchData(BaseModel):
    location: Location
    sort_by: SortBy
    count_of_results: int
    radius_km: float

def get_result(search_data: SearchData):
    file_name = "web/data/all_locations.geojson"
    locator = GeoLocator(file_name)

    lat = search_data.location.lat
    lon = search_data.location.lon
    sort_by = search_data.sort_by
    count_of_results = search_data.count_of_results
    radius_km = search_data.radius_km

    results = locator.get_nearest_locations(lat, lon, radius_km)

    if sort_by == SortBy.DISTANCE:
        results = locator.sort_by_distance(results)
    elif sort_by == SortBy.FINAL_SCORE:
        results = locator.sort_by_final_score(results)
    elif sort_by == SortBy.HEAT_SCORE:
        results = locator.sort_by_heat_score(results)
    
    results = locator.select_top_n(results, count_of_results)

    return results

# # --- Usage ---
# locator = GeoLocator("web/data/all_locations.geojson")

# # This lookup is now instant, even with millions of rows
# result = locator.find_closest(49.131130, 9.3)
# print(json.dumps(result['properties'], indent=2))

def extract_useful_info(location_info: dict) -> dict:
    props = location_info.get("properties", {})

    # mapping of field -> new name (None = keep same)
    fields = {
        "latitude": None,
        "longitude": None,
        "heat_score": None,
        "spatial_score": None,
        "social_score": None,
        "maintenance_score": None,  # assuming this was a typo in your list
        "final_score": None,
        "rank": None,
        "location_type": None,
        "recommended_species": "recommended_species_to_plant",
        "cooling_estimate": None,
        "schools_nearby": None,
        "residents_nearby": None,
        "distance_from_search_point": None,
    }

    flat = {}

    for old_key, new_key in fields.items():
        if old_key in props:
            flat[new_key or old_key] = props[old_key]

    return flat

if __name__ == "__main__":
    # Dummy settings
    my_lat = 49.13113
    my_lon = 9.22358
    search_radius = 0.5  # 500 meters
    num_results = 10
    sort_by = SortBy.FINAL_SCORE

    search_data = SearchData(location=Location(lat=my_lat, lon=my_lon), sort_by=sort_by, count_of_results=num_results, radius_km=search_radius)

    results = get_result(search_data)

    print(f"Found {len(results)} top locations within {search_radius}km:\n")
    # print(results)
    for result in results:
        # print(result)
        print(extract_useful_info(result))
        print('_________')
    # for i, item in enumerate(results, 1):
    #     props = item['properties']
    #     print(f"{i}. Rank {props.get('rank')} | Score: {props.get('final_score')}")
    #     print(f"   Species: {props.get('recommended_species')}")
    #     print("---")
