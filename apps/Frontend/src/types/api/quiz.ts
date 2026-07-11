export interface QuizQuestionPublic {
  id: string; // question UUID
  question_text: string;
  options: [string, string, string, string]; // exactly four options
  difficulty: "easy" | "medium" | "hard";
  concept?: string | null;
}

export interface QuizDetail {
  quiz_id: string; // quiz UUID
  title: string;
  questions: QuizQuestionPublic[];
}

export interface QuizRequest {
  session_id: string;
  language?: "ar" | "en";
  user_level?: string;
  difficulty?: "easy" | "medium" | "hard" | null;
  number_of_questions?: number;
  question_type?: "multiple_choice" | "true_false" | "short_answer" | "mixed" | null;
}

export interface QuizResponseItem {
  question_id: string;
  selected_option_id: number; // 0-based or 1-based index as returned by options
}

export interface QuizSubmissionRequest {
  attempt_number: number;
  idempotency_key: string;
  responses: QuizResponseItem[];
}

export interface GradedResponseItem {
  question_id: string;
  selected_option_id: number;
  is_correct: boolean;
  correct_option_id: number;
  explanation: string;
  question_text: string;
  options: [string, string, string, string];
}

export interface QuizSubmissionResponse {
  status: "completed" | "failed";
  attempt_id: string;
  correct_count: number;
  total_questions: number;
  score_percentage: number;
  responses: GradedResponseItem[];
}
