/* eslint-disable @typescript-eslint/no-unused-vars */
import React from "react";
import { Sparkles, Loader2, CheckCircle2, AlertCircle } from "lucide-react";

interface PipelineStatusProps {
  stage: string | null;
  progress: number;
  status: string | null; // "started", "completed", "failed"
}

export const PipelineStatus: React.FC<PipelineStatusProps> = ({
  stage,
  progress,
  status,
}) => {
  if (!stage || status === "completed" || status === "failed") return null;

  const getFriendlyStageName = (s: string) => {
    switch (s.toLowerCase()) {
      case "authentication":
        return "Authenticating Session";
      case "input_validation":
        return "Validating Query";
      case "planning":
        return "Planning Tasks";
      case "dag_routing":
        return "Routing Execution DAG";
      case "chat_answer":
        return "Generating Answer";
      case "explain":
        return "Formulating Explanation";
      case "summary":
        return "Creating Summary";
      case "quiz":
        return "Drafting Quiz";
      case "key_points":
        return "Extracting Key Points";
      case "comparison_table":
        return "Structuring Table";
      case "verification":
        return "Verifying Grounding";
      default:
        return s.charAt(0).toUpperCase() + s.slice(1);
    }
  };

  return (
    <div className="p-3.5 mx-4 mb-4 rounded-xl border border-zinc-800 bg-[#161616]/60 backdrop-blur-md flex flex-col gap-2">
      <div className="flex items-center justify-between text-xs font-semibold tracking-wide text-zinc-400">
        <div className="flex items-center gap-2">
          <Loader2 className="h-3.5 w-3.5 text-primary animate-spin" />
          <span>{getFriendlyStageName(stage)}</span>
        </div>
        <span>{Math.round(progress)}%</span>
      </div>
      
      {/* Progress Bar */}
      <div className="w-full h-1.5 rounded-full bg-zinc-950 overflow-hidden">
        <div
          className="h-full rounded-full bg-gradient-to-r from-primary to-purple-500 transition-all duration-300 ease-out"
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  );
};
