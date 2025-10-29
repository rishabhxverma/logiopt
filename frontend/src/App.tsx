import { useState, useEffect } from "react";
import { CreateJob } from "./components/CreateJob";
import { AddShipmentForm } from "./components/AddShipmentForm";
import { JobStatus } from "./components/JobStatus";
import { SolutionDisplay } from "./components/SolutionDisplay";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Loader2 } from "lucide-react";
import * as api from "./api";

function App() {
  // State for the entire application
  const [currentJob, setCurrentJob] = useState<api.Job | null>(null);
  const [solution, setSolution] = useState<api.Solution | null>(null);
  const [isLoading, setIsLoading] = useState(false); // For loading job or solution
  const [error, setError] = useState<string | null>(null);

  /**
   * Fetches the full job object from the API and updates state.
   */
  const fetchJob = async (jobId: number) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await api.getJobById(jobId);
      setCurrentJob(response.data);
    } catch (err) {
      console.error("Failed to fetch job", err);
      setError("Failed to fetch job details.");
    }
    setIsLoading(false);
  };

  /**
   * Callback for when the 'CreateJob' component succeeds.
   */
  const handleJobCreated = (jobId: number) => {
    fetchJob(jobId); // Fetch the new job to get it into state
  };

  /**
   * Callback for when 'AddShipmentForm' adds a new shipment.
   */
  const handleShipmentAdded = () => {
    if (currentJob) {
      fetchJob(currentJob.id); // Re-fetch the job to get the new shipment list
    }
  };

  /**
   * Callback for when 'JobStatus' clicks "Run Optimization".
   */
  const handleRunOptimization = async () => {
    if (!currentJob) return;

    setIsLoading(true);
    setError(null);
    setSolution(null);
    try {
      const response = await api.solveJob(currentJob.id);
      setSolution(response.data); // Set the final solution
      fetchJob(currentJob.id); // Re-fetch the job to show "completed" status
    } catch (err) {
      console.error("Failed to solve job", err);
      setError("Failed to solve job. Check API logs.");
    }
    setIsLoading(false);
  };

  /**
   * Renders the main content based on the current application state.
   */
  const renderContent = () => {
    // 1. If we have a solution, show it
    if (solution) {
      return <SolutionDisplay solution={solution} />;
    }

    // 2. If we are actively working on a job, show the job UI
    if (currentJob) {
      return (
        <>
          {/* We pass the 'job' object down to both components */}
          <AddShipmentForm
            {...({
              jobId: currentJob.id,
              onShipmentAdded: handleShipmentAdded,
            } as any)}
          />
          <JobStatus
            job={currentJob}
            onRunOptimization={handleRunOptimization}
            isLoading={isLoading} // Pass loading state to disable button
          />
        </>
      );
    }

    // 3. If we are in a loading state (e.g., fetching job)
    if (isLoading) {
      return <Loader2 className="animate-spin" size={48} />;
    }

    // 4. If we have no job, show the create button
    return <CreateJob onJobCreated={handleJobCreated} />;
  };

  return (
    <div className="flex flex-col items-center min-h-screen p-8 bg-gray-50">
      <h1 className="text-3xl font-bold mb-8">LogiOpt Dashboard</h1>

      {/* Render any top-level errors */}
      {error && (
        <Alert variant="destructive" className="w-full max-w-md mb-6">
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Render the main content based on state */}
      {renderContent()}
    </div>
  );
}

export default App;
