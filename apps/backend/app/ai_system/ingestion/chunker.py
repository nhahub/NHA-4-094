from typing import List, Dict, Any

def chunk_document(
    pages: List[Dict[str, Any]],
    chunk_size: int = 800,
    chunk_overlap: int = 150
) -> List[Dict[str, Any]]:
    """
    Splits document pages into paragraph-aware text chunks.
    Tracks starting and ending pages for each chunk.
    
    Args:
        pages: List of dictionaries containing page_number and cleaned text.
        chunk_size: Target maximum size of each chunk in characters.
        chunk_overlap: The character-based overlap between consecutive chunks.
        
    Returns:
        A list of dictionaries representing chunks. Each chunk contains:
        - chunk_index (int)
        - content (str)
        - page_start (int)
        - page_end (int)
    """
    # 1. Flatten all pages into paragraphs with their respective page numbers
    paragraphs = []
    for page in pages:
        page_num = page["page_number"]
        page_text = page["text"]
        
        # Split on double newlines to find paragraph boundaries
        raw_paras = page_text.split("\n\n")
        for para in raw_paras:
            cleaned_para = para.strip()
            if cleaned_para:
                paragraphs.append((cleaned_para, page_num))
                 
    # Fallback if no paragraphs are found: treat each page text as a paragraph
    if not paragraphs:
        for page in pages:
            text = page["text"].strip()
            if text:
                paragraphs.append((text, page["page_number"]))

    chunks = []
    current_chunk_paragraphs = []
    current_chunk_len = 0
    chunk_index = 0

    for i in range(len(paragraphs)):
        para_text, page_num = paragraphs[i]
        
        # If a single paragraph is larger than chunk_size, handle it specially:
        if len(para_text) > chunk_size:
            # If we have existing text in the current chunk, save it first
            if current_chunk_paragraphs:
                content = "\n\n".join([p[0] for p in current_chunk_paragraphs])
                pages_in_chunk = [p[1] for p in current_chunk_paragraphs]
                chunks.append({
                    "chunk_index": chunk_index,
                    "content": content,
                    "page_start": min(pages_in_chunk),
                    "page_end": max(pages_in_chunk)
                })
                chunk_index += 1
                current_chunk_paragraphs = []
                current_chunk_len = 0

            # Split the oversized paragraph into chunk_size pieces with chunk_overlap
            start_char = 0
            para_len = len(para_text)
            while start_char < para_len:
                end_char = min(start_char + chunk_size, para_len)
                sub_text = para_text[start_char:end_char]
                chunks.append({
                    "chunk_index": chunk_index,
                    "content": sub_text,
                    "page_start": page_num,
                    "page_end": page_num
                })
                chunk_index += 1
                start_char += (chunk_size - chunk_overlap)
            continue

        # If adding this paragraph exceeds the chunk size, close current chunk
        if current_chunk_paragraphs and (current_chunk_len + 2 + len(para_text) > chunk_size):
            # Save current chunk
            content = "\n\n".join([p[0] for p in current_chunk_paragraphs])
            pages_in_chunk = [p[1] for p in current_chunk_paragraphs]
            chunks.append({
                "chunk_index": chunk_index,
                "content": content,
                "page_start": min(pages_in_chunk),
                "page_end": max(pages_in_chunk)
            })
            chunk_index += 1

            # Build overlap for the next chunk from the end of current_chunk_paragraphs
            overlap_paras = []
            overlap_len = 0
            for prev_para, prev_page in reversed(current_chunk_paragraphs):
                if overlap_len + len(prev_para) <= chunk_overlap:
                    overlap_paras.insert(0, (prev_para, prev_page))
                    overlap_len += len(prev_para) + (2 if overlap_paras else 0)
                else:
                    break
            
            current_chunk_paragraphs = overlap_paras
            current_chunk_len = overlap_len

        # Add the paragraph to the current chunk
        current_chunk_paragraphs.append((para_text, page_num))
        current_chunk_len += len(para_text) + (2 if len(current_chunk_paragraphs) > 1 else 0)

    # Save any remaining paragraph chunk
    if current_chunk_paragraphs:
        content = "\n\n".join([p[0] for p in current_chunk_paragraphs])
        pages_in_chunk = [p[1] for p in current_chunk_paragraphs]
        chunks.append({
            "chunk_index": chunk_index,
            "content": content,
            "page_start": min(pages_in_chunk),
            "page_end": max(pages_in_chunk)
        })

    return chunks
