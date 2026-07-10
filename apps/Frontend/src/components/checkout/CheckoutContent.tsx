"use client"

import { useState } from "react"
import Link from "next/link"
import { ArrowLeft } from "lucide-react"

import CheckoutPlanCard from "./CheckoutPlanCard"
import OrderSummary from "./OrderSummary"
import PaymentDetailsCard from "./PaymentDetailsCard"
import TrustRow from "./TrustRow"
import type { BillingCycle, PricingPlan } from "./checkout-types"

type CheckoutContentProps = {
  initialBillingCycle: BillingCycle
  plan: PricingPlan
}

const CheckoutContent = ({
  initialBillingCycle,
  plan,
}: CheckoutContentProps) => {
  const [billingCycle, setBillingCycle] =
    useState<BillingCycle>(initialBillingCycle)

  return (
    <main className="relative overflow-hidden bg-background px-4 pb-12 pt-5 sm:px-6 md:pt-6">
      <div
        aria-hidden="true"
        className="absolute left-[12%] top-[28%] size-[380px] rounded-full bg-primary/15 blur-[150px]"
      />
      <div
        aria-hidden="true"
        className="absolute right-[16%] top-[36%] size-[320px] rounded-full bg-secondary/10 blur-[150px]"
      />

      <div className="relative z-10 mx-auto w-full max-w-300">
        <div className="mb-5">
          <Link
            className="inline-flex items-center gap-2 text-[14px] font-semibold text-[#df8cff] transition-colors hover:text-text-primary"
            href="/pricing"
          >
            <ArrowLeft aria-hidden="true" className="size-4" />
            Back to Pricing
          </Link>
          <h1 className="mt-3 text-[34px]! font-extrabold leading-tight text-text-primary md:text-[38px]!">
            Checkout
          </h1>
          <p className="mt-2 max-w-full text-[15px]! leading-7 text-text-secondary sm:max-w-140">
            You&apos;re one step away from unlocking the full power of AI
            learning.
          </p>
        </div>

        <div className="grid gap-6 lg:grid-cols-[1.02fr_1fr]">
          <CheckoutPlanCard
            billingCycle={billingCycle}
            onBillingCycleChange={setBillingCycle}
            plan={plan}
          />

          <div className="flex flex-col gap-4">
            <PaymentDetailsCard />
            <OrderSummary billingCycle={billingCycle} plan={plan} />
          </div>
        </div>

        <TrustRow />
      </div>
    </main>
  )
}

export default CheckoutContent
