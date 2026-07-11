/* eslint-disable @typescript-eslint/no-explicit-any, react-hooks/set-state-in-effect */
import { useState, useEffect, useCallback } from "react";
import { documentsService } from "@/services/documents.service";
import { DocumentListItem } from "@/types/api/documents";
import { ApiError } from "@/types/api/common";

export function useDocuments() {
  const [documents, setDocuments] = useState<DocumentListItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<ApiError | null>(null);
  const [activeDocumentId, setActiveDocumentId] = useState<string | null>(null);

  const fetchDocuments = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await documentsService.listDocuments();
      setDocuments(data.items);
      
      // Auto-select first document if nothing selected, or if selected is not in the list
      setActiveDocumentId((current) => {
        if (data.items.length === 0) return null;
        if (current && data.items.some((doc) => doc.id === current)) {
          return current;
        }
        return data.items[0].id;
      });
    } catch (err: any) {
      setError(err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const activeDocument = documents.find((doc) => doc.id === activeDocumentId) || null;

  return {
    documents,
    isLoading,
    error,
    activeDocumentId,
    activeDocument,
    setActiveDocumentId,
    refreshDocuments: fetchDocuments,
  };
}
