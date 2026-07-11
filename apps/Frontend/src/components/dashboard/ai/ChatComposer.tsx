import React, { useState } from "react";
import { Send, Square } from "lucide-react";

interface ChatComposerProps {
  onSend: (text: string) => void;
  isSending: boolean;
  disabled: boolean;
  onStop: () => void;
}

export const ChatComposer: React.FC<ChatComposerProps> = ({
  onSend,
  isSending,
  disabled,
  onStop,
}) => {
  const [text, setText] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim() || disabled || isSending) return;
    onSend(text.trim());
    setText("");
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="p-4 bg-zinc-950/60 border-t border-zinc-800/80 backdrop-blur-md"
    >
      <div className="flex items-center gap-2 rounded-full border border-zinc-800 bg-zinc-900/80 px-4 py-2 focus-within:border-primary/60 transition-colors">
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          disabled={disabled && !isSending}
          placeholder={disabled ? "Select a ready document to chat..." : "Ask AI about this document..."}
          className="min-w-0 flex-1 bg-transparent text-sm text-zinc-200 placeholder-zinc-500 outline-none disabled:cursor-not-allowed"
        />

        {isSending ? (
          <button
            type="button"
            onClick={onStop}
            className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-red-950 text-red-400 hover:bg-red-900 transition-colors cursor-pointer"
            title="Stop generation"
          >
            <Square className="h-3.5 w-3.5 fill-red-400" />
          </button>
        ) : (
          <button
            type="submit"
            disabled={disabled || !text.trim()}
            className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-white hover:bg-primary-dark transition-all hover:scale-105 active:scale-95 disabled:opacity-30 disabled:scale-100 disabled:cursor-not-allowed cursor-pointer"
            title="Send query"
          >
            <Send className="h-3.5 w-3.5" />
          </button>
        )}
      </div>
    </form>
  );
};
