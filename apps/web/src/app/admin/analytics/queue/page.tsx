import { getQueueAnalytics } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";

function statusVariant(status: string) {
  if (status === "completed") return "default";
  if (status === "failed") return "destructive";
  if (status === "processing") return "secondary";
  return "outline";
}

export default async function QueuePage() {
  const queue = await getQueueAnalytics();

  return (
    <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <div className="mb-8">
        <p className="text-sm uppercase tracking-[0.24em] text-muted-foreground">Queue Monitoring</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">
          Prediction queue health and backlog
        </h1>
        <p className="mt-3 text-base leading-7 text-muted-foreground max-w-2xl">
          Live queue analytics from the backend reflecting pending, processing, and failed jobs.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="border border-border p-6">
          <CardTitle>Total jobs</CardTitle>
          <CardDescription>Total jobs created in the prediction queue.</CardDescription>
          <div className="mt-6 text-4xl font-semibold">{queue.total_jobs}</div>
        </Card>
        <Card className="border border-border p-6">
          <CardTitle>Success rate</CardTitle>
          <CardDescription>Completed job percentage.</CardDescription>
          <div className="mt-6 text-4xl font-semibold">{queue.success_rate.toFixed(1)}%</div>
        </Card>
        <Card className="border border-border p-6">
          <CardTitle>Failure rate</CardTitle>
          <CardDescription>Failed job percentage.</CardDescription>
          <div className="mt-6 text-4xl font-semibold">{queue.failure_rate.toFixed(1)}%</div>
        </Card>
      </div>

      <Card className="mt-8 border border-border">
        <CardHeader className="px-6 py-5">
          <CardTitle>Queue distribution</CardTitle>
          <CardDescription>Current breakdown of queue statuses.</CardDescription>
        </CardHeader>
        <CardContent className="px-6 pb-6 pt-0 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[
            { label: "Pending", value: queue.pending },
            { label: "Processing", value: queue.processing },
            { label: "Retrying", value: queue.retrying },
            { label: "Completed", value: queue.completed },
            { label: "Failed", value: queue.failed },
          ].map((item) => (
            <div key={item.label} className="rounded-3xl border border-border p-5">
              <p className="text-sm text-muted-foreground">{item.label}</p>
              <p className="mt-2 text-3xl font-semibold">{item.value}</p>
            </div>
          ))}
        </CardContent>
      </Card>

      <Card className="mt-8 border border-border">
        <CardHeader className="px-6 py-5">
          <CardTitle>Recent jobs</CardTitle>
          <CardDescription>Latest queue jobs from the backend.</CardDescription>
        </CardHeader>
        <CardContent className="px-6 pb-6 pt-0 space-y-4">
          {queue.recent_jobs.length === 0 ? (
            <p className="text-sm text-muted-foreground">No recent jobs available.</p>
          ) : (
            queue.recent_jobs.map((job) => (
              <div key={job.job_id} className="rounded-3xl border border-border p-4">
                <div className="flex flex-wrap items-center justify-between gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Job ID</p>
                    <p className="font-semibold">{job.job_id}</p>
                  </div>
                  <Badge variant={statusVariant(job.status) as "default" | "secondary" | "destructive" | "outline"}>
                    {job.status}
                  </Badge>
                </div>
                <div className="mt-3 grid gap-3 sm:grid-cols-3">
                  <div>
                    <p className="text-xs uppercase text-muted-foreground">Student profile</p>
                    <p className="mt-1 text-sm font-semibold">{job.student_profile_id}</p>
                  </div>
                  <div>
                    <p className="text-xs uppercase text-muted-foreground">Attempts</p>
                    <p className="mt-1 text-sm font-semibold">{job.attempts}/{job.max_attempts}</p>
                  </div>
                  <div>
                    <p className="text-xs uppercase text-muted-foreground">Queued at</p>
                    <p className="mt-1 text-sm font-semibold">{job.queued_at ?? "—"}</p>
                  </div>
                </div>
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  );
}
