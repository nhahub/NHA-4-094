"use client"

import { useState } from "react"

import Hero from "./Hero"
import PricingCards from "./PricingCards"
import type { BillingCycle } from "./pricing-data"

const PricingContent = () => {
  // Keeps the selected billing cycle shared between the hero toggle and cards.
  const [billingCycle, setBillingCycle] = useState<BillingCycle>("monthly")

  return (
    <>
      <Hero
        billingCycle={billingCycle}
        onBillingCycleChange={setBillingCycle}
      />
      <PricingCards billingCycle={billingCycle} />
    </>
  )
}

export default PricingContent
