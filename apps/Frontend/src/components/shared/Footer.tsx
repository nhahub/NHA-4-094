import React from 'react'
import Image from 'next/image'
import Link from 'next/link'
import { navItems } from '@/constants'

const Footer = () => {
  return (
    <footer className="w-full bg-background border-t border-white/10 mt-20 py-10">
      <div className="max-w-[1100px] mx-auto py-12 px-6 md:px-8 flex flex-col md:flex-row justify-between items-start md:items-center gap-8">
        
        {/* Left Side: Logo & Description */}
        <div className="flex flex-col gap-4 max-w-[300px]">
          <Image src="/icons/logo.svg" alt="Learner Logo" width={109} height={28} />
          <h4 className="text-text-secondary text-[15px] leading-relaxed">
            Personalized AI-powered study companion. Summaries, interactive quizzes, and 24/7 assistance tailored for students.
          </h4>
        </div>

        {/* Right Side: Links & Socials */}
        <div className="flex flex-col md:flex-row gap-8 md:gap-16">
          {/* Quick Links */}
          <div className="flex flex-col gap-3">
            <h4 className="text-sm font-semibold text-text-primary">Platform</h4>
            <ul className="flex flex-col gap-2">
              {navItems.map((item) => (
                <li key={item.id}>
                  <Link href={item.url} className="text-text-secondary text-[13px] hover:text-text-primary transition-colors duration-200">
                    {item.title}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Socials / Support */}
          <div className="flex flex-col gap-3">
            <h4 className="text-sm font-semibold text-text-primary">Connect</h4>
            <ul className="flex flex-col gap-2 text-[13px]">
              <li>
                <a href="#" className="text-text-secondary hover:text-text-primary transition-colors duration-200">
                  Twitter
                </a>
              </li>
              <li>
                <a href="#" className="text-text-secondary hover:text-text-primary transition-colors duration-200">
                  GitHub
                </a>
              </li>
              <li>
                <a href="mailto:support@learner.ai" className="text-text-secondary hover:text-text-primary transition-colors duration-200">
                  support@learner.ai
                </a>
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* Bottom Copyright */}
      <div className="max-w-[1100px] mx-auto border-t border-white/5 py-6 px-6 md:px-8 flex flex-col sm:flex-row justify-between items-center gap-4">
        <h4 className="text-text-secondary text-[12px]">
          © {new Date().getFullYear()} Learner. All rights reserved.
        </h4>
        <div className="flex gap-4 text-[12px]">
          <a href="#" className="text-text-secondary hover:text-text-primary transition-colors duration-200">Privacy Policy</a>
          <a href="#" className="text-text-secondary hover:text-text-primary transition-colors duration-200">Terms of Service</a>
        </div>
      </div>
    </footer>
  )
}

export default Footer