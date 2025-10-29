import axios from "axios";

// The base URL for our FastAPI backend
const API_BASE_URL = "http://localhost:8000";

/**
 * Creates an Axios client instance pre-configured with the backend URL
 * and default headers. This instance can be used for all API requests.
 */
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

//==============================================================================
// API Types
// (These should mirror the Pydantic schemas in backend/schemas.py)
//==============================================================================

/**
 * Represents a single Shipment object as returned by the API.
 */
export interface Shipment {
  id: number;
  job_id: number;
  origin: string;
  destination: string;
  weight: number;
}

/**
 * Represents a single Job object as returned by the API.
 */
export interface Job {
  id: number;
  status: string;
  created_at: string;
  updated_at: string | null;
  shipments: Shipment[];
}

/**
 * Represents the input for creating a new Shipment.
 */
export interface ShipmentCreate {
  origin: string;
  destination: string;
  weight: number;
}

//==============================================================================
// API Functions
//==============================================================================

/**
 * Fetches a list of all jobs.
 * @returns A promise that resolves to an array of Job objects.
 */
export const getJobs = () => {
  return apiClient.get<Job[]>("/jobs/");
};

/**
 * Fetches a single job by its ID.
 * @param jobId The ID of the job to fetch.
 * @returns A promise that resolves to a single Job object.
 */
export const getJobById = (jobId: number) => {
  return apiClient.get<Job>(`/jobs/${jobId}`);
};

/**
 * Creates a new, empty job.
 * @returns A promise that resolves to the newly created Job object.
 */
export const createJob = () => {
  // A new job is created with a default 'pending' status on the backend.
  return apiClient.post<Job>("/jobs/", { status: "pending" });
};

/**
 * Creates a new shipment for a specific job.
 * @param jobId The ID of the parent job.
 * @param shipment The shipment data to create.
 * @returns A promise that resolves to the newly created Shipment object.
 */
export const createShipment = (jobId: number, shipment: ShipmentCreate) => {
  return apiClient.post<Shipment>(`/jobs/${jobId}/shipments/`, shipment);
};

/**
 * Represents a single stop in an optimized route.
 */
export interface SolutionStop {
  id: number;
  location: string;
  type: "PICKUP" | "DROP";

  // --- ADD THESE TWO LINES ---
  lat: number;
  lng: number;
  // --- END OF ADDITION ---
}

/**
 * Represents a single vehicle's route.
 */
export interface SolutionRoute {
  stops: SolutionStop[];
}

/**
 * The complete solution object returned from the /solve endpoint.
 */
export interface Solution {
  routes: SolutionRoute[];
}

/**
 * Triggers the optimization solver for a given job.
 * @param jobId The ID of the job to solve.
 * @returns A promise that resolves to the Solution object.
 */
export const solveJob = (jobId: number) => {
  return apiClient.post<Solution>(`/jobs/${jobId}/solve`);
};
