import type { LucideIcon } from "lucide-react";

export interface ProblemSolutionCardProps {
  icon: LucideIcon;
  title: string;
  description: string;
  glowColor: string;
  index: number;
}

export interface Problem {
  icon: LucideIcon;
  title: string;
  description: string;
  glowColor: string;
}

export interface Solution {
  icon: LucideIcon;
  title: string;
  description: string;
  glowColor: string;
}
