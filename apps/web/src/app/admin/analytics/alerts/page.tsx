"use client";

import { getAlerts } from "@/lib/api";
import { useApi } from "@/hooks/use-api";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";

function severityVariant(severity: string) {
  if (severity?.toLowerCase() === "critical") return "destructive";
  if (severity?.toLowerCase() === "warning") return "secondary";
  return "default";
}

export default function AlertsPage() {
  const { data: alerts, error, loading } = useApi(getAlerts);

  return (
    <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <div className="mb-8">
        <p className="text-sm uppercase tracking-[0.24em] text-muted-foreground">
          Alert Center
        </p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">
          Live alerts and monitoring events
        </h1>
        <p className="mt-3 text-base leading-7 text-muted-foreground max-w-2xl">
          Generated alerts and recent activity from backend monitoring services.
        </p>
      </div>

      {loading ? (
        <div className="rounded-3xl border border-border bg-muted/50 p-8 text-center">
          Loading alerts…
        </div>
      ) : error ? (
        <div className="rounded-3xl border border-destructive/30 bg-destructive/10 p-6 text-sm text-destructive">
          {error}
        </div>
      ) : alerts ? (
        <div className="grid gap-6 lg:grid-cols-2">
          <Card className="border border-border">
            <CardHeader className="px-6 py-5">
              <CardTitle>Generated alerts</CardTitle>
              <CardDescription>
                Alerts created by automatic drift, queue, and failure detection.
              </CardDescription>
            </CardHeader>
            <CardContent className="px-6 pb-6 pt-0 space-y-4">
              {alerts.generated.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  No generated alerts were returned.
                </p>
              ) : (
                alerts.generated.map((alert) => (
                  <div
                    key={alert.alert_id}
                    className="rounded-3xl border border-border p-5"
                  >
                    <div className="flex items-center justify-between gap-4">
                      <p className="font-medium">
                        {alert.alert_type.replaceAll("_", " ")}
                      </p>
                      <Badge
                        variant={
                          severityVariant(alert.severity) as
                            | "default"
                            | "secondary"
                            | "destructive"
                        }
                      >
                        {alert.severity}
                      </Badge>
                    </div>
                    <p className="mt-2 text-sm text-muted-foreground">
                      {alert.message}
                    </p>
                    <p className="mt-3 text-xs uppercase tracking-[0.2em] text-muted-foreground">
                      Created at
                    </p>
                    <p className="text-sm font-medium">{alert.created_at}</p>
                  </div>
                ))
              )}
            </CardContent>
          </Card>

          <Card className="border border-border">
            <CardHeader className="px-6 py-5">
              <CardTitle>Recent alerts</CardTitle>
              <CardDescription>
                Most recent persisted alert records.
              </CardDescription>
            </CardHeader>
            <CardContent className="px-6 pb-6 pt-0 space-y-4">
              {alerts.recent_alerts.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  No recent alerts were found.
                </p>
              ) : (
                alerts.recent_alerts.map((alert) => (
                  <div
                    key={alert.alert_id}
                    className="rounded-3xl border border-border p-5"
                  >
                    <div className="flex items-center justify-between gap-4">
                      <p className="font-medium">
                        {alert.alert_type.replaceAll("_", " ")}
                      </p>
                      <Badge
                        variant={
                          severityVariant(alert.severity) as
                            | "default"
                            | "secondary"
                            | "destructive"
                        }
                      >
                        {alert.severity}
                      </Badge>
                    </div>
                    <p className="mt-2 text-sm text-muted-foreground">
                      {alert.message}
                    </p>
                    <p className="mt-3 text-xs uppercase tracking-[0.2em] text-muted-foreground">
                      Created at
                    </p>
                    <p className="text-sm font-medium">{alert.created_at}</p>
                  </div>
                ))
              )}
            </CardContent>
          </Card>
        </div>
      ) : null}
    </div>
  );
}
