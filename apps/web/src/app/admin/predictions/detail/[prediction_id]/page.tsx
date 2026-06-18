import { getPredictionDetail } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface PredictionDetailsPageProps {
  params: { prediction_id: string };
}

export default async function PredictionDetailsPage({ params }: PredictionDetailsPageProps) {
  let detail = null;
  let errorMessage: string | null = null;

  try {
    detail = await getPredictionDetail(params.prediction_id);
  } catch (error) {
    errorMessage = error instanceof Error ? error.message : "Unable to load prediction details.";
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-12 sm:px-6 lg:px-8">
      <div className="mb-8">
        <p className="text-sm uppercase tracking-[0.24em] text-muted-foreground">Prediction Details</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">
          Prediction {params.prediction_id}
        </h1>
        <p className="mt-3 text-base leading-7 text-muted-foreground max-w-2xl">
          This page pulls the prediction record directly from the backend.
        </p>
      </div>

      {errorMessage ? (
        <div className="rounded-3xl border border-destructive/30 bg-destructive/10 p-6 text-sm text-destructive">
          {errorMessage}
        </div>
      ) : detail ? (
        <div className="grid gap-6 lg:grid-cols-2">
          <Card className="border border-border">
            <CardHeader className="px-6 py-5">
              <CardTitle>Summary</CardTitle>
              <CardDescription>Core prediction details, risk score, and model metadata.</CardDescription>
            </CardHeader>
            <CardContent className="px-6 pb-6 pt-0 space-y-4">
              <div>
                <p className="text-sm text-muted-foreground">Risk level</p>
                <Badge variant={detail.risk_level === "HIGH" ? "destructive" : detail.risk_level === "MEDIUM" ? "secondary" : "default"}>
                  {detail.risk_level ?? "Unknown"}
                </Badge>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Final risk score</p>
                <p className="mt-1 text-3xl font-semibold">{detail.final_risk ?? "—"}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Model</p>
                <p className="mt-1 text-lg font-semibold">{detail.model_name ?? "Unknown"}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Version</p>
                <p className="mt-1 text-lg font-semibold">{detail.model_version ?? "Unknown"}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Inferred at</p>
                <p className="mt-1 text-lg font-semibold">{detail.prediction_timestamp ?? detail.created_at}</p>
              </div>
            </CardContent>
          </Card>

          <Card className="border border-border">
            <CardHeader className="px-6 py-5">
              <CardTitle>Risk contributions</CardTitle>
              <CardDescription>Show how the score was assembled from feature risks.</CardDescription>
            </CardHeader>
            <CardContent className="px-6 pb-6 pt-0 space-y-4">
              <div>
                <p className="text-sm text-muted-foreground">Income risk</p>
                <p className="mt-1 text-lg font-semibold">{detail.income_risk ?? "—"}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Caste risk</p>
                <p className="mt-1 text-lg font-semibold">{detail.caste_risk ?? "—"}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Transaction risk</p>
                <p className="mt-1 text-lg font-semibold">{detail.transaction_risk ?? "—"}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Medical risk</p>
                <p className="mt-1 text-lg font-semibold">{detail.medical_risk ?? "—"}</p>
              </div>
            </CardContent>
          </Card>

          <Card className="lg:col-span-2 border border-border">
            <CardHeader className="px-6 py-5">
              <CardTitle>Context and explanation</CardTitle>
              <CardDescription>Raw insight returned from the prediction record.</CardDescription>
            </CardHeader>
            <CardContent className="px-6 pb-6 pt-0 space-y-4">
              <div>
                <p className="text-sm text-muted-foreground">Inference source</p>
                <p className="mt-1 text-lg font-semibold">{detail.inference_source ?? "Unknown"}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Prediction duration</p>
                <p className="mt-1 text-lg font-semibold">{detail.prediction_duration_ms ?? "—"} ms</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Explanation</p>
                <pre className="mt-2 overflow-x-auto rounded-2xl border border-border bg-muted/60 p-4 text-sm text-foreground">
                  {detail.explanation ?? "No explanation available."}
                </pre>
              </div>
            </CardContent>
          </Card>
        </div>
      ) : null}
    </div>
  );
}
