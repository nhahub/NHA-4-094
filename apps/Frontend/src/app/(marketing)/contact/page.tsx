import Footer from '@/components/shared/Footer'
import Header from '@/components/shared/Header'
import React from 'react'


/*shared styles*/
const buttonStyle = 
"w-full bg-purple-600 hover:bg-purple-700 hover:scale-[1.02] transition rounded-xl py-3 md:py-4 text-base md:text-lg font-semibold shadow-lg shadow-purple-500/30"

/*input field component*/
type InputFieldProps = {
  icon: React.ReactNode
  type: string
  placeholder: string
}

const InputField = ({ icon, type, placeholder }: InputFieldProps) => {
  return (
    <div className="flex bg-[#111827] border border-gray-800 rounded-xl px-4 py-4 focus-within:border-purple-500 transition">
      {icon}
      <input
        type={type}
        placeholder={placeholder}
        className="w-full bg-transparent outline-none placeholder:text-gray-500"
      />
    </div>
  )
}

/*message field component*/
type MessageFieldProps = {
  icon: React.ReactNode
  placeholder: string
}

const MessageField = ({ icon, placeholder }: MessageFieldProps) => {
  return (
    <div className="flex bg-[#111827] border border-gray-800 rounded-xl px-4 py-4 focus-within:border-purple-500 transition">
      {icon}
      <textarea
        placeholder={placeholder}
        rows={6}
        className="w-full bg-transparent outline-none resize-none placeholder:text-gray-500"
      />
    </div>
  )
}


const page = () => {
  return (
    /*main page wrapper*/
    <div className="relative pt-[70px] z-0 bg-black min-h-screen text-white">
      <Header />

      {/*purple blur effect*/}
        <div className="absolute top-10 right-0 w-[450px] h-[450px] bg-purple-500/20 rounded-full blur-[140px] pointer-events-none"></div>
      
      {/*contact section*/}
         <section className="px-6 py-10">
        <div className="w-[95%] md:w-[92%] mx-auto bg-[#040b18] rounded-[24px] md:rounded-[40px] px-5 md:px-12 py-6 md:py-10 min-h-auto md:min-h-[650px]">
        <div className="grid grid-cols-1 md:grid-cols-[0.85fr_1.15fr] gap-8 md:gap-6 items-start">
            
  {/*left side content*/}
  <div className="relative flex flex-col justify-start md:pr-8 pt-0 md:pt-2">
   {/* vertical line */}
    <div className="hidden md:block absolute right-0 top-[60px] h-full w-[1px] bg-gray-800"></div>
    
    {/*contact badge*/}
<div className="inline-flex items-center gap-2 w-fit px-4 py-1.5 rounded-full border border-gray-800 bg-[#111827] text-gray-500 text-sm tracking-[0.2em] mb-10">
  <span className="inline-block w-2 h-2 rounded-full bg-purple-500"></span>
  CONTACT
</div>

  {/* Main Heading */}
  <h1 className="text-4xl md:text-6xl font-bold">
      Contact <br />
    <span className="mt-2 text-purple-500">Us</span>
  </h1>

  <div className="w-16 h-1 bg-purple-500 my-6 rounded-full"></div>

   {/* Description */}
  <p className="text-gray-400 text-base md:text-lg leading-7 md:leading-8">
    Need help or have questions?
    <br />
    Our team is here for you.
  </p>

{/*Contact Email */}
<div className="flex items-center gap-2 mt-5">
  {/* icon */}
  <div className="flex items-center justify-center w-9 h-9 rounded-lg border border-purple-500/30 bg-purple-500/10">
    <svg
      className="w-4 h-4 text-purple-400"
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1.8}
        d="M3 8l9 6 9-6"
      />
      <rect
        x="3"
        y="6"
        width="18"
        height="12"
        rx="2"
        ry="2"
        strokeWidth={1.8}
      />
    </svg>
  </div>
<a
  href="mailto:support@dexa.com"
  className="text-purple-400 text-sm hover:underline"
>
  support@dexa.com
</a>
</div>  
</div>
    
    {/* Right Side Form */} 
    <div className="w-full md:w-[90%] ml-0 md:ml-auto bg-[#08101d] rounded-[20px] md:rounded-[30px] p-5 md:p-10 shadow-lg mt-6 md:mt-10">
    <form className="space-y-6">

{/* Name Input Field */}
<InputField
  type="text"
  placeholder="Your Name"
  icon={
    <svg
      className="w-5 h-5 text-gray-500 mr-3 shrink-0"
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1.8}
        d="M12 12a4 4 0 100-8 4 4 0 000 8zm0 2c-4 0-7 2-7 4v1h14v-1c0-2-3-4-7-4z"
      />
    </svg>
  }
/>

{/* Email Input Field */}
<InputField
  type="email"
  placeholder="Your Email"
  icon={
    <svg
      className="w-5 h-5 text-gray-500 mr-3 shrink-0"
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1.8}
        d="M3 8l9 6 9-6"
      />
      <rect
        x="3"
        y="6"
        width="18"
        height="12"
        rx="2"
        ry="2"
        strokeWidth={1.8}
      />
    </svg>
  }
/>

{/* Message Textarea Field */}
<MessageField
  placeholder="Your Message"
  icon={
    <svg
      className="w-5 h-5 text-gray-500 mr-3 mt-1 shrink-0"
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1.8}
        d="M8 10h8M8 14h5"
      />
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1.8}
        d="M21 12c0 4.5-4 8-9 8-1.2 0-2.4-.2-3.4-.6L3 21l1.8-4.2C4.3 15.4 4 13.7 4 12c0-4.5 4-8 9-8s9 3.5 9 8z"
      />
    </svg>
  }
/>

<button type="submit" className={`${buttonStyle} flex items-center justify-center gap-2`}>
  <span>Send Message</span>

  <svg
    className="w-5 h-5"
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={1.8}
      d="M3 10l18-7-7 18-2.5-7.5L3 10z"
    />
  </svg>
</button>
</form>
    </div>
    </div>
        </div>
      </section>
        <Footer />
      
    </div>
  )
}

export default page