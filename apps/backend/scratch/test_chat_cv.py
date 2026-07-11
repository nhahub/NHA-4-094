import sys
import os
import requests
from dotenv import load_dotenv
load_dotenv("../.env")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://localhost:8000"
DOC_ID = "358c6517-5c77-40f2-b483-9415b3a91241"

headers = {
    "Authorization": "Bearer mock-token"
}

try:
    session_resp = requests.post(f"{BASE_URL}/api/v1/documents/{DOC_ID}/sessions", headers=headers)
    session_id = session_resp.json()["id"]
    
    payload = {
        "user_id": session_resp.json()["user_id"],
        "session_id": session_id,
        "message": "مين صاحب السي في؟",
        "language": "ar"
    }
    
    resp = requests.post(f"{BASE_URL}/api/v1/documents/{DOC_ID}/chat", json=payload, headers=headers)
    import json
    print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print("Error:", e)
