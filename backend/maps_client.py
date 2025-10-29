import os
import googlemaps
from dotenv import load_dotenv
from datetime import datetime

# Load .env file to get the API key
load_dotenv()
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# Initialize the client with our API key
gmaps = googlemaps.Client(key=API_KEY)

def get_distance_matrix(locations: list[str]):
    """
    Fetches a real-world distance and duration matrix from Google Maps.
    
    Args:
        locations: A list of location strings (e.g., addresses or city names).
        
    Returns:
        A 2D list (matrix) of travel *durations* in seconds.
    """
    
    try:
        # Get the matrix from Google, departing "now"
        matrix_result = gmaps.distance_matrix(
            origins=locations,
            destinations=locations,
            mode="driving",
            departure_time=datetime.now()
        )
    except Exception as e:
        print(f"Error calling Google Maps API: {e}")
        return None

    # Parse the complex response from Google into a simple 2D list
    num_locations = len(locations)
    duration_matrix = [[0] * num_locations for _ in range(num_locations)]

    for i in range(num_locations):
        for j in range(num_locations):
            if i == j:
                continue # Travel time from a place to itself is 0
            
            element = matrix_result["rows"][i]["elements"][j]
            
            if element["status"] == "OK":
                # We use 'duration_in_traffic' for the most realistic data
                # Fallback to 'duration' if not available
                duration = element.get("duration_in_traffic", element.get("duration"))
                if duration:
                    duration_matrix[i][j] = duration["value"] # Duration in seconds
                else:
                    # Handle cases where a route might not be found
                    duration_matrix[i][j] = 99999999 # A very large number
            else:
                # Handle cases where a route might not be found
                duration_matrix[i][j] = 99999999 # A very large number

    return duration_matrix