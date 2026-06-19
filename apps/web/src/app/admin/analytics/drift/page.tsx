"use client";

import { useApi } from "@/hooks/use-api";
import { getDriftAnalytics } from "@/lib/api";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

function getSeverityLabel(score: number) {
  if (score >= 50) return "critical";
  if (score >= 20) return "warning";
  return "default";
}

export default function DriftPage() {
  const { data: drift, error, loading } = useApi(getDriftAnalytics);

  if (loading) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="rounded-3xl border border-border bg-muted/50 p-8 text-center">
          Loading drift analytics…
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="rounded-3xl border border-destructive/30 bg-destructive/10 p-6 text-sm text-destructive">
          {error}
        </div>
      </div>
    );
  }

  if (!drift) {
    return null;
  }

  const latest = drift.latest_snapshot;

  return (
    <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <div className="mb-8">
        <p className="text-sm uppercase tracking-[0.24em] text-muted-foreground">
          Drift Monitoring
        </p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">
          Model drift and feature distribution trends
        </h1>
        <p className="mt-3 text-base leading-7 text-muted-foreground max-w-2xl">
          Live drift analytics generated from the backend snapshot pipeline.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="border border-border p-6">
          <CardTitle>Drift score</CardTitle>
          <CardDescription>Latest window drift severity.</CardDescription>
          <div className="mt-6 flex items-center gap-4">
            <p className="text-5xl font-semibold">
              {latest.drift_score.toFixed(2)}
            </p>
            <Badge
              variant={
                getSeverityLabel(latest.drift_score) as
                  | "default"
                  | "secondary"
                  | "destructive"
              }
            >
              {latest.drift_score >= 50
                ? "Critical"
                : latest.drift_score >= 20
                  ? "Warning"
                  : "Normal"}
            </Badge>
          </div>
        </Card>
        <Card className="border border-border p-6">
          <CardTitle>Snapshot window</CardTitle>
          <CardDescription>Newest monitoring snapshot window.</CardDescription>
          <div className="mt-6 text-3xl font-semibold">{latest.window}</div>
        </Card>
        <Card className="border border-border p-6">
          <CardTitle>Created at</CardTitle>
          <CardDescription>
            Timestamp for the latest drift snapshot.
          </CardDescription>
          <div className="mt-6 text-3xl font-semibold">{latest.created_at}</div>
        </Card>
      </div>

      <Card className="mt-8 border border-border">
        <CardHeader className="px-6 py-5">
          <CardTitle>Prediction volume change</CardTitle>
          <CardDescription>
            Baseline vs current prediction volume across the selected window.
          </CardDescription>
        </CardHeader>
        <CardContent className="px-6 pb-6 pt-0 space-y-4">
          <div className="grid gap-4 sm:grid-cols-3">
            <div className="rounded-3xl border border-border p-4">
              <p className="text-sm text-muted-foreground">Baseline count</p>
              <p className="mt-2 text-xl font-semibold">
                {latest.prediction_volume_changes.baseline_count}
              </p>
            </div>
            <div className="rounded-3xl border border-border p-4">
              <p className="text-sm text-muted-foreground">Current count</p>
              <p className="mt-2 text-xl font-semibold">
                {latest.prediction_volume_changes.current_count}
              </p>
            </div>
            <div className="rounded-3xl border border-border p-4">
              <p className="text-sm text-muted-foreground">Change %</p>
              <p className="mt-2 text-xl font-semibold">
                {latest.prediction_volume_changes.change_percentage.toFixed(2)}%
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="mt-8 border border-border">
        <CardHeader className="px-6 py-5">
          <CardTitle>Risk distribution</CardTitle>
          <CardDescription>
            Baseline and current risk distribution by level.
          </CardDescription>
        </CardHeader>
        <CardContent className="px-6 pb-6 pt-0 grid gap-4 sm:grid-cols-2">
          <div className="rounded-3xl border border-border p-4">
            <p className="text-sm text-muted-foreground">
              Baseline risk levels
            </p>
            <pre className="mt-3 overflow-x-auto rounded-2xl border border-border bg-muted/50 p-4 text-sm">
              {JSON.stringify(
                latest.risk_distribution_changes.baseline_risk_levels,
                null,
                2,
              )}
            </pre>
          </div>
          <div className="rounded-3xl border border-border p-4">
            <p className="text-sm text-muted-foreground">Current risk levels</p>
            <pre className="mt-3 overflow-x-auto rounded-2xl border border-border bg-muted/50 p-4 text-sm">
              {JSON.stringify(
                latest.risk_distribution_changes.current_risk_levels,
                null,
                2,
              )}
            </pre>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
