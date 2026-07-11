import React from "react";
import { Bookmark } from "lucide-react";
import { Citation } from "@/types/api/ai";

interface CitationListProps {
  citations: Citation[];
}

export const CitationList: React.FC<CitationListProps> = ({ citations }) => {
  if (!citations || citations.length === 0) return null;

  // De-duplicate citations by page_number
  const uniqueCitations = citations.reduce<Citation[]>((acc, current) => {
    const exists = acc.find(item => item.page_number === current.page_number);
    if (!exists) {
      acc.push(current);
    }
    return acc;
  }, []);

  return (
    <div className="mt-3.5 pt-3 border-t border-zinc-800/60">
      <span className="text-[11px] font-semibold text-zinc-500 uppercase tracking-wider block mb-2">
        Sources & Grounding References
      </span>
      <div className="flex flex-wrap gap-2">
        {uniqueCitations.map((cit, idx) => (
          <div
            key={cit.chunk_id || idx}
            className="group relative flex items-center gap-1.5 px-3 py-1 rounded-full border border-zinc-800 bg-zinc-950/60 text-xs font-semibold text-zinc-400 hover:border-zinc-700 hover:text-zinc-200 transition-all duration-200 cursor-help"
          >
            <Bookmark className="h-3 w-3 text-primary/80" />
            <span>Page {cit.page_number}</span>
            
            {/* Tooltip for snippet/section title */}
            {(cit.section_title || cit.snippet) && (
              <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-64 p-2.5 rounded-lg border border-zinc-800 bg-zinc-950/95 text-[11px] leading-relaxed text-zinc-300 font-medium opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none shadow-xl z-55">
                {cit.section_title && (
                  <p className="font-bold text-zinc-100 mb-1">{cit.section_title}</p>
                )}
                {cit.snippet && (
                  <p className="italic text-zinc-400">&quot;{cit.snippet}&quot;</p>
                )}
                {cit.score !== undefined && (
                  <p className="text-[9px] text-zinc-600 mt-1 font-mono">Similarity: {Number(cit.score).toFixed(4)}</p>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
