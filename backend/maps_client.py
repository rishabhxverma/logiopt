import os
from dotenv import load_dotenv
from datetime import datetime

# Import the modern Routes API client and request types
from google.maps.routing_v2 import RoutesClient, ComputeRouteMatrixRequest
from google.maps.routing_v2.types import RouteMatrixOrigin, RouteMatrixDestination, Waypoint, Location, RouteTravelMode, RoutingPreference

# Load .env file to get the API key
load_dotenv()
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY") 

# Initialize the client
gmaps_client = RoutesClient(client_options={"api_key": API_KEY})


def get_distance_matrix(locations: list[str]):
    """
    Fetches a real-world duration matrix from the Google "Routes API".
    """

    matrix_origins = [
        RouteMatrixOrigin(waypoint=Waypoint(address=loc))
        for loc in locations
    ]

    matrix_destinations = [
        RouteMatrixDestination(waypoint=Waypoint(address=loc))
        for loc in locations
    ]

    # 2. Build the request
    try:
        request = ComputeRouteMatrixRequest(
            origins=matrix_origins,
            destinations=matrix_destinations,
            travel_mode=RouteTravelMode.DRIVE,
            routing_preference=RoutingPreference.TRAFFIC_AWARE,
        )

        # --- THIS IS THE FIX ---
        # The gRPC metadata key must be all lowercase.
        metadata = [
            ('x-goog-fieldmask', 'status,duration,origin_index,destination_index')
        ]

        # 3. Call the API, passing the metadata as a header
        response_stream = gmaps_client.compute_route_matrix(
            request, 
            metadata=metadata
        )

        # 4. Parse the stream into our 2D list
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