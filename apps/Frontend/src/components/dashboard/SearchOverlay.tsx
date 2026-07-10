"use client";

import React, { useEffect, useMemo, useRef, useState } from "react";
import { Search, X, Pencil } from "lucide-react";
import type { PageItem } from "@/app/dashboard/DashboardContent";

type SearchOverlayProps = {
  isOpen: boolean;
  pages: PageItem[];
  onClose: () => void;
  onSelectPage: (id: string) => void;
};

const SearchOverlay = ({ isOpen, pages, onClose, onSelectPage }: SearchOverlayProps) => {
  const [query, setQuery] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  const results = useMemo(() => {
    const value = query.trim().toLowerCase();
    if (!value) return pages;
    return pages.filter((page) => {
      const title = page.title.toLowerCase();
      const content = page.content.replace(/<[^>]*>/g, " ").toLowerCase();
      return title.includes(value) || content.includes(value);
    });
  }, [pages, query]);

  useEffect(() => {
    if (!isOpen) return;
    const timer = window.setTimeout(() => inputRef.current?.focus(), 0);
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.clearTimeout(timer);
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen, onClose]);

  useEffect(() => {
    if (!isOpen) setQuery("");
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="absolute inset-0 z-[80] flex items-start justify-center px-6 pt-[7vh] backdrop-blur-xs">
      <div className="w-full max-w-[680px] rounded-2xl border border-[#666565]/50 bg-[#111116]/95 p-7 text-white ">
        <div className="flex items-center gap-4 border-b border-white/10 pb-4">
          <Search className="h-6 w-6 text-white" />
          <input
            ref={inputRef}
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search your pages..."
            className="min-w-0 flex-1 bg-transparent text-[16px] text-white placeholder:text-[#9ca3af] outline-none"
          />
          <button
            type="button"
            onClick={onClose}
            className="rounded-full p-1 text-[#d1d5db] transition-colors hover:bg-white/10 hover:text-white"
            aria-label="Close search"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="pt-4">
          <p className="mb-2 text-[14px] text-[#9ca3af]">Results</p>
          <div className="max-h-[320px] overflow-y-auto">
            {results.map((page) => (
              <button
                type="button"
                key={page.id}
                onClick={() => {
                  onSelectPage(page.id);
                  onClose();
                }}
                className="flex w-full items-center gap-4 border-b border-white/10 px-2 py-3 text-left transition-colors hover:bg-white/[0.04]"
              >
                <Pencil className="h-5 w-5 shrink-0 fill-[#8b5cf6] text-[#8b5cf6]" />
                <span className="min-w-0 flex-1 truncate text-[15px] font-semibold text-white">{page.title || "Untitled"}</span>
                <span className="text-[14px] text-[#9ca3af]">Page</span>
              </button>
            ))}
          </div>

          {results.length === 0 && (
            <div className="flex flex-col items-center justify-center py-8 text-center text-[#9ca3af]">
              <Search className="mb-3 h-8 w-8" />
              <p className="text-[14px] text-white">No results found</p>
              <p className="text-[13px]">Try a different keyword</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SearchOverlay;
