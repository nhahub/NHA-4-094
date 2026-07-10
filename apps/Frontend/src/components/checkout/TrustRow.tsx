import { LockKeyhole } from "lucide-react"

import { trustItems } from "@/constants"

const TrustRow = () => {
  return (
    <div className="mx-auto flex flex-col items-center justify-center gap-3 pt-6 text-[14px] text-text-secondary sm:flex-row sm:gap-5">
      {trustItems.map((item, index) => (
        <div className="flex items-center gap-3" key={item}>
          {index === 0 ? (
            <LockKeyhole aria-hidden="true" className="size-4" />
          ) : (
            <span
              aria-hidden="true"
              className="hidden size-1 rounded-full bg-text-secondary sm:block"
            />
          )}
          <span>{item}</span>
        </div>
      ))}
    </div>
  )
}

export default TrustRow
