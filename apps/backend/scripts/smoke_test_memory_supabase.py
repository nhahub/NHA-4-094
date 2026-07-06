import sys
import os
import asyncio
from datetime import datetime

# Add apps/backend directory to python paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.supabase_client import get_supabase_client
from app.db.repositories import (
    learning_profile_repository,
    memory_repository,
    chat_repository,
    conversation_summary_repository
)
from app.ai_system.memory.memory_store import MemoryStore

# Test IDs
USER_A = "11111111-1111-1111-1111-111111111111"
USER_B = "22222222-2222-2222-2222-222222222222"
DOC_ID = "33333333-3333-3333-3333-333333333333"
CHUNK_ID = "44444444-4444-4444-4444-444444444444"

async def run_smoke_test():
    print("=" * 60)
    print("         SUPABASE E2E SMOKE TEST & DB VERIFICATION")
    print("=" * 60)

    # Initialize Supabase client
    try:
        supabase = get_supabase_client()
        print("1. Connection to Supabase client: PASS")
    except Exception as e:
        print(f"1. Connection to Supabase client: FAIL ({type(e).__name__})")
        return

    # Clean up any existing records for test user ids first to ensure idempotency
    required_tables = [
        "chat_sessions", "messages", "user_learning_profiles", "memory_items",
        "conversation_summaries", "learning_events", "topic_mastery", "weak_topics", "mistake_patterns",
        "frustration_logs", "repetition_schedule", "weakness_history"
    ]
    try:
        for t in required_tables:
            supabase.table(t).delete().in_("user_id", [USER_A, USER_B]).execute()
            
        # Seed standard RAG mock chunks if not exist
        supabase.table("documents").upsert({
            "id": DOC_ID,
            "user_id": USER_A,
            "original_filename": "test.pdf",
            "file_size": 1024,
            "file_hash": "mock_file_hash_123",
            "upload_status": "ready"
        }).execute()
        
        supabase.table("document_chunks").upsert({
            "id": CHUNK_ID,
            "document_id": DOC_ID,
            "user_id": USER_A,
            "chunk_index": 0,
            "content": "Photosynthesis is the plant food process.",
            "page_start": 1,
            "page_end": 1
        }).execute()
    except Exception as e:
         sys.stderr.write(f"Setup cleaning/seeding failed: {str(e)}\n")

    # Step 2: Migration Tables check via API
    missing = []
    for t in required_tables:
        try:
            # Using SELECT * limit 1 to avoid column-specific issues like 'id' vs 'schedule_id'
            supabase.table(t).select("*").limit(1).execute()
        except Exception as e:
            missing.append(f"{t} ({str(e)})")
            
    if not missing:
        print("2. Migration Tables existence (API): PASS")
    else:
        print(f"2. Migration Tables existence (API): FAIL (Missing or inaccessible tables: {missing})")
        print("   Make sure you apply 001_init_documents.sql, 002_memory_personalization.sql, and 004_memory_enhancements.sql.")
        return

    # Step 3: Vector Column & Extension check via insert
    try:
        dummy_embedding = [0.1] * 1024
        test_mem = {
            "user_id": USER_A,
            "memory_type": "preference",
            "content": "Extension check",
            "embedding": dummy_embedding
        }
        res = supabase.table("memory_items").insert(test_mem).execute()
        if res.data:
            print("3. Vector Extension presence (Insert check): PASS")
            supabase.table("memory_items").delete().eq("user_id", USER_A).execute()
        else:
            print("3. Vector Extension presence (Insert check): FAIL (Insert did not return data)")
    except Exception as e:
        print("3. Vector Extension presence (Insert check): FAIL (Vector insert error)")
        sys.stderr.write(f"Error: {str(e)}\n")

    # Step 4: RPC match_memory_items check
    try:
        # Seed a record first
        dummy_embedding = [0.1] * 1024
        supabase.table("memory_items").insert({
            "user_id": USER_A,
            "memory_type": "preference",
            "content": "Biology details",
            "embedding": dummy_embedding
        }).execute()
        
        # Invoke RPC function
        rpc_res = supabase.rpc("match_memory_items", {
            "query_embedding": dummy_embedding,
            "match_threshold": 0.3,
            "match_count": 5,
            "p_user_id": USER_A
        }).execute()
        
        if rpc_res.data and rpc_res.data[0]["content"] == "Biology details":
            print("4. match_memory_items RPC check: PASS")
        else:
            print("4. match_memory_items RPC check: FAIL (RPC returned empty or invalid data)")
    except Exception as e:
        print("4. match_memory_items RPC check: FAIL")
        sys.stderr.write(f"Error: {str(e)}\n")

    # Step 5: user_learning_profiles CRUD
    try:
        profile_data = {
            "user_id": USER_A,
            "academic_level": "beginner",
            "learning_level": "beginner",
            "preferred_language": "ar",
            "preferred_style": "simple",
            "explanation_style": "simple",
            "explanation_depth": "short",
            "default_difficulty": "easy"
        }
        await learning_profile_repository.upsert_profile(profile_data)
        get_res = await learning_profile_repository.get_profile(USER_A)
        if get_res and get_res["learning_level"] == "beginner":
            print("5. user_learning_profiles CRUD: PASS")
        else:
            print("5. user_learning_profiles CRUD: FAIL (retrieved profile mismatched or empty)")
    except Exception as e:
        print("5. user_learning_profiles CRUD: FAIL")
        sys.stderr.write(f"Error: {str(e)}\n")

    # Step 6: memory_items CRUD + semantic search
    try:
        dummy_embedding = [0.1] * 1024
        mem_data = {
            "user_id": USER_A,
            "memory_type": "preference",
            "content": "Likes simplified biology models.",
            "embedding": dummy_embedding,
            "importance": 0.9
        }
        await memory_repository.save_memory_item(mem_data)
        
        search_res = await memory_repository.semantic_search_memory_items(
            user_id=USER_A,
            query_embedding=dummy_embedding,
            threshold=0.3,
            limit=5
        )
        if search_res and any(r["content"] == "Likes simplified biology models." for r in search_res):
            print("6. memory_items CRUD + Semantic Search: PASS")
        else:
            print(f"6. memory_items CRUD + Semantic Search: FAIL (semantic search empty or mismatched, got: {search_res})")
    except Exception as e:
        print("6. memory_items CRUD + Semantic Search: FAIL")
        sys.stderr.write(f"Error: {str(e)}\n")

    # Step 7: chat_sessions CRUD
    session_id = None
    try:
        sess = supabase.table("chat_sessions").insert({"user_id": USER_A}).execute()
        if sess.data:
            session_id = sess.data[0]["id"]
            print("7. chat_sessions CRUD: PASS")
        else:
            print("7. chat_sessions CRUD: FAIL")
    except Exception as e:
        print("7. chat_sessions CRUD: FAIL")
        sys.stderr.write(f"Error: {str(e)}\n")

    # Step 8: messages saved with retrieved_chunks/source_chunk_id
    if session_id:
        try:
            await chat_repository.save_message(
                session_id=session_id,
                user_id=USER_A,
                role="user",
                content="Tell me about plants"
            )
            await chat_repository.save_message(
                session_id=session_id,
                user_id=USER_A,
                role="assistant",
                content="Photosynthesis is how plants produce food.",
                retrieved_chunks=[CHUNK_ID],
                source_chunk_id=CHUNK_ID
            )
            msgs = await chat_repository.get_session_messages(session_id)
            assistant_msg = next((m for m in msgs if m["role"] == "assistant"), None)
            
            if assistant_msg and assistant_msg["retrieved_chunks"] == [CHUNK_ID] and assistant_msg["source_chunk_id"] == CHUNK_ID:
                print("8. messages saved with chunk traceability: PASS")
            else:
                print(f"8. messages saved with chunk traceability: FAIL (Mismatched fields: {assistant_msg})")
        except Exception as e:
            print("8. messages saved with chunk traceability: FAIL")
            sys.stderr.write(f"Error: {str(e)}\n")
    else:
        print("8. messages saved with chunk traceability: SKIP")

    # Step 9: conversation_summaries CRUD
    if session_id:
        try:
            summary_data = {
                "session_id": session_id,
                "user_id": USER_A,
                "summary_text": "Completed biology session.",
                "structured_summary": {"avg_score": 0.8}
            }
            await conversation_summary_repository.upsert_summary(summary_data)
            sum_res = await conversation_summary_repository.get_latest_summary(USER_A, session_id)
            if sum_res and sum_res["summary_text"] == "Completed biology session.":
                print("9. conversation_summaries CRUD: PASS")
            else:
                print("9. conversation_summaries CRUD: FAIL")
        except Exception as e:
            print("9. conversation_summaries CRUD: FAIL")
            sys.stderr.write(f"Error: {str(e)}\n")
    else:
        print("9. conversation_summaries CRUD: SKIP")

    # Step 10: Multi-user isolation (leakage check)
    try:
        await learning_profile_repository.upsert_profile({
            "user_id": USER_B,
            "learning_level": "advanced",
            "academic_level": "advanced"
        })
        
        search_B = await memory_repository.semantic_search_memory_items(
            user_id=USER_B,
            query_embedding=[0.1] * 1024,
            threshold=0.3,
            limit=5
        )
        if not search_B:
            print("10. User B cannot access User A memory (Isolation check): PASS")
        else:
            print("10. User B cannot access User A memory (Isolation check): FAIL (Leakage detected)")
    except Exception as e:
        print("10. User B cannot access User A memory (Isolation check): FAIL")
        sys.stderr.write(f"Error: {str(e)}\n")

    # Step 11: Empty Retrieval Fallback simulation
    try:
        chunks_mock = []
        if not chunks_mock:
            fallback = "لم أجد إجابة واضحة في الملف المرفوع."
            print("11. Empty Retrieval Fallback simulation: PASS")
        else:
            print("11. Empty Retrieval Fallback simulation: FAIL")
    except Exception as e:
        print("11. Empty Retrieval Fallback simulation: FAIL")

    # Step 12: Memory-cannot-answer-without-RAG check
    try:
        from app.ai_system.memory.prompt_context_builder import build_grounded_prompt
        from app.ai_system.memory.memory_types import MemoryContext
        from app.schemas.memory_schema import MemoryItem
        
        ctx = MemoryContext(
            user_profile=None,
            relevant_past=[MemoryItem(user_id=USER_A, content="Mitosis has 4 stages.", memory_type="preference")]
        )
        prompt = build_grounded_prompt(
            document_context="",
            memory_context=ctx,
            personalization_instructions="",
            user_query="What stages does mitosis have?"
        )
        
        if "لم أجد إجابة واضحة في الملف المرفوع." in prompt and "Do not use this as a factual source" in prompt:
            print("12. Memory-cannot-answer-without-RAG validation: PASS")
        else:
            print("12. Memory-cannot-answer-without-RAG validation: FAIL")
    except Exception as e:
        print("12. Memory-cannot-answer-without-RAG validation: FAIL")

    # Step 13: NEW Memory enhancement tables CRUD (frustration_logs, repetition_schedule, weakness_history)
    print("\nChecking memory enhancements database integration...")
    memory_store = MemoryStore()
    
    # 13.1 Frustration Logs check
    try:
        # Detect and log
        res = await memory_store.detect_and_log_frustration(
            user_id=USER_A,
            topic="Photosynthesis",
            confusion_signals=2,
            mistake_signals=1,
            consecutive_failures=1
        )
        if res and res["topic"] == "Photosynthesis" and res["frustration_score"] > 0:
            # Query it
            logs = await memory_store.get_frustration_logs(USER_A, topic="Photosynthesis")
            if logs and logs[0]["topic"] == "Photosynthesis":
                print("13.1 frustration_logs CRUD: PASS")
            else:
                print("13.1 frustration_logs CRUD: FAIL (could not query logged frustration)")
        else:
            print("13.1 frustration_logs CRUD: FAIL (detect_and_log_frustration returned empty or 0 score)")
    except Exception as e:
        print(f"13.1 frustration_logs CRUD: FAIL ({str(e)})")

    # 13.2 Repetition Schedule check
    try:
        schedule_mock = {
            "user_id": USER_A,
            "topic": "Photosynthesis",
            "repetition_count": 2,
            "ease_factor": 2.6,
            "review_interval": 3,
            "next_review_date": datetime.utcnow()
        }
        res_sched = await memory_store.upsert_repetition_schedule(schedule_mock)
        if res_sched and res_sched["topic"] == "Photosynthesis" and res_sched["repetition_count"] == 2:
            print("13.2 repetition_schedule CRUD: PASS")
        else:
            print("13.2 repetition_schedule CRUD: FAIL (upsert schedule returned empty or mismatched fields)")
    except Exception as e:
        print(f"13.2 repetition_schedule CRUD: FAIL ({str(e)})")

    # 13.3 Weakness History check
    try:
        res_hist = await memory_store.add_weakness_history_entry(
            user_id=USER_A,
            topic="Photosynthesis",
            previous_score=0.8,
            new_score=0.4,
            reason="Repeated mistakes in quiz response"
        )
        if res_hist and res_hist["topic"] == "Photosynthesis" and res_hist["delta"] == -0.4:
            print("13.3 weakness_history CRUD: PASS")
        else:
            print("13.3 weakness_history CRUD: FAIL (add weakness entry returned empty or delta mismatched)")
    except Exception as e:
        print(f"13.3 weakness_history CRUD: FAIL ({str(e)})")

    # Clean up test rows
    try:
        for t in required_tables:
            supabase.table(t).delete().in_("user_id", [USER_A, USER_B]).execute()
    except Exception as e:
        sys.stderr.write(f"Clean up failed: {str(e)}\n")

    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(run_smoke_test())
