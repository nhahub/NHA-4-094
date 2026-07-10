import { Info, LockKeyhole } from "lucide-react"

import { Button } from "@/components/ui/button"

import {
  formatEgp,
  getBillingLabel,
  getOrderSummary,
} from "./checkout-utils"
import type { BillingCycle, PricingPlan } from "./checkout-types"

type OrderSummaryProps = {
  billingCycle: BillingCycle
  plan: PricingPlan
}

const OrderSummary = ({ billingCycle, plan }: OrderSummaryProps) => {
  // Updates the checkout total when the billing interval changes.
  const summary = getOrderSummary(plan, billingCycle)

  return (
    <section className="rounded-[18px] border border-white/10 bg-white/2.5 p-5 sm:p-6">
      <h2 className="text-[21px]! font-extrabold text-text-primary">
        Order summary
      </h2>

      <div className="mt-5 flex flex-col gap-3 text-[14px]">
        <div className="flex items-center justify-between gap-4 text-text-secondary">
          <span>
            {plan.name} Plan - {getBillingLabel(billingCycle)}
          </span>
          <span>{formatEgp(summary.subtotal)}</span>
        </div>
        <div className="flex items-center justify-between gap-4 text-text-secondary">
          <span>Subtotal</span>
          <span>{formatEgp(summary.subtotal)}</span>
        </div>
        <div className="flex items-center justify-between gap-4 text-text-secondary">
          <span className="flex items-center gap-1.5">
            Tax <Info aria-hidden="true" className="size-3.5" />
          </span>
          <span>{formatEgp(summary.tax)}</span>
        </div>
      </div>

      <div className="my-4 h-px bg-white/10" />

      <div className="flex items-center justify-between gap-4">
        <span className="text-[17px] font-extrabold text-text-primary">
          Total
        </span>
        <span className="text-[17px] font-extrabold text-text-primary">
          {formatEgp(summary.total)}
        </span>
      </div>

      <Button className="mt-5 h-12 w-full rounded-sm bg-gradient-to-r from-primary to-secondary text-[15px] font-extrabold text-white shadow-[0_0_28px_rgba(115,51,210,0.32)]">
        <LockKeyhole data-icon="inline-start" />
        Complete Payment
      </Button>

      <p className="mx-auto mt-5 max-w-105 text-center text-[12px]! leading-5 text-text-secondary">
        By completing your purchase, you agree to our Terms of Service and
        Privacy Policy.
      </p>
    </section>
  )
}

export default OrderSummary
