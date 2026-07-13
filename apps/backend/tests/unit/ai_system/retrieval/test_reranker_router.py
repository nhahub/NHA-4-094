import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.ai_system.retrieval.reranker import MultilingualRerankerRouter, RerankResult, RuleBasedReranker
from app.ai_system.retrieval.schemas import RetrievedChunk, MetadataFilters
from app.core.config import settings

def make_chunk(chunk_id, text, score=0.8):
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id="doc123",
        user_id="user123",
        text=text,
        score=score,
        vector_score=score,
        keyword_score=score,
        page_number=1,
        section_title="Intro",
        metadata={}
    )

@pytest.mark.asyncio
async def test_jina_selected_when_healthy():
    chunks = [make_chunk("c1", "Photosynthesis processes", 0.8)]
    router = MultilingualRerankerRouter()
    
    # Mock settings
    with patch.object(settings, "JINA_API_KEY", "jina_mock_key"), \
         patch.object(settings, "RERANKER_PROVIDER_ORDER", "jina"), \
         patch.object(router.adapters["jina"], "rerank", new_callable=AsyncMock) as mock_jina:
        
        mock_jina.return_value = [{"index": 0, "score": 0.95}]
        
        res = await router.rerank_async(
            chunks=chunks,
            query="photosynthesis",
            query_terms=["photosynthesis"],
            filters=MetadataFilters(),
            limit=1
        )
        assert len(res.chunks) == 1
        assert res.chunks[0].score == 0.95
        assert res.chunks[0].metadata["active_reranker_provider"] == "jina"
        assert res.chunks[0].metadata["original_hybrid_score"] == 0.8
        mock_jina.assert_called_once()

@pytest.mark.asyncio
async def test_missing_jina_key_skips_jina_cohere_becomes_primary():
    chunks = [make_chunk("c1", "Photosynthesis processes", 0.8)]
    router = MultilingualRerankerRouter()
    
    with patch.object(settings, "JINA_API_KEY", ""), \
         patch.object(settings, "COHERE_API_KEY", "cohere_mock_key"), \
         patch.object(settings, "RERANKER_PROVIDER_ORDER", "jina,cohere"), \
         patch.object(router.adapters["jina"], "rerank", new_callable=AsyncMock) as mock_jina, \
         patch.object(router.adapters["cohere"], "rerank", new_callable=AsyncMock) as mock_cohere:
        
        mock_cohere.return_value = [{"index": 0, "score": 0.92}]
        
        res = await router.rerank_async(
            chunks=chunks,
            query="photosynthesis",
            query_terms=["photosynthesis"],
            filters=MetadataFilters(),
            limit=1
        )
        assert len(res.chunks) == 1
        assert res.chunks[0].score == 0.92
        assert res.chunks[0].metadata["active_reranker_provider"] == "cohere"
        mock_jina.assert_not_called()
        mock_cohere.assert_called_once()

@pytest.mark.asyncio
async def test_cloudflare_used_when_jina_and_cohere_unavailable():
    chunks = [make_chunk("c1", "Photosynthesis", 0.8)]
    router = MultilingualRerankerRouter()
    
    with patch.object(settings, "JINA_API_KEY", "jina_key"), \
         patch.object(settings, "COHERE_API_KEY", "cohere_key"), \
         patch.object(settings, "CLOUDFLARE_ACCOUNT_ID", "cf_acc"), \
         patch.object(settings, "CLOUDFLARE_API_TOKEN", "cf_token"), \
         patch.object(settings, "RERANKER_PROVIDER_ORDER", "jina,cohere,cloudflare"), \
         patch.object(router.adapters["jina"], "rerank", new_callable=AsyncMock) as mock_jina, \
         patch.object(router.adapters["cohere"], "rerank", new_callable=AsyncMock) as mock_cohere, \
         patch.object(router.adapters["cloudflare"], "rerank", new_callable=AsyncMock) as mock_cf:
        
        mock_jina.side_effect = Exception("Jina failed")
        mock_cohere.side_effect = Exception("Cohere failed")
        mock_cf.return_value = [{"index": 0, "score": 0.89}]
        
        res = await router.rerank_async(
            chunks=chunks,
            query="photosynthesis",
            query_terms=["photosynthesis"],
            filters=MetadataFilters(),
            limit=1
        )
        assert len(res.chunks) == 1
        assert res.chunks[0].score == 0.89
        assert res.chunks[0].metadata["active_reranker_provider"] == "cloudflare"
        mock_jina.assert_called_once()
        mock_cohere.assert_called_once()
        mock_cf.assert_called_once()

@pytest.mark.asyncio
async def test_rule_based_reranker_used_when_api_providers_fail():
    chunks = [make_chunk("c1", "Photosynthesis", 0.8)]
    router = MultilingualRerankerRouter()
    
    with patch.object(settings, "JINA_API_KEY", "jina_key"), \
         patch.object(settings, "RERANKER_PROVIDER_ORDER", "jina,rule_based"), \
         patch.object(router.adapters["jina"], "rerank", new_callable=AsyncMock) as mock_jina, \
         patch.object(router.rule_based_reranker, "rerank") as mock_rule:
        
        mock_jina.side_effect = Exception("Jina failed")
        mock_rule.return_value = RerankResult([make_chunk("c1", "Photosynthesis", 0.85)], 5)
        
        res = await router.rerank_async(
            chunks=chunks,
            query="photosynthesis",
            query_terms=["photosynthesis"],
            filters=MetadataFilters(),
            limit=1
        )
        assert len(res.chunks) == 1
        assert res.chunks[0].score == 0.85
        assert res.chunks[0].metadata["active_reranker_provider"] == "rule_based"
        mock_jina.assert_called_once()
        mock_rule.assert_called_once()

@pytest.mark.asyncio
async def test_original_hybrid_ordering_preserved_when_all_fail():
    chunks = [make_chunk("c1", "Photosynthesis", 0.8)]
    router = MultilingualRerankerRouter()
    
    with patch.object(settings, "JINA_API_KEY", "jina_key"), \
         patch.object(settings, "RERANKER_PROVIDER_ORDER", "jina,rule_based,hybrid"), \
         patch.object(router.adapters["jina"], "rerank", new_callable=AsyncMock) as mock_jina, \
         patch.object(router.rule_based_reranker, "rerank") as mock_rule:
        
        mock_jina.side_effect = Exception("Jina failed")
        mock_rule.side_effect = Exception("Rule based failed")
        
        res = await router.rerank_async(
            chunks=chunks,
            query="photosynthesis",
            query_terms=["photosynthesis"],
            filters=MetadataFilters(),
            limit=1
        )
        assert len(res.chunks) == 1
        assert res.chunks[0].score == 0.8
        assert res.chunks[0].metadata["active_reranker_provider"] == "hybrid"
