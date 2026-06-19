"use client";

import Link from "next/link";
import { useApi } from "@/hooks/use-api";
import { getPredictionAnalytics } from "@/lib/api";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function AnalyticsSummaryPage() {
  const { data: analytics, error, loading } = useApi(getPredictionAnalytics);

  if (loading) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="rounded-3xl border border-border bg-muted/50 p-8 text-center">
          Loading analytics…
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

  if (!analytics) {
    return null;
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <div className="mb-8">
        <p className="text-sm uppercase tracking-[0.24em] text-muted-foreground">
          Analytics
        </p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">
          Prediction analytics and trend overview
        </h1>
        <p className="mt-3 text-base leading-7 text-muted-foreground max-w-2xl">
          Live operational analytics from the backend, including model and date
          breakdowns.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="border border-border p-6">
          <CardTitle>Total predictions</CardTitle>
          <CardDescription>
            {analytics.total_predictions} records processed
          </CardDescription>
          <div className="mt-6 text-4xl font-semibold">
            {analytics.total_predictions}
          </div>
        </Card>
        <Card className="border border-border p-6">
          <CardTitle>Average risk</CardTitle>
          <CardDescription>
            Live average risk across all predictions.
          </CardDescription>
          <div className="mt-6 text-4xl font-semibold">
            {analytics.average_risk.toFixed(2)}
          </div>
        </Card>
        <Card className="border border-border p-6">
          <CardTitle>Latency</CardTitle>
          <CardDescription>Average backend prediction latency.</CardDescription>
          <div className="mt-6 text-4xl font-semibold">
            {analytics.average_latency_ms.toFixed(1)} ms
          </div>
        </Card>
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        <Card className="border border-border">
          <CardHeader className="px-6 py-5">
            <CardTitle>Top models</CardTitle>
            <CardDescription>
              Predictions grouped by model and version.
            </CardDescription>
          </CardHeader>
          <CardContent className="px-6 pb-6 pt-0">
            <div className="space-y-4">
              {analytics.predictions_by_model_version.map((item) => (
                <div
                  key={`${item.model_name}-${item.model_version}`}
                  className="rounded-3xl border border-border p-4"
                >
                  <div className="flex items-center justify-between gap-4">
                    <div>
                      <p className="font-medium">{item.model_name}</p>
                      <p className="text-sm text-muted-foreground">
                        Version {item.model_version}
                      </p>
                    </div>
                    <Badge variant="secondary">{item.count}</Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="border border-border">
          <CardHeader className="px-6 py-5">
            <CardTitle>Volume by date</CardTitle>
            <CardDescription>
              Rolling prediction volume for each date bucket.
            </CardDescription>
          </CardHeader>
          <CardContent className="px-6 pb-6 pt-0">
            <div className="space-y-4">
              {analytics.predictions_by_date.map((row) => (
                <div
                  key={row.date}
                  className="rounded-3xl border border-border p-4"
                >
                  <div className="flex items-center justify-between gap-4">
                    <p className="font-medium">{row.date}</p>
                    <Badge variant="secondary">{row.count}</Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-3">
        <Card className="border border-border p-6">
          <CardTitle>Model monitoring</CardTitle>
          <CardDescription>
            Inspect performance and review rules.
          </CardDescription>
          <div className="mt-6">
            <Link
              href="/admin/analytics/model-performance"
              className="text-sm font-semibold text-primary hover:underline"
            >
              Open model monitoring page
            </Link>
          </div>
        </Card>
        <Card className="border border-border p-6">
          <CardTitle>Queue monitoring</CardTitle>
          <CardDescription>
            Review current backlog and success rates.
          </CardDescription>
          <div className="mt-6">
            <Link
              href="/admin/analytics/queue"
              className="text-sm font-semibold text-primary hover:underline"
            >
              Open queue monitoring page
            </Link>
          </div>
        </Card>
        <Card className="border border-border p-6">
          <CardTitle>Alert center</CardTitle>
          <CardDescription>
            Track generated alerts and severity events.
          </CardDescription>
          <div className="mt-6">
            <Link
              href="/admin/analytics/alerts"
              className="text-sm font-semibold text-primary hover:underline"
            >
              Open alert center
            </Link>
          </div>
        </Card>
      </div>
    </div>
  );
}
