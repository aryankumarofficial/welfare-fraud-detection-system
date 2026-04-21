"use client";

import { motion } from "motion/react";
import { cn } from "@/lib/utils";
import type { ProblemSolutionCardProps } from "./types";

export function SolutionCard({
  icon: Icon,
  title,
  description,
  glowColor,
  index,
}: ProblemSolutionCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-50px" }}
      transition={{ duration: 0.5, delay: index * 0.1 + 0.2, ease: "easeOut" }}
      whileHover={{ scale: 1.02, y: -4 }}
      className={cn(
        "group relative overflow-hidden rounded-2xl border border-emerald-500/20 bg-gradient-to-br from-emerald-950/30 via-card to-card p-6 transition-all duration-300",
        glowColor,
        "hover:border-emerald-500/40 hover:shadow-xl"
      )}
    >
      <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/[0.03] to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100" />

      <div className="absolute -right-12 -top-12 h-32 w-32 rounded-full bg-emerald-500/10 blur-2xl transition-all duration-500 group-hover:bg-emerald-500/20 group-hover:scale-150" />

      <div className="relative z-10">
        <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-500/20 to-emerald-600/10 border border-emerald-500/30">
          <Icon className="h-6 w-6 text-emerald-400" />
        </div>

        <h3 className="mb-2 text-lg font-semibold text-foreground">{title}</h3>

        <p className="text-sm leading-relaxed text-muted-foreground">
          {description}
        </p>
      </div>

      <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-emerald-500/0 via-emerald-500/50 to-emerald-500/0 scale-x-0 transition-transform duration-300 group-hover:scale-x-100" />
    </motion.div>
  );
}