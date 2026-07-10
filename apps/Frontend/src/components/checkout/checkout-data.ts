import {
  BarChart3,
  Brain,
  Clock,
  CreditCard,
  FileText,
  HelpCircle,
  Layers,
  MessageCircle,
  Network,
  NotebookTabs,
  Sparkles,
  Users,
  Zap,
  type LucideIcon,
} from "lucide-react"

import type {
  CheckoutFeature,
  CheckoutPlanId,
  PaymentMethod,
} from "./checkout-types"

export type CheckoutFeatureItem = CheckoutFeature & {
  icon: LucideIcon
}

export type PaymentMethodOption = {
  icon: LucideIcon
  label: string
  value: PaymentMethod
}

export const paymentMethods: PaymentMethodOption[] = [
  { icon: CreditCard, label: "Card", value: "card" },
  { icon: Zap, label: "PayPal", value: "paypal" },
]

// Features shown for the selected checkout plan.
export const checkoutFeaturesByPlan: Record<CheckoutPlanId, CheckoutFeatureItem[]> = {
  pro: [
    {
      description: "Upload and analyze more documents.",
      icon: FileText,
      title: "50 Documents",
    },
    {
      description: "Get deeper, more accurate summaries.",
      icon: NotebookTabs,
      title: "Unlimited Summaries",
    },
    {
      description: "Generate quizzes in seconds.",
      icon: HelpCircle,
      title: "Unlimited Quizzes",
    },
    {
      description: "Organize your study schedule.",
      icon: Layers,
      title: "Study Plans",
    },
    {
      description: "Turn notes into review cards.",
      icon: Sparkles,
      title: "Flashcards Generation",
    },
    {
      description: "Use stronger AI for complex topics.",
      icon: Brain,
      title: "Advanced AI Models",
    },
  ],
  premium: [
    {
      description: "Study without document limits.",
      icon: FileText,
      title: "Unlimited Documents",
    },
    {
      description: "Ask AI freely under fair use.",
      icon: MessageCircle,
      title: "Unlimited AI Usage",
    },
    {
      description: "Handle difficult reasoning tasks.",
      icon: Brain,
      title: "Deep Reasoning Models",
    },
    {
      description: "Collaborate with classmates.",
      icon: Users,
      title: "Study Rooms",
    },
    {
      description: "Track progress and study patterns.",
      icon: BarChart3,
      title: "Learning Analytics",
    },
    {
      description: "Get faster processing when it matters.",
      icon: Clock,
      title: "Priority Processing",
    },
  ],
}

export const trustItems = [
  "Secure payments",
  "Cancel anytime",
  "30-day money-back guarantee",
]

export const guaranteeFeature = {
  description: "Try Learner risk-free. Cancel anytime.",
  icon: Network,
  title: "30-day money-back guarantee",
}
