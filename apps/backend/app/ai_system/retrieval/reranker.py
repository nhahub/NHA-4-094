import re
import time
import logging
from app.core.config import settings
from .reranker_adapters import JinaRerankerAdapter, CohereRerankerAdapter, CloudflareRerankerAdapter

logger = logging.getLogger(__name__)


class RerankResult:
    def __init__(self, chunks, latency_ms):
        self.chunks = chunks
        self.latency_ms = latency_ms


class RuleBasedReranker:
    def rerank(self, *, chunks, query_terms, filters, limit):
        start = time.perf_counter()
        terms = [term.lower() for term in query_terms if term]
        seen = set()
        ranked = []
        for chunk in chunks:
            fingerprint = re.sub(r"\s+", " ", chunk.text.lower()).strip()[:240]
            duplicate_penalty = 0.20 if fingerprint in seen else 0.0
            seen.add(fingerprint)

            overlap = self.term_overlap(chunk.text, terms) * 0.12
            metadata = self.metadata_boost(chunk, filters) * 0.10
            length_penalty = self.length_penalty(chunk.text)
            score = max(0.0, chunk.score + overlap + metadata - duplicate_penalty - length_penalty)
            # Use model_copy instead of copy (Pydantic V2)
            ranked.append(chunk.model_copy(update={"score": round(score, 6)}))

        ranked = sorted(ranked, key=lambda item: item.score, reverse=True)[:limit]
        return RerankResult(ranked, int((time.perf_counter() - start) * 1000))

    def term_overlap(self, text, terms):
        if not terms:
            return 0.0
        lower = text.lower()
        return sum(1 for term in terms if term in lower) / len(terms)

    def metadata_boost(self, chunk, filters):
        boost = 0.0
        if filters.page_number is not None and chunk.page_number == filters.page_number:
            boost += 1.0
        if filters.section_title and filters.section_title.lower() in (chunk.section_title or "").lower():
            boost += 1.0
        if filters.chapter:
            wanted = filters.chapter.lower()
            if wanted in (chunk.section_title or "").lower() or wanted == str(chunk.metadata.get("chapter", "")).lower():
                boost += 1.0
        return min(boost, 1.0)

    def length_penalty(self, text):
        words = len(text.split())
        if words < 12:
            return 0.12
        if words > 900:
            return 0.08
        return 0.0


