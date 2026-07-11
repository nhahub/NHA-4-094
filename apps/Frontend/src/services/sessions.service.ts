import { backendClient } from "./backend-client";
import { SessionResponse, SessionMessagesResponse } from "@/types/api/sessions";

export const sessionsService = {
  async createDocumentSession(documentId: string): Promise<SessionResponse> {
    return backendClient.post<SessionResponse>(`/api/v1/documents/${documentId}/sessions`);
  },

  async getSessionMessages(documentId: string, sessionId: string): Promise<SessionMessagesResponse> {
    return backendClient.get<SessionMessagesResponse>(`/api/v1/documents/${documentId}/sessions/${sessionId}/messages`);
  },

  async getDocumentSessions(documentId: string): Promise<SessionResponse[]> {
    return backendClient.get<SessionResponse[]>(`/api/v1/documents/${documentId}/sessions`);
  }
};
