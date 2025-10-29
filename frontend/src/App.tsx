import { useState } from "react";
import { CreateJob } from "./components/CreateJob";
import { AddShipmentForm } from "./components/AddShipmentForm";
import { JobStatus } from "./components/JobStatus";
import { SolutionDisplay } from "./components/SolutionDisplay";
import { MapDisplay } from "./components/MapDisplay";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Loader2 } from "lucide-react";
import { APIProvider } from "@vis.gl/react-google-maps";
import * as api from "./api";

// 1. Get the Google Maps API key from our .env.local file
const GOOGLE_MAPS_API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;

function App() {
  const [currentJob, setCurrentJob] = useState<api.Job | null>(null);
  const [solution, setSolution] = useState<api.Solution | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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

  const handleJobCreated = (jobId: number) => {
    fetchJob(jobId);
  };

  const handleShipmentAdded = () => {
    if (currentJob) {
      fetchJob(currentJob.id);
    }
  };

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

  // A new function to reset the app state
  const handleStartNewJob = () => {
    setCurrentJob(null);
    setSolution(null);
    setError(null);
  };

  /**
   * Renders the main panel (left side)
   */
  const renderPanel = () => {
    // 1. Loading state (before job is created)
    if (isLoading && !currentJob) {
      return (
        <div className="flex justify-center items-center h-full">
          <Loader2 className="animate-spin" size={48} />
        </div>
      );
    }

    // 2. Initial state: No job created yet
    if (!currentJob) {
      return (
        <div className="p-8">
          <CreateJob onJobCreated={handleJobCreated} />
        </div>
      );
    }

    // 3. Main state: Job is active, show inputs and status
    return (
      <ScrollArea className="h-full">
        <div className="p-6 space-y-6">
          <AddShipmentForm
            jobId={currentJob.id}
            onShipmentAdded={handleShipmentAdded}
          />
          <JobStatus
            job={currentJob}
            onRunOptimization={handleRunOptimization}
            isLoading={isLoading}
          />
          {solution && (
            <>
              <SolutionDisplay solution={solution} />
              <Button
                onClick={handleStartNewJob}
                variant="outline"
                className="w-full"
              >
                Start New Job
              </Button>
            </>
          )}
        </div>
      </ScrollArea>
    );
  };

  // 2. Check if the key exists before rendering
  if (!GOOGLE_MAPS_API_KEY) {
    return (
      <div className="flex justify-center items-center h-screen">
        <Alert variant="destructive" className="w-96">
          <AlertTitle>Configuration Error</AlertTitle>
          <AlertDescription>
            <p>VITE_GOOGLE_MAPS_API_KEY is not set.</p>
            <p className="mt-2">
              Please create a <strong>.env.local</strong> file in the /frontend
              folder and add your key.
            </p>
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  // 3. Wrap the ENTIRE app in APIProvider
  return (
    <APIProvider apiKey={GOOGLE_MAPS_API_KEY}>
      <div className="w-screen h-screen flex flex-col">
        <header className="p-4 border-b bg-white shadow-sm z-10">
          <h1 className="text-2xl font-bold">LogiOpt Dashboard</h1>
        </header>

        {error && (
          <Alert
            variant="destructive"
            className="m-4 z-10 max-w-lg self-center"
          >
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* 4. This is the new two-column layout */}
        <ResizablePanelGroup direction="horizontal" className="flex-grow">
          <ResizablePanel defaultSize={35} minSize={25} className="bg-white">
            {/* --- Left Panel (Controls) --- */}
            {renderPanel()}
          </ResizablePanel>
          <ResizableHandle withHandle />
          <ResizablePanel defaultSize={65} minSize={30}>
            {/* --- Right Panel (Map) --- */}
            <MapDisplay solution={solution} />
          </ResizablePanel>
        </ResizablePanelGroup>
      </div>
    </APIProvider>
  );
}

export default App;
