import { backendClient } from "./backend-client";
import { QuizSubmissionRequest, QuizSubmissionResponse } from "@/types/api/quiz";

export const quizService = {
  async submitQuiz(quizId: string, payload: QuizSubmissionRequest): Promise<QuizSubmissionResponse> {
    return backendClient.post<QuizSubmissionResponse>(`/api/v1/documents/quizzes/${quizId}/submit`, payload);
  }
};
