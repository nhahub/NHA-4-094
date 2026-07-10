import type {
  BillingCycle,
  PlanId,
  PricingPlan as BasePricingPlan,
} from "@/components/pricing/pricing-data"

export type CheckoutPlanId = Exclude<PlanId, "free">
export type PricingPlan = BasePricingPlan & { id: CheckoutPlanId }

export type { BillingCycle, PlanId }

export type PaymentMethod = "card" | "paypal"

export type CheckoutFeature = {
  title: string
  description: string
}

export type OrderSummary = {
  billingCycle: BillingCycle
  plan: PricingPlan
  subtotal: number
  tax: number
  total: number
}
