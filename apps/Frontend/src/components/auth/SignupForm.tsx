"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { Loader2, ArrowRight, Check, X, User, Mail } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { PasswordInput } from "@/components/auth/PasswordInput";
import { SocialButton } from "@/components/auth/SocialButton";
import { Divider } from "@/components/auth/Divider";
import { useSignup } from "@/hooks/use-signup";
import { getPasswordStrength } from "@/lib/validations/auth";
import { cn } from "@/lib/utils";

// ─── Animation variants ──────────────────────────────────────────────────────
const formItemVariants = {
  hidden: { opacity: 0, y: 12 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: 0.15 + i * 0.07, duration: 0.4, ease: "easeOut" as const },
  }),
};

// ─── Password Requirements ───────────────────────────────────────────────────
const passwordRequirements = [
  { label: "At least 8 characters", regex: /.{8,}/ },
  { label: "One uppercase letter", regex: /[A-Z]/ },
  { label: "One lowercase letter", regex: /[a-z]/ },
  { label: "One number", regex: /[0-9]/ },
  { label: "One special character", regex: /[^A-Za-z0-9]/ },
];

function PasswordStrengthIndicator({ password }: { password: string }) {
  const strength = getPasswordStrength(password);

  if (!password) return null;

  return (
    <motion.div
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: "auto" }}
      exit={{ opacity: 0, height: 0 }}
      className="space-y-3"
    >
      {/* Strength bar */}
      <div className="space-y-1.5">
        <div className="flex items-center justify-between">
          <span className="text-xs text-muted-foreground">
            Password strength
          </span>
          <span
            className={cn(
              "text-xs font-medium",
              strength.score <= 1 && "text-red-500",
              strength.score === 2 && "text-yellow-500",
              strength.score === 3 && "text-blue-500",
              strength.score >= 4 && "text-emerald-500"
            )}
          >
            {strength.label}
          </span>
        </div>
        <div className="flex gap-1">
          {Array.from({ length: 5 }).map((_, i) => (
            <motion.div
              key={i}
              className={cn(
                "h-1.5 flex-1 rounded-full transition-colors duration-300",
                i < strength.score ? strength.color : "bg-muted"
              )}
              initial={{ scaleX: 0 }}
              animate={{ scaleX: 1 }}
              transition={{ delay: i * 0.05, duration: 0.3 }}
            />
          ))}
        </div>
      </div>

      {/* Requirement checklist */}
      <ul className="grid grid-cols-1 gap-1 sm:grid-cols-2" aria-label="Password requirements">
        {passwordRequirements.map((req) => {
          const met = req.regex.test(password);
          return (
            <li
              key={req.label}
              className={cn(
                "flex items-center gap-1.5 text-xs transition-colors",
                met ? "text-emerald-600 dark:text-emerald-400" : "text-muted-foreground"
              )}
            >
              {met ? (
                <Check className="h-3 w-3 shrink-0" />
              ) : (
                <X className="h-3 w-3 shrink-0" />
              )}
              {req.label}
            </li>
          );
        })}
      </ul>
    </motion.div>
  );
}

