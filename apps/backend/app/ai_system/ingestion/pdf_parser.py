import io
import fitz  # PyMuPDF
from typing import List, Dict, Any

def parse_pdf(file_bytes: bytes) -> List[Dict[str, Any]]:
    """
    Extracts text page-by-page from raw PDF file bytes using PyMuPDF (fitz).
    
    Returns:
        List of dicts, each with "page_number" (1-indexed) and "text" (extracted string).
        
    Raises:
        ValueError: If PDF is corrupt, has no pages, or contains no extractable text.
    """
    try:
        # PyMuPDF can open directly from a memory stream
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        
        pages_data = []
        total_extracted_chars = 0
        
        for idx in range(len(doc)):
            page = doc.load_page(idx)
            # Extract text from the page. PyMuPDF is much better at extracting
            # text from complex layouts and mixed fonts than pypdf.
            text = page.get_text() or ""
            
            pages_data.append({
                "page_number": idx + 1,
                "text": text
            })
            total_extracted_chars += len(text.strip())
            
        doc.close()
            
        if not pages_data:
            raise ValueError("The PDF document does not contain any pages.")
            
        if total_extracted_chars == 0:
            raise ValueError("Could not extract readable text from this PDF. It might be a scanned image requiring OCR.")
            
        return pages_data
        
    except Exception as e:
        if isinstance(e, ValueError):
            raise e
        raise ValueError(f"Failed to parse PDF document: {str(e)}")
