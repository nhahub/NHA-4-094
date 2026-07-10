import React from 'react'
import Image from 'next/image'
import { Button } from '../ui/button'

const Demo = () => {
  return (
    <section className="relative w-full flex justify-center items-center px-5 ">
      <div className="relative w-full max-w-[1100px] rounded-lg border border-white/15 bg-text-primary/2 p-2 md:p-3 z-10 overflow-hidden group backdrop-blur-md">
        <div className="relative rounded-lg overflow-hidden border border-white/10 shadow-2xl">
          <Image 
              src="/images/Dashboard.svg" 
              alt="AI Study Platform Dashboard" 
              width={1200} 
              height={800} 
              className="w-full h-auto object-cover" 
          />
          
        </div>
      </div>
      <div className="absolute bottom-8 md:bottom-12 left-1/2 -translate-x-1/2 z-20">
        <Button variant="purple" className='h-12 text-button '>
            Try It Now
        </Button>
    </div>
      <div className="absolute inset-x-0 bottom-0 h-[50%] bg-gradient-to-t from-background via-background/80 to-transparent pointer-events-none z-10"></div>
    </section>
  )
}

export default Demo