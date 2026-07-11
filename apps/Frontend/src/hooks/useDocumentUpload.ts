/* eslint-disable @typescript-eslint/no-explicit-any */
import { useState } from "react";
import { documentsService } from "@/services/documents.service";
import { ApiError } from "@/types/api/common";

interface UseDocumentUploadOptions {
  onUploadSuccess?: (documentId: string) => void;
}

export function useDocumentUpload(options?: UseDocumentUploadOptions) {
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const uploadFile = async (file: File): Promise<string | null> => {
    setIsUploading(true);
    setError(null);

    // 1. Validation
    if (file.type !== "application/pdf" && !file.name.toLowerCase().endsWith(".pdf")) {
      setError("Only PDF files are supported.");
      setIsUploading(false);
      return null;
    }

    const MAX_SIZE_MB = 10;
    if (file.size > MAX_SIZE_MB * 1024 * 1024) {
      setError(`File size exceeds the limit of ${MAX_SIZE_MB}MB.`);
      setIsUploading(false);
      return null;
    }

    try {
      const response = await documentsService.uploadDocument(file);
      setIsUploading(false);
      if (options?.onUploadSuccess) {
        options.onUploadSuccess(response.document_id);
      }
      return response.document_id;
    } catch (err: any) {
      const apiError: ApiError = err;
      setError(apiError.message || "Failed to upload document.");
      setIsUploading(false);
      return null;
    }
  };

  return {
    uploadFile,
    isUploading,
    error,
    clearError: () => setError(null),
  };
}
