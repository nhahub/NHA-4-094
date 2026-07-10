import { ChevronDown } from "lucide-react"

import { billingOptions, type BillingCycle } from "@/components/pricing/pricing-data"

type BillingSelectorProps = {
  billingCycle: BillingCycle
  onBillingCycleChange: (billingCycle: BillingCycle) => void
}

const BillingSelector = ({
  billingCycle,
  onBillingCycleChange,
}: BillingSelectorProps) => {
  return (
    <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
      <span className="text-[14px] font-medium text-text-primary">
        Billing interval
      </span>
      <div className="relative w-full sm:w-auto">
        <select
          aria-label="Billing interval"
          className="h-11 w-full appearance-none rounded-[9px] border border-white/10 bg-white/3.5 px-4 pr-10 text-[14px] font-medium text-text-primary outline-none transition-colors focus:border-primary/80 focus:ring-2 focus:ring-primary/40 sm:min-w-[150px]"
          onChange={(event) =>
            onBillingCycleChange(event.target.value as BillingCycle)
          }
          value={billingCycle}
        >
          {billingOptions.map((option) => (
            <option className="bg-background text-text-primary" key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        <ChevronDown
          aria-hidden="true"
          className="pointer-events-none absolute right-3 top-1/2 size-4 -translate-y-1/2 text-text-primary"
        />
      </div>
      <span className="rounded-[8px] bg-emerald-500/10 px-4 py-3 text-center text-[13px] font-semibold text-emerald-300">
        Save 20% with yearly
      </span>
    </div>
  )
}

export default BillingSelector
