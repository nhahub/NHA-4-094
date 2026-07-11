import React from "react";
import { QuizSubmissionResponse, GradedResponseItem } from "@/types/api/quiz";
import { CheckCircle2, XCircle, Award, RotateCcw } from "lucide-react";

interface QuizResultProps {
  result: QuizSubmissionResponse;
  onRetry: () => void;
}

export const QuizResult: React.FC<QuizResultProps> = ({ result, onRetry }) => {
  const getScoreColor = (pct: number) => {
    if (pct >= 80) return "text-emerald-400";
    if (pct >= 50) return "text-yellow-400";
    return "text-red-400";
  };

  return (
    <div className="flex flex-col gap-5.5">
      {/* Score Header Card */}
      <div className="p-5 rounded-2xl border border-zinc-800 bg-zinc-900/30 backdrop-blur-md flex flex-col items-center gap-2.5 text-center shadow-lg">
        <Award className="h-10 w-10 text-primary" />
        <div className="flex flex-col">
          <span className="text-xs font-bold text-zinc-500 uppercase tracking-wider">Quiz Completed</span>
          <span className={`text-4xl font-extrabold font-mono mt-1 ${getScoreColor(result.score_percentage)}`}>
            {result.score_percentage}%
          </span>
          <span className="text-xs text-zinc-400 font-semibold mt-1">
            Correct: {result.correct_count} / {result.total_questions} questions
          </span>
        </div>

        <button
          onClick={onRetry}
          className="flex items-center justify-center gap-2 h-9 px-6 rounded-full bg-zinc-900 border border-zinc-800 text-xs font-semibold text-zinc-300 hover:border-zinc-700 transition-all cursor-pointer mt-2"
        >
          <RotateCcw className="h-3.5 w-3.5" />
          Retake Quiz / Generate New
        </button>
      </div>

      {/* Graded Questions List */}
      <div className="flex flex-col gap-4">
        {result.responses.map((resp: GradedResponseItem, idx) => (
          <div
            key={resp.question_id || idx}
            className={`p-4 rounded-xl border ${
              resp.is_correct
                ? "border-emerald-950/40 bg-emerald-950/5 text-zinc-100"
                : "border-red-950/40 bg-red-950/5 text-zinc-100"
            }`}
          >
            <div className="flex items-start gap-3">
              {resp.is_correct ? (
                <CheckCircle2 className="h-5 w-5 text-emerald-400 shrink-0 mt-0.5" />
              ) : (
                <XCircle className="h-5 w-5 text-red-400 shrink-0 mt-0.5" />
              )}
              <div className="flex-1">
                <p className="text-sm font-semibold leading-relaxed mb-3">
                  {idx + 1}. {resp.question_text}
                </p>

                {/* Options List */}
                <div className="flex flex-col gap-2">
                  {resp.options.map((opt, optIdx) => {
                    const isSelected = resp.selected_option_id === optIdx;
                    const isCorrect = resp.correct_option_id === optIdx;

                    let optionStyle = "border-zinc-800 bg-zinc-900/30 text-zinc-400";
                    if (isSelected) {
                      optionStyle = resp.is_correct
                        ? "border-emerald-500/40 bg-emerald-950/40 text-emerald-200"
                        : "border-red-500/40 bg-red-950/40 text-red-200";
                    } else if (isCorrect) {
                      // Highlight correct answer if user missed it
                      optionStyle = "border-emerald-500/30 bg-emerald-950/20 text-emerald-400";
                    }

                    return (
                      <div
                        key={optIdx}
                        className={`flex items-center gap-3 px-3.5 py-2.5 rounded-lg border text-xs font-semibold ${optionStyle}`}
                      >
                        <div className="h-5 w-5 shrink-0 flex items-center justify-center rounded-full bg-zinc-950 border border-zinc-800 text-[10px] font-bold font-mono">
                          {String.fromCharCode(65 + optIdx)}
                        </div>
                        <span className="flex-1 leading-snug">{opt}</span>
                      </div>
                    );
                  })}
                </div>

                {/* Explanation */}
                {resp.explanation && (
                  <div className="mt-3.5 p-3 rounded-lg border border-zinc-800/60 bg-zinc-950/30 text-[11px] leading-relaxed text-zinc-400 font-medium">
                    <span className="font-bold text-zinc-300 block mb-1">Explanation</span>
                    {resp.explanation}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
