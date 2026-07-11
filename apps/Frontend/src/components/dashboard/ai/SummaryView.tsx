/* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars */
import React, { useState } from "react";
import { aiService } from "@/services/ai.service";
import { AIResponse, Citation } from "@/types/api/ai";
import { FileText, Loader2, Sparkles, BookOpen } from "lucide-react";
import { CitationList } from "./CitationList";
import { toast } from "sonner";

interface SummaryViewProps {
  documentId: string | null;
  sessionId: string | null;
  disabled: boolean;
  activePageId?: string;
  activePageContent?: string;
  onUpdatePage?: (id: string, updates: { content: string }) => void;
}

const markdownToHtml = (markdown: string): string => {
  let html = markdown;
  
  // Replace headers: ### text -> <h3>text</h3>
  html = html.replace(/^### (.*?)$/gm, '<h3>$1</h3>');
  html = html.replace(/^## (.*?)$/gm, '<h2>$1</h2>');
  html = html.replace(/^# (.*?)$/gm, '<h1>$1</h1>');
  
  // Bold: **text** -> <strong>text</strong>
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  
  // Lists: - item or * item
  const lines = html.split('\n');
  let inList = false;
  const resultLines: string[] = [];
  
  for (const line of lines) {
    const trimmed = line.trim();
    if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
      if (!inList) {
        resultLines.push('<ul>');
        inList = true;
      }
      const itemText = trimmed.substring(2);
      resultLines.push(`<li>${itemText}</li>`);
    } else {
      if (inList) {
        resultLines.push('</ul>');
        inList = false;
      }
      if (trimmed) {
        if (!trimmed.startsWith('<h') && !trimmed.startsWith('<u') && !trimmed.startsWith('<l')) {
          resultLines.push(`<p>${trimmed}</p>`);
        } else {
          resultLines.push(trimmed);
        }
      } else {
        resultLines.push('<p></p>');
      }
    }
  }
  if (inList) {
    resultLines.push('</ul>');
  }
  
  return resultLines.join('\n');
};

export const SummaryView: React.FC<SummaryViewProps> = ({
  documentId,
  sessionId,
  disabled,
  activePageId,
  activePageContent,
  onUpdatePage,
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState<AIResponse | null>(null);
  const [style, setStyle] = useState<"bullet_points" | "paragraph">("bullet_points");
  const [size, setSize] = useState<"concise" | "medium" | "detailed">("medium");
  const [language, setLanguage] = useState<"ar" | "en">("ar");

  const handleGenerateSummary = async () => {
    if (!documentId || !sessionId || isLoading || disabled) return;

    setIsLoading(true);
    setResponse(null);
    try {
      const summaryRes = await aiService.generateSummary(documentId, {
        session_id: sessionId,
        language,
        summary_style: style,
        summary_size: size,
      });
      setResponse(summaryRes);
    } catch (err: any) {
      toast.error(err.message || "Failed to generate summary.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateSummaryInPage = async () => {
    if (!documentId || !sessionId || isLoading || disabled) return;
    if (!activePageId || !onUpdatePage) {
      toast.error("Please select a page first.");
      return;
    }

    setIsLoading(true);
    setResponse(null);
    try {
      const summaryRes = await aiService.generateSummary(documentId, {
        session_id: sessionId,
        language,
        summary_style: style,
        summary_size: size,
      });
      setResponse(summaryRes);
      
      if (summaryRes.message) {
        const summaryHtml = markdownToHtml(summaryRes.message);
        const existingContent = activePageContent || "";
        const separator = existingContent ? '<p></p><hr><p></p>' : '';
        const newContent = existingContent + separator + summaryHtml;
        onUpdatePage(activePageId, { content: newContent });
        toast.success("Summary successfully inserted into page!");
      }
    } catch (err: any) {
      toast.error(err.message || "Failed to generate summary.");
    } finally {
      setIsLoading(false);
    }
  };

  const renderContent = (content: string) => {
    return content.split("\n").map((line, idx) => {
      const trimmed = line.trim();
      if (!trimmed) return <div key={idx} className="h-2" />;

      // Parse bold elements (**text**) safely
      const parts = line.split(/(\*\*.*?\*\*)/g);
      const elements = parts.map((part, pIdx) => {
        if (part.startsWith("**") && part.endsWith("**")) {
          return (
            <strong key={pIdx} className="font-bold text-zinc-100">
              {part.slice(2, -2)}
            </strong>
          );
        }
        return part;
      });

      // Render bullet list items
      if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
        const listText = line.substring(2);
        return (
          <li key={idx} className="ml-4 list-disc text-sm text-zinc-300 leading-relaxed font-medium mb-1.5">
            {listText}
          </li>
        );
      }

      return (
        <p key={idx} className="text-sm text-zinc-300 leading-relaxed font-medium mb-2.5">
          {elements}
        </p>
      );
    });
  };

  return (
    <div className="flex-1 overflow-y-auto px-5 py-4 flex flex-col gap-4 scrollbar-hide">
      {/* Configuration Header Card */}
      <div className="p-4 rounded-xl border border-zinc-800 bg-zinc-900/30 backdrop-blur-md flex flex-col gap-3">
        <div className="flex items-center justify-between gap-3">
          <div className="flex flex-col">
            <span className="text-sm font-bold text-zinc-200">Document Summarizer</span>
            <span className="text-xs text-zinc-500 font-medium">Condense the context into study formats</span>
          </div>
          <BookOpen className="h-5 w-5 text-primary/80" />
        </div>

        <div className="grid grid-cols-3 gap-2 mt-1">
          {/* Format Selection */}
          <div className="flex flex-col gap-1">
            <label htmlFor="summary-format" className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider">Format</label>
            <select
              id="summary-format"
              value={style}
              onChange={(e) => setStyle(e.target.value as any)}
              className="h-9 px-1 rounded-lg border border-zinc-800 bg-zinc-950 text-[10px] text-zinc-300 outline-none cursor-pointer"
            >
              <option value="bullet_points">Bullet Points</option>
              <option value="paragraph">Paragraph</option>
            </select>
          </div>

          {/* Size Selection */}
          <div className="flex flex-col gap-1">
            <label htmlFor="summary-size" className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider">Size</label>
            <select
              id="summary-size"
              value={size}
              onChange={(e) => setSize(e.target.value as any)}
              className="h-9 px-1 rounded-lg border border-zinc-800 bg-zinc-950 text-[10px] text-zinc-300 outline-none cursor-pointer"
            >
              <option value="concise">Small</option>
              <option value="medium">Medium</option>
              <option value="detailed">Large</option>
            </select>
          </div>

          {/* Language Selection */}
          <div className="flex flex-col gap-1">
            <label htmlFor="summary-language" className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider">Language</label>
            <select
              id="summary-language"
              value={language}
              onChange={(e) => setLanguage(e.target.value as any)}
              className="h-9 px-1 rounded-lg border border-zinc-800 bg-zinc-950 text-[10px] text-zinc-300 outline-none cursor-pointer"
            >
              <option value="ar">العربية</option>
              <option value="en">English</option>
            </select>
          </div>
        </div>

        <div className="flex flex-col gap-2 mt-2">
          <button
            onClick={handleGenerateSummary}
            disabled={disabled || isLoading}
            className="flex items-center justify-center gap-2 h-9 w-full rounded-full bg-primary text-white text-xs font-semibold hover:bg-primary-dark transition-all hover:scale-[1.01] active:scale-[0.99] disabled:opacity-40 disabled:scale-100 disabled:cursor-not-allowed cursor-pointer"
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Sparkles className="h-4 w-4" />
            )}
            Generate Summary
          </button>

          <button
            onClick={handleGenerateSummaryInPage}
            disabled={disabled || isLoading || !activePageId}
            className="flex items-center justify-center gap-2 h-9 w-full rounded-full bg-purple-950/60 border border-purple-500/30 text-white text-xs font-semibold hover:bg-purple-900/80 transition-all hover:scale-[1.01] active:scale-[0.99] disabled:opacity-40 disabled:scale-100 disabled:cursor-not-allowed cursor-pointer"
            title={!activePageId ? "Select a page to write summary" : "Generate and write summary directly to page content"}
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <FileText className="h-4 w-4" />
            )}
            Generate Summary in Page
          </button>
        </div>
      </div>

      {/* Summary Output */}
      {isLoading && (
        <div className="flex-1 flex flex-col items-center justify-center gap-2.5 text-zinc-500 min-h-[160px]">
          <Loader2 className="h-6 w-6 animate-spin text-primary" />
          <span className="text-xs font-semibold tracking-wide">
            Analyzing document structure...
          </span>
        </div>
      )}

      {response && (
        <div className="p-5 rounded-2xl border border-zinc-800 bg-zinc-900/40 backdrop-blur-md shadow-md animate-fade-in">
          <div className="flex flex-col">
            {response.error ? (
              <p className="text-sm text-red-400 font-semibold">{response.error}</p>
            ) : (
              <>
                {renderContent(response.message)}
                {response.citations && response.citations.length > 0 && (
                  <CitationList citations={response.citations} />
                )}
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
