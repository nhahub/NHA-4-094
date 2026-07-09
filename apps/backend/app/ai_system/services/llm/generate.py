from .schemas import LLMEngineerPayload, LLMResponsePayload
from .generation_service import GenerationService

async def llm_generate(payload: LLMEngineerPayload) -> LLMResponsePayload:
    """
    Core generation function.
    """
    service = GenerationService()
    return await service.execute_task(payload)

async def generate(payload: LLMEngineerPayload) -> LLMResponsePayload:
    """
    Required public integration endpoint for the LLM layer.
    Delegates task execution to llm_generate.
    """
    return await llm_generate(payload)
