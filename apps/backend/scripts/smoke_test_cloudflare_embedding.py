import sys
import os
import asyncio

# Setup path so it finds 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings
from app.ai_system.providers.embedding_client import embed_texts

def main():
    print("=" * 60)
    print("      CLOUDFLARE WORKERS AI EMBEDDING SMOKE TEST")
    print("=" * 60)
    
    print(f"Provider:   {settings.EMBEDDING_PROVIDER}")
    print(f"Model Name: {settings.EMBEDDING_MODEL_NAME}")
    print(f"Dimensions: {settings.EMBEDDING_DIMENSIONS}")
    print(f"Batch Size: {settings.EMBEDDING_BATCH_SIZE}")
    print(f"Account ID: {settings.CLOUDFLARE_ACCOUNT_ID[:6]}... (hidden)" if settings.CLOUDFLARE_ACCOUNT_ID else "Account ID: Missing!")
    
    if not settings.CLOUDFLARE_ACCOUNT_ID or not settings.CLOUDFLARE_API_TOKEN:
        print("ERROR: Cloudflare credentials are not set in .env!")
        sys.exit(1)
        
    sentences = [
        "Welcome to the machine learning platform.",
        "Deep learning is a subset of artificial intelligence."
    ]
    
    print(f"\nSending {len(sentences)} test sentences to Cloudflare Workers AI...")
    try:
        vectors = embed_texts(sentences)
        print("Embeddings received successfully!")
        print(f"Number of vectors returned: {len(vectors)}")
        
        for idx, vec in enumerate(vectors):
            dim = len(vec)
            print(f"  Vector {idx + 1} size: {dim}")
            if dim != settings.EMBEDDING_DIMENSIONS:
                print(f"  FAIL: Expected dimension {settings.EMBEDDING_DIMENSIONS}, got {dim}")
                sys.exit(1)
                
        print("\nSUCCESS: Cloudflare embedding smoke test PASSED!")
    except Exception as e:
        print(f"\nFAIL: Embedding generation failed with exception: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
