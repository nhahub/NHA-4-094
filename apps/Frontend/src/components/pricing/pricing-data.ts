import type { LucideIcon } from "lucide-react"
import { BadgeCheck, CreditCard, ShieldCheck } from "lucide-react"

export type PlanId = "free" | "pro" | "premium"
export type PlanName = "Free" | "Pro" | "Premium"

export type PricingPlan = {
  id: PlanId
  name: PlanName
  monthlyPrice: number
  description: string
  features: string[]
  cta: string
  featured?: boolean
}

export type ComparisonRow = {
  feature: string
  values: Record<PlanName, string | boolean>
}

export type PricingFAQ = {
  question: string
  answer: string
}

export type TrustItem = {
  label: string
  icon: LucideIcon
}

export type BillingOption = {
  value: "monthly" | "yearly"
  label: string
  note?: string
}

// Controls whether prices are shown monthly or yearly.
export type BillingCycle = BillingOption["value"]

export const billingOptions: BillingOption[] = [
  { value: "monthly", label: "Monthly" },
  { value: "yearly", label: "Yearly", note: "Save 20%" },
]

// Store base monthly prices; yearly prices are calculated in the card.
export const pricingPlans: PricingPlan[] = [
  {
    id: "free",
    name: "Free",
    monthlyPrice: 0,
    description: "Get started with basic AI study features.",
    cta: "Get Started",
    features: [
      "3 Documents",
      "20 AI Messages / Day",
      "3 Summaries / Day",
      "2 Quizzes / Day",
      "Basic AI Model",
    ],
  },
  {
    id: "pro",
    name: "Pro",
    monthlyPrice: 149,
    description: "Perfect for most students.",
    cta: "Upgrade Now",
    featured: true,
    features: [
      "50 Documents",
      "Unlimited Summaries",
      "Unlimited Quizzes",
      "Study Plans",
      "Flashcards Generation",
      "Advanced AI Models",
    ],
  },
  {
    id: "premium",
    name: "Premium",
    monthlyPrice: 299,
    description: "For power users and heavy learners.",
    cta: "Upgrade Now",
    features: [
      "Unlimited Documents",
      "Unlimited AI Usage (Fair Use)",
      "Deep Reasoning Models",
      "Study Rooms",
      "Learning Analytics",
      "Priority Processing",
    ],
  },
]

// Calculates yearly pricing with a 20% discount.
export const getPlanPriceValue = (
  monthlyPrice: number,
  billingCycle: BillingCycle,
) => {
  if (monthlyPrice === 0) {
    return 0
  }

  return billingCycle === "yearly"
    ? Math.round(monthlyPrice * 12 * 0.8)
    : monthlyPrice
}

export const getPlanPrice = (
  monthlyPrice: number,
  billingCycle: BillingCycle,
) => {
  const priceValue = getPlanPriceValue(monthlyPrice, billingCycle)

  return {
    period: priceValue === 0 ? undefined : `/${billingCycle === "yearly" ? "year" : "month"}`,
    price: `${priceValue} EGP`,
    priceValue,
  }
}

export const getCheckoutHref = (
  plan: PricingPlan,
  billingCycle: BillingCycle,
) => `/checkout?plan=${plan.id}&billing=${billingCycle}`

export const comparisonRows: ComparisonRow[] = [
  {
    feature: "Documents",
    values: {
      Free: "3 Documents",
      Pro: "50 Documents",
      Premium: "Unlimited Documents",
    },
  },
  {
    feature: "AI Messages",
    values: {
      Free: "20 / Day",
      Pro: "Unlimited",
      Premium: "Unlimited AI Usage (Fair Use)",
    },
  },
  {
    feature: "Summaries",
    values: {
      Free: "3 / Day",
      Pro: "Unlimited",
      Premium: "Unlimited",
    },
  },
  {
    feature: "Quizzes",
    values: {
      Free: "2 / Day",
      Pro: "Unlimited",
      Premium: "Unlimited",
    },
  },
  {
    feature: "AI Model",
    values: {
      Free: "Basic AI Model",
      Pro: "Advanced AI Models",
      Premium: "Deep Reasoning Models",
    },
  },
  {
    feature: "Study Plans",
    values: {
      Free: false,
      Pro: true,
      Premium: true,
    },
  },
  {
    feature: "Flashcards",
    values: {
      Free: false,
      Pro: true,
      Premium: true,
    },
  },
  {
    feature: "Study Rooms",
    values: {
      Free: false,
      Pro: false,
      Premium: true,
    },
  },
  {
    feature: "Learning Analytics",
    values: {
      Free: false,
      Pro: false,
      Premium: true,
    },
  },
  {
    feature: "Priority Processing",
    values: {
      Free: false,
      Pro: false,
      Premium: true,
    },
  },
]

export const pricingFaqs: PricingFAQ[] = [
  {
    question: "Can I start for free?",
    answer:
      "Yes. You can start with the Free plan and upgrade whenever you need more documents, summaries, quizzes, or advanced AI features.",
  },
  {
    question: "Can I cancel my subscription anytime?",
    answer:
      "Yes. You can cancel, upgrade, or downgrade from your billing settings whenever you need to.",
  },
  {
    question: "What is the difference between Pro and Premium?",
    answer:
      "Pro is built for most students with generous AI study limits. Premium adds fair-use unlimited AI, deeper models, study rooms, analytics, and priority processing.",
  },
  {
    question: "Is my payment secure?",
    answer:
      "Payments are processed through secure billing infrastructure. Learner does not store your full card details.",
  },
  {
    question: "Do I get a money-back guarantee?",
    answer:
      "Yes. Paid plans include a 30-day money-back guarantee if Learner is not the right fit for your study workflow.",
  },
  {
    question: "What does Fair Use mean in Premium?",
    answer:
      "Fair Use keeps Premium fast and reliable for every learner while still supporting heavy study sessions and advanced AI workflows.",
  },
]

export const trustItems: TrustItem[] = [
  { label: "Secure payments", icon: CreditCard },
  { label: "Cancel anytime", icon: BadgeCheck },
  { label: "30-day money-back guarantee", icon: ShieldCheck },
]