export function SignupForm() {
  const { form, isLoading, onSubmit, handleSocialLogin } = useSignup();

  const {
    register,
    formState: { errors },
    setValue,
    watch,
  } = form;

  const password = watch("password");
  const acceptTerms = watch("acceptTerms");

  return (
    <form onSubmit={onSubmit} className="flex flex-col gap-5" noValidate>
      {/* ── Social buttons ──────────────────────────────────────── */}
      <motion.div
        variants={formItemVariants}
        initial="hidden"
        animate="visible"
        custom={0}
        className="grid grid-cols-2 gap-3 w-full"
      >
        <SocialButton
          provider="google"
          onClick={() => handleSocialLogin("google")}
          disabled={isLoading}
        />
        <SocialButton
          provider="github"
          onClick={() => handleSocialLogin("github")}
          disabled={isLoading}
        />
      </motion.div>

      <Divider text="or continue with email" />

      {/* ── Full Name field ─────────────────────────────────────── */}
      <motion.div
        variants={formItemVariants}
        initial="hidden"
        animate="visible"
        custom={1}
        className="space-y-2"
      >
        <Label htmlFor="signup-fullname">Full Name</Label>
        <div className="relative flex items-center">
          <User className="absolute left-3.5 h-4 w-4 text-muted-foreground/70 pointer-events-none" />
          <Input
            id="signup-fullname"
            type="text"
            placeholder="John Doe"
            autoComplete="name"
            aria-invalid={!!errors.fullName}
            aria-describedby={errors.fullName ? "signup-fullname-error" : undefined}
            className="h-11 rounded-xl pl-10 bg-white/[0.03] border-white/10 text-white placeholder:text-muted-foreground/50 focus-visible:border-[#8b5cf6]/80 focus-visible:ring-1 focus-visible:ring-[#8b5cf6]/80 focus:bg-[#111116] transition-all"
            {...register("fullName")}
          />
        </div>
        {errors.fullName && (
          <p
            id="signup-fullname-error"
            className="text-sm text-destructive"
            role="alert"
          >
            {errors.fullName.message}
          </p>
        )}
      </motion.div>

      {/* ── Email field ─────────────────────────────────────────── */}
      <motion.div
        variants={formItemVariants}
        initial="hidden"
        animate="visible"
        custom={2}
        className="space-y-2"
      >
        <Label htmlFor="signup-email">Email</Label>
        <div className="relative flex items-center">
          <Mail className="absolute left-3.5 h-4 w-4 text-muted-foreground/70 pointer-events-none" />
          <Input
            id="signup-email"
            type="email"
            placeholder="you@example.com"
            autoComplete="email"
            aria-invalid={!!errors.email}
            aria-describedby={errors.email ? "signup-email-error" : undefined}
            className="h-11 rounded-xl pl-10 bg-white/[0.03] border-white/10 text-white placeholder:text-muted-foreground/50 focus-visible:border-[#8b5cf6]/80 focus-visible:ring-1 focus-visible:ring-[#8b5cf6]/80 focus:bg-[#111116] transition-all"
            {...register("email")}
          />
        </div>
        {errors.email && (
          <p
            id="signup-email-error"
            className="text-sm text-destructive"
            role="alert"
          >
            {errors.email.message}
          </p>
        )}
      </motion.div>

      {/* ── Password field ──────────────────────────────────────── */}
      <motion.div
        variants={formItemVariants}
        initial="hidden"
        animate="visible"
        custom={3}
        className="space-y-2"
      >
        <Label htmlFor="signup-password">Password</Label>
        <PasswordInput
          id="signup-password"
          placeholder="Create a strong password"
          autoComplete="new-password"
          error={errors.password?.message}
          className="h-11 rounded-xl bg-white/[0.03] border-white/10 text-white placeholder:text-muted-foreground/50 focus-visible:border-[#8b5cf6]/80 focus-visible:ring-1 focus-visible:ring-[#8b5cf6]/80 focus:bg-[#111116] transition-all"
          {...register("password")}
        />
        {errors.password && (
          <p
            id="signup-password-error"
            className="text-sm text-destructive"
            role="alert"
          >
            {errors.password.message}
          </p>
        )}

        {/* Password strength indicator */}
        <PasswordStrengthIndicator password={password || ""} />
      </motion.div>

      {/* ── Confirm Password field ──────────────────────────────── */}
      <motion.div
        variants={formItemVariants}
        initial="hidden"
        animate="visible"
        custom={4}
        className="space-y-2"
      >
        <Label htmlFor="signup-confirm-password">Confirm Password</Label>
        <PasswordInput
          id="signup-confirm-password"
          placeholder="Re-enter your password"
          autoComplete="new-password"
          error={errors.confirmPassword?.message}
          className="h-11 rounded-xl bg-white/[0.03] border-white/10 text-white placeholder:text-muted-foreground/50 focus-visible:border-[#8b5cf6]/80 focus-visible:ring-1 focus-visible:ring-[#8b5cf6]/80 focus:bg-[#111116] transition-all"
          {...register("confirmPassword")}
        />
        {errors.confirmPassword && (
          <p
            id="signup-confirm-password-error"
            className="text-sm text-destructive"
            role="alert"
          >
            {errors.confirmPassword.message}
          </p>
        )}
      </motion.div>

      {/* ── Terms checkbox ──────────────────────────────────────── */}
      <motion.div
        variants={formItemVariants}
        initial="hidden"
        animate="visible"
        custom={5}
        className="space-y-2"
      >
        <div className="flex items-start gap-2">
          <Checkbox
            id="signup-terms"
            checked={acceptTerms}
            onCheckedChange={(checked) =>
              setValue("acceptTerms", checked === true, { shouldValidate: true })
            }
            aria-label="Accept terms and conditions"
            className="mt-0.5"
          />
          <Label
            htmlFor="signup-terms"
            className="text-sm font-normal leading-relaxed text-muted-foreground cursor-pointer"
          >
            I agree to the{" "}
            <Link
              href="/terms"
              className="font-medium text-primary hover:text-[#8b5cf6] underline underline-offset-4 transition-colors"
            >
              Terms of Service
            </Link>{" "}
            and{" "}
            <Link
              href="/privacy"
              className="font-medium text-primary hover:text-[#8b5cf6] underline underline-offset-4 transition-colors"
            >
              Privacy Policy
            </Link>
          </Label>
        </div>
        {errors.acceptTerms && (
          <p
            id="signup-terms-error"
            className="text-sm text-destructive"
            role="alert"
          >
            {errors.acceptTerms.message}
          </p>
        )}
      </motion.div>

      {/* ── Submit button ───────────────────────────────────────── */}
      <motion.div
        variants={formItemVariants}
        initial="hidden"
        animate="visible"
        custom={6}
      >
        <Button
          type="submit"
          disabled={isLoading}
          className="h-11 w-full rounded-xl bg-primary font-semibold text-white shadow-[0_0_20px_rgba(115,51,210,0.3)] transition-all hover:bg-[#8b5cf6] hover:shadow-[0_0_25px_rgba(139,92,246,0.5)] focus-visible:ring-primary/50 disabled:opacity-70 cursor-pointer"
        >
          {isLoading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Creating account...
            </>
          ) : (
            <>
              Create Account
              <ArrowRight className="h-4 w-4" />
            </>
          )}
        </Button>
      </motion.div>

      {/* ── Footer link ─────────────────────────────────────────── */}
      <motion.p
        variants={formItemVariants}
        initial="hidden"
        animate="visible"
        custom={7}
        className="text-center text-sm text-muted-foreground"
      >
        Already have an account?{" "}
        <Link
          href="/auth/login"
          className="font-semibold text-primary hover:text-[#8b5cf6] transition-colors"
        >
          Sign in
        </Link>
      </motion.p>
    </form>
  );
}
