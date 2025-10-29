"""
Optimization module for solving Vehicle Routing Problems (VRP).
This module uses Google OR-Tools to compute optimal routes for shipments
associated with a logistics optimization job.
"""

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from . import schemas

def create_data_model(job):
    """
    Prepares the data for the VRP solver.
    
    The solver needs:
    1. A list of all locations (our 'depot' + all shipment origins/destinations).
    2. A distance matrix: a grid of travel times between ALL points.
    3. A list of pickups/deliveries: which location is a 'pickup'
       and which is its corresponding 'drop'.
    """
    
    # --- 1. Build Location List & Pickups/Deliveries ---
    
    # For now, we assume a single 'depot' at a fixed location
    locations = ["Depot"]
    pickups_deliveries = []
    
    for shipment in job.shipments:
        # Add the origin (pickup)
        locations.append(shipment.origin)
        pickup_index = len(locations) - 1
        
        # Add the destination (drop)
        locations.append(shipment.destination)
        drop_index = len(locations) - 1
        
        # Link them
        pickups_deliveries.append([pickup_index, drop_index])

    
    # --- 2. Build Distance Matrix ---
    #TODO: Replace this dummy distance matrix with real distances
    # from a mapping API (e.g., Google Maps, OpenRouteService, etc.)
    # !! DUMMY DATA !!
    # This is the most important part to replace in Phase 5.
    # We are faking the distances. This matrix MUST be
    # len(locations) x len(locations).
    
    # For N locations, create an NxN matrix of all 0s
    size = len(locations)
    matrix = [[0] * size for _ in range(size)]
    
    # Fake some simple distances
    for i in range(size):
        for j in range(size):
            if i != j:
                matrix[i][j] = abs(i - j) * 10 # Arbitrary simple cost

    data = {}
    data['distance_matrix'] = matrix
    data['pickups_deliveries'] = pickups_deliveries
    data['num_vehicles'] = 1 # We are only solving for one truck
    data['depot'] = 0 # The depot is the first item in our 'locations' list
    
    # Store this for later
    data['locations_map'] = locations
    data['shipment_map'] = job.shipments
    
    return data


def solve_vrp(job):
    """
    Solves the Vehicle Routing Problem for a given job.
    """
    
    # 1. Prepare the data
    data = create_data_model(job)

    # 2. Setup the VRP problem
    manager = pywrapcp.RoutingIndexManager(
        len(data['distance_matrix']),
        data['num_vehicles'],
        data['depot']
    )
    routing = pywrapcp.RoutingModel(manager)

    # 3. Create the "cost" callback (how long is each segment?)
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    
    # 4. Add "Pickup & Delivery" constraints
    for request in data['pickups_deliveries']:
        pickup_index = manager.NodeToVecIndex(request[0])
        delivery_index = manager.NodeToVecIndex(request[1])
        routing.AddPickupAndDelivery(pickup_index, delivery_index)
        routing.solver().Add(
            routing.VehicleVar(pickup_index) == routing.VehicleVar(delivery_index)
        )

    # 5. Set search parameters and solve
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    solution = routing.SolveWithParameters(search_parameters)

    # 6. If a solution is found, parse it into our schema
    if solution:
        return parse_solution(data, manager, routing, solution, job)
    else:
        return None

def parse_solution(data, manager, routing, solution, job):
    """
    Converts the solver's output into our Pydantic schemas.
    """
    # Maps are for reconstructing the route
    locations_map = data['locations_map']
    
    # Map location-list-index to a shipment ID
    # e.g., locations_map[3] ('New York') belongs to shipment_id=1
    shipment_lookup = {}
    shipment_id_counter = 0
    for i, loc in enumerate(locations_map):
        if i == 0: # Skip depot
            continue
        
        # Every 2 locations (origin, dest) belong to one shipment
        shipment_id = job.shipments[shipment_id_counter].id
        
        if (i % 2) == 1: # Odd index = origin
            shipment_lookup[i] = (shipment_id, loc, "PICKUP")
        else: # Even index = destination
            shipment_lookup[i] = (shipment_id, loc, "DROP")
            shipment_id_counter += 1 # Move to next shipment

    
    route_obj = schemas.SolutionRoute()
    
    # We only have one vehicle (index 0)
    index = routing.Start(0)
    
    while not routing.IsEnd(index):
        node_index = manager.IndexToNode(index)
        
        if node_index != 0: # Don't add the depot to the stop list
            ship_id, loc_name, stop_type = shipment_lookup[node_index]
            route_obj.stops.append(schemas.SolutionStop(
                id=ship_id,
                location=loc_name,
                type=stop_type
            ))
        
        index = solution.Value(routing.NextVar(index))
    
    return schemas.Solution(routes=[route_obj])