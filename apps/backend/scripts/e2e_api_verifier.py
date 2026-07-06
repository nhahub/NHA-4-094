import sys
import os
import time
import subprocess
import requests
import asyncio

# Add apps/backend directory to python paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.supabase_client import get_supabase_client

# Test constants
PORT = 8099
BASE_URL = f"http://localhost:{PORT}"
USER_A = "a1a1a1a1-a1a1-a1a1-a1a1-a1a1a1a1a1a1"
USER_B = "b2b2b2b2-b2b2-b2b2-b2b2-b2b2b2b2b2b2"
DOC_A = "dddddddd-aaaa-1111-1111-aaaaaaaaaaaa"
DOC_EMPTY = "dddddddd-eeee-2222-2222-eeeeeeeeeeee"
CHUNK_A = "cccccccc-aaaa-1111-1111-aaaaaaaaaaaa"

def clean_database(supabase):
    print("Cleaning database test records...")
    tables = [
        "chat_sessions", "messages", "user_learning_profiles", "memory_items",
        "conversation_summaries", "learning_events", "topic_mastery", "weak_topics", "mistake_patterns"
    ]
    try:
        for t in tables:
            supabase.table(t).delete().in_("user_id", [USER_A, USER_B]).execute()
            
        supabase.table("document_chunks").delete().eq("id", CHUNK_A).execute()
        supabase.table("documents").delete().in_("id", [DOC_A, DOC_EMPTY]).execute()
    except Exception as e:
        print(f"Cleanup warning: {str(e)}")

def seed_database(supabase):
    print("Seeding database test records...")
    
    # 1. Profiles
    supabase.table("user_learning_profiles").upsert({
        "user_id": USER_A,
        "academic_level": "beginner",
        "learning_level": "beginner",
        "preferred_language": "ar",
        "preferred_style": "simple",
        "explanation_style": "simple",
        "explanation_depth": "short",
        "default_difficulty": "easy"
    }).execute()
    
    supabase.table("user_learning_profiles").upsert({
        "user_id": USER_B,
        "academic_level": "advanced",
        "learning_level": "advanced",
        "preferred_language": "en"
    }).execute()

    # 2. Documents
    supabase.table("documents").upsert({
        "id": DOC_A,
        "user_id": USER_A,
        "original_filename": "biology_notes.pdf",
        "file_size": 2048,
        "file_hash": "hash_biology_notes_123",
        "upload_status": "ready",
        "chunk_count": 1
    }).execute()

    supabase.table("documents").upsert({
        "id": DOC_EMPTY,
        "user_id": USER_A,
        "original_filename": "empty_doc.pdf",
        "file_size": 1024,
        "file_hash": "hash_empty_doc_456",
        "upload_status": "ready",
        "chunk_count": 1
    }).execute()

    # 3. Document Chunk
    supabase.table("document_chunks").upsert({
        "id": CHUNK_A,
        "document_id": DOC_A,
        "user_id": USER_A,
        "chunk_index": 0,
        "content": "Photosynthesis is how green plants use sunlight to synthesize nutrients.",
        "page_start": 1,
        "page_end": 1
    }).execute()

    # 4. Seed memory items
    dummy_embedding = [0.1] * 1024
    supabase.table("memory_items").insert({
        "user_id": USER_A,
        "memory_type": "preference",
        "content": "Likes simplified biology models.",
        "embedding": dummy_embedding
    }).execute()

    supabase.table("memory_items").insert({
        "user_id": USER_A,
        "memory_type": "preference",
        "content": "Mitosis has 4 stages.",
        "embedding": dummy_embedding
    }).execute()
    print("Database seeding completed.")

