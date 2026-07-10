import { Check } from "lucide-react"

import { cn } from "@/lib/utils"

import { comparisonRows, type PlanName } from "./pricing-data"

const planColumns: PlanName[] = ["Free", "Pro", "Premium"]

const renderValue = (value: string | boolean) => {
  if (typeof value === "boolean") {
    return value ? (
      <span className="mx-auto flex size-6 items-center justify-center rounded-full bg-gradient-to-br from-primary to-[#7d3cff] text-white shadow-[0_0_18px_rgba(115,51,210,0.42)]">
        <span className="sr-only">Included</span>
        <Check className="size-3.5" aria-hidden="true" />
      </span>
    ) : (
      <span className="text-text-secondary" aria-label="Not included">
        -
      </span>
    )
  }

  return value
}

const ComparisonTable = () => {
  return (
    <section className="relative z-10 px-4 pt-8 sm:px-6 md:pt-10">
      <div className="mx-auto max-w-260 overflow-hidden rounded-[14px] border border-white/12 bg-white/1.5 shadow-[0_0_70px_rgba(115,51,210,0.07)]">
        <div className="overflow-x-auto">
          <table
            aria-label="Pricing plan feature comparison"
            className="w-full min-w-190 border-collapse text-left text-[14px]"
          >
            <thead>
              <tr className="border-b border-white/12 text-text-primary">
                <th className="w-[20%] px-6 py-5 font-bold" scope="col">
                  Feature
                </th>
                {planColumns.map((plan) => (
                  <th
                    className={cn(
                      "w-[26.666%] border-l border-white/12 px-6 py-5 text-center font-bold",
                      plan === "Pro" && "text-[#d580ff]",
                    )}
                    key={plan}
                    scope="col"
                  >
                    {plan}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {comparisonRows.map((row) => (
                <tr className="border-b border-white/10 last:border-b-0" key={row.feature}>
                  <th className="px-6 py-4 font-medium text-text-primary" scope="row">
                    {row.feature}
                  </th>
                  {planColumns.map((plan) => (
                    <td
                      className="border-l border-white/10 px-6 py-4 text-center text-text-primary/90"
                      key={plan}
                    >
                      {renderValue(row.values[plan])}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  )
}

export default ComparisonTable
