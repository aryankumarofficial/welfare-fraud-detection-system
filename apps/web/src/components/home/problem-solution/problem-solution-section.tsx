"use client";

import { SectionHeader } from "./section-header";
import { SectionCta } from "./section-cta";
import { ConnectorLine } from "./connector-line";
import { ProblemsColumn } from "./problems-column";
import { SolutionsColumn } from "./solutions-column";

export function ProblemSolutionSection() {
  return (
    <section className="relative overflow-hidden bg-background py-24 lg:py-32">
      <div className="absolute inset-0 bg-grid-pattern bg-size-[32px_32px] opacity-[0.02] dark:opacity-[0.03]" />

      <div className="absolute top-0 left-1/2 -translate-x-1/2 h-125 w-200 bg-primary/5 rounded-full blur-3xl" />

      <div className="container relative mx-auto px-4 sm:px-6 lg:px-8">
        <SectionHeader />

        <div className="relative grid gap-8 lg:grid-cols-2 lg:gap-12">
          <ConnectorLine />
          <ProblemsColumn />
          <SolutionsColumn />
        </div>

        <SectionCta />
      </div>
    </section>
  );
}