def verify_endpoints():
    print("\nRunning HTTP E2E checks...")
    results = {}

    # Check 1: Health check
    try:
        resp = requests.get(f"{BASE_URL}/")
        if resp.status_code == 200 and resp.json().get("status") == "healthy":
            results["FastAPI Server Launch"] = "PASS"
        else:
            results["FastAPI Server Launch"] = f"FAIL (Status: {resp.status_code})"
    except Exception as e:
        results["FastAPI Server Launch"] = f"FAIL ({str(e)})"
        return results

    # Check 2: Grounded QA Search
    try:
        payload = {
            "user_id": USER_A,
            "session_id": "sess-e2e-chat",
            "message": "Explain photosynthesis to me",
            "language": "ar"
        }
        resp = requests.post(f"{BASE_URL}/api/v1/documents/{DOC_A}/chat", json=payload)
        data = resp.json()
        if resp.status_code == 200 and data.get("status") == "success" and len(data.get("tasks", [])) > 0:
            results["Grounded QA over HTTP"] = "PASS"
        else:
            results["Grounded QA over HTTP"] = f"FAIL (Status: {resp.status_code}, Res: {resp.text})"
    except Exception as e:
        results["Grounded QA over HTTP"] = f"FAIL ({str(e)})"

    # Check 3: Personalization adaptation (Arabic beginner, simple tone)
    try:
        payload = {
            "user_id": USER_A,
            "session_id": "sess-e2e-chat",
            "message": "Explain photosynthesis to me",
            "language": "ar"
        }
        resp = requests.post(f"{BASE_URL}/api/v1/documents/{DOC_A}/chat", json=payload)
        data = resp.json()
        message = data.get("message", "")
        # Response should be personalized (e.g. contains personalized level tag or simpler terms)
        if resp.status_code == 200 and "level=beginner" in message and "style=simple" in message:
            results["Personalization Tone Adaptation"] = "PASS"
        else:
            results["Personalization Tone Adaptation"] = f"FAIL (Message: {message})"
    except Exception as e:
        results["Personalization Tone Adaptation"] = f"FAIL ({str(e)})"

    # Check 4: Empty retrieval fallback returning "لم أجد إجابة واضحة في الملف المرفوع."
    try:
        payload = {
            "user_id": USER_A,
            "session_id": "sess-e2e-empty",
            "message": "What is gravity?",
            "language": "ar"
        }
        resp = requests.post(f"{BASE_URL}/api/v1/documents/{DOC_EMPTY}/chat", json=payload)
        data = resp.json()
        if resp.status_code == 200 and data.get("status") == "no_answer" and data.get("message") == "لم أجد إجابة واضحة في الملف المرفوع.":
            results["Empty Retrieval Fallback"] = "PASS"
        else:
            results["Empty Retrieval Fallback"] = f"FAIL (Status: {resp.status_code}, Res: {data})"
    except Exception as e:
        results["Empty Retrieval Fallback"] = f"FAIL ({str(e)})"

    # Check 5: Memory-cannot-answer-without-RAG check
    try:
        # Ask a query that exists in memory ("Mitosis has 4 stages"), but on an empty document DOC_EMPTY
        payload = {
            "user_id": USER_A,
            "session_id": "sess-e2e-empty",
            "message": "How many stages does mitosis have?",
            "language": "ar"
        }
        resp = requests.post(f"{BASE_URL}/api/v1/documents/{DOC_EMPTY}/chat", json=payload)
        data = resp.json()
        # Even if memory has the answer, empty document RAG must return the grounding fallback!
        if resp.status_code == 200 and data.get("status") == "no_answer" and data.get("message") == "لم أجد إجابة واضحة في الملف المرفوع.":
            results["Memory-Cannot-Answer-Without-RAG Check"] = "PASS"
        else:
            results["Memory-Cannot-Answer-Without-RAG Check"] = f"FAIL (Status: {resp.status_code}, Msg: {data.get('message')})"
    except Exception as e:
        results["Memory-Cannot-Answer-Without-RAG Check"] = f"FAIL ({str(e)})"

    # Check 6: Multi-user security isolation over HTTP
    try:
        # USER_B tries to query USER_A's document DOC_A
        payload = {
            "user_id": USER_B,
            "session_id": "sess-e2e-chat-b",
            "message": "What is photosynthesis?",
            "language": "en"
        }
        resp = requests.post(f"{BASE_URL}/api/v1/documents/{DOC_A}/chat", json=payload)
        data = resp.json()
        if resp.status_code == 403 and data.get("detail") == "DOCUMENT_ACCESS_DENIED":
            results["Multi-User Isolation Check"] = "PASS"
        else:
            results["Multi-User Isolation Check"] = f"FAIL (Status: {resp.status_code}, Detail: {data})"
    except Exception as e:
        results["Multi-User Isolation Check"] = f"FAIL ({str(e)})"

    return results

def main():
    print("=" * 60)
    print("        FASTAPI END-TO-END HTTP API VERIFIER")
    print("=" * 60)

    # 1. Clean & Seed
    supabase = get_supabase_client()
    clean_database(supabase)
    seed_database(supabase)

    # 2. Start Uvicorn process on port 8099
    # Use PYTHONPATH=. to resolve apps imports
    env = os.environ.copy()
    env["PYTHONPATH"] = "."
    print(f"\nStarting Uvicorn server on port {PORT}...")
    log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../uvicorn_e2e.log"))
    log_file = open(log_path, "w", encoding="utf-8")
    
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--port", str(PORT)],
        cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
        env=env,
        stdout=log_file,
        stderr=log_file
    )

    # Wait for server to start
    time.sleep(4)

    # 3. Verify
    try:
        results = verify_endpoints()
    finally:
        # Kill server process
        print("\nShutting down Uvicorn server...")
        proc.terminate()
        proc.wait()
        log_file.close()
        
        # If server failed, print server log
        if "PASS" not in results.get("FastAPI Server Launch", ""):
            print("\n" + "="*40 + " SERVER LOGS " + "="*40)
            if os.path.exists(log_path):
                with open(log_path, "r", encoding="utf-8") as lf:
                    print(lf.read())
            print("="*93)
            
        # Clean up database
        clean_database(supabase)
        if os.path.exists(log_path):
            try:
                os.remove(log_path)
            except Exception:
                pass

    # 4. Print E2E Checklist
    print("\n" + "=" * 60)
    print("          E2E CHECKLIST RESULTS")
    print("=" * 60)
    all_pass = True
    for test_name, status in results.items():
        print(f" - {test_name:<40} : {status}")
        if "PASS" not in status:
            all_pass = False
    print("=" * 60)

    if not all_pass:
        print("Verification Failed.")
        sys.exit(1)
    else:
        print("Verification Succeeded! All E2E checks passed.")
        sys.exit(0)

if __name__ == "__main__":
    main()
