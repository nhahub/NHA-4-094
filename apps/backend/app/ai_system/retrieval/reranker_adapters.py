import logging
import httpx
import asyncio
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.ai_system.utils.circuit_breaker import circuit_breaker_registry

logger = logging.getLogger(__name__)

class RerankerAdapter:
    async def rerank(self, query: str, texts: List[str], timeout: float) -> List[Dict[str, Any]]:
        """
        Reranks a list of texts against a query.
        Returns a list of dictionaries containing:
          - index: int (original index in the texts list)
          - score: float (relevance score)
        """
        raise NotImplementedError()


class JinaRerankerAdapter(RerankerAdapter):
    def __init__(self):
        self.api_key = settings.JINA_API_KEY.strip()
        self.endpoint = settings.JINA_RERANKER_ENDPOINT.strip() or "https://api.jina.ai/v1/rerank"
        self.model = settings.JINA_RERANKER_MODEL.strip() or "jina-reranker-v3"
        self._client = None

    def get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient()
        return self._client

    async def rerank(self, query: str, texts: List[str], timeout: float) -> List[Dict[str, Any]]:
        if not self.api_key:
            logger.info("[JINA RERANKER] Skipping: Missing JINA_API_KEY.")
            return []

        if not await circuit_breaker_registry.allow_request("jina"):
            logger.warning("[JINA RERANKER] Skipping: Circuit breaker is OPEN.")
            return []

        payload = {
            "model": self.model,
            "query": query,
            "documents": texts
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Bounded retry: 1 retry
        client = self.get_client()
        for attempt in range(1, 3):
            try:
                response = await client.post(
                    self.endpoint,
                    json=payload,
                    headers=headers,
                    timeout=httpx.Timeout(timeout, connect=5.0)
                )
                if response.status_code == 200:
                    data = response.json()
                    results = []
                    for item in data.get("results", []):
                        results.append({
                            "index": item["index"],
                            "score": item.get("relevance_score", 0.0)
                        })
                    await circuit_breaker_registry.record_success("jina")
                    return results
                else:
                    logger.error(f"[JINA RERANKER] Error (status {response.status_code}): {response.text[:300]}")
                    await circuit_breaker_registry.record_failure("jina")
            except Exception as e:
                logger.error(f"[JINA RERANKER] Exception on attempt {attempt}: {e}")
                await circuit_breaker_registry.record_failure("jina")
                if attempt < 2:
                    await asyncio.sleep(1.0)
        return []


class CohereRerankerAdapter(RerankerAdapter):
    def __init__(self):
        self.api_key = settings.COHERE_API_KEY.strip()
        self.endpoint = settings.COHERE_RERANKER_ENDPOINT.strip() or "https://api.cohere.com/v2/rerank"
        self.model = settings.COHERE_RERANKER_MODEL.strip() or "rerank-v4.0-pro"
        self._client = None

    def get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient()
        return self._client

    async def rerank(self, query: str, texts: List[str], timeout: float) -> List[Dict[str, Any]]:
        if not self.api_key:
            logger.info("[COHERE RERANKER] Skipping: Missing COHERE_API_KEY.")
            return []

        if not await circuit_breaker_registry.allow_request("cohere"):
            logger.warning("[COHERE RERANKER] Skipping: Circuit breaker is OPEN.")
            return []

        payload = {
            "model": self.model,
            "query": query,
            "documents": texts
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Bounded retry: 1 retry
        client = self.get_client()
        for attempt in range(1, 3):
            try:
                response = await client.post(
                    self.endpoint,
                    json=payload,
                    headers=headers,
                    timeout=httpx.Timeout(timeout, connect=5.0)
                )
                if response.status_code == 200:
                    data = response.json()
                    results = []
                    for item in data.get("results", []):
                        results.append({
                            "index": item["index"],
                            "score": item.get("relevance_score", 0.0)
                        })
                    await circuit_breaker_registry.record_success("cohere")
                    return results
                else:
                    logger.error(f"[COHERE RERANKER] Error (status {response.status_code}): {response.text[:300]}")
                    await circuit_breaker_registry.record_failure("cohere")
            except Exception as e:
                logger.error(f"[COHERE RERANKER] Exception on attempt {attempt}: {e}")
                await circuit_breaker_registry.record_failure("cohere")
                if attempt < 2:
                    await asyncio.sleep(1.0)
        return []


class CloudflareRerankerAdapter(RerankerAdapter):
    def __init__(self):
        self.account_id = settings.CLOUDFLARE_ACCOUNT_ID.strip()
        self.api_token = settings.CLOUDFLARE_API_TOKEN.strip()
        self.base_url = settings.CLOUDFLARE_AI_BASE_URL.strip() or "https://api.cloudflare.com/client/v4"
        self.model = settings.CLOUDFLARE_RERANKER_MODEL.strip() or "@cf/baai/bge-reranker-base"
        self._client = None

    def get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient()
        return self._client

    async def rerank(self, query: str, texts: List[str], timeout: float) -> List[Dict[str, Any]]:
        if not self.account_id or not self.api_token:
            logger.info("[CLOUDFLARE RERANKER] Skipping: Missing Cloudflare credentials.")
            return []

        if not await circuit_breaker_registry.allow_request("cloudflare_rerank"):
            logger.warning("[CLOUDFLARE RERANKER] Skipping: Circuit breaker is OPEN.")
            return []

        url = f"{self.base_url.rstrip('/')}/accounts/{self.account_id}/ai/run/{self.model}"
        payload = {
            "query": query,
            "text": texts
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

        # Bounded retry: 1 retry
        client = self.get_client()
        for attempt in range(1, 3):
            try:
                response = await client.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=httpx.Timeout(timeout, connect=5.0)
                )
                if response.status_code == 200:
                    data = response.json()
                    result_list = data.get("result", [])
                    results = []
                    for item in result_list:
                        results.append({
                            "index": item["index"],
                            "score": item.get("score", 0.0)
                        })
                    await circuit_breaker_registry.record_success("cloudflare_rerank")
                    return results
                else:
                    logger.error(f"[CLOUDFLARE RERANKER] Error (status {response.status_code}): {response.text[:300]}")
                    await circuit_breaker_registry.record_failure("cloudflare_rerank")
            except Exception as e:
                logger.error(f"[CLOUDFLARE RERANKER] Exception on attempt {attempt}: {e}")
                await circuit_breaker_registry.record_failure("cloudflare_rerank")
                if attempt < 2:
                    await asyncio.sleep(1.0)
        return []
