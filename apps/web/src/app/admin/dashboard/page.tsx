import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Activity, Database, AlertTriangle, Sparkles, Layers } from "lucide-react";
import { getDashboardSummary } from "@/lib/api";

const statCards = [
  {
    title: "Beneficiaries",
    key: "profiles",
    icon: Database,
    description: "Total student profiles processed.",
  },
  {
    title: "Snapshots",
    key: "snapshots",
    icon: Layers,
    description: "Feature snapshots stored in the system.",
  },
  {
    title: "Predictions",
    key: "predictions",
    icon: Activity,
    description: "Total prediction records generated.",
  },
  {
    title: "High Risk Alerts",
    key: "high_risk",
    icon: AlertTriangle,
    description: "Predictions marked at the highest fraud risk level.",
  },
  {
    title: "Medium Risk",
    key: "medium_risk",
    icon: Sparkles,
    description: "Predictions with medium risk exposure.",
  },
];

export default async function DashboardPage() {
  const summary = await getDashboardSummary();

  return (
    <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.24em] text-muted-foreground">Live Dashboard</p>
          <h1 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">
            System summary and risk posture
          </h1>
          <p className="mt-3 text-base leading-7 text-muted-foreground max-w-2xl">
            Live backend data for predictions, models, and operational risk indicators.
          </p>
        </div>
        <Badge variant="secondary" className="uppercase tracking-[0.18em]">
          Connected to backend
        </Badge>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {statCards.map((card) => {
          const Icon = card.icon;
          return (
            <Card key={card.title} className="border border-border">
              <CardHeader className="flex items-start gap-4 px-6 py-5">
                <div className="rounded-2xl bg-primary/10 p-3 text-primary">
                  <Icon className="h-5 w-5" />
                </div>
                <div>
                  <CardTitle>{card.title}</CardTitle>
                  <CardDescription>{card.description}</CardDescription>
                </div>
              </CardHeader>
              <CardContent className="px-6 pb-6 pt-0">
                <p className="text-4xl font-semibold">
                  {summary[card.key as keyof typeof summary] ?? 0}
                </p>
              </CardContent>
            </Card>
          );
        })}

        <Card className="lg:col-span-3 border border-border">
          <CardHeader className="px-6 py-5">
            <CardTitle>High risk insights</CardTitle>
            <CardDescription>
              Monitor the ratio of profiles and active high risk predictions across the platform.
            </CardDescription>
          </CardHeader>
          <CardContent className="px-6 pb-6 pt-0">
            <div className="grid gap-4 md:grid-cols-3">
              <div className="rounded-3xl border border-border p-5">
                <p className="text-sm font-medium text-muted-foreground">High Risk</p>
                <p className="mt-3 text-3xl font-semibold text-rose-600">
                  {summary.high_risk}
                </p>
              </div>
              <div className="rounded-3xl border border-border p-5">
                <p className="text-sm font-medium text-muted-foreground">Medium Risk</p>
                <p className="mt-3 text-3xl font-semibold text-amber-600">
                  {summary.medium_risk}
                </p>
              </div>
              <div className="rounded-3xl border border-border p-5">
                <p className="text-sm font-medium text-muted-foreground">Low Risk</p>
                <p className="mt-3 text-3xl font-semibold text-emerald-600">
                  {summary.low_risk}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
