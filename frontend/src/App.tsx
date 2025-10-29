import { useState } from "react";
import { CreateJob } from "./components/CreateJob";
import { AddShipmentForm } from "./components/AddShipmentForm";

function App() {
  // This state will hold the ID of the job we are working on
  const [currentJobId, setCurrentJobId] = useState<number | null>(null);

  return (
    <div className="flex flex-col items-center min-h-screen p-8 bg-gray-50">
      <h1 className="text-3xl font-bold mb-8">LogiOpt Dashboard</h1>

      {/* This is a conditional render.
        If we DON'T have a job ID, show the 'CreateJob' component.
        If we DO have a job ID, show the 'AddShipmentForm' component.
      */}

      {!currentJobId ? (
        <CreateJob onJobCreated={setCurrentJobId} />
      ) : (
        <AddShipmentForm jobId={currentJobId} />
      )}
    </div>
  );
}

export default App;
