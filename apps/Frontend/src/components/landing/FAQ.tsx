'use client'

import React, { useState } from 'react'
import { faqsList } from '@/constants'

const FAQ = () => {
  const [openIndex, setOpenIndex] = useState<number | null>(null)

  const toggleFAQ = (idx: number) => {
    setOpenIndex(openIndex === idx ? null : idx)
  }

  return (
    <section id="faq" className="relative w-full max-w-[850px] mx-auto py-20 px-4 md:px-8 z-10 bg-background">
      {/* Title */}
      <div className="text-center mb-12">
        <h2 className="text-3xl md:text-4xl font-bold mb-4 bg-gradient-to-r from-white to-neutral-400 bg-clip-text text-transparent">
          Frequently Asked Questions
        </h2>
        <p className="text-text-secondary max-w-[600px] mx-auto text-sm md:text-base">
          Got questions? We&apos;ve got answers. If you can&apos;t find what you are looking for, contact our support team.
        </p>
      </div>

      {/* Accordion Wrapper */}
      <div className="flex flex-col gap-4">
        {faqsList.map((faq, idx) => {
          const isOpen = openIndex === idx
          return (
            <div 
              key={idx}
              className={`rounded-2xl border border-white/10 bg-text-secondary/5 transition-all duration-300 overflow-hidden ${
                isOpen ? 'border-primary/40 bg-[#060606]' : ''
              }`}
            >
              {/* Question Trigger */}
              <button
                onClick={() => toggleFAQ(idx)}
                className="w-full py-5 px-6 flex justify-between items-center text-left text-text-primary hover:text-white font-medium text-sm md:text-base transition-colors duration-200"
              >
                <span>{faq.question}</span>
                <span className="ml-4 shrink-0">
                  <svg 
                    className={`w-5 h-5 transition-transform duration-300 text-text-secondary ${
                      isOpen ? 'transform rotate-180 text-primary' : ''
                    }`} 
                    fill="none" 
                    viewBox="0 0 24 24" 
                    stroke="currentColor" 
                    strokeWidth="2"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
                  </svg>
                </span>
              </button>

              {/* Answer Content */}
              <div 
                className={`transition-all duration-300 ease-in-out overflow-hidden ${
                  isOpen ? 'max-h-[200px] opacity-100' : 'max-h-0 opacity-0'
                }`}
              >
                <div className="px-6 pb-5 pt-1 border-t border-white/5 text-text-secondary text-xs md:text-sm leading-relaxed">
                  {faq.answer}
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </section>
  )
}

export default FAQ
