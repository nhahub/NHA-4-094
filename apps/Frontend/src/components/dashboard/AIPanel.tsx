import React from 'react';
import { Sparkles, Send, Pencil, Plus } from 'lucide-react';

const AIPanel = () => {
  return (
    <aside className="w-[420px] h-[calc(100vh-40px)] ml-0 bg-background/20 backdrop-blur-sm border border-[#666565]/50 rounded-lg flex flex-col m-[20px] relative shrink-0 overflow-hidden">

      {/* ── Header ─────────────────────────────────────────────── */}
      <div className="px-6 pt-6 pb-4">
        <h4 className="text-[21px] font-semibold tracking-wide">
          Learner AI
        </h4>
      </div>

      {/* ── Scrollable Body ────────────────────────────────────── */}
      <div className="flex-1 overflow-y-auto px-5 pb-4 flex flex-col scrollbar-hide">

        {/* Feature Cards */}
        <div className="grid grid-cols-2 gap-3">
          {/* Summarize Card */}
          <button
            onClick={() => {}}
            className="group flex items-center justify-between rounded-[22px] border border-zinc-800/50 bg-[#121212] p-5 text-left transition-all duration-200 hover:border-zinc-700 hover:bg-[#161616]"
          >
            <div className="flex flex-col gap-1 pr-1">
              <span className="text-[17px] font-medium leading-none text-white tracking-tight">Summarize</span>
              <span className="text-[14px] text-zinc-500 leading-snug">
                You can summarize what you want
              </span>
            </div>
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-[#1c1c1c] text-white transition-colors group-hover:bg-[#252525]">
              <Pencil className="h-4.5 w-4.5" />
            </div>
          </button>

          {/* Quiz Maker Card */}
          <button
            onClick={() => {}}
            className="group flex items-center justify-between rounded-[22px] border border-zinc-800/50 bg-[#121212] p-5 text-left transition-all duration-200 hover:border-zinc-700 hover:bg-[#161616]"
          >
            <div className="flex flex-col gap-1 pr-1">
              <span className="text-[17px] font-medium leading-none text-white tracking-tight">Quiz Maker</span>
              <span className="text-[14px] text-zinc-500 leading-snug">
                You can summarize what you want
              </span>
            </div>
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-[#1c1c1c] text-white transition-colors group-hover:bg-[#252525]">
              <Pencil className="h-4.5 w-4.5" />
            </div>
          </button>
        </div>

        {/* ── Hero Text ──────────────────────────────────────── */}
        <div className="flex flex-1 flex-col items-center justify-center py-10">
          <h4 className="text-center text-[36px] font-semibold leading-tight tracking-tight">
            Tell Us What<br />You Need.
          </h4>

          {/* Suggestion Pills */}
          <div className="mt-6 flex flex-wrap items-center justify-center gap-2">
            <button
              onClick={() => {}}
              className="flex items-center gap-1.5 rounded-full border border-zinc-700/60 bg-transparent px-4 py-1.5 font-medium text-zinc-400 transition-all duration-200 hover:border-zinc-500 hover:text-zinc-200"
            >
              Summarize
              <Plus className="h-4 w-4" />
            </button>
            <button
              onClick={() => {}}
              className="flex items-center gap-1.5 rounded-full border border-zinc-700/60 bg-transparent px-4 py-1.5 font-medium text-zinc-400 transition-all duration-200 hover:border-zinc-500 hover:text-zinc-200"
            >
              Generate
              <Plus className="h-4 w-4" />
            </button>
          </div>
          <div className="mt-2 flex items-center justify-center">
            <button
              onClick={() => {}}
              className="flex items-center gap-1.5 rounded-full border border-zinc-700/60 bg-transparent px-4 py-1.5 font-medium text-zinc-400 transition-all duration-200 hover:border-zinc-500 hover:text-zinc-200"
            >
              Ask
              <Plus className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      {/* ── Chat Input Bar ─────────────────────────────────────── */}
      <div className="px-4 pb-4 pt-2">
        <div className="flex items-center gap-2 rounded-full border bg-zinc-900/80 px-2 py-1.5 transition-colors border-zinc-700">
          {/* Plus button */}
          <button
            onClick={() => {}}
            className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-zinc-800 text-zinc-400 transition-colors hover:bg-zinc-700 hover:text-zinc-200"
          >
            <Plus className="h-4 w-4" />
          </button>

          {/* Text input */}
          <input
            type="text"
            placeholder="tell us..."
            className="min-w-0 flex-1 bg-transparent text-sm text-zinc-200 placeholder-zinc-600 outline-none"
          />

          {/* Send button */}
          <button
            onClick={() => {}}
            className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-zinc-800 text-zinc-400 transition-colors hover:bg-zinc-700 hover:text-zinc-200"
          >
            <Send className="h-4 w-4" />
          </button>
        </div>
      </div>

    </aside>
  );
};

export default AIPanel;
