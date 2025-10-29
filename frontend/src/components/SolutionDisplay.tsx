import type { Solution } from "@/api";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

interface SolutionDisplayProps {
  solution: Solution;
}

export function SolutionDisplay({ solution }: SolutionDisplayProps) {
  // We only expect one route for our simple VRP
  const route = solution.routes[0];

  return (
    <Card className="w-full max-w-md mt-6 bg-green-50 border-green-200">
      <CardHeader>
        <CardTitle className="text-green-800">Optimization Complete!</CardTitle>
        <CardDescription>
          Here is the most efficient route for your vehicle.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col space-y-2">
          <div className="font-semibold text-gray-700">Depot (Start)</div>
          <ol className="list-decimal list-inside pl-2 space-y-2">
            {route.stops.map((stop, index) => (
              <li key={index} className="text-gray-900">
                <span
                  className={`font-medium ${
                    stop.type === "PICKUP" ? "text-blue-600" : "text-purple-600"
                  }`}
                >
                  {stop.type}
                </span>
                : {stop.location} (Shipment #{stop.id})
              </li>
            ))}
          </ol>
          <div className="font-semibold text-gray-700 mt-2">Depot (End)</div>
        </div>
      </CardContent>
    </Card>
  );
}
