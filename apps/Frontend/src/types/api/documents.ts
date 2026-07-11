export type DocumentStatus = "stored" | "parsing" | "chunking" | "embedding" | "ready" | "failed";

export interface DocumentListItem {
  id: string;
  original_filename: string;
  upload_status: DocumentStatus;
  page_count?: number;
  chunk_count?: number;
  error_message?: string | null;
  created_at: string;
  updated_at?: string | null;
}

export interface DocumentListResponse {
  items: DocumentListItem[];
  total: number;
}

export interface UploadResponse {
  document_id: string;
  status: string;
  message: string;
}

export interface StatusResponse {
  document_id: string;
  status: DocumentStatus;
  page_count?: number | null;
  chunk_count?: number | null;
  error_message?: string | null;
  processing_time_seconds?: number | null;
}
