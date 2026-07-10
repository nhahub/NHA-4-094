import React from 'react'

const CTA = () => {
  return (
    <section className="relative w-full max-w-[1100px] mx-auto py-20 px-4 md:px-8 z-10 bg-background">
      {/* Background Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[70%] h-[300px] bg-gradient-to-r from-primary to-secondary blur-[100px] opacity-25 rounded-full z-0 pointer-events-none" />

      {/* CTA Box */}
      <div className="relative rounded-3xl bg-[#060606] border border-white/10 p-8 md:p-16 flex flex-col items-center text-center gap-6 z-10 overflow-hidden shadow-2xl">
        {/* Shimmer Effect */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none z-0">
          <div className="absolute inset-0 w-[200%] h-full bg-gradient-to-r from-transparent via-white/5 to-transparent -skew-x-12 animate-shimmer" />
        </div>

        <div className="relative z-10 flex flex-col items-center gap-4 max-w-[700px]">
          <h2 className="text-3xl md:text-5xl font-extrabold leading-tight tracking-tight bg-gradient-to-r from-white to-neutral-400 bg-clip-text text-transparent">
            Ready to Study 10x Faster?
          </h2>
          <p className="text-text-secondary text-sm md:text-base leading-relaxed">
            Join thousands of smart students who are already using AI to summarize lessons, generate custom quizzes, and accelerate their learning.
          </p>
        </div>

        <div className="relative z-10 flex flex-col sm:flex-row gap-4 mt-4 w-full sm:w-auto">
          <button className="px-8 py-3 rounded-xl bg-white text-black font-semibold hover:bg-neutral-200 hover:scale-[1.01] transition-all duration-300 shadow-[0_0_20px_rgba(255,255,255,0.2)]">
            Get Started Free
          </button>
          <button className="px-8 py-3 rounded-xl bg-transparent border border-white/20 text-white font-semibold hover:bg-white/5 hover:border-white/50 hover:scale-[1.01] transition-all duration-300">
            View Pricing
          </button>
        </div>
      </div>
    </section>
  )
}

export default CTA
