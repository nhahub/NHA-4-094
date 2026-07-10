import { CheckCircle2 } from "lucide-react"

import type { CheckoutFeatureItem } from "@/constants"

type PlanFeaturesProps = {
  features: CheckoutFeatureItem[]
}

const PlanFeatures = ({ features }: PlanFeaturesProps) => {
  return (
    <div className="grid gap-5 sm:grid-cols-2">
      {features.map((feature) => (
        <div className="flex gap-4" key={feature.title}>
          <CheckCircle2
            aria-hidden="true"
            className="mt-0.5 size-5 shrink-0 text-[#c56cff]"
          />
          <div className="flex flex-col gap-1">
            <h3 className="text-[15px]! font-bold text-text-primary">
              {feature.title}
            </h3>
            <p className="text-[13px]! leading-6 text-text-secondary">
              {feature.description}
            </p>
          </div>
        </div>
      ))}
    </div>
  )
}

export default PlanFeatures
