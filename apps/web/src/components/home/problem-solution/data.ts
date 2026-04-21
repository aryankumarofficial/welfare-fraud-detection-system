import { Users, UserX, Layers, Activity, Brain, ShieldCheck, Link2, AlertTriangle } from "lucide-react";
import type { Problem, Solution } from "./types";

export const problems: Problem[] = [
  {
    icon: Users,
    title: "Duplicate Beneficiaries",
    description:
      "Same individual registered multiple times under different identities, draining resources.",
    glowColor: "hover:shadow-red-500/20",
  },
  {
    icon: UserX,
    title: "Ghost / Fake Identities",
    description:
      "Fabricated identities created to funnel welfare funds to non-existent people.",
    glowColor: "hover:shadow-orange-500/20",
  },
  {
    icon: Layers,
    title: "Multiple Scheme Abuse",
    description:
      "Individuals exploiting loopholes to receive benefits from multiple welfare programs simultaneously.",
    glowColor: "hover:shadow-amber-500/20",
  },
  {
    icon: Activity,
    title: "Unusual Transaction Patterns",
    description:
      "Suspicious fund movements that go undetected by traditional rule-based monitoring systems.",
    glowColor: "hover:shadow-yellow-500/20",
  },
];

export const solutions: Solution[] = [
  {
    icon: Brain,
    title: "AI-Based Duplicate Detection",
    description:
      "Machine learning algorithms identify potential duplicates with 99.2% accuracy using fuzzy matching.",
    glowColor: "hover:shadow-emerald-500/20",
  },
  {
    icon: ShieldCheck,
    title: "Identity Verification via Data Patterns",
    description:
      "Cross-references government databases to validate authentic identities in real-time.",
    glowColor: "hover:shadow-teal-500/20",
  },
  {
    icon: Link2,
    title: "Cross-Scheme Linking Detection",
    description:
      "Analyzes relationships between beneficiaries across all schemes to flag potential fraud rings.",
    glowColor: "hover:shadow-cyan-500/20",
  },
  {
    icon: AlertTriangle,
    title: "Behavioral Anomaly Detection",
    description:
      "Continuous monitoring with ML models that learn normal patterns and flag deviations instantly.",
    glowColor: "hover:shadow-sky-500/20",
  },
];