class MultilingualRerankerRouter:
    """
    Reranker router that chains Jina -> Cohere -> Cloudflare -> Rule-Based -> Hybrid.
    """
    def __init__(self, rule_based_reranker=None):
        self.adapters = {
            "jina": JinaRerankerAdapter(),
            "cohere": CohereRerankerAdapter(),
            "cloudflare": CloudflareRerankerAdapter()
        }
        self.rule_based_reranker = rule_based_reranker or RuleBasedReranker()

    async def rerank_async(
        self,
        *,
        chunks: list,
        query: str,
        query_terms: list,
        filters: any,
        limit: int
    ):
        start_time = time.perf_counter()
        
        # Check enabled
        if not settings.RERANKER_ENABLED:
            logger.info("Reranking disabled. Preserving original hybrid order.")
            return RerankResult(chunks[:limit], 0)

        # Parse provider order
        provider_order = [p.strip().lower() for p in settings.RERANKER_PROVIDER_ORDER.split(",") if p.strip()]
        
        # If texts is empty, return empty
        if not chunks:
            return RerankResult([], 0)

        texts = [chunk.text for chunk in chunks]
        timeout = float(settings.RERANKER_TIMEOUT_SECONDS)
        total_budget = float(settings.RERANKER_TOTAL_BUDGET_SECONDS)
        
        for provider in provider_order:
            elapsed = time.perf_counter() - start_time
            remaining = total_budget - elapsed
            if remaining <= 0.05:
                logger.warning(f"[RERANKER ROUTER] Reranking total budget ({total_budget}s) exhausted. Skipping remaining providers.")
                break
                
            current_timeout = min(timeout, remaining)
            
            if provider in self.adapters:
                adapter = self.adapters[provider]
                if provider == "jina" and not settings.JINA_API_KEY.strip():
                    continue
                if provider == "cohere" and not settings.COHERE_API_KEY.strip():
                    continue
                if provider == "cloudflare" and (not settings.CLOUDFLARE_ACCOUNT_ID.strip() or not settings.CLOUDFLARE_API_TOKEN.strip()):
                    continue
 
                try:
                    logger.info(f"[RERANKER ROUTER] Attempting rerank via '{provider}' with timeout {current_timeout:.2f}s...")
                    adapter_start = time.perf_counter()
                    results = await adapter.rerank(query, texts, current_timeout)
                    adapter_latency = int((time.perf_counter() - adapter_start) * 1000)
                    
                    if results:
                        reranked_chunks = []
                        for rank_idx, item in enumerate(results):
                            orig_chunk = chunks[item["index"]]
                            
                            # Preserve original properties and score, saving provider details
                            updated_chunk = orig_chunk.model_copy(update={"score": round(item["score"], 6)})
                            # Save metadata details
                            updated_chunk.metadata["original_hybrid_score"] = orig_chunk.score
                            updated_chunk.metadata["provider_rank"] = rank_idx + 1
                            updated_chunk.metadata["provider_relevance_score"] = item["score"]
                            updated_chunk.metadata["active_reranker_provider"] = provider
                            updated_chunk.metadata["active_reranker_model"] = getattr(adapter, "model", "")
                            
                            reranked_chunks.append(updated_chunk)
                        
                        reranked_chunks = sorted(reranked_chunks, key=lambda x: x.score, reverse=True)[:limit]
                        total_latency = int((time.perf_counter() - start_time) * 1000)
                        
                        logger.info(
                            f"[OBSERVABILITY] Rerank Success: provider={provider}, model={getattr(adapter, 'model', '')}, "
                            f"candidates={len(chunks)}, top_k={limit}, returned={len(reranked_chunks)}, "
                            f"provider_latency={adapter_latency}ms, total_latency={total_latency}ms"
                        )
                        return RerankResult(reranked_chunks, total_latency)
                except Exception as e:
                    logger.error(f"[RERANKER ROUTER] Provider '{provider}' failed: {e}")

            elif provider == "rule_based" or provider == "rulebased":
                if settings.RERANKER_RULE_BASED_FALLBACK:
                    logger.info("[RERANKER ROUTER] Falling back to RuleBasedReranker...")
                    try:
                        res = self.rule_based_reranker.rerank(
                            chunks=chunks,
                            query_terms=query_terms,
                            filters=filters,
                            limit=limit
                        )
                        for rank_idx, c in enumerate(res.chunks):
                            c.metadata["active_reranker_provider"] = "rule_based"
                            c.metadata["provider_rank"] = rank_idx + 1
                        
                        logger.info(
                            f"[OBSERVABILITY] Rerank Success: provider=rule_based, model=RuleBasedReranker, "
                            f"candidates={len(chunks)}, top_k={limit}, returned={len(res.chunks)}, "
                            f"provider_latency={res.latency_ms}"
                        )
                        return res
                    except Exception as e:
                        logger.error(f"[RERANKER ROUTER] Rule-based reranker failed: {e}")
            
            elif provider == "hybrid":
                logger.info("[RERANKER ROUTER] Preserving original hybrid retrieval order.")
                break

        logger.warning("[RERANKER ROUTER] All rerankers failed or skipped. Preserving original hybrid order.")
        res_chunks = chunks[:limit]
        for rank_idx, c in enumerate(res_chunks):
            c.metadata["active_reranker_provider"] = "hybrid"
            c.metadata["provider_rank"] = rank_idx + 1
            
        total_latency = int((time.perf_counter() - start_time) * 1000)
        logger.info(
            f"[OBSERVABILITY] Rerank Fallback: provider=hybrid, candidates={len(chunks)}, top_k={limit}, returned={len(res_chunks)}"
        )
        return RerankResult(res_chunks, total_latency)
