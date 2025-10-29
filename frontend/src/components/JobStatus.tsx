import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import type { Job } from "@/api";

interface JobStatusProps {
  job: Job;
  onRunOptimization: () => void; // Callback to parent
  isLoading: boolean;
}

export function JobStatus({ job, onRunOptimization, isLoading }: JobStatusProps) {
  return (
    <Card className="w-full max-w-md mt-6">
      <CardHeader>
        <CardTitle>Job #{job.id} Status: <span className="text-blue-600 uppercase">{job.status}</span></CardTitle>
        <CardDescription>
          {job.shipments.length === 0 
            ? "No shipments added yet." 
            : `${job.shipments.length} shipment(s) added.`
          }
        </CardDescription>
      </CardHeader>
      
      {/* Only show the table if there are shipments */}
      {job.shipments.length > 0 && (
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Origin</TableHead>
                <TableHead>Destination</TableHead>
                <TableHead className="text-right">Weight</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {job.shipments.map((shipment) => (
                <TableRow key={shipment.id}>
                  <TableCell>{shipment.origin}</TableCell>
                  <TableCell>{shipment.destination}</TableCell>
                  <TableCell className="text-right">{shipment.weight} kg</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          
          <Button 
            onClick={onRunOptimization} 
            disabled={isLoading} 
            className="w-full mt-6"
          >
            {isLoading ? "Optimizing..." : "Run Optimization"}
          </Button>
        </CardContent>
      )}
    </Card>
  );
}