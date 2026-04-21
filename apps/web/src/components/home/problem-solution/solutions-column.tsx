"use client";

import { ShieldCheck } from "lucide-react";
import { SolutionCard } from "./solution-card";
import { solutions } from "./data";

export function SolutionsColumn() {
  return (
    <div className="relative">
      <div className="mb-6 flex items-center gap-3">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-500/20 border border-emerald-500/30">
          <ShieldCheck className="h-4 w-4 text-emerald-400" />
        </div>
        <h3 className="text-xl font-semibold text-foreground">Our Solutions</h3>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-1">
        {solutions.map((solution, index) => (
          <SolutionCard key={solution.title} {...solution} index={index} />
        ))}
      </div>
    </div>
  );
}