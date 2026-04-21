"use client";

import { motion } from "motion/react";

export function ConnectorLine() {
  return (
    <div className="pointer-events-none absolute left-1/2 top-1/2 hidden -translate-x-1/2 -translate-y-1/2 lg:block">
      <div className="relative h-full w-16">
        <svg
          viewBox="0 0 64 400"
          fill="none"
          className="h-full w-full"
          preserveAspectRatio="none"
        >
          <defs>
            <linearGradient id="connector-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#ef4444" stopOpacity="0.3" />
              <stop offset="50%" stopColor="#a855f7" stopOpacity="0.6" />
              <stop offset="100%" stopColor="#10b981" stopOpacity="0.3" />
            </linearGradient>
          </defs>

          <path
            d="M32 0 C32 100, 32 300, 32 400"
            stroke="url(#connector-gradient)"
            strokeWidth="2"
            fill="none"
            strokeLinecap="round"
            className="opacity-60"
          />

          <motion.circle
            cx="32"
            cy="200"
            r="6"
            fill="url(#connector-gradient)"
            animate={{
              scale: [1, 1.5, 1],
              opacity: [0.5, 1, 0.5],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          />

          <motion.path
            d="M32 160 L38 175 L32 190 L26 175 Z"
            fill="#a855f7"
            animate={{
              y: [0, 8, 0],
            }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          />
        </svg>
      </div>
    </div>
  );
}