import { trustItems } from "./pricing-data"

const TrustSection = () => {
  return (
    <section className="relative z-10 px-4 pt-8 sm:px-6">
      <div className="mx-auto flex max-w-180 flex-col items-center justify-center gap-4 text-[14px] text-text-secondary sm:flex-row sm:gap-7">
        {trustItems.map((item, index) => {
          const Icon = item.icon

          return (
            <div className="flex items-center gap-3" key={item.label}>
              {index > 0 ? (
                <span className="hidden size-1 rounded-full bg-primary sm:block" aria-hidden="true" />
              ) : null}
              <Icon className="size-4 text-[#b65cff]" aria-hidden="true" />
              <span>{item.label}</span>
            </div>
          )
        })}
      </div>
    </section>
  )
}

export default TrustSection
