import { Hero } from "@/components/home/hero/hero";
import { StatsSection } from "@/components/home/stats/stats-section";
import { ProblemSolutionSection } from "@/components/home/problem-solution/problem-solution-section";

export default function Home() {
  return (
    <div className="min-h-screen">
      <Hero />
      <StatsSection />
      <ProblemSolutionSection />
    </div>
  );
}