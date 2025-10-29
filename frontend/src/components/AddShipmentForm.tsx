import { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import * as api from '@/api';

interface AddShipmentFormProps {
  jobId: number;
}

export function AddShipmentForm({ jobId }: AddShipmentFormProps) {
  const [origin, setOrigin] = useState("");
  const [destination, setDestination] = useState("");
  const [weight, setWeight] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    const shipmentData: api.ShipmentCreate = { origin, destination, weight: +weight };

    try {
      await api.createShipment(jobId, shipmentData);
      // Clear the form on success
      setOrigin("");
      setDestination("");
      setWeight(0);
    } catch (err) {
      console.error("Failed to add shipment", err);
      setError("Failed to add shipment. Please try again.");
    }
    setIsLoading(false);
  };

  return (
    <Card className="w-full max-w-md mt-6">
      <CardHeader>
        <CardTitle>Add Shipments to Job #{jobId}</CardTitle>
        <CardDescription>Add at least one shipment to optimize.</CardDescription>
      </CardHeader>
      <form onSubmit={handleSubmit}>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="origin">Origin</Label>
            <Input
              id="origin"
              placeholder="e.g., 1600 Amphitheatre Parkway, Mountain View, CA"
              value={origin}
              onChange={(e) => setOrigin(e.target.value)}
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="destination">Destination</Label>
            <Input
              id="destination"
              placeholder="e.g., 1 Letterman Dr, San Francisco, CA"
              value={destination}
              onChange={(e) => setDestination(e.target.value)}
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="weight">Weight (kg)</Label>
            <Input
              id="weight"
              type="number"
              value={weight}
              onChange={(e) => setWeight(Number(e.target.value))}
              required
            />
          </div>
        </CardContent>
        <CardFooter>
          <Button type="submit" disabled={isLoading}>
            {isLoading ? "Adding..." : "Add Shipment"}
          </Button>
        </CardFooter>
      </form>
      {error && <p className="text-red-500 text-sm p-4 pt-0">{error}</p>}
    </Card>
  );
}