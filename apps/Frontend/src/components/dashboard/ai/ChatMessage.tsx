import React from "react";
import { MessageItem } from "@/types/api/sessions";
import { Citation } from "@/types/api/ai";
import { CitationList } from "./CitationList";

interface ChatMessageProps {
  message: MessageItem;
  citations?: Citation[];
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message, citations }) => {
  const isUser = message.role === "user";

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
          <li key={idx} className="ml-4 list-disc text-sm text-zinc-300 leading-relaxed font-medium mb-1">
            {listText}
          </li>
        );
      }

      return (
        <p key={idx} className="text-sm text-zinc-300 leading-relaxed font-medium mb-2">
          {elements}
        </p>
      );
    });
  };

  return (
    <div className={`flex flex-col gap-1.5 max-w-[85%] ${isUser ? "self-end items-end" : "self-start items-start"}`}>
      {/* Bubble container */}
      <div
        className={`px-4.5 py-3 rounded-2xl transition-all duration-200 shadow-md ${
          isUser
            ? "bg-primary text-white rounded-br-none font-semibold text-sm"
            : "bg-zinc-900/60 border border-zinc-800 text-zinc-200 rounded-bl-none"
        }`}
      >
        {isUser ? (
          <p className="text-sm leading-relaxed font-medium whitespace-pre-wrap">{message.content}</p>
        ) : (
          <div className="flex flex-col">
            {renderContent(message.content)}
            {citations && citations.length > 0 && <CitationList citations={citations} />}
          </div>
        )}
      </div>
      
      {/* Timestamp info */}
      <span className="text-[10px] text-zinc-500 font-mono px-1">
        {new Date(message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
      </span>
    </div>
  );
};
