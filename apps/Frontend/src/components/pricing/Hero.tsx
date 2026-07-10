import BillingToggle from "./BillingToggle"
import type { BillingCycle } from "./pricing-data"

type HeroProps = {
  billingCycle: BillingCycle
  onBillingCycleChange: (billingCycle: BillingCycle) => void
}

const Hero = ({ billingCycle, onBillingCycleChange }: HeroProps) => {
  return (
    <section className="relative overflow-hidden px-4 pb-10 pt-16 sm:px-6 md:pb-12 md:pt-20">
      <div
        aria-hidden="true"
        className="absolute left-1/2 top-1/2 size-[520px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-primary/20 blur-[170px]"
      />
      <div
        aria-hidden="true"
        className="absolute left-[28%] top-[36%] size-[260px] rounded-full bg-secondary/10 blur-[130px]"
      />

      <div className="relative z-10 mx-auto flex max-w-205 flex-col items-center text-center">
        <div className="mb-5 rounded-full border border-primary/80 bg-primary/10 px-4 py-2 text-[13px] font-semibold text-[#d696ff] shadow-[0_0_24px_rgba(115,51,210,0.32)]">
          Simple Pricing
        </div>

        <h1 className="max-w-195 text-[40px] font-extrabold leading-[1.08] text-text-primary sm:text-[52px] md:text-[64px]">
          Choose the plan that fits your{" "}
          <span className="bg-gradient-to-r from-primary via-[#a855ff] to-secondary bg-clip-text text-transparent">
            learning journey
          </span>
        </h1>

        <p className="mt-5 max-w-140 text-[15px] leading-7 text-text-secondary md:text-[17px]">
          Start free, upgrade when you need more AI power.
        </p>

        <div className="mt-8 w-full">
          <BillingToggle
            billingCycle={billingCycle}
            onBillingCycleChange={onBillingCycleChange}
          />
        </div>
      </div>
    </section>
  )
}

export default Hero
