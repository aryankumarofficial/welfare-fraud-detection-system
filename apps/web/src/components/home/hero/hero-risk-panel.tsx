"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { AlertTriangle, Shield, Activity } from "lucide-react";

const risks = [
  { label: "Low", value: 72, color: "bg-primary" },
  { label: "Medium", value: 18, color: "bg-yellow-500" },
  { label: "High", value: 10, color: "bg-red-500" },
];

export function HeroRiskPanel() {
  return (
    <Card className="h-full">
      <CardHeader className="border-b">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base font-semibold uppercase tracking-wide">
            Risk Assessment
          </CardTitle>
          <Badge variant="outline" className="text-xs font-medium">
            <span className="w-1.5 h-1.5 bg-green-500 rounded-full mr-1.5 animate-pulse" />
            Live
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="pt-6 space-y-6">
        <div className="flex h-4 rounded-sm overflow-hidden gap-px">
          {risks.map((risk) => (
            <div
              key={risk.label}
              className={`${risk.color} transition-all`}
              style={{ width: `${risk.value}%` }}
            />
          ))}
        </div>

        <div className="space-y-0">
          {risks.map((risk) => (
            <div
              key={risk.label}
              className="flex items-center justify-between py-3 border-b border-border last:border-0"
            >
              <div className="flex items-center gap-3">
                <div className={`w-2 h-2 rounded-full ${risk.color}`} />
                <span className="text-sm font-medium">{risk.label} Risk</span>
              </div>
              <span className="text-sm font-bold">{risk.value}%</span>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-2 gap-4 pt-2">
          <div className="border border-border p-4">
            <AlertTriangle className="h-4 w-4 text-red-500 mb-2" />
            <p className="text-2xl font-bold">2,847</p>
            <p className="text-xs text-muted-foreground uppercase">Fraud Cases</p>
          </div>
          <div className="border border-border p-4">
            <Shield className="h-4 w-4 text-primary mb-2" />
            <p className="text-2xl font-bold">1.2M</p>
            <p className="text-xs text-muted-foreground uppercase">Beneficiaries</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}