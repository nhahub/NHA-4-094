import {
  getPlanPriceValue,
  pricingPlans,
  type BillingCycle,
  type PricingPlan as BasePricingPlan,
} from "@/components/pricing/pricing-data"

import type {
  CheckoutPlanId,
  OrderSummary,
  PricingPlan,
} from "./checkout-types"

const DEFAULT_PLAN_ID: CheckoutPlanId = "pro"
const DEFAULT_BILLING_CYCLE: BillingCycle = "monthly"

const isCheckoutPlanId = (
  value: string | undefined,
): value is CheckoutPlanId => value === "pro" || value === "premium"

const isBillingCycle = (
  value: string | undefined,
): value is BillingCycle => value === "monthly" || value === "yearly"

const isCheckoutPlan = (plan: BasePricingPlan): plan is PricingPlan =>
  isCheckoutPlanId(plan.id)

const checkoutPlans = pricingPlans.filter(isCheckoutPlan)

export const getCheckoutPlan = (planId: CheckoutPlanId): PricingPlan =>
  checkoutPlans.find((plan) => plan.id === planId) ?? getDefaultCheckoutPlan()

const getDefaultCheckoutPlan = (): PricingPlan => {
  const defaultPlan = checkoutPlans.find((plan) => plan.id === DEFAULT_PLAN_ID)

  if (!defaultPlan) {
    throw new Error("Default checkout plan is missing.")
  }

  return defaultPlan
}

// Reads selected plan and billing cycle from the checkout URL.
export const getInitialCheckoutState = (searchParams?: {
  billing?: string | string[]
  plan?: string | string[]
}) => {
  const planParam = Array.isArray(searchParams?.plan)
    ? searchParams?.plan[0]
    : searchParams?.plan
  const billingParam = Array.isArray(searchParams?.billing)
    ? searchParams?.billing[0]
    : searchParams?.billing

  const hasValidCheckoutState =
    isCheckoutPlanId(planParam) && isBillingCycle(billingParam)
  const planId = hasValidCheckoutState ? planParam : DEFAULT_PLAN_ID
  const billingCycle = hasValidCheckoutState
    ? billingParam
    : DEFAULT_BILLING_CYCLE

  return {
    billingCycle,
    plan: getCheckoutPlan(planId),
  }
}

// Renders the final order summary based on the selected plan.
export const getOrderSummary = (
  plan: PricingPlan,
  billingCycle: BillingCycle,
): OrderSummary => {
  const subtotal = getPlanPriceValue(plan.monthlyPrice, billingCycle)
  const tax = 0

  return {
    billingCycle,
    plan,
    subtotal,
    tax,
    total: subtotal + tax,
  }
}

export const formatEgp = (value: number) => `${value} EGP`

export const getBillingLabel = (billingCycle: BillingCycle) =>
  billingCycle === "yearly" ? "Yearly" : "Monthly"
