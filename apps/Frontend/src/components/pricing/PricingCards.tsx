import PricingCard from "./PricingCard"
import { pricingPlans, type BillingCycle } from "./pricing-data"

type PricingCardsProps = {
  billingCycle: BillingCycle
}

const PricingCards = ({ billingCycle }: PricingCardsProps) => {
  return (
    <section className="relative z-10 px-4 sm:px-6">
      <div className="mx-auto grid max-w-245 grid-cols-1 gap-6 md:grid-cols-3">
        {/* Renders each pricing plan using the selected billing cycle. */}
        {pricingPlans.map((plan) => (
          <PricingCard
            billingCycle={billingCycle}
            key={plan.id}
            plan={plan}
          />
        ))}
      </div>
    </section>
  )
}

export default PricingCards
