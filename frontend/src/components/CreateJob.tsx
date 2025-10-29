import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import * as api from "@/api";

// Define a type for the component's props
interface CreateJobProps {
  onJobCreated: (jobId: number) => void;
}

export function CreateJob({ onJobCreated }: CreateJobProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCreateJob = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await api.createJob();
      console.log("Job created:", response.data);
      onJobCreated(response.data.id); // Pass the new ID to the parent
    } catch (err) {
      console.error("Failed to create job", err);
      setError("Failed to create job. Please try again.");
    }
    setIsLoading(false);
  };

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle>New Optimization Job</CardTitle>
        <CardDescription>
          Start by creating a new job. You can add shipments in the next step.
        </CardDescription>
      </CardHeader>
      <CardFooter>
        <Button onClick={handleCreateJob} disabled={isLoading}>
          {isLoading ? "Creating..." : "Create New Job"}
        </Button>
      </CardFooter>
      {error && <p className="text-red-500 text-sm p-4 pt-0">{error}</p>}
    </Card>
  );
}
