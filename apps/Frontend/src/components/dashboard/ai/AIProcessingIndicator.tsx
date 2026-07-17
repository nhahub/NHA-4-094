import React from "react";
import { AIProcessingOrb } from "./AIProcessingOrb";
import { WordRevealText } from "./WordRevealText";

interface AIProcessingIndicatorProps {
  stage: string | null;
  progress: number;
  status: string | null; // "started", "progress", "completed", "failed", "cancelled"
  completedStages: string[];
  publicRequestSummary?: string | null;
  metadata?: Record<string, any>;
}

function getDisplaySentence(
  stage: string,
  publicRequestSummary?: string | null,
  metadata?: Record<string, any>
): string {
  const stageLower = stage.toLowerCase();

  // If planning and we have a concise public request summary, show it!
  if (stageLower === "planning" && publicRequestSummary) {
    return publicRequestSummary.length > 70
      ? publicRequestSummary.slice(0, 67) + "..."
      : publicRequestSummary;
  }

  switch (stageLower) {
    case "document_check":
      return "Checking the selected document...";
    case "input_analysis":
      return "Understanding your request...";
    case "planning":
      return "Planning the best response...";
    case "personalization":
      return "Adapting the response to your learning preferences...";
    case "query_preparation":
      return "Preparing the document search...";
    case "retrieval":
      return "Searching the selected document...";
    case "reranking":
      return "Selecting the best evidence...";
    case "context_building":
      return "Preparing the document context...";
    case "generation":
      const taskType = metadata?.task_type;
      if (taskType === "explain") return "Writing your explanation...";
      if (taskType === "summary") return "Creating your summary...";
      if (taskType === "quiz") return "Creating your quiz...";
      if (taskType === "comparison_table") return "Building the comparison...";
      if (taskType === "flashcards") return "Creating your flashcards...";
      return "Writing your answer...";
    case "verification":
      return "Verifying accuracy and grounding...";
    case "refining":
      return "Refining the response...";
    case "citations":
      return "Linking the answer to its sources...";
    case "finalizing":
      return "Finalizing your answer...";
    case "failed":
      return metadata?.error_message || "An error occurred during processing.";
    case "cancelled":
      return "Operation cancelled by user.";
    default:
      return "Processing...";
  }
}

export const AIProcessingIndicator: React.FC<AIProcessingIndicatorProps> = ({
  stage,
  progress,
  status,
  completedStages,
  publicRequestSummary,
  metadata,
}) => {
  if (!stage || status === "completed") return null;

  const isFailed = status === "failed";
  const isCancelled = status === "cancelled";
  const activeStageLower = stage.toLowerCase();
  
  const sentence = getDisplaySentence(activeStageLower, publicRequestSummary, metadata);

  return (
    <div 
      className="flex items-center gap-3 py-1.5 px-1 select-none w-full"
      role="status"
      aria-live="polite"
    >
      {/* Small animated AI symbol */}
      <AIProcessingOrb status={status} />

      {/* Word-by-word reveal text */}
      <WordRevealText
        key={sentence} // Restart animation when stage text changes
        text={sentence}
        speed={45} // 45ms per word reveal
        className={`text-sm font-medium tracking-wide transition-colors duration-300 ${
          isFailed
            ? "text-red-400/90"
            : isCancelled
            ? "text-zinc-500"
            : "text-zinc-300/85" // approximately 85% opacity
        }`}
      />
    </div>
  );
};
