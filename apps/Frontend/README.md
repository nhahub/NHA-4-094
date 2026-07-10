# 🎨 AI Study Platform - Frontend

Frontend application for the AI Study Platform, built to provide an interactive and accessible learning experience for students.

---

## 📖 Overview

The frontend delivers a modern study environment where users can:

- Organize study materials and notes
- Upload learning resources
- Interact with AI assistants
- Generate quizzes and summaries
- Track their learning progress
- Access personalized educational tools

The application focuses on simplicity, accessibility, and a responsive user experience across all devices.

---

## 🚀 Features

### 🔐 Authentication
- User registration and login
- Secure session management
- Profile settings

### 📚 Study Workspace
- Subject and course organization
- Notes management
- Learning resources dashboard
- Personalized study environment

### 📄 Document Management
- Upload PDF, DOCX, and TXT files
- Manage study materials
- Connect documents with AI features

### 🤖 AI Interaction
- Real-time AI chat interface
- AI-generated summaries
- Adaptive quizzes
- Step-by-step explanations
- Personalized learning assistance

### 📊 Progress Tracking
- Quiz results
- Learning analytics
- Study activity monitoring

### ♿ Accessibility
- Keyboard navigation
- Screen reader support
- RTL support
- Responsive design
- Simplified learning mode

---

## 🛠 Tech Stack

### Core Technologies
- Next.js
- React
- TypeScript

### UI & Styling
- Tailwind CSS
- shadcn/ui
- Lucide Icons

### State Management
- Zustand

### Forms & Validation
- React Hook Form
- Zod

### Backend Integration
- Supabase Client
- REST APIs

---

## 📂 Project Structure

```bash
frontend/

├── app/
├── components/
│   ├── ui/
│   ├── auth/
│   ├── dashboard/
│   ├── workspace/
│   ├── chat/
│   └── quiz/
│
├── hooks/
├── lib/
├── services/
├── types/
├── public/
└── styles/
````

---

## ⚙️ Getting Started

Install dependencies:

```bash
npm install
```

Run the development server:

```bash
npm run dev
```

Build for production:

```bash
npm run build
```

---

## 🔐 Environment Variables

```env
NEXT_PUBLIC_SUPABASE_URL=

NEXT_PUBLIC_SUPABASE_ANON_KEY=

NEXT_PUBLIC_API_BASE_URL=
```

---

## 🎯 Frontend Goals

* Deliver a clean and intuitive user experience
* Support accessibility for all learners
* Maintain responsive layouts across devices
* Provide seamless integration with AI services
* Build reusable and scalable UI components

---