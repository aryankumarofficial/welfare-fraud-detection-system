"use client";

import { Button } from "@/components/ui/button";
import { ArrowRight, Zap, Target, Users } from "lucide-react";

const badges = [
  { icon: Zap, label: "Real-time Detection" },
  { icon: Target, label: "96.8% Accuracy" },
  { icon: Users, label: "1.2M+ Beneficiaries" },
];

export function HeroContent() {
  return (
    <div className="flex flex-col gap-8">
      <div className="flex items-center gap-3">
        <div className="h-8 w-1 bg-primary" />
        <span className="text-xs font-bold uppercase tracking-widest text-muted-foreground">
          AI-Powered Fraud Detection
        </span>
      </div>

      <div className="space-y-4">
        <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tight leading-[0.95]">
          Detect Fraud.
          <br />
          <span className="text-primary">Prevent Loss.</span>
          <br />
          <span className="text-muted-foreground">Protect Welfare.</span>
        </h1>
      </div>

      <p className="text-lg text-muted-foreground max-w-md leading-relaxed">
        ML-powered system analyzing beneficiary data, transactions, and behavioral patterns to identify anomalies and prevent welfare fraud.
      </p>

      <div className="flex flex-wrap gap-4">
        {badges.map((badge) => (
          <div
            key={badge.label}
            className="flex items-center gap-2 px-3 py-1.5 bg-muted border border-border text-xs font-medium"
          >
            <badge.icon className="h-3.5 w-3.5 text-primary" />
            {badge.label}
          </div>
        ))}
      </div>

      <div className="flex gap-3 pt-2">
        <Button size="lg" className="gap-2">
          Get Started
          <ArrowRight className="h-4 w-4" />
        </Button>
        <Button size="lg" variant="outline">
          View Demo
        </Button>
      </div>
    </div>
  );
}