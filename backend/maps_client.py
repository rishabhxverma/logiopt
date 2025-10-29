import os
from dotenv import load_dotenv
from datetime import datetime

import googlemaps

# 2. Import the MODERN routes client and its types
from google.maps.routing_v2 import RoutesClient, ComputeRouteMatrixRequest
from google.maps.routing_v2.types import (
    RouteMatrixOrigin, RouteMatrixDestination, Waypoint, 
    RouteTravelMode, RoutingPreference
)
import googlemaps

# Load .env file
load_dotenv()
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY") 

# 3. Initialize BOTH clients
routes_client = RoutesClient(client_options={"api_key": API_KEY})
# The legacy client takes the key directly
geocoding_client = googlemaps.Client(key=API_KEY) 


def get_distance_matrix(locations: list[str]):
    """
    Fetches a real-world duration matrix from the Google "Routes API".
    (This function is unchanged and works)
    """
    
    matrix_origins = [
        RouteMatrixOrigin(waypoint=Waypoint(address=loc))
        for loc in locations
    ]
    
    matrix_destinations = [
        RouteMatrixDestination(waypoint=Waypoint(address=loc))
        for loc in locations
    ]

    try:
        request = ComputeRouteMatrixRequest(
            origins=matrix_origins,
            destinations=matrix_destinations,
            travel_mode=RouteTravelMode.DRIVE,
            routing_preference=RoutingPreference.TRAFFIC_AWARE,
        )
        metadata = [
            ('x-goog-fieldmask', 'status,duration,origin_index,destination_index')
        ]
        
        response_stream = routes_client.compute_route_matrix(
            request, 
            metadata=metadata
        )

        num_locations = len(locations)
        duration_matrix = [[0] * num_locations for _ in range(num_locations)]

        for element in response_stream:
            if element.status.code == 0: # 0 = 'OK'
                duration = element.duration.seconds
                if duration:
                    duration_matrix[element.origin_index][element.destination_index] = duration
            else:
                duration_matrix[element.origin_index][element.destination_index] = 99999999 

        return duration_matrix

    except Exception as e:
        print(f"Error calling Google Routes API: {e}")
        return None

# --- NEW FUNCTION (Rewritten to use the legacy client) ---
def geocode_locations(locations: list[str]):
    """
    Geocodes a list of location strings (addresses) using the
    legacy (but still supported) Geocoding API.
    
    Returns:
        A dictionary mapping the location string to its {lat, lng}.
    """
    geocoded_data = {}
    for location_str in locations:
        try:
            # Use the legacy client's geocode method
            response = geocoding_client.geocode(location_str)
            
            if response:
                # The response structure is a list
                geo_loc = response[0]['geometry']['location']
                geocoded_data[location_str] = {"lat": geo_loc['lat'], "lng": geo_loc['lng']}
            else:
                print(f"Geocoding failed for: {location_str}")
                geocoded_data[location_str] = None
        
        except Exception as e:
            print(f"Error calling Geocoding API for {location_str}: {e}")
            geocoded_data[location_str] = None
            
    return geocoded_data
# --- END OF REWRITE ---