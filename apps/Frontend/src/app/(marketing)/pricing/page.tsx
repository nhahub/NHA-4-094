import Footer from "@/components/shared/Footer"
import {
  ComparisonTable,
  FAQ,
  PricingContent,
} from "@/components/pricing"
import Header from "@/components/shared/Header"

const page = () => {
  return (
    <div className="relative pt-17.5 z-0">
      <Header />
      <main className="relative overflow-hidden bg-background flex flex-col gap-10">
        <PricingContent />
        <ComparisonTable />
        <FAQ />
      </main>
      <Footer />
    </div>
  )
}

export default page
