"use client";

import React, { useState } from "react";
import { ChevronDown, Plus, Send, Pencil, Search } from "lucide-react";
import type { PageItem } from "@/app/dashboard/DashboardContent";

type DashboardHomeProps = {
  displayName: string;
  pages: PageItem[];
  onOpenSearch: () => void;
  onSelectPage: (id: string) => void;
};

const DashboardHome = ({ displayName, pages, onOpenSearch, onSelectPage }: DashboardHomeProps) => {
  const firstName = displayName.split(" ")[0] || displayName;
  const recentPages = pages.slice(0, 3);
  const [isRecentExpanded, setIsRecentExpanded] = useState(true);

  return (
    <main className="flex-1 h-[calc(100vh-40px)] overflow-y-auto text-white my-[20px] border border-[#666565]/50 rounded-lg px-[45px] py-[35px] mx-[20px] relative">
      <div className="absolute top-[25px] left-[45px] right-[45px] flex items-center justify-between z-10">
        <span className="text-[14px] text-[#9ca3af] font-light">../ home</span>
        <span className="text-[#9ca3af]">...</span>
      </div>

      <div className="mx-auto flex min-h-full w-full max-w-[860px] flex-col items-center justify-center py-16">
        <h1 className="text-center text-[28px] font-semibold leading-tight text-white">
          Welcome Back, {firstName}
        </h1>

        <button
          type="button"
          onClick={onOpenSearch}
          className="mt-9 pl-5 flex w-full max-w-[560px] items-center gap-3 rounded-full border border-[#666565]/50 px-3 py-2 text-left text-[#9ca3af] transition-colors hover:border-[#8b5cf6]/70 hover:bg-white/[0.06]"
        >
          <span className="min-w-0 flex-1 text-[14px]">Search About Any Page...</span>
          <span className="flex h-8 w-8 items-center justify-center rounded-full bg-white/10 text-white">
            <Search className="h-4 w-4" />
          </span>
        </button>

        <section className="mt-10 w-full">
          <button
            type="button"
            onClick={() => setIsRecentExpanded(!isRecentExpanded)}
            className="mb-4 flex items-center gap-2 text-[15px] text-[#d1d5db] hover:text-white transition-colors"
          >
            <span>Recent</span>
            <ChevronDown className={`h-4 w-4 text-[#9ca3af] transition-transform duration-200 ${isRecentExpanded ? "" : "-rotate-90"}`} />
          </button>

          {isRecentExpanded && (
            recentPages.length > 0 ? (
              <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
                {recentPages.map((page) => (
                  <button
                    type="button"
                    key={page.id}
                    onClick={() => onSelectPage(page.id)}
                    className="group overflow-hidden rounded-lg border border-[#666565]/50 bg-white/[0.04] text-left transition-colors hover:border-[#8b5cf6]/70 hover:bg-white/[0.06]"
                  >
                    <div className="h-[82px] bg-gradient-to-br from-white/20 via-white/10 to-[#8b5cf6]/10" />
                    <div className="relative px-6 pb-5 pt-9">
                      <span className="absolute -top-6 left-6 flex h-12 w-12 items-center justify-center rounded-full bg-[#211336] text-[#8b5cf6]">
                        <Pencil className="h-6 w-6 fill-[#8b5cf6]" />
                      </span>
                      <h4 className="truncate text-[18px] font-semibold text-white">{page.title || "Untitled"}</h4>
                    </div>
                  </button>
                ))}
              </div>
            ) : (
              <button
                type="button"
                onClick={onOpenSearch}
                className="flex w-full items-center justify-center gap-3 rounded-lg border border-[#666565]/50 py-10 text-[#9ca3af] hover:text-white"
              >
                <Search className="h-5 w-5" />
                No recent pages yet
              </button>
            )
          )}
        </section>
      </div>
    </main>
  );
};

export default DashboardHome;
