import { Check } from "lucide-react"
import Link from "next/link"

import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

import {
  getCheckoutHref,
  getPlanPrice,
  type BillingCycle,
  type PricingPlan,
} from "./pricing-data"

type PricingCardProps = {
  billingCycle: BillingCycle
  plan: PricingPlan
}

const PricingCard = ({ billingCycle, plan }: PricingCardProps) => {
  const isFeatured = Boolean(plan.featured)
  const isFree = plan.id === "free"
  const isPremium = plan.id === "premium"
  const ctaHref = isFree ? "/auth/signup" : getCheckoutHref(plan, billingCycle)
  const { period, price } = getPlanPrice(plan.monthlyPrice, billingCycle)

  return (
    <article
      className={cn(
        "group relative flex min-h-[450px] flex-col rounded-[18px] border bg-[#050505] p-6 transition-all duration-300 hover:-translate-y-1 hover:border-white/25 hover:bg-white/4 md:p-7",
        isFeatured
          ? "border-primary/90 shadow-[0_0_46px_rgba(115,51,210,0.32),inset_0_0_42px_rgba(115,51,210,0.07)]"
          : "border-white/12",
      )}
    >
      {isFeatured ? (
        <div className="absolute -top-4 left-1/2 -translate-x-1/2 rounded-full bg-gradient-to-r from-primary to-secondary px-5 py-2 text-[11px] font-extrabold uppercase tracking-wide text-white shadow-[0_0_28px_rgba(248,83,174,0.42)]">
          Most Popular
        </div>
      ) : null}

      <div className="flex flex-1 flex-col">
        <header>
          <h2 className="text-[20px] font-semibold text-text-primary">{plan.name}</h2>
          <div className="mt-4 flex items-end gap-2">
            <span className="text-[32px] font-extrabold leading-none text-text-primary md:text-[36px]">
              {price}
            </span>
            {period ? (
              <span className="pb-1 text-[13px] font-medium text-text-secondary">
                {period}
              </span>
            ) : null}
          </div>
          <p className="mt-4 min-h-11 text-[14px] leading-6 text-text-secondary">
            {plan.description}
          </p>
        </header>

        <div className="my-6 h-px w-full bg-white/10" />

        <ul className="flex flex-col gap-4">
          {plan.features.map((feature) => (
            <li className="flex items-start gap-3 text-[14px] leading-5 text-text-primary" key={feature}>
              <Check className="mt-0.5 size-4 shrink-0 text-[#b65cff]" aria-hidden="true" />
              <span>{feature}</span>
            </li>
          ))}
        </ul>

        <div className="mt-auto pt-8">
          <Button
            asChild
            className={cn(
              "h-12 w-full rounded-sm text-[14px] font-extrabold",
              isFree &&
                "border border-white/80 bg-transparent text-text-primary hover:border-primary hover:bg-white/5 hover:text-white",
              isFeatured &&
                "bg-gradient-to-r from-primary to-secondary text-white shadow-[0_0_28px_rgba(115,51,210,0.34)] hover:shadow-[0_0_34px_rgba(248,83,174,0.42)]",
              isPremium && "bg-white text-background hover:bg-white/90",
            )}
            variant={isFree ? "noOutline" : "default"}
          >
            <Link href={ctaHref}>{plan.cta}</Link>
          </Button>
        </div>
      </div>
    </article>
  )
}

export default PricingCard
