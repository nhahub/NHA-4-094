import { LockKeyhole } from "lucide-react"

const inputClassName =
  "w-full border-white/10 bg-white/2.5 px-4 text-[14px] text-text-primary outline-none transition-colors placeholder:text-text-secondary focus:border-primary/80 focus:ring-2 focus:ring-primary/40"

const CheckoutForm = () => {
  return (
    <form className="flex flex-col gap-4">
      <div className="flex flex-col gap-2">
        <label className="text-[14px] font-medium text-text-primary" htmlFor="card-number">
          Card information
        </label>
        <div className="overflow-hidden rounded-sm border border-white/10">
          <div className="relative">
            <input
              autoComplete="cc-number"
              className={`${inputClassName} h-11 border-0 border-b border-white/10 pr-4 sm:pr-44`}
              id="card-number"
              inputMode="numeric"
              placeholder="1234 1234 1234 1234"
              type="text"
            />
            <div
              aria-hidden="true"
              className="absolute right-4 top-1/2 hidden -translate-y-1/2 gap-1 sm:flex"
            >
              {["VISA", "MC", "AMEX", "DISC"].map((card) => (
                <span
                  className="rounded bg-white px-1.5 py-0.5 text-[9px] font-black text-background"
                  key={card}
                >
                  {card}
                </span>
              ))}
            </div>
          </div>
          <div className="grid grid-cols-2">
            <input
              aria-label="Expiration date"
              autoComplete="cc-exp"
              className={`${inputClassName} h-11 border-0 border-r border-white/10`}
              inputMode="numeric"
              placeholder="MM / YY"
              type="text"
            />
            <input
              aria-label="Security code"
              autoComplete="cc-csc"
              className={`${inputClassName} h-11 border-0`}
              inputMode="numeric"
              placeholder="CVC"
              type="text"
            />
          </div>
        </div>
      </div>

      <div className="flex flex-col gap-2">
        <label className="text-[14px] font-medium text-text-primary" htmlFor="cardholder-name">
          Cardholder name
        </label>
        <input
          autoComplete="cc-name"
          className={`${inputClassName} h-11 rounded-sm border`}
          id="cardholder-name"
          placeholder="Full name on card"
          type="text"
        />
      </div>

      <div className="flex flex-col gap-2">
        <label className="text-[14px] font-medium text-text-primary" htmlFor="country-region">
          Country or region
        </label>
        <select
          autoComplete="country-name"
          className={`${inputClassName} h-11 rounded-sm border`}
          id="country-region"
          defaultValue="Egypt"
        >
          <option className="bg-background text-text-primary">Egypt</option>
          <option className="bg-background text-text-primary">United States</option>
          <option className="bg-background text-text-primary">United Kingdom</option>
        </select>
      </div>

      <p className="flex items-center gap-2 text-[13px]! text-text-secondary">
        <LockKeyhole aria-hidden="true" className="size-4" />
        Your payment information is encrypted and secure.
      </p>
    </form>
  )
}

export default CheckoutForm
