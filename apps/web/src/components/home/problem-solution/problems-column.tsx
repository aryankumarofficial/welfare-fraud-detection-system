"use client";

import { AlertTriangle } from "lucide-react";
import { ProblemCard } from "./problem-card";
import { problems } from "./data";

export function ProblemsColumn() {
  return (
    <div className="relative">
      <div className="mb-6 flex items-center gap-3">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-red-500/20 border border-red-500/30">
          <AlertTriangle className="h-4 w-4 text-red-400" />
        </div>
        <h3 className="text-xl font-semibold text-foreground">The Problems</h3>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-1">
        {problems.map((problem, index) => (
          <ProblemCard key={problem.title} {...problem} index={index} />
        ))}
      </div>
    </div>
  );
}