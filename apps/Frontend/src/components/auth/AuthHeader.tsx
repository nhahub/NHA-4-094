"use client";

import { Sparkles } from "lucide-react";
import Link from "next/link";
import { motion } from "framer-motion";

interface AuthHeaderProps {
  title: string;
  description: string;
}

export function AuthHeader({ title, description }: AuthHeaderProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.1 }}
      className="flex flex-col items-center gap-2 text-center"
    >
      {/* Logo */}
      <Link
        href="/"
        className="mb-2 flex items-center gap-2 transition-opacity hover:opacity-80"
        aria-label="Go to homepage"
      >
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-purple-600 to-pink-500 shadow-lg shadow-purple-500/25">
          <Sparkles className="h-5 w-5 text-white" />
        </div>
        <span className="text-xl font-bold tracking-tight text-foreground">
          Learner<span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-500">.ai</span>
        </span>
      </Link>

      {/* Heading */}
      <h1 className="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">
        {title}
      </h1>
      <p className="text-sm text-muted-foreground max-w-xs">
        {description}
      </p>
    </motion.div>
  );
}
