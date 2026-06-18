import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { getPredictionHistory, generateSnapshot, generatePrediction, queuePrediction, createPredictionReview } from "@/lib/api";
import type { PredictionHistoryResponse, PredictionJob, SnapshotGenerationResult, PredictionGenerationResult, PredictionReviewsResponse } from "@/lib/types";

interface WorkflowsPageProps {
  searchParams: {
    action?: string | string[];
    student_profile_id?: string | string[];
    prediction_id?: string | string[];
    reviewer?: string | string[];
    decision?: string | string[];
    notes?: string | string[];
  };
}

function getQueryParam(value: string | string[] | undefined) {
  return Array.isArray(value) ? value[0] : value;
}

export default async function WorkflowsPage({ searchParams }: WorkflowsPageProps) {
  const action = getQueryParam(searchParams.action);
  const studentProfileId = getQueryParam(searchParams.student_profile_id);
  const predictionId = getQueryParam(searchParams.prediction_id);
  const reviewer = getQueryParam(searchParams.reviewer) ?? "Analyst";
  const decision = getQueryParam(searchParams.decision) ?? "confirmed";
  const notes = getQueryParam(searchParams.notes) ?? "";

  let snapshotResult: SnapshotGenerationResult | null = null;
  let predictionResult: PredictionGenerationResult | null = null;
  let jobResult: PredictionJob | null = null;
  let history: PredictionHistoryResponse | null = null;
  let reviewResult: PredictionReviewsResponse | null = null;
  let errorMessage: string | null = null;
  let successMessage: string | null = null;

  try {
    if (action === "generate_snapshot") {
      if (!studentProfileId) throw new Error("Student profile ID is required for snapshot generation.");
      snapshotResult = await generateSnapshot(studentProfileId);
      successMessage = `Snapshot generated for profile ${studentProfileId}.`;
    }

    if (action === "predict_generated") {
      if (!studentProfileId) throw new Error("Student profile ID is required for prediction generation.");
      predictionResult = await generatePrediction(studentProfileId);
      successMessage = `Prediction generated for profile ${studentProfileId}.`;
    }

    if (action === "queue_prediction") {
      if (!studentProfileId) throw new Error("Student profile ID is required to queue a prediction.");
      jobResult = await queuePrediction(studentProfileId);
      successMessage = `Prediction job queued for profile ${studentProfileId}.`;
    }

    if (action === "load_history") {
      if (!studentProfileId) throw new Error("Student profile ID is required to load history.");
      history = await getPredictionHistory(studentProfileId);
      successMessage = `Loaded prediction history for profile ${studentProfileId}.`;
    }

    if (action === "submit_review") {
      if (!predictionId) throw new Error("Prediction ID is required to submit a review.");
      reviewResult = await createPredictionReview(predictionId, reviewer, decision, notes || undefined);
      successMessage = `Review submitted for prediction ${predictionId}.`;
    }
  } catch (error) {
    if (error instanceof Error) {
      errorMessage = error.message;
    } else {
      errorMessage = "Unable to process request.";
    }
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <div className="mb-8">
        <p className="text-sm uppercase tracking-[0.24em] text-muted-foreground">Interactive Workflows</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">
          Execute profile-driven snapshot, prediction, queue, and review workflows
        </h1>
        <p className="mt-3 text-base leading-7 text-muted-foreground max-w-2xl">
          Use a student profile ID to generate a feature snapshot, run a prediction, enqueue a job, or submit an analyst review directly through the ML backend.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="border border-border p-6">
          <CardHeader>
            <CardTitle>Profile workflow actions</CardTitle>
            <CardDescription>Enter a student profile ID and select the action to perform.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6 pt-4">
            <form className="space-y-4" action="." method="get">
              <label className="block text-sm font-medium text-muted-foreground" htmlFor="student_profile_id">
                Student profile ID
              </label>
              <input
                id="student_profile_id"
                name="student_profile_id"
                defaultValue={studentProfileId ?? ""}
                placeholder="Profile UUID"
                className="w-full rounded-xl border border-input bg-background px-4 py-3 text-base text-foreground shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
              />

              <div className="grid gap-3 sm:grid-cols-2">
                <button
                  type="submit"
                  name="action"
                  value="generate_snapshot"
                  className="rounded-xl bg-primary px-4 py-3 text-sm font-semibold text-primary-foreground transition hover:bg-primary/90"
                >
                  Generate snapshot
                </button>
                <button
                  type="submit"
                  name="action"
                  value="predict_generated"
                  className="rounded-xl bg-secondary px-4 py-3 text-sm font-semibold text-secondary-foreground transition hover:bg-secondary/90"
                >
                  Generate prediction
                </button>
                <button
                  type="submit"
                  name="action"
                  value="queue_prediction"
                  className="rounded-xl bg-emerald-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-emerald-700"
                >
                  Queue prediction
                </button>
                <button
                  type="submit"
                  name="action"
                  value="load_history"
                  className="rounded-xl bg-muted px-4 py-3 text-sm font-semibold text-foreground transition hover:bg-muted/90"
                >
                  Load history
                </button>
              </div>
            </form>
          </CardContent>
        </Card>

        <Card className="border border-border p-6">
          <CardHeader>
            <CardTitle>Review submission</CardTitle>
            <CardDescription>Submit an analyst review for a prediction result.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 pt-4">
            <form className="space-y-4" action="." method="get">
              <input type="hidden" name="action" value="submit_review" />
              <label className="block text-sm font-medium text-muted-foreground" htmlFor="prediction_id">
                Prediction ID
              </label>
              <input
                id="prediction_id"
                name="prediction_id"
                defaultValue={predictionId ?? ""}
                placeholder="Prediction UUID"
                className="w-full rounded-xl border border-input bg-background px-4 py-3 text-base text-foreground shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
              />

              <label className="block text-sm font-medium text-muted-foreground" htmlFor="reviewer">
                Reviewer name
              </label>
              <input
                id="reviewer"
                name="reviewer"
                defaultValue={reviewer}
                placeholder="Analyst name"
                className="w-full rounded-xl border border-input bg-background px-4 py-3 text-base text-foreground shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
              />

              <label className="block text-sm font-medium text-muted-foreground" htmlFor="decision">
                Decision
              </label>
              <select
                id="decision"
                name="decision"
                defaultValue={decision}
                className="w-full rounded-xl border border-input bg-background px-4 py-3 text-base text-foreground shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
              >
                <option value="confirmed">confirmed</option>
                <option value="rejected">rejected</option>
                <option value="under_review">under_review</option>
              </select>

              <label className="block text-sm font-medium text-muted-foreground" htmlFor="notes">
                Notes
              </label>
              <textarea
                id="notes"
                name="notes"
                defaultValue={notes}
                placeholder="Optional notes for the review"
                rows={4}
                className="w-full rounded-3xl border border-input bg-background px-4 py-3 text-base text-foreground shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
              />

              <button
                type="submit"
                className="inline-flex items-center justify-center rounded-xl bg-primary px-4 py-3 text-sm font-semibold text-primary-foreground transition hover:bg-primary/90"
              >
                Submit review
              </button>
            </form>
          </CardContent>
        </Card>
      </div>

      {errorMessage ? (
        <div className="mt-8 rounded-3xl border border-destructive/30 bg-destructive/10 p-6 text-sm text-destructive">
          {errorMessage}
        </div>
      ) : null}

      {successMessage ? (
        <div className="mt-8 rounded-3xl border border-emerald-300 bg-emerald-50 p-6 text-sm text-foreground">
          {successMessage}
        </div>
      ) : null}

      <div className="mt-8 space-y-6">
        {snapshotResult ? (
          <Card className="border border-border">
            <CardHeader className="px-6 py-5">
              <CardTitle>Snapshot result</CardTitle>
              <CardDescription>Feature snapshot created for the student profile.</CardDescription>
            </CardHeader>
            <CardContent className="px-6 pb-6 pt-0 space-y-4">
              <div>
                <p className="text-sm text-muted-foreground">Snapshot ID</p>
                <p className="mt-1 font-semibold">{snapshotResult.feature_snapshot_id}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Feature schema</p>
                <p className="mt-1 font-semibold">{snapshotResult.feature_schema_version ?? "Unknown"}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Source</p>
                <p className="mt-1 font-semibold">{snapshotResult.source ?? "Unknown"}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Feature payload</p>
                <pre className="mt-2 overflow-x-auto rounded-2xl border border-border bg-muted/50 p-4 text-sm text-muted-foreground">
                  {JSON.stringify(snapshotResult.features, null, 2)}
                </pre>
              </div>
            </CardContent>
          </Card>
        ) : null}

        {predictionResult ? (
          <Card className="border border-border">
            <CardHeader className="px-6 py-5">
              <CardTitle>Generated prediction</CardTitle>
              <CardDescription>Prediction result created from a fresh snapshot.</CardDescription>
            </CardHeader>
            <CardContent className="px-6 pb-6 pt-0 space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <p className="text-sm text-muted-foreground">Prediction ID</p>
                  <p className="mt-1 font-semibold">{predictionResult.prediction_id}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Risk level</p>
                  <Badge variant={predictionResult.risk_level === "HIGH" ? "destructive" : predictionResult.risk_level === "MEDIUM" ? "secondary" : "default"}>
                    {predictionResult.risk_level ?? "Unknown"}
                  </Badge>
                </div>
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <p className="text-sm text-muted-foreground">Model version</p>
                  <p className="mt-1 font-semibold">{predictionResult.model_version_id ?? "N/A"}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Latency</p>
                  <p className="mt-1 font-semibold">{predictionResult.prediction_duration_ms ?? "—"} ms</p>
                </div>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Explanation</p>
                <pre className="mt-2 overflow-x-auto rounded-2xl border border-border bg-muted/50 p-4 text-sm text-muted-foreground">
                  {predictionResult.explanation ?? "No explanation provided."}
                </pre>
              </div>
            </CardContent>
          </Card>
        ) : null}

        {jobResult ? (
          <Card className="border border-border">
            <CardHeader className="px-6 py-5">
              <CardTitle>Queued prediction</CardTitle>
              <CardDescription>Job record created in the backend queue.</CardDescription>
            </CardHeader>
            <CardContent className="px-6 pb-6 pt-0 space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <p className="text-sm text-muted-foreground">Job ID</p>
                  <p className="mt-1 font-semibold">{jobResult.job_id}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Status</p>
                  <Badge variant={jobResult.status === "completed" ? "default" : jobResult.status === "failed" ? "destructive" : "secondary"}>
                    {jobResult.status}
                  </Badge>
                </div>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Student profile</p>
                <p className="mt-1 font-semibold">{jobResult.student_profile_id}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Result payload</p>
                <pre className="mt-2 overflow-x-auto rounded-2xl border border-border bg-muted/50 p-4 text-sm text-muted-foreground">
                  {JSON.stringify(jobResult.result, null, 2)}
                </pre>
              </div>
            </CardContent>
          </Card>
        ) : null}

        {history ? (
          <Card className="border border-border">
            <CardHeader className="px-6 py-5">
              <CardTitle>Prediction history</CardTitle>
              <CardDescription>Recent predictions for this profile.</CardDescription>
            </CardHeader>
            <CardContent className="px-6 pb-6 pt-0 space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <p className="text-sm text-muted-foreground">Student profile</p>
                  <p className="mt-1 font-semibold">{history.student_profile_id}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">History count</p>
                  <p className="mt-1 font-semibold">{history.prediction_history.length}</p>
                </div>
              </div>
              <div className="space-y-4">
                {history.prediction_history.map((item) => (
                  <div key={item.prediction_id} className="rounded-3xl border border-border p-5">
                    <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                      <p className="font-semibold">{item.prediction_id}</p>
                      <Badge variant={item.risk_level === "HIGH" ? "destructive" : item.risk_level === "MEDIUM" ? "secondary" : "default"}>
                        {item.risk_level ?? "Unknown"}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mt-2">Model: {item.model_name ?? "Unknown"}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        ) : null}

        {reviewResult ? (
          <Card className="border border-border">
            <CardHeader className="px-6 py-5">
              <CardTitle>Review created</CardTitle>
              <CardDescription>Analyst review was submitted successfully.</CardDescription>
            </CardHeader>
            <CardContent className="px-6 pb-6 pt-0 space-y-4">
              <div>
                <p className="text-sm text-muted-foreground">Review ID</p>
                <p className="mt-1 font-semibold">{reviewResult.review_id}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Prediction ID</p>
                <p className="mt-1 font-semibold">{reviewResult.prediction_id}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Decision</p>
                <p className="mt-1 font-semibold">{reviewResult.decision}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Notes</p>
                <p className="mt-1 text-lg font-semibold">{reviewResult.notes ?? "None"}</p>
              </div>
            </CardContent>
          </Card>
        ) : null}
      </div>
    </div>
  );
}
