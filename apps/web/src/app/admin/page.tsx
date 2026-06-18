import Link from "next/link";
import { ArrowRight, BarChart3, Bell, ShieldCheck, Sparkles, Terminal, TrendingUp } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";

const cards = [
  {
    title: "Dashboard",
    description: "Real-time risk metrics, traffic, and operational signals.",
    href: "/admin/dashboard",
    icon: BarChart3,
  },
  {
    title: "Predictions",
    description: "Browse prediction history and inspect individual results.",
    href: "/admin/predictions",
    icon: Terminal,
  },
  {
    title: "Queue Monitoring",
    description: "Track job status, backlog, and queue health.",
    href: "/admin/analytics/queue",
    icon: TrendingUp,
  },
  {
    title: "Model Monitoring",
    description: "Review model performance and review agreement rates.",
    href: "/admin/analytics/model-performance",
    icon: ShieldCheck,
  },
  {
    title: "Alert Center",
    description: "Inspect generated alerts and active severity events.",
    href: "/admin/analytics/alerts",
    icon: Bell,
  },
  {
    title: "Reviews Management",
    description: "Browse analyst reviews for prediction accuracy and outcome.",
    href: "/admin/reviews",
    icon: Sparkles,
  },
];

export default function AdminIndexPage() {
  return (
    <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <div className="mb-10">
        <p className="text-sm uppercase tracking-[0.24em] text-muted-foreground">Admin Dashboard</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">
          Live analytics and prediction operations
        </h1>
        <p className="mt-4 max-w-2xl text-base leading-7 text-muted-foreground">
          This admin workspace connects to the ML backend and exposes live monitoring, prediction history, queue status, and review operations.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2 xl:grid-cols-3">
        {cards.map((card) => (
          <Card key={card.title} className="group hover:border-primary/50 hover:shadow-xl transition">
            <CardHeader className="gap-3 px-6 py-5">
              <card.icon className="h-6 w-6 text-primary" />
              <CardTitle className="text-lg">{card.title}</CardTitle>
            </CardHeader>
            <CardContent className="px-6 pb-6 pt-0">
              <CardDescription>{card.description}</CardDescription>
              <div className="mt-6">
                <Button asChild size="sm">
                  <Link href={card.href} className="flex items-center gap-2">
                    Open
                    <ArrowRight className="h-4 w-4" />
                  </Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
