import { ShieldCheck, Star } from "lucide-react"

import { getPlanPrice } from "@/components/pricing/pricing-data"

import BillingSelector from "./BillingSelector"
import { checkoutFeaturesByPlan, guaranteeFeature } from "@/constants"
import type { BillingCycle, PricingPlan } from "./checkout-types"
import PlanFeatures from "./PlanFeatures"

type CheckoutPlanCardProps = {
  billingCycle: BillingCycle
  onBillingCycleChange: (billingCycle: BillingCycle) => void
  plan: PricingPlan
}

const CheckoutPlanCard = ({
  billingCycle,
  onBillingCycleChange,
  plan,
}: CheckoutPlanCardProps) => {
  const { period, price } = getPlanPrice(plan.monthlyPrice, billingCycle)
  const features = checkoutFeaturesByPlan[plan.id]

  return (
    <section className="relative overflow-hidden rounded-[18px] border border-primary/80 bg-white/2.5 p-5 shadow-[0_0_50px_rgba(115,51,210,0.24)] sm:p-6">
      <div
        aria-hidden="true"
        className="absolute -left-12 top-16 size-48 rounded-full bg-primary/20 blur-[90px]"
      />
      <div
        aria-hidden="true"
        className="absolute -right-12 bottom-20 size-48 rounded-full bg-secondary/10 blur-[90px]"
      />

      <div className="relative z-10 flex flex-col gap-6">
        <div className="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
          <div className="flex gap-5">
            <div className="flex size-16 shrink-0 items-center justify-center rounded-sm bg-white/6 text-[#b65cff] shadow-[0_0_28px_rgba(115,51,210,0.18)]">
              <Star className="size-9 fill-current" aria-hidden="true" />
            </div>
            <div>
              <h2 className="text-[25px]! font-extrabold leading-tight text-text-primary">
                {plan.name} Plan
              </h2>
              <p className="mt-3 max-w-87.5 text-[14px]! leading-6 text-text-secondary">
                {plan.description}
              </p>
            </div>
          </div>

          <div className="min-w-0 sm:text-right">
            <div className="wrap-break-word text-[34px] font-extrabold leading-none text-text-primary sm:text-[38px]">
              {price}
            </div>
            {period ? (
              <div className="mt-2 text-[14px] text-text-primary">{period}</div>
            ) : null}
            <div className="mt-3 text-[13px] text-text-secondary">
              Billed {billingCycle === "yearly" ? "yearly" : "monthly"}
            </div>
          </div>
        </div>

        <BillingSelector
          billingCycle={billingCycle}
          onBillingCycleChange={onBillingCycleChange}
        />

        <div className="h-px bg-white/10" />

        <div className="flex flex-col gap-5">
          <h2 className="text-[21px]! font-extrabold text-text-primary">
            Everything in {plan.name}
          </h2>
          <PlanFeatures features={features} />
        </div>

        <div className="flex gap-4 rounded-[14px] border border-white/10 bg-white/2.5 p-4">
          <ShieldCheck
            aria-hidden="true"
            className="mt-0.5 size-7 shrink-0 text-[#c56cff]"
          />
          <div>
            <h3 className="text-[17px]! font-extrabold text-text-primary">
              {guaranteeFeature.title}
            </h3>
            <p className="mt-1 text-[14px]! text-text-secondary">
              {guaranteeFeature.description}
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}

export default CheckoutPlanCard
