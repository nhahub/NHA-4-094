"use client"

import { paymentMethods } from "@/constants"
import type { PaymentMethod } from "./checkout-types"
import { cn } from "@/lib/utils"

type PaymentMethodTabsProps = {
  paymentMethod: PaymentMethod
  onPaymentMethodChange: (paymentMethod: PaymentMethod) => void
}

const PaymentMethodTabs = ({
  paymentMethod,
  onPaymentMethodChange,
}: PaymentMethodTabsProps) => {
  return (
    <div
      aria-label="Payment method"
      className="grid grid-cols-2 gap-2"
      role="group"
    >
      {paymentMethods.map((method) => {
        const Icon = method.icon
        const isActive = method.value === paymentMethod

        return (
          <button
            aria-pressed={isActive}
            className={cn(
              "flex h-12 items-center justify-center gap-3 rounded-sm border border-white/10 bg-white/2 text-[14px] font-semibold text-text-primary outline-none transition-colors hover:border-primary/60 focus-visible:ring-2 focus-visible:ring-primary/70",
              isActive && "border-primary bg-primary/10 text-[#efc7ff]",
            )}
            key={method.value}
            onClick={() => onPaymentMethodChange(method.value)}
            type="button"
          >
            <Icon aria-hidden="true" className="size-5 text-[#c56cff]" />
            {method.label}
          </button>
        )
      })}
    </div>
  )
}

export default PaymentMethodTabs
