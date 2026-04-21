"use client";

import { motion } from "motion/react";
import { Badge } from "@/components/ui/badge";

export function SectionHeader() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.6 }}
      className="mx-auto mb-16 max-w-3xl text-center"
    >
      <Badge variant="secondary" className="mb-6 gap-1.5 px-4 py-1.5 text-xs font-medium">
        <span className="relative flex h-2 w-2">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-primary opacity-75" />
          <span className="relative inline-flex h-2 w-2 rounded-full bg-primary" />
        </span>
        Challenges & Solutions
      </Badge>

      <h2 className="mb-6 text-3xl font-bold tracking-tight sm:text-4xl lg:text-5xl">
        Eliminating Fraud in{" "}
        <span className="bg-gradient-to-r from-primary via-violet-500 to-primary bg-clip-text text-transparent">
          Welfare Systems
        </span>
      </h2>

      <p className="mx-auto max-w-2xl text-lg text-muted-foreground">
        Traditional systems fail to detect complex fraud patterns. Our AI-driven approach ensures
        transparency and accuracy.
      </p>
    </motion.div>
  );
}