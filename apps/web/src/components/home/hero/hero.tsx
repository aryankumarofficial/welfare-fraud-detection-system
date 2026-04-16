"use client";

import { HeroContent } from "./hero-content";
import { HeroRiskPanel } from "./hero-risk-panel";
import { HeroStatsStrip } from "./hero-stats-strip";

export function Hero() {
  return (
    <section className="relative border-b border-border/40 bg-gradient-to-b from-primary/5 to-transparent">
      <div className="absolute inset-0 -z-10" />
      <div className="mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl py-16 md:py-24">
        <div className="grid lg:grid-cols-12 gap-8 lg:gap-12">
          <div className="lg:col-span-7">
            <HeroContent />
          </div>
          <div className="lg:col-span-5">
            <HeroRiskPanel />
          </div>
        </div>
        <div className="mt-12">
          <HeroStatsStrip />
        </div>
      </div>
    </section>
  );
}