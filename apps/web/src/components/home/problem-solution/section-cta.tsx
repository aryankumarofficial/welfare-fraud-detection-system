"use client";

import { motion } from "motion/react";
import { ArrowRight } from "lucide-react";

export function SectionCta() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.6, delay: 0.4 }}
      className="mt-16 text-center"
    >
      <div className="inline-flex items-center gap-2 rounded-full bg-muted/50 px-6 py-3 text-sm text-muted-foreground border border-border">
        <span>Ready to transform your fraud detection?</span>
        <a
          href="#"
          className="inline-flex items-center gap-1 font-medium text-primary hover:underline"
        >
          Get Started <ArrowRight className="h-4 w-4" />
        </a>
      </div>
    </motion.div>
  );
}