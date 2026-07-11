import React, { useRef } from "react";
import { FileUp, Loader2, FileText } from "lucide-react";
import { DocumentListItem } from "@/types/api/documents";

interface DocumentControlsProps {
  documents: DocumentListItem[];
  activeDocumentId: string | null;
  onSelectDocument: (id: string) => void;
  onUploadFile: (file: File) => void;
  isUploading: boolean;
  uploadError: string | null;
}

export const DocumentControls: React.FC<DocumentControlsProps> = ({
  documents,
  activeDocumentId,
  onSelectDocument,
  onUploadFile,
  isUploading,
  uploadError,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onUploadFile(e.target.files[0]);
    }
  };

  const triggerUpload = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="flex flex-col gap-3 p-4 bg-zinc-900/40 border-b border-zinc-800/80 backdrop-blur-md">
      <div className="flex items-center justify-between gap-3">
        {/* Document Selector */}
        <div className="flex-1 relative">
          <label htmlFor="document-selector" className="sr-only">Select Document</label>
          <select
            id="document-selector"
            value={activeDocumentId || ""}
            onChange={(e) => onSelectDocument(e.target.value)}
            disabled={isUploading}
            className="w-full h-10 px-3 pr-8 rounded-full border border-zinc-800 bg-zinc-950 text-sm text-zinc-200 outline-none appearance-none cursor-pointer transition-all duration-200 hover:border-zinc-700 focus:border-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {documents.length === 0 ? (
              <option value="" disabled>No documents uploaded</option>
            ) : (
              documents.map((doc) => (
                <option key={doc.id} value={doc.id}>
                  {doc.original_filename}
                </option>
              ))
            )}
          </select>
          <div className="absolute right-3.5 top-1/2 -translate-y-1/2 pointer-events-none text-zinc-500">
            <FileText className="h-4.5 w-4.5" />
          </div>
        </div>

        {/* Upload Button */}
        <div>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".pdf,application/pdf"
            className="hidden"
            aria-label="Upload PDF Document"
          />
          <button
            onClick={triggerUpload}
            disabled={isUploading}
            className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/20 text-primary border border-primary/30 transition-all duration-200 hover:bg-primary/30 hover:scale-105 active:scale-95 disabled:opacity-50 disabled:scale-100 cursor-pointer"
            title="Upload PDF Document"
          >
            {isUploading ? (
              <Loader2 className="h-4.5 w-4.5 animate-spin" />
            ) : (
              <FileUp className="h-4.5 w-4.5" />
            )}
          </button>
        </div>
      </div>

      {/* Upload Error display */}
      {uploadError && (
        <span className="text-xs text-red-400 font-medium px-2 animate-pulse">
          {uploadError}
        </span>
      )}
    </div>
  );
};
