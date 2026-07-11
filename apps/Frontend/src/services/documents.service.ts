import { backendClient } from "./backend-client";
import { DocumentListResponse, UploadResponse, StatusResponse } from "@/types/api/documents";

export const documentsService = {
  async listDocuments(): Promise<DocumentListResponse> {
    return backendClient.get<DocumentListResponse>("/api/v1/documents");
  },

  async uploadDocument(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append("file", file);
    return backendClient.post<UploadResponse>("/api/v1/documents/upload", formData);
  },

  async getDocumentStatus(documentId: string): Promise<StatusResponse> {
    return backendClient.get<StatusResponse>(`/api/v1/documents/${documentId}/status`);
  },

  async reprocessDocument(documentId: string): Promise<StatusResponse> {
    return backendClient.post<StatusResponse>(`/api/v1/documents/${documentId}/reprocess`);
  }
};
