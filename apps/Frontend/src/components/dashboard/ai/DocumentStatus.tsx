/* eslint-disable @typescript-eslint/no-unused-vars */
import React from "react";
import { AlertCircle, RefreshCw, Loader2, CheckCircle2 } from "lucide-react";
import { DocumentStatus as StatusType } from "@/types/api/documents";

interface DocumentStatusProps {
  status: StatusType | null;
  errorMessage?: string | null;
  onReprocess: () => void;
  isReprocessing: boolean;
}

export const DocumentStatus: React.FC<DocumentStatusProps> = ({
  status,
  errorMessage,
  onReprocess,
  isReprocessing,
}) => {
  if (!status || status === "ready") return null;

  const getStatusDisplay = () => {
    switch (status) {
      case "stored":
        return { text: "Stored, queuing ingestion...", color: "text-zinc-400" };
      case "parsing":
        return { text: "Extracting text content...", color: "text-blue-400" };
      case "chunking":
        return { text: "Splitting sections...", color: "text-indigo-400" };
      case "embedding":
        return { text: "Generating vector embeddings...", color: "text-purple-400" };
      case "failed":
        return { text: "Processing failed", color: "text-red-400" };
      default:
        return { text: "Processing...", color: "text-zinc-400" };
    }
  };

  const config = getStatusDisplay();

  return (
    <div className="flex flex-col gap-2.5 p-4 mx-4 mt-4 rounded-xl border border-zinc-800 bg-[#121212]/90 backdrop-blur-md">
      <div className="flex items-center gap-3">
        {status === "failed" ? (
          <AlertCircle className="h-5 w-5 text-red-400 shrink-0" />
        ) : (
          <Loader2 className="h-5 w-5 text-primary shrink-0 animate-spin" />
        )}
        <div className="flex-1 min-w-0">
          <span className="text-sm font-semibold text-zinc-100 block">
            Ingestion Pipeline Status
          </span>
          <span className={`text-xs block truncate font-medium ${config.color}`}>
            {config.text}
          </span>
        </div>
      </div>

      {status === "failed" && (
        <div className="flex flex-col gap-2 border-t border-zinc-800/80 pt-2.5 mt-1">
          {errorMessage && (
            <p className="text-xs text-zinc-500 leading-relaxed font-medium">
              Reason: {errorMessage}
            </p>
          )}
          <button
            onClick={onReprocess}
            disabled={isReprocessing}
            className="flex items-center justify-center gap-2 w-full h-8 rounded-lg bg-red-950/40 text-red-400 border border-red-900/40 text-xs font-semibold hover:bg-red-900/30 transition-all duration-200 disabled:opacity-50 cursor-pointer"
          >
            {isReprocessing ? (
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
            ) : (
              <RefreshCw className="h-3.5 w-3.5" />
            )}
            Reprocess Document
          </button>
        </div>
      )}
    </div>
  );
};
