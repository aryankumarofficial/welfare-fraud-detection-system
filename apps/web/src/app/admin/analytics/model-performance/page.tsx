import { getModelPerformance } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

function getVariant(value: number) {
  if (value >= 0.75) return "default";
  if (value >= 0.4) return "secondary";
  return "destructive";
}

export default async function ModelPerformancePage() {
  const modelPerformance = await getModelPerformance();

  return (
    <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <div className="mb-8">
        <p className="text-sm uppercase tracking-[0.24em] text-muted-foreground">Model Monitoring</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">
          Model performance and review quality
        </h1>
        <p className="mt-3 text-base leading-7 text-muted-foreground max-w-2xl">
          Live model evaluation metrics from analyst review outcomes.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="border border-border p-6">
          <CardTitle>Reviewed predictions</CardTitle>
          <CardDescription>Number of reviewed outcomes in the system.</CardDescription>
          <div className="mt-6 text-4xl font-semibold">{modelPerformance.reviewed_predictions}</div>
        </Card>
        <Card className="border border-border p-6">
          <CardTitle>Confirmed fraud</CardTitle>
          <CardDescription>Confirmed fraud decisions by reviewers.</CardDescription>
          <div className="mt-6 text-4xl font-semibold">{modelPerformance.confirmed_fraud_count}</div>
        </Card>
        <Card className="border border-border p-6">
          <CardTitle>False positives</CardTitle>
          <CardDescription>Predictions flagged incorrectly as fraud.</CardDescription>
          <div className="mt-6 text-4xl font-semibold">{modelPerformance.false_positives}</div>
        </Card>
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        <Card className="border border-border">
          <CardHeader className="px-6 py-5">
            <CardTitle>Precision</CardTitle>
            <CardDescription>Higher values indicate better review agreement.</CardDescription>
          </CardHeader>
          <CardContent className="px-6 pb-6 pt-0">
            <div className="flex items-center gap-4">
              <p className="text-5xl font-semibold">{(modelPerformance.precision * 100).toFixed(1)}%</p>
              <Badge variant={getVariant(modelPerformance.precision)}>
                {modelPerformance.precision >= 0.75 ? "Good" : modelPerformance.precision >= 0.4 ? "Moderate" : "Low"}
              </Badge>
            </div>
          </CardContent>
        </Card>

        <Card className="border border-border">
          <CardHeader className="px-6 py-5">
            <CardTitle>Agreement rate</CardTitle>
            <CardDescription>Share of reviewed predictions matching confirmed fraud decisions.</CardDescription>
          </CardHeader>
          <CardContent className="px-6 pb-6 pt-0">
            <div className="flex items-center gap-4">
              <p className="text-5xl font-semibold">{(modelPerformance.review_agreement_rate * 100).toFixed(1)}%</p>
              <Badge variant={getVariant(modelPerformance.review_agreement_rate)}>
                {modelPerformance.review_agreement_rate >= 0.75 ? "Stable" : modelPerformance.review_agreement_rate >= 0.4 ? "Watch" : "Review"}
              </Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="mt-8 border border-border">
        <CardHeader className="px-6 py-5">
          <CardTitle>Decision distribution</CardTitle>
          <CardDescription>Counts by individual review decisions.</CardDescription>
        </CardHeader>
        <CardContent className="px-6 pb-6 pt-0 space-y-4">
          {Object.entries(modelPerformance.decision_counts).map(([decision, count]) => (
            <div key={decision} className="rounded-3xl border border-border p-4">
              <div className="flex items-center justify-between gap-4">
                <p className="font-medium">{decision.replaceAll("_", " ")}</p>
                <Badge variant="secondary">{count}</Badge>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
