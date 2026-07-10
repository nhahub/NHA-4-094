import React from 'react'
import { Button } from '../ui/button'

const Hero = () => {
  return (
    <main className='relative w-full flex flex-col justify-center items-center gap-8 py-24 md:py-40'>
        <div className="absolute top-[35%] left-1/2 -translate-x-1/2 w-[70vw] max-w-[1300px] h-[600px] bg-primary/30 blur-[210px] rounded-full z-0 pointer-events-none"></div>

        <div className='text-center flex flex-col justify-center items-center gap-3 relative z-10'>
            <h1 className='w-full max-w-[800px] leading-[1.1] text-[75px] font-extrabold'>
                AI-Powered Learning <br />
                for <span className="relative whitespace-nowrap text-transparent bg-clip-text bg-gradient-to-r from-[var(--color-primary)] to-[var(--color-secondary)]">
                    Every Student
                </span>
            </h1>
            <p className=" text-text-secondary w-[70%] mt-2">Learn smarter with AI. Personalized lessons, instant feedback, and support tailored to every student.</p>
        </div>
        <Button className="px-6 h-12 text-sm shadow-[0_0_20px_rgba(115,51,210,0.2)] hover:shadow-[0_0_30px_rgba(115,51,210,0.7)] hover:-translate-y-0.5 hover:text-white transition-all duration-300">Get Started</Button>
    </main>
  )
}

export default Hero