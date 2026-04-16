"use client";

import { AlertTriangle, Shield, Target, Activity } from "lucide-react";

const stats = [
  { label: "Fraud Detected", value: "23", sub: "Today", icon: AlertTriangle },
  { label: "High Risk Flags", value: "147", sub: "Active", icon: Activity },
  { label: "Model Accuracy", value: "96.8", sub: "Percent", icon: Target },
  { label: "Active Nodes", value: "8,432", sub: "Monitoring", icon: Shield },
];

export function HeroStatsStrip() {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-px bg-border">
      {stats.map((stat) => (
        <div
          key={stat.label}
          className="bg-background p-6 flex items-start justify-between"
        >
          <div className="space-y-1">
            <p className="text-sm font-medium text-muted-foreground">{stat.label}</p>
            <p className="text-3xl font-bold tracking-tight">{stat.value}</p>
            <p className="text-xs text-muted-foreground uppercase tracking-wide">{stat.sub}</p>
          </div>
          <stat.icon className="h-5 w-5 text-muted-foreground/60" />
        </div>
      ))}
    </div>
  );
}