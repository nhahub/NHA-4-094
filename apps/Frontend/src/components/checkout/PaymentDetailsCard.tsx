"use client"

import { useState } from "react"

import CheckoutForm from "./CheckoutForm"
import PaymentMethodTabs from "./PaymentMethodTabs"
import type { PaymentMethod } from "./checkout-types"

const PaymentDetailsCard = () => {
  const [paymentMethod, setPaymentMethod] = useState<PaymentMethod>("card")

  return (
    <section className="rounded-[18px] border border-white/10 bg-white/2.5 p-5 sm:p-6">
      <div className="mb-5 flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h2 className="text-[21px]! font-extrabold text-text-primary">
            Payment details
          </h2>
          <p className="mt-2 text-[14px]! text-text-secondary">
            Secure checkout powered by Stripe.
          </p>
        </div>
        <div className="w-full sm:w-[300px]">
          <PaymentMethodTabs
            paymentMethod={paymentMethod}
            onPaymentMethodChange={setPaymentMethod}
          />
        </div>
      </div>

      {/* Payment form is UI-only until a real payment API is connected. */}
      <CheckoutForm />
    </section>
  )
}

export default PaymentDetailsCard
