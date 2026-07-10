import {
  BarChart3,
  Brain,
  Clock,
  CreditCard,
  FileText,
  HelpCircle,
  Layers,
  MessageCircle,
  Network,
  NotebookTabs,
  Sparkles,
  Users,
  Zap,
  type LucideIcon,
} from "lucide-react"

import type {
  CheckoutFeature,
  CheckoutPlanId,
  PaymentMethod,
} from "@/components/checkout/checkout-types"

export const navItems = [
    {
        id: 0,
        title: "Home",
        url: "/"
    },
    {
        id: 1,
        title: "Pricing",
        url: "/pricing"
    },
    {
        id: 2,
        title: "About",
        url: "/about"
    },
    {
        id: 3,
        title: "Contact",
        url: "/contact"
    },
]

export const featuresList = [
  {
    title: '10X Faster Study',
    description: 'Study smarter with instant summaries and efficient revision tools.',
    emoji: '⚡',
  },
  {
    title: '24/7 AI Assistance',
    description: 'Ask questions anytime and receive instant academic support.',
    emoji: '🤖',
  },
  {
    title: 'Instant Smart Quizzes',
    description: 'Turn your materials into interactive quizzes in seconds.',
    emoji: '📝',
  },
  {
    title: '95%+ Satisfaction',
    description: 'Students enjoy a faster and more personalized learning experience.',
    emoji: '⭐',
  },
]

export const pricingPlans = [
  {
    name: "Free",
    price: "0 EGP",
    description: "Get started with basic AI study features.",
    features: [
      "3 Documents",
      "20 AI Messages / Day",
      "3 Summaries / Day",
      "2 Quizzes / Day",
      "Basic AI Model",
    ],
  },
  {
    name: "Pro",
    price: "149 EGP",
    description: "Perfect for most students.",
    popular: true,
    features: [
      "50 Documents",
      "Unlimited Summaries",
      "Unlimited Quizzes",
      "Study Plans",
      "Flashcards Generation",
      "Advanced AI Models",
    ],
  },
  {
    name: "Premium",
    price: "299 EGP",
    description: "For power users and heavy learners.",
    features: [
      "Unlimited Documents",
      "Unlimited AI Usage (Fair Use)",
      "Deep Reasoning Models",
      "Study Rooms",
      "Learning Analytics",
      "Priority Processing",
    ],
  },
]

export const faqsList = [
  {
    question: "How does the AI helper work?",
    answer: "Our AI processes your study materials (PDFs, docs, text) to create instant summaries, flashcards, and interactive quizzes tailored to your content.",
  },
  {
    question: "Can I cancel my subscription anytime?",
    answer: "Yes, you can cancel, upgrade, or downgrade your plan at any time from your billing settings. No hidden fees.",
  },
  {
    question: "What document formats are supported?",
    answer: "We support PDFs, DOCX, TXT, and direct text copy-paste. More formats are coming soon!",
  },
  {
    question: "Is there a limit to how many quizzes I can create?",
    answer: "Free plans have a daily limit, while Pro and Premium plans offer unlimited quiz creation to help you study without boundaries.",
  },
  {
    question: "Does the AI support languages other than English?",
    answer: "Yes, our AI supports Arabic, English, and several other languages for summarizing and answering questions.",
  },
]

export const testimonialsList = [
  {
    name: "Omar Sherif",
    role: "Engineering Student, Cairo University",
    avatar: "OS",
    stars: 5,
    text: "This platform completely changed how I prepare for exams. The instant summaries save me hours of reading, and the smart quizzes are perfect for testing my knowledge before midterms.",
  },
  {
    name: "Farida Ahmed",
    role: "Medicine Student, Ain Shams University",
    avatar: "FA",
    stars: 5,
    text: "Generating flashcards and custom quizzes from my massive PDF lectures is a lifesaver. The advanced AI model answers my academic questions in seconds with extreme accuracy.",
  },
  {
    name: "Youssef Hassan",
    role: "Computer Science Student, Alexandria University",
    avatar: "YH",
    stars: 5,
    text: "I love the clean interface and the deep reasoning explanations. Highly recommend the Pro plan for any college student looking to boost their study efficiency.",
  },
]

export type CheckoutFeatureItem = CheckoutFeature & {
  icon: LucideIcon
}

export type PaymentMethodOption = {
  icon: LucideIcon
  label: string
  value: PaymentMethod
}

export const paymentMethods: PaymentMethodOption[] = [
  { icon: CreditCard, label: "Card", value: "card" },
  { icon: Zap, label: "PayPal", value: "paypal" },
]

// Features shown for the selected checkout plan.
export const checkoutFeaturesByPlan: Record<CheckoutPlanId, CheckoutFeatureItem[]> = {
  pro: [
    {
      description: "Upload and analyze more documents.",
      icon: FileText,
      title: "50 Documents",
    },
    {
      description: "Get deeper, more accurate summaries.",
      icon: NotebookTabs,
      title: "Unlimited Summaries",
    },
    {
      description: "Generate quizzes in seconds.",
      icon: HelpCircle,
      title: "Unlimited Quizzes",
    },
    {
      description: "Organize your study schedule.",
      icon: Layers,
      title: "Study Plans",
    },
    {
      description: "Turn notes into review cards.",
      icon: Sparkles,
      title: "Flashcards Generation",
    },
    {
      description: "Use stronger AI for complex topics.",
      icon: Brain,
      title: "Advanced AI Models",
    },
  ],
  premium: [
    {
      description: "Study without document limits.",
      icon: FileText,
      title: "Unlimited Documents",
    },
    {
      description: "Ask AI freely under fair use.",
      icon: MessageCircle,
      title: "Unlimited AI Usage",
    },
    {
      description: "Handle difficult reasoning tasks.",
      icon: Brain,
      title: "Deep Reasoning Models",
    },
    {
      description: "Collaborate with classmates.",
      icon: Users,
      title: "Study Rooms",
    },
    {
      description: "Track progress and study patterns.",
      icon: BarChart3,
      title: "Learning Analytics",
    },
    {
      description: "Get faster processing when it matters.",
      icon: Clock,
      title: "Priority Processing",
    },
  ],
}

export const trustItems = [
  "Secure payments",
  "Cancel anytime",
  "30-day money-back guarantee",
]

export const guaranteeFeature = {
  description: "Try Learner risk-free. Cancel anytime.",
  icon: Network,
  title: "30-day money-back guarantee",
}