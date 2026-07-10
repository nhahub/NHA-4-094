import React from 'react'
import { featuresList } from '@/constants'

const Features = () => {
  return (
    <section className="relative w-full max-w-[1100px] mx-auto py-34 px-4 md:px-8 z-10 bg-background">
      <div className="text-center mb-8">
        <h2 className="text-3xl md:text-4xl font-bold mb-4 bg-gradient-to-r from-white to-neutral-400 bg-clip-text text-transparent">
          Features
        </h2>
        <p className="text-text-secondary max-w-[600px] mx-auto text-sm md:text-base">
          Unlock your academic potential with powerful features tailored to speed up your learning curve.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {featuresList.map((feat, idx) => (
          <div 
            key={idx}
            className="relative rounded-2xl border border-white/15 bg-text-primary/4 backdrop-blur-md p-6 md:p-8 hover:scale-[1.015] hover:bg-text-primary/5 transition-transform duration-300 overflow-hidden"
          >
            <div className="relative z-10 flex flex-col gap-1">
              <div className="w-12 h-12 rounded-xl items-center justify-center text-3xl">
                {feat.emoji}
              </div>
              <h4 className="text-[20px] font-bold text-text-primary">
                {feat.title}
              </h4>
              <h4 className="text-text-secondary text-[14px] leading-relaxed">
                {feat.description}
              </h4>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}

export default Features