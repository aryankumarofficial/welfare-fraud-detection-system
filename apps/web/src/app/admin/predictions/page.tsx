import Link from "next/link";
import { getPredictionHistory } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface AdminPredictionsPageProps {
  searchParams: { student_profile_id?: string | string[] };
}

export default async function AdminPredictionsPage({ searchParams }: AdminPredictionsPageProps) {
  const studentProfileId = Array.isArray(searchParams.student_profile_id)
    ? searchParams.student_profile_id[0]
    : searchParams.student_profile_id;

  let history = null;
  let errorMessage: string | null = null;

  if (studentProfileId) {
    try {
      history = await getPredictionHistory(studentProfileId);
    } catch (error) {
      errorMessage = error instanceof Error ? error.message : "Unable to load prediction history.";
    }
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <div className="mb-8">
        <p className="text-sm uppercase tracking-[0.24em] text-muted-foreground">Prediction History</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">
          Lookup predictions by profile
        </h1>
        <p className="mt-3 text-base leading-7 text-muted-foreground max-w-2xl">
          Enter a student profile ID to browse prediction history and inspect recent model decisions.
        </p>
      </div>

      <Card className="border border-border p-6">
        <form className="grid gap-4 sm:grid-cols-[1fr_auto]" action="." method="get">
          <label className="sr-only" htmlFor="student_profile_id">
            Student profile ID
          </label>
          <input
            id="student_profile_id"
            name="student_profile_id"
            defaultValue={studentProfileId ?? ""}
            placeholder="Student profile ID"
            className="w-full rounded-xl border border-input bg-background px-4 py-3 text-base text-foreground shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
          />
          <button
            type="submit"
            className="inline-flex items-center justify-center rounded-xl bg-primary px-5 py-3 text-sm font-semibold text-primary-foreground transition hover:bg-primary/90"
          >
            Search history
          </button>
        </form>
      </Card>

      {errorMessage ? (
        <div className="mt-6 rounded-3xl border border-destructive/30 bg-destructive/10 p-6 text-sm text-destructive">
          {errorMessage}
        </div>
      ) : null}

      {studentProfileId ? (
        history ? (
          <div className="mt-8 space-y-6">
            <Card className="border border-border">
              <CardHeader className="px-6 py-5">
                <CardTitle>Profile snapshot</CardTitle>
                <CardDescription>
                  Student profile ID: {history.student_profile_id}
                </CardDescription>
              </CardHeader>
              <CardContent className="px-6 pb-6 pt-0">
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="rounded-3xl border border-border p-5">
                    <p className="text-sm text-muted-foreground">Total predictions</p>
                    <p className="mt-2 text-3xl font-semibold">{history.prediction_history.length}</p>
                  </div>
                  <div className="rounded-3xl border border-border p-5">
                    <p className="text-sm text-muted-foreground">Most recent prediction</p>
                    <p className="mt-2 text-3xl font-semibold">{history.latest_prediction.risk_level ?? "Unknown"}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="border border-border">
              <CardHeader className="px-6 py-5">
                <CardTitle>Prediction history</CardTitle>
                <CardDescription>
                  Results are pulled directly from the backend for this student profile.
                </CardDescription>
              </CardHeader>
              <CardContent className="px-6 pb-6 pt-0">
                {history.prediction_history.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No predictions were found for this profile.</p>
                ) : (
                  <div className="grid gap-4">
                    {history.prediction_history.map((item) => (
                      <div key={item.prediction_id} className="rounded-3xl border border-border p-5">
                        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                          <div>
                            <p className="text-sm text-muted-foreground">Prediction ID</p>
                            <p className="mt-1 font-semibold">{item.prediction_id}</p>
                          </div>
                          <Badge variant="secondary">{item.risk_level ?? "Unknown"}</Badge>
                        </div>
                        <div className="mt-4 grid gap-3 sm:grid-cols-3">
                          <div>
                            <p className="text-xs uppercase text-muted-foreground">Final risk</p>
                            <p className="mt-1 text-lg font-semibold">{item.final_risk ?? "—"}</p>
                          </div>
                          <div>
                            <p className="text-xs uppercase text-muted-foreground">Model</p>
                            <p className="mt-1 text-lg font-semibold">{item.model_name ?? "Unknown"}</p>
                          </div>
                          <div>
                            <p className="text-xs uppercase text-muted-foreground">Timestamp</p>
                            <p className="mt-1 text-lg font-semibold">{item.prediction_timestamp ?? item.created_at}</p>
                          </div>
                        </div>
                        <div className="mt-4 flex flex-wrap gap-2 text-sm text-muted-foreground">
                          <Link href={`/admin/predictions/detail/${item.prediction_id}`} className="font-medium text-primary hover:underline">
                            View details
                          </Link>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        ) : (
          <div className="mt-8 rounded-3xl border border-border bg-muted/50 p-6 text-sm text-muted-foreground">
            No record was returned for the requested profile.
          </div>
        )
      ) : (
        <Card className="mt-8 border border-border p-6">
          <CardHeader>
            <CardTitle>Ready to explore prediction history</CardTitle>
            <CardDescription>
              Enter a valid student profile ID to load predictions from the ML backend.
            </CardDescription>
          </CardHeader>
        </Card>
      )}
    </div>
  );
}
