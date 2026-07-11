import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
load_dotenv("../.env")

import asyncio
from app.ai_system.retrieval import get_document_retriever
from app.ai_system.retrieval.schemas import RetrievalRequest

async def main():
    retriever = get_document_retriever()
    doc_id = "358c6517-5c77-40f2-b483-9415b3a91241"
    user_id = "c9d079ce-1858-437f-a168-99a85d28218b"
    
    queries = [
        "مين صاحب السي في؟",
        "صاحب ال cv اسمه ايه؟"
    ]
    
    for q in queries:
        req = RetrievalRequest(
            user_id=user_id,
            document_id=doc_id,
            query=q,
            intent="chat_answer"
        )
        res = await retriever.retrieve(req)
        print(f"Query: {q}")
        print(f"Status: {res.status}")
        print(f"Reason: {res.reason}")
        print(f"Chunks found: {len(res.chunks)}")
        for idx, chunk in enumerate(res.chunks):
            print(f"  [{idx}] score={chunk.score} (vector={chunk.vector_score}, keyword={chunk.keyword_score}): {chunk.text[:100]}...")
        print("-" * 50)

asyncio.run(main())
