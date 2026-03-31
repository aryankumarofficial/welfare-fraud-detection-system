"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Shield, Search, Home, AlertTriangle } from "lucide-react";
import { motion } from "motion/react";

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center px-4 relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute inset-0 bg-gradient-to-b from-primary/5 via-muted/10 to-transparent" />
        <div className="absolute inset-0 bg-grid-pattern opacity-[0.2]" />
        
        {/* Floating Orbs */}
        <motion.div
          animate={{
            scale: [1, 1.3, 1],
            opacity: [0.2, 0.4, 0.2],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          className="absolute -top-20 -right-20 w-72 h-72 bg-primary/10 rounded-full blur-3xl"
        />
        <motion.div
          animate={{
            scale: [1.3, 1, 1.3],
            opacity: [0.15, 0.3, 0.15],
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          className="absolute top-1/2 -left-20 w-60 h-60 bg-chart-3/10 rounded-full blur-3xl"
        />
      </div>

      <div className="text-center max-w-3xl mx-auto">
        {/* Animated 404 */}
        <motion.div
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="relative mb-12"
        >
          {/* Glitch Effect Layers */}
          <motion.h1
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="text-[12rem] md:text-[16rem] font-black leading-none tracking-tighter text-transparent bg-clip-text bg-gradient-to-b from-primary/30 via-primary/10 to-transparent select-none"
          >
            404
          </motion.h1>
          
          {/* Shield Icon Overlay */}
          <motion.div
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ 
              type: "spring", 
              stiffness: 260, 
              damping: 20,
              delay: 0.4 
            }}
            className="absolute inset-0 flex items-center justify-center"
          >
            <div className="relative">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                className="absolute inset-0 -m-4 rounded-full border-2 border-dashed border-primary/20"
              />
              <div className="relative bg-primary/10 p-6 rounded-full backdrop-blur-sm border border-primary/20">
                <Shield className="h-16 w-16 md:h-20 md:w-20 text-primary" />
              </div>
            </div>
          </motion.div>
        </motion.div>

        {/* Alert Badge */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.6 }}
          className="inline-flex items-center gap-2 px-4 py-2 bg-destructive/10 border border-destructive/20 rounded-full mb-6"
        >
          <AlertTriangle className="h-4 w-4 text-destructive" />
          <span className="text-sm font-medium text-destructive">System Alert</span>
        </motion.div>

        {/* Message */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-4 tracking-tight">
            Page Not Found
          </h2>
          <p className="text-muted-foreground text-lg md:text-xl mb-10 max-w-lg mx-auto leading-relaxed">
            The page you're looking for doesn't exist or has been moved. 
            Let's get you back to safety.
          </p>
        </motion.div>

        {/* Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="flex gap-4 justify-center flex-wrap"
        >
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Button asChild size="lg" className="group">
              <Link href="/">
                <Home className="h-4 w-4 mr-2 group-hover:-translate-y-0.5 transition-transform" />
                Back to Home
              </Link>
            </Button>
          </motion.div>
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Button asChild variant="outline" size="lg" className="group">
              <Link href="/analytics">
                <Search className="h-4 w-4 mr-2 group-hover:rotate-12 transition-transform" />
                View Analytics
              </Link>
            </Button>
          </motion.div>
        </motion.div>

        {/* Quick Links */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
          className="mt-12 pt-8 border-t border-border/50"
        >
          <p className="text-sm text-muted-foreground mb-4">Quick navigation</p>
          <div className="flex gap-6 justify-center flex-wrap">
            {[
              { label: "Schemes", href: "/schemes" },
              { label: "Admin", href: "/admin/dashboard" },
              { label: "Contact", href: "/contact" },
            ].map((link) => (
              <motion.div key={link.href} whileHover={{ y: -2 }}>
                <Link
                  href={link.href}
                  className="text-sm text-muted-foreground hover:text-primary transition-colors flex items-center gap-1"
                >
                  {link.label}
                  <ArrowLeft className="h-3 w-3 rotate-180" />
                </Link>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
