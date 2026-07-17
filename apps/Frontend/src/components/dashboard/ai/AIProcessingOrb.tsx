import React, { useEffect, useState } from "react";

interface AIProcessingOrbProps {
  status?: string | null;
}

export const AIProcessingOrb: React.FC<AIProcessingOrbProps> = ({ status }) => {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    setPrefersReducedMotion(mediaQuery.matches);

    const handler = (e: MediaQueryListEvent) => setPrefersReducedMotion(e.matches);
    mediaQuery.addEventListener("change", handler);
    return () => mediaQuery.removeEventListener("change", handler);
  }, []);

  const isFailed = status === "failed";
  const isCancelled = status === "cancelled";

  return (
    <div className="relative flex items-center justify-center w-7 h-7 select-none">
      {/* Glow Effect */}
      <div 
        className={`absolute inset-0 rounded-full blur-sm opacity-20 transition-colors duration-500 ${
          isFailed ? "bg-red-500" : isCancelled ? "bg-zinc-500" : "bg-purple-500"
        }`}
      />

      {/* Outer Orbital Ring */}
      <div
        className={`absolute w-6 h-6 rounded-full border border-dashed transition-all duration-750 ${
          isFailed ? "border-red-500/30" : isCancelled ? "border-zinc-500/30" : "border-purple-500/30"
        } ${prefersReducedMotion ? "" : "animate-[spin_8s_linear_infinite]"}`}
        style={{
          animationDirection: prefersReducedMotion ? undefined : "normal",
        }}
      />

      {/* Inner Orbital Ring */}
      <div
        className={`absolute w-4.5 h-4.5 rounded-full border border-double transition-all duration-750 ${
          isFailed ? "border-red-500/40" : isCancelled ? "border-zinc-500/40" : "border-purple-500/40"
        } ${prefersReducedMotion ? "" : "animate-[spin_4s_linear_infinite]"}`}
        style={{
          animationDirection: prefersReducedMotion ? undefined : "reverse",
        }}
      />

      {/* Center ✦ Symbol */}
      <span
        className={`text-xs font-bold select-none z-10 transition-colors duration-500 opacity-95 ${
          isFailed ? "text-red-400" : isCancelled ? "text-zinc-400" : "text-purple-400"
        } ${prefersReducedMotion ? "" : "animate-pulse"}`}
      >
        ✦
      </span>
    </div>
  );
};
