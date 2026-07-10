import Image from "next/image";
import Footer from '@/components/shared/Footer'
import Header from '@/components/shared/Header'
import React from 'react'

   const cards = [
    {
      icon: "/images/mindset.svg",
      title: "Smart",
      desc: "Organize tasks efficiently with intelligent workflow.",
    },
    {
      icon: "/images/clock.svg",
      title: "Fast",
      desc: "Save time and boost productivity quickly.",
    },
    {
      icon: "/images/security.svg",
      title: "Secure",
      desc: "Keep your data safe with advanced protection.",
    },
  ]

const AboutPage = () => {
  return (
    /* Main page wrapper */
    <div className="relative pt-[70px] z-0">
        <Header />
    {/* About section */}
      <section className="bg-black px-6 py-24 text-white">
      <div className="relative mx-auto max-w-6xl rounded-[24px] md:rounded-[30px] border border-purple-500/10 bg-[#040b18] p-5 md:p-8">

    {/* Badge */}
<div className="mb-6 md:mb-8 inline-flex items-center gap-2 rounded-full border border-gray-800 bg-[#111827] px-3 md:px-4 py-1.5 md:py-2 text-xs md:text-sm text-gray-400">
<span className="inline-block w-2 h-2 rounded-full bg-purple-500"></span>
      WHO WE ARE
    </div>
    <div className="relative z-10 grid items-center gap-6 md:grid-cols-2">

    {/* Top Section */}
      <div>
        <h1 className="text-4xl md:text-7xl lg:text-[92px] font-bold">
          About <span className="text-purple-500">Us</span>
        </h1>

        <p className="mt-4 md:mt-6 max-w-lg text-base md:text-xl leading-relaxed text-gray-300">
          We are a smart productivity platform designed to help
          individuals and teams stay organized, focused, and
          efficient in achieving their goals.
        </p>
      </div>

      {/* Planet image section */}
<div className="relative flex justify-center items-center md:translate-x-6 md:translate-y-5 mt-8 md:mt-0">
   <div className="absolute w-[180px] h-[180px] md:w-[420px] md:h-[420px] rounded-full bg-purple-500/50 md:bg-purple-500/70 blur-[80px] md:blur-[140px]"></div>

  <Image
    src="/images/planet.png"
    alt="Planet"
    width={370}
    height={370}
    style={{ height: "auto" }}
    className="relative z-10 w-[220px] md:w-[280px] lg:w-[330px] object-contain"
  />
</div>    
</div>

    {/* Cards */}
<div className="relative z-10 mt-20 grid gap-6 md:grid-cols-3">
  {cards.map((card, index) => (
    <div
      key={index}
      className="flex flex-col rounded-3xl border border-purple-500/20 bg-[#0b1120]/80 p-5 md:p-8 min-h-[200px] md:min-h-[220px] transition-all duration-300 hover:-translate-y-1 hover:border-purple-500/40 hover:shadow-[0_0_35px_rgba(168,85,247,0.18)]"
    >
      <Image
        src={card.icon}
        alt={card.title}
        width={28}
        height={28}
      />

      <h3 className="mt-4 text-2xl font-semibold">
        {card.title}
      </h3>

      <p className="mt-2 leading-relaxed text-gray-400">
        {card.desc}
      </p>
    </div>
  ))}
</div>
</div>
</section>
        <Footer />
      
    </div>
  )
}

export default AboutPage