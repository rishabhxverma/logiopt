from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from . import schemas

# NEW: Import our Google Maps client
from . import maps_client

def create_data_model(job):
    """
    Prepares the data for the VRP solver.
    This version now calls the Google Maps API for a REAL distance matrix.
    """
    
    # --- 1. Build Location List ---
    
    # The 'depot' is our fixed warehouse.
    # In a real app, this would come from the user or database.
    DEPOT_LOCATION = "450 W 33rd St, New York, NY 10001" # Example: An office in NYC
    
    locations = [DEPOT_LOCATION]
    pickups_deliveries = []
    
    for shipment in job.shipments:
        locations.append(shipment.origin)
        pickup_index = len(locations) - 1
        
        locations.append(shipment.destination)
        drop_index = len(locations) - 1
        
        pickups_deliveries.append([pickup_index, drop_index])

    
    # --- 2. Build REAL Distance Matrix ---

    
    print(f"Fetching distance matrix for {len(locations)} locations...")
    matrix = maps_client.get_distance_matrix(locations)
    
    if matrix is None:
        print("Error: Failed to get distance matrix from Google Maps.")
        return None # Abort optimization if we have no data

    print("Successfully fetched matrix.")

    # --- 3. Package data for the solver ---
    data = {}
    data['distance_matrix'] = matrix
    data['pickups_deliveries'] = pickups_deliveries
    data['num_vehicles'] = 1 # We are only solving for one truck
    data['depot'] = 0 # The depot is the first item (index 0)
    
    # Store maps for parsing the solution later
    data['locations_map'] = locations
    data['shipment_map'] = job.shipments
    
    return data


def solve_vrp(job):
    """
    Solves the Vehicle Routing Problem for a given job.
    (This function remains unchanged, as it just operates on 'data')
    """
    
    # 1. Prepare the data
    data = create_data_model(job)
    
    # Handle failure from create_data_model
    if data is None:
        return None

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
        print("Optimization failed: No solution found.")
        return None

def parse_solution(data, manager, routing, solution, job):
    """
    Converts the solver's output into our Pydantic schemas.
    (This function remains unchanged)
    """
    locations_map = data['locations_map']
    
    shipment_lookup = {}
    shipment_id_counter = 0
    for i, loc in enumerate(locations_map):
        if i == 0: continue # Skip depot
        
        shipment_id = job.shipments[shipment_id_counter].id
        
        if (i % 2) == 1: # Odd index = origin
            shipment_lookup[i] = (shipment_id, loc, "PICKUP")
        else: # Even index = destination
            shipment_lookup[i] = (shipment_id, loc, "DROP")
            shipment_id_counter += 1
    
    route_obj = schemas.SolutionRoute()
    index = routing.Start(0)
    
    while not routing.IsEnd(index):
        node_index = manager.IndexToNode(index)
        
        if node_index != 0: # Don't add the depot (index 0)
            ship_id, loc_name, stop_type = shipment_lookup[node_index]
            route_obj.stops.append(schemas.SolutionStop(
                id=ship_id,
                location=loc_name,
                type=stop_type
            ))
        
        index = solution.Value(routing.NextVar(index))
    
    return schemas.Solution(routes=[route_obj])