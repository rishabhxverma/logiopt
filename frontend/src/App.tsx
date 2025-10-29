import React, { useState } from "react";
// Import our new API function
import { createJob } from "./api";

// Remove all the default CSS and logo imports
// import './App.css';

function App() {
  // Create state variables to hold the job ID or any error
  const [jobId, setJobId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  // This function will be called when the button is clicked
  const handleCreateJob = async () => {
    try {
      // Clear any old errors
      setError(null);
      setJobId(null);

      // Call our API!
      console.log("Creating new job...");
      const response = await createJob();

      // On success, 'response.data' will be our new Job object
      console.log("Success!", response.data);
      setJobId(response.data.id);
    } catch (err: any) {
      // On failure, log the error and show it to the user
      console.error("Failed to create job:", err);
      setError(err.message || "An unknown error occurred.");
    }
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h1>LogiOpt Dashboard</h1>

      {/* Our main action button */}
      <button onClick={handleCreateJob}>Create New Job</button>

      {/* Show the job ID on success */}
      {jobId && (
        <div style={{ marginTop: "1rem" }}>
          <h3>New Job Created!</h3>
          <p>Job ID: {jobId}</p>
        </div>
      )}

      {/* Show an error message on failure */}
      {error && (
        <div style={{ marginTop: "1rem", color: "red" }}>
          <h3>Error:</h3>
          <p>{error}</p>
        </div>
      )}
    </div>
  );
}

export default App;
