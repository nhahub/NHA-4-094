import React from 'react'
import { testimonialsList } from '@/constants'

const Testimonials = () => {
  return (
    <section id="testimonials" className="relative w-full max-w-[1100px] mx-auto py-20 px-4 md:px-8 z-10 bg-background">
      {/* Title */}
      <div className="text-center mb-16">
        <h2 className="text-3xl md:text-4xl font-bold mb-4 bg-gradient-to-r from-white to-neutral-400 bg-clip-text text-transparent">
          Loved by Students
        </h2>
        <p className="text-text-secondary max-w-[600px] mx-auto text-sm md:text-base">
          See how students from leading universities are using Learner to accelerate their study performance.
        </p>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {testimonialsList.map((test, idx) => (
          <div 
            key={idx}
            className="relative rounded-2xl border border-white/10 bg-text-primary/4 hover:bg-text-primary/5   p-8 flex flex-col justify-between gap-6 hover:scale-[1.02] transition-transform duration-300"
          >
            <div className="flex flex-col gap-4">
              {/* Stars */}
              <div className="flex gap-1">
                {[...Array(test.stars)].map((_, sIdx) => (
                  <svg key={sIdx} className="w-4 h-4 text-amber-500 fill-current" viewBox="0 0 24 24">
                    <path d="M12 17.27L18.18 21L16.54 13.97L22 9.24L14.81 8.62L12 2L9.19 8.62L2 9.24L7.45 13.97L5.82 21L12 17.27Z" />
                  </svg>
                ))}
              </div>

              {/* Text */}
              <p className="text-text-secondary text-sm leading-relaxed italic">
                &quot;{test.text}&quot;
              </p>
            </div>

            {/* Author */}
            <div className="flex items-center gap-3">
              {/* Avatar Bubble */}
              <div className="w-10 h-10 rounded-full bg-primary/15 border border-primary/30 flex items-center justify-center text-primary font-bold text-xs">
                {test.avatar}
              </div>
              <div className="flex flex-col">
                <h4 className="text-sm font-semibold text-text-primary">{test.name}</h4>
                <h4 className="text-text-secondary text-[11px]">{test.role}</h4>
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}

export default Testimonials
