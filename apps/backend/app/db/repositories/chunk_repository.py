from typing import List, Dict, Any
from app.db.supabase_client import get_supabase_client

# Get the Supabase client
supabase = get_supabase_client()

async def insert_chunks(
    document_id: str,
    user_id: str,
    chunks: List[Dict[str, Any]],
    embeddings: List[List[float]]
) -> List[Dict[str, Any]]:
    """
    Inserts a list of document chunks and their corresponding embeddings into the database.
    Batches database writes in chunks of 50 to prevent statement timeouts.
    """
    rows = []
    for idx, chunk in enumerate(chunks):
        rows.append({
            "document_id": document_id,
            "user_id": user_id,
            "chunk_index": chunk["chunk_index"],
            "content": chunk["content"],
            "page_start": chunk["page_start"],
            "page_end": chunk["page_end"],
            "metadata": chunk["metadata"],
            "embedding": embeddings[idx]
        })
    
    inserted_data = []
    batch_size = 50
    for i in range(0, len(rows), batch_size):
        batch = rows[i : i + batch_size]
        print(f"[DB] Inserting chunk batch {i // batch_size + 1}/{((len(rows)-1)//batch_size)+1} ({len(batch)} rows)...")
        response = supabase.table("document_chunks").insert(batch).execute()
        if response.data:
            inserted_data.extend(response.data)
            
    return inserted_data

async def delete_chunks_by_document(document_id: str) -> List[Dict[str, Any]]:
    """
    Deletes all chunks associated with a specific document.
    """
    response = supabase.table("document_chunks").delete().eq("document_id", document_id).execute()
    return response.data

async def get_chunks_by_document(document_id: str) -> List[Dict[str, Any]]:
    """
    Retrieves all chunks of a document ordered by their indexing sequence.
    """
    response = (
        supabase.table("document_chunks")
        .select("*")
        .eq("document_id", document_id)
        .order("chunk_index", desc=False)
        .execute()
    )
    return response.data
