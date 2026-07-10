import Header from "@/components/shared/Header";
import Hero from "@/components/landing/Hero";
import Demo from "@/components/landing/Demo";
import Features from "@/components/landing/Features";
import Pricing from "@/components/landing/Pricing";
import Testimonials from "@/components/landing/Testimonials";
import FAQ from "@/components/landing/FAQ";
import CTA from "@/components/landing/CTA";
import Footer from "@/components/shared/Footer";

export default function Home() {
  return (
    <div className="relative pt-[70px] z-0">
      
      <Header />
      <Hero />
      <Demo />
      <Features />
      <Testimonials />
      <Pricing />
      <FAQ />
      <CTA />
      <Footer />
    </div>
  );
}
