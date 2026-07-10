"use client";

import { Toaster } from "sonner";
import { Sparkles } from "lucide-react";
import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";

interface AuthLayoutProps {
  children: React.ReactNode;
}

export function AuthLayout({ children }: AuthLayoutProps) {
  const pathname = usePathname();
  const isLogin = pathname === "/auth/login";

  return (
    <>
      <Toaster
        position="top-center"
        toastOptions={{
          style: {
            background: "hsl(var(--card))",
            border: "1px solid hsl(var(--border))",
            color: "hsl(var(--foreground))",
          },
        }}
      />

      <div className="flex min-h-svh w-full bg-black text-white relative overflow-hidden">
        {/* Glow effects */}
        <div className="absolute top-[-25%] left-[-30%] w-[70vw] max-w-[1300px] h-[600px] bg-primary/20 blur-[210px] rounded-full z-0 pointer-events-none"></div>
        <div className="absolute bottom-[-35%] right-[-45%] w-[70vw] max-w-[1300px] h-[600px] bg-primary/15 blur-[210px] rounded-full z-0 pointer-events-none"></div>

        {/* ── Left Side (Branding) ─────────────────────────────────── */}
        <div className="relative z-10 hidden w-1/2 lg:flex flex-col justify-between p-12 bg-white/[0.01] backdrop-blur-xs">
          <div>
            <Link
              href="/"
              className="flex items-center transition-opacity hover:opacity-80 w-fit"
              aria-label="Go to homepage"
            >
              <Image
                src="/icons/logo.svg"
                alt="Learner Logo"
                width={130}
                height={33.39}
                priority
              />
            </Link>
          </div>

          <div className="flex flex-col gap-6 max-w-md">
            <div className="w-fit rounded-full bg-white/[0.04] px-3 py-1 border border-white/10 flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-primary" />
              <span className="text-xs font-semibold tracking-wider text-muted-foreground uppercase">
                {isLogin ? "Welcome Back" : "Join Learner"}
              </span>
            </div>

            <h1 className="text-5xl font-bold tracking-tight leading-[1.15]">
              {isLogin ? "Continue your" : "Start your"}{" "}
              <span className="text-primary block mt-2">
                learning journey
              </span>
            </h1>

            <p className="text-lg text-muted-foreground leading-relaxed">
              {isLogin
                ? "Sign in to access your personalized AI study materials, continue from where you left off, and master your subjects faster."
                : "Create an account to unlock AI-powered study tools, personalized flashcards, and comprehensive progress tracking."}
            </p>
          </div>
          
          <div className="text-sm text-muted-foreground">
            © {new Date().getFullYear()} Learner. All rights reserved.
          </div>
        </div>

        {/* ── Right Side (Auth Form) ───────────────────────────────── */}
        <div className="relative z-10 flex w-full lg:w-1/2 flex-col items-center justify-center p-6 sm:p-12">
          {/* Radial glow background effect */}
          <div className="pointer-events-none absolute inset-0 flex items-center justify-center overflow-hidden" aria-hidden="true">
            <div className="h-[400px] w-[400px] lg:h-[600px] lg:w-[600px] rounded-full bg-primary/10 blur-[100px]" />
          </div>

          {/* Form Card Container */}
          <div className="relative z-10 w-full max-w-[440px]">
            {/* Mobile branding (visible only on small screens) */}
            <div className="mb-8 flex lg:hidden items-center justify-center">
              <Link
                href="/"
                className="flex items-center transition-opacity hover:opacity-80"
                aria-label="Go to homepage"
              >
                <Image
                  src="/icons/logo.svg"
                  alt="Learner Logo"
                  width={130}
                  height={33.39}
                  priority
                />
              </Link>
            </div>

            {/* The form card itself */}
            <div className="rounded-2xl border border-[#666565]/40 bg-[#111116]/85 backdrop-blur-md p-8 shadow-[0_0_50px_-12px_rgba(115,51,210,0.25)] relative overflow-hidden">
              {children}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
