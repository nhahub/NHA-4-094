import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from app.ai_system.services.llm.generation_service import GenerationService
from app.ai_system.services.llm.providers.groq_provider import GroqProvider
from app.ai_system.services.llm.schemas import LLMEngineerPayload
from app.ai_system.services.llm.exceptions import (
    LLMTimeoutError,
    LLMRateLimitError,
    LLMProviderUnavailableError,
    JSONParsingException
)
from app.ai_system.retrieval.schemas import RetrievedChunk, MetadataFilters

def make_payload():
    from app.ai_system.services.llm.schemas import (
        SourceInfo,
        StrictGroundingPolicy,
        ExpectedLLMOutputFormat,
        ChunkContext
    )
    from app.schemas.ai_schema import TaskType
    return LLMEngineerPayload(
        task_id="task-123",
        task_type="explain",
        pipeline_type="standard_rag",
        original_user_query="explain photosyn",
        task_query="explain photosyn",
        source=SourceInfo(source_id="doc-123", source_type="document"),
        retrieved_document_context=[
            ChunkContext(
                chunk_id="chunk-1",
                page_number=1,
                score=0.9,
                content="Photosynthesis process happens in cells."
            )
        ],
        strict_grounding_policy=StrictGroundingPolicy(
            academic_source_of_truth="retrieved_document_context_only",
            memory_usage="personalization_only",
            if_document_context_insufficient="fallback answer"
        ),
        expected_llm_output_format=ExpectedLLMOutputFormat(type="text"),
        memory_context=None
    )

@pytest.mark.asyncio
async def test_parameter_stripping_non_gpt_oss():
    provider = GroqProvider()
    
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Explanation text"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5}
        }
        mock_post.return_value = mock_response
        
        # Test calling with reasoning_effort for llama model
        await provider.generate(
            model="llama-3.3-70b-versatile",
            prompt="hello",
            api_key="gsk_key",
            reasoning_effort="high"
        )
        
        # Verify that reasoning_effort was stripped
        called_payload = mock_post.call_args[1]["json"]
        assert "reasoning_effort" not in called_payload
        assert "include_reasoning" not in called_payload

@pytest.mark.asyncio
async def test_parameter_forwarding_gpt_oss():
    provider = GroqProvider()
    
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Explanation text"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5}
        }
        mock_post.return_value = mock_response
        
        # Test calling with reasoning_effort for GPT-OSS model
        await provider.generate(
            model="openai/gpt-oss-120b",
            prompt="hello",
            api_key="gsk_key",
            reasoning_effort="high"
        )
        
        # Verify that reasoning_effort was forwarded
        called_payload = mock_post.call_args[1]["json"]
        assert called_payload["reasoning_effort"] == "high"
        assert called_payload["include_reasoning"] is False

@pytest.mark.asyncio
async def test_timeout_retries_once_then_falls_back():
    service = GenerationService()
    
    with patch.object(service.provider, "generate", new_callable=AsyncMock) as mock_gen:
        # First call: Timeout. Second call: Timeout -> Fall back to Qwen
        mock_gen.side_effect = [
            LLMTimeoutError("Timeout error"),
            LLMTimeoutError("Timeout error"),
            {"text": "Fallback Qwen success", "input_tokens": 10, "output_tokens": 5, "latency_ms": 100, "key_alias": "k1"}
        ]
        
        payload = make_payload()
        res = await service.execute_task(payload)
        
        # Ensure it completed successfully via fallback
        assert res.status == "success"
        assert res.output_text == "Fallback Qwen success"
        # Should have called generate 3 times (attempt 1, attempt 2 of primary model, then attempt 1 of qwen fallback)
        assert mock_gen.call_count == 3
        # First two calls should be for primary model
        assert mock_gen.call_args_list[0][1]["model"] == "openai/gpt-oss-120b"
        assert mock_gen.call_args_list[1][1]["model"] == "openai/gpt-oss-120b"
        # Third call should be for fallback Qwen
        assert mock_gen.call_args_list[2][1]["model"] == "qwen/qwen3-32b"

@pytest.mark.asyncio
async def test_429_immediately_falls_back():
    service = GenerationService()

    with patch.object(service.provider, "generate", new_callable=AsyncMock) as mock_gen, \
         patch("app.ai_system.services.llm.api_key_pool.APIKey.is_available", return_value=True):
        # First call to primary model returns HTTP 429
        mock_gen.side_effect = [
            LLMRateLimitError("Rate limit"),
            {"text": "Fallback Qwen success", "input_tokens": 10, "output_tokens": 5, "latency_ms": 100, "key_alias": "k1"}
        ]
        
        payload = make_payload()
        res = await service.execute_task(payload)
        
        assert res.status == "success"
        assert res.output_text == "Fallback Qwen success"
        assert mock_gen.call_count == 2
        assert mock_gen.call_args_list[0][1]["model"] == "openai/gpt-oss-120b"
        assert mock_gen.call_args_list[1][1]["model"] == "qwen/qwen3-32b"
