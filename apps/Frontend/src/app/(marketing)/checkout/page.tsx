import CheckoutContent from "@/components/checkout/CheckoutContent"
import { getInitialCheckoutState } from "@/components/checkout/checkout-utils"
import Footer from "@/components/shared/Footer"
import Header from "@/components/shared/Header"

type CheckoutPageProps = {
  searchParams?: Promise<{
    billing?: string | string[]
    plan?: string | string[]
  }>
}

const CheckoutPage = async ({ searchParams }: CheckoutPageProps) => {
  const resolvedSearchParams = searchParams ? await searchParams : undefined
  const { billingCycle, plan } = getInitialCheckoutState(resolvedSearchParams)

  return (
    <div className="relative pt-17.5 z-0">
      <Header />
      <CheckoutContent initialBillingCycle={billingCycle} plan={plan} />
      <Footer />
    </div>
  )
}

export default CheckoutPage
