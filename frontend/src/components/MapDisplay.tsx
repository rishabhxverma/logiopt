import { Map, AdvancedMarker, useMap } from "@vis.gl/react-google-maps";
import type { Solution } from "@/api";
import { useEffect } from "react";

interface MapDisplayProps {
  solution: Solution | null;
}

// A bright color for the route line
const ROUTE_COLOR = "#007BFF";

/**
 * A helper component to automatically adjust the map's viewport
 * and draw the polyline.
 */
function MapBoundsUpdater({ solution }: MapDisplayProps) {
  const map = useMap();

  useEffect(() => {
    if (!map || !solution || solution.routes[0].stops.length === 0) return;

    // Create a new bounds object
    const bounds = new google.maps.LatLngBounds();

    // Build the path for the polyline
    const path = solution.routes[0].stops.map((stop) => ({
      lat: stop.lat,
      lng: stop.lng,
    }));

    // Extend the bounds to include every stop in the route
    path.forEach((point) => {
      bounds.extend(point);
    });

    // Create the polyline using the Google Maps API
    const polyline = new google.maps.Polyline({
      path: path,
      strokeColor: ROUTE_COLOR,
      strokeOpacity: 0.8,
      strokeWeight: 5,
      map: map,
    });

    // Tell the map to fit those bounds
    map.fitBounds(bounds, 100); // 100px padding

    // Cleanup function to remove the polyline when component unmounts or solution changes
    return () => {
      polyline.setMap(null);
    };
  }, [map, solution]); // Re-run whenever the map or solution changes

  return null;
}

/**
 * Renders the main map display, including markers and the route polyline.
 */
export function MapDisplay({ solution }: MapDisplayProps) {
  // Define a default map center (e.g., center of North America)
  const defaultCenter = { lat: 45.0, lng: -98.0 };
  const defaultZoom = 3;

  // Calculate the path for the markers
  const routePath = solution
    ? solution.routes[0].stops.map((stop) => ({ lat: stop.lat, lng: stop.lng }))
    : [];

  return (
    <div className="w-full h-full min-h-[400px]">
      <Map
        defaultCenter={defaultCenter}
        defaultZoom={defaultZoom}
        gestureHandling={"greedy"}
        disableDefaultUI={true}
        mapId="logiopt-map-id" // A simple ID for styling/customization
      >
        {/* Draw all the markers */}
        {solution &&
          routePath.map((point, index) => (
            <AdvancedMarker key={index} position={point}>
              <div className="bg-blue-600 text-white rounded-full w-8 h-8 flex items-center justify-center font-bold shadow-lg">
                {index + 1}
              </div>
            </AdvancedMarker>
          ))}

        {/* Mount the helper component to update bounds and draw polyline */}
        <MapBoundsUpdater solution={solution} />
      </Map>
    </div>
  );
}
