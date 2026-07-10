import React from 'react'
import { Button } from '../ui/button'
import { pricingPlans } from '@/constants'

const Pricing = () => {
  return (
    <section id="pricing" className="relative w-full max-w-[1100px] mx-auto py-20 px-4 md:px-8 z-10 bg-background">
      {/* Title */}
      <div className="text-center mb-16">
        <h2 className="text-3xl md:text-4xl font-bold mb-4 bg-gradient-to-r from-white to-neutral-400 bg-clip-text text-transparent">
          Simple, Transparent Pricing
        </h2>
        <p className="text-text-secondary max-w-[600px] mx-auto text-sm md:text-base">
          Choose the plan that fits your study needs. Upgrade or downgrade anytime.
        </p>
      </div>

      {/* Plans Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-stretch">
        {pricingPlans.map((plan, idx) => {
          const isPro = plan.popular;
          const isFree = plan.name === "Free";
          const isPremium = plan.name === "Premium";
          
          return (
            <div
              key={idx}
              className={`relative flex flex-col  justify-between transition-all duration-300 hover:scale-[1.02] ${
                isPro ? 'md:-translate-y-2' : ''
              }`}
            >
              {/* Outer Glow & Gradient Border for Pro card */}
              {isPro && (
                <>
                  <div className="absolute -inset-[3px] bg-gradient-to-r from-primary to-secondary rounded-[24px] blur-xl opacity-75 animate-[pulse_4s_infinite]" />
                  <div className="absolute -inset-[1px] bg-gradient-to-r from-primary to-secondary rounded-[24px] opacity-40" />
                  {/* Shimmer Effect */}
                  <div className="absolute inset-0 overflow-hidden rounded-[24px] pointer-events-none z-0">
                    <div className="absolute inset-0 w-[200%] h-full bg-gradient-to-r from-transparent via-white/10 to-transparent -skew-x-12 animate-shimmer" />
                  </div>
                </>
              )}

              {isPro && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-gradient-to-r from-primary to-secondary text-white text-xs font-semibold px-4 py-1.5 rounded-full uppercase tracking-wider shadow-[0_0_15px_rgba(115,51,210,0.4)] z-20">
                  Most Popular
                </div>
              )}

              <div
                className={`relative w-full h-full rounded-[24px] p-8 flex flex-col justify-between z-10 ${
                  isPro 
                    ? 'bg-[#060606] border border-transparent' 
                    : 'border border-white/10 bg-text-secondary/5'
                }`}
              >
                <div>
                  {/* Plan Header */}
                  <div className="mb-6">
                    <h3 className="text-xl font-bold text-text-primary mb-2">{plan.name}</h3>
                    <div className="flex items-baseline gap-1 mb-2">
                      <span className="text-3xl md:text-4xl font-extrabold text-text-primary">{plan.price}</span>
                      {plan.price !== "0 EGP" && <span className="text-text-secondary text-sm">/ month</span>}
                    </div>
                    <p className="text-text-secondary text-sm leading-relaxed">{plan.description}</p>
                  </div>

                  {/* Divider */}
                  <div className="w-full h-px bg-white/10 my-6" />

                  {/* Features List */}
                  <ul className="flex flex-col gap-4 mb-8">
                    {plan.features.map((feature, fIdx) => (
                      <li key={fIdx} className={`flex items-start gap-3 text-sm ${isFree ? 'text-text-secondary' : 'text-text-primary/95'}`}>
                        <svg className={`w-5 h-5 shrink-0 mt-0.5 ${isFree ? 'text-text-secondary' : 'text-primary'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="3">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                        </svg>
                        <span>{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Action Button */}
                {isFree && (
                  <button 
                    className="w-full h-12 rounded-xl text-sm font-semibold bg-transparent border border-text-secondary/50 hover:border-white/70 hover:text-white/70  text-text-secondary hover:bg-white/10 transition-all duration-300"
                  >
                    Get Started
                  </button>
                )}
                
                {isPro && (
                  <Button 
                    variant="default" 
                    className="w-full h-12 rounded-xl text-sm font-semibold transition-all duration-300 shadow-[0_0_20px_rgba(115,51,210,0.4)] hover:shadow-[0_0_30px_rgba(115,51,210,0.7)] hover:scale-[1.01]"
                  >
                    Upgrade Now
                  </Button>
                )}

                {isPremium && (
                  <button 
                    className="w-full h-12 rounded-xl text-sm font-semibold bg-white text-black hover:bg-white/90 transition-all duration-300"
                  >
                    Upgrade Now
                  </button>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </section>
  )
}

export default Pricing