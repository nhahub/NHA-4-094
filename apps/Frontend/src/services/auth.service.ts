import { createClient } from "@/lib/supabase/client";

// ─── Types ───────────────────────────────────────────────────────────────────
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface SignupCredentials {
  fullName: string;
  email: string;
  password: string;
}

export interface AuthResponse {
  success: boolean;
  message: string;
  data?: unknown;
}

// ─── Auth Service ────────────────────────────────────────────────────────────
export const authService = {
  /**
   * Sign in with email and password
   */
  async login({ email, password }: LoginCredentials): Promise<AuthResponse> {
    const supabase = createClient();

    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    if (error) {
      return {
        success: false,
        message: error.message,
      };
    }

    return {
      success: true,
      message: "Logged in successfully!",
      data: data.user,
    };
  },

  /**
   * Create a new account with email and password.
   * The full name is stored in auth.users.raw_user_meta_data as "full_name".
   */
  async signup({
    fullName,
    email,
    password,
  }: SignupCredentials): Promise<AuthResponse> {
    const supabase = createClient();

    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: {
          full_name: fullName,
        },
      },
    });

    if (error) {
      return {
        success: false,
        message: error.message,
      };
    }

    // Supabase may return a user with a fake session if email confirmation
    // is enabled but the user already exists. Detect this edge-case.
    if (data.user?.identities?.length === 0) {
      return {
        success: false,
        message: "An account with this email already exists.",
      };
    }

    return {
      success: true,
      message:
        "Account created successfully! Please check your email to verify your account.",
      data: data.user,
    };
  },

  /**
   * Sign in with a third-party OAuth provider (Google or GitHub).
   * Redirects the user to the provider's consent screen.
   */
  async socialLogin(provider: "google" | "github"): Promise<AuthResponse> {
    const supabase = createClient();

    const { error } = await supabase.auth.signInWithOAuth({
      provider,
      options: {
        redirectTo: `${window.location.origin}/auth/callback`,
      },
    });

    if (error) {
      return {
        success: false,
        message: error.message,
      };
    }

    return {
      success: true,
      message: "Redirecting...",
    };
  },

  /**
   * Send a password reset email
   */
  async forgotPassword(email: string): Promise<AuthResponse> {
    const supabase = createClient();

    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/auth/reset-password`,
    });

    if (error) {
      return {
        success: false,
        message: error.message,
      };
    }

    return {
      success: true,
      message: "Password reset email sent! Check your inbox.",
    };
  },

  /**
   * Sign out the current user
   */
  async logout(): Promise<AuthResponse> {
    const supabase = createClient();

    const { error } = await supabase.auth.signOut();

    if (error) {
      return {
        success: false,
        message: error.message,
      };
    }

    return {
      success: true,
      message: "Logged out successfully.",
    };
  },
};
