"use client";

import { useApi } from "@/hooks/use-api";
import { getModelHealth } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function ModelHealthPage() {
  const { data: health, error, loading } = useApi(getModelHealth);

  return (
    <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <div className="mb-8">
        <p className="text-sm uppercase tracking-[0.24em] text-muted-foreground">Model Health</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">Champion model health</h1>
        <p className="mt-3 text-base leading-7 text-muted-foreground max-w-2xl">
          Live champion health metrics and recent model evaluation data from the backend.
        </p>
      </div>

      {loading ? (
        <div className="rounded-3xl border border-border bg-muted/50 p-8 text-center">Loading model health…</div>
      ) : error ? (
        <div className="rounded-3xl border border-destructive/30 bg-destructive/10 p-6 text-sm text-destructive">
          {error}
        </div>
      ) : null}

      {health ? (
        <div className="grid gap-6 lg:grid-cols-3">
          <Card className="border border-border p-6">
            <CardTitle>Champion model</CardTitle>
            <CardDescription>{health.champion?.name ?? "No champion model"}</CardDescription>
            <div className="mt-6 text-3xl font-semibold">{health.champion?.version ?? "—"}</div>
          </Card>
          <Card className="border border-border p-6">
            <CardTitle>False positive rate</CardTitle>
            <CardDescription>Calculated from recent review decisions.</CardDescription>
            <div className="mt-6 text-3xl font-semibold">
              {health.false_positive_rate != null ? `${(health.false_positive_rate * 100).toFixed(1)}%` : "—"}
            </div>
          </Card>
          <Card className="border border-border p-6">
            <CardTitle>Total registered models</CardTitle>
            <CardDescription>All models currently tracked by the registry.</CardDescription>
            <div className="mt-6 text-3xl font-semibold">{health.total_registered_models ?? 0}</div>
          </Card>
        </div>
      ) : null}

      {health?.latest_evaluation ? (
        <Card className="mt-6 border border-border">
          <CardHeader>
            <CardTitle>Latest champion evaluation</CardTitle>
            <CardDescription>Most recent evaluation run for the champion model.</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-4 sm:grid-cols-2">
            <div>
              <p className="text-sm text-muted-foreground">Precision</p>
              <p className="mt-2 text-3xl font-semibold">{health.latest_evaluation.precision}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">False positive rate</p>
              <p className="mt-2 text-3xl font-semibold">{health.latest_evaluation.false_positive_rate}</p>
            </div>
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}
