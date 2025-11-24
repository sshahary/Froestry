import pandas as pd
import requests
import os
import time

# --- CONFIGURATION ---
API_KEY = "AIzaSyBzjy1Dq3CBBo0v-U2M42MTqb2VA2ezwA0"
CSV_FILE = "data/outputs/nearest_fresh_locations.csv"
OUTPUT_DIR = "marked_satellite_images"

# Image settings
ZOOM_LEVEL = 18          # 15-19 is usually best for building views
IMAGE_SIZE = "600x600"   # Max size for standard API
MAP_TYPE = "satellite"   # 'satellite' or 'hybrid' (satellite + labels)

# Marker settings (Google API styling)
# You can change color to blue, green, yellow, etc.
MARKER_STYLE = "color:red|size:mid"
# ---------------------


# 1. Setup Output Directory
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# 2. Define Download Function
def download_image_with_marker(lat, lon, index, location_number):
    base_url = "https://maps.googleapis.com/maps/api/staticmap"
    
    # Combine lat/lon into string format for the API
    coord_string = f"{lat},{lon}"

    params = {
        'center': coord_string,
        'zoom': ZOOM_LEVEL,
        'size': IMAGE_SIZE,
        'maptype': MAP_TYPE,
        'key': API_KEY,
        # HERE IS THE MAGIC LINE:
        # It tells Google to place a marker with the specific style at the coordinate
        'markers': f"{MARKER_STYLE}|{coord_string}"
    }

    try:
        print(f"Downloading location {location_number}...")
        response = requests.get(base_url, params=params)
        response.raise_for_status()

        # Using the 'Number' column from CSV for the filename for easy matching
        filename = f"{OUTPUT_DIR}/location_{location_number}_lat{lat:.4f}.png"
        
        with open(filename, "wb") as file:
            file.write(response.content)
            
        print(f"[SUCCESS] Saved: {filename}")
        # Be polite to the API rate limits
        time.sleep(0.2) 

    except requests.exceptions.HTTPError as err:
        print(f"[ERROR] HTTP error for loc {location_number}: {err}")
    except Exception as e:
        print(f"[ERROR] Error for loc {location_number}: {e}")


# 3. Main Execution Flow
try:
    # --- A. Load and Parse CSV ---
    print(f"Reading {CSV_FILE}...")
    # Read the CSV
    df = pd.read_csv(CSV_FILE)

    # Ensure necessary columns exist before proceeding
    if not all(col in df.columns for col in ['Latitude', 'Longitude', 'Number']):
         raise ValueError("CSV is missing required columns: Latitude, Longitude, or Number")

    total_locs = len(df)
    print(f"Found {total_locs} locations to process.")

    # --- B. Iterate and Download ---
    # iterrows gives us the index and the row data
    for index, row in df.iterrows():
        if index >= 1: # temp cut
            break
        lat = row['Latitude']
        lon = row['Longitude']
        # Using the 'Number' column from your CSV as an identifier
        loc_num = row['Number'] 

        # Validate coordinate data types before request
        if pd.notnull(lat) and pd.notnull(lon):
             download_image_with_marker(lat, lon, index, loc_num)
        else:
             print(f"[SKIPPING] Row {index} has missing coordinates.")

    print("\nBatch download complete.")

except FileNotFoundError:
    print(f"[ERROR] Could not find {CSV_FILE}. Check file path.")
except ValueError as ve:
    print(f"[ERROR] Data issue: {ve}")
except Exception as e:
    print(f"[CRITICAL ERROR] {e}")
