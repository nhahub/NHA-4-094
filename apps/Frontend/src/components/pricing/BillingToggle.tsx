"use client"

import { motion } from "framer-motion"

import { billingOptions, type BillingCycle } from "./pricing-data"

type BillingToggleProps = {
  billingCycle: BillingCycle
  onBillingCycleChange: (billingCycle: BillingCycle) => void
}

const BillingToggle = ({
  billingCycle,
  onBillingCycleChange,
}: BillingToggleProps) => {
  return (
    // Lets learners switch the card prices between monthly and yearly billing.
    <div
      aria-label="Billing frequency"
      className="mx-auto flex h-11 w-full max-w-[320px] items-center rounded-full border border-white/10 bg-white/3 p-1 text-[13px] text-text-secondary shadow-[0_0_45px_rgba(115,51,210,0.16)]"
      role="group"
    >
      {billingOptions.map((option) => {
        const isActive = option.value === billingCycle

        return (
          <button
            aria-pressed={isActive}
            className="relative flex h-full flex-1 items-center justify-center gap-2 rounded-full font-semibold outline-none transition-colors duration-200 focus-visible:ring-2 focus-visible:ring-primary/70 data-[active=true]:text-text-primary"
            data-active={isActive}
            key={option.value}
            onClick={() => onBillingCycleChange(option.value)}
            type="button"
          >
            {isActive ? (
              <motion.span
                aria-hidden="true"
                className="absolute inset-0 rounded-full bg-gradient-to-r from-primary/80 to-primary/45 shadow-[0_0_24px_rgba(115,51,210,0.36)]"
                layoutId="pricing-billing-active"
                transition={{ duration: 0.25, ease: "easeOut" }}
              />
            ) : null}
            <span className="relative z-10">{option.label}</span>
            {option.note ? (
              <span className="relative z-10 text-[12px] font-bold text-[#43d36f]">
                {option.note}
              </span>
            ) : null}
          </button>
        )
      })}
    </div>
  )
}

export default BillingToggle
