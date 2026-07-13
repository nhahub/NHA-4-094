"""
PipelineState — typed dataclass carrying per-request pipeline metadata.

Replaces dynamic attributes (_retrieval_result, _input_validation, _trace_stages)
previously set directly on the request object. Attach one instance per request as:

    request._pipeline_state = PipelineState()

All callers should prefer `getattr(request, "_pipeline_state", None)` for backward
compatibility, but new code should always use this typed container.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.ai_system.validation.schemas import InputValidationResult
    from app.ai_system.retrieval.schemas import RetrievalResult  # type: ignore[attr-defined]


@dataclass
class PipelineState:
    """
    Carries transient per-request state across pipeline stages.

    Fields
    ------
    retrieval_result:
        The raw RetrievalResult from the DocumentRetriever.  Set by
        collect_context() during focused_retrieval and used downstream by the
        citation builder and evidence gate.  None until retrieval completes.

    input_validation:
        The result of validate_input().  Set by ai_orchestrator.py before
        any pipeline step runs.

    trace_stages:
        Ordered list of stage diagnostic dicts appended throughout execution.
        Each dict has at least {"stage": str, "status": str}.

    NOTE (asyncio.create_task):
        Title generation inside chat_repository uses asyncio.create_task, which
        is non-durable: if the event loop exits before the task completes, the
        title update is silently dropped.  This is acceptable for the current
        single-process deployment.  For production durability, migrate to an
        explicit background queue (e.g. ARQ or Celery) tied to a persistent
        job store.
    """
    retrieval_result: Optional[Any] = None           # RetrievalResult | None
    input_validation: Optional[Any] = None           # InputValidationResult | None
    trace_stages: List[Any] = field(default_factory=list)


class PipelineRequestContext:
    """
    Robust wrapper around FastAPI/Pydantic request objects.
    Explicitly carries PipelineState to prevent loss of dynamic underscore attributes
    when models are copied or mocked.
    """
    def __init__(self, request: Any, state: PipelineState):
        super().__setattr__("request", request)
        super().__setattr__("state", state)

    def __getattr__(self, name: str) -> Any:
        return getattr(self.request, name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name in ("request", "state"):
            super().__setattr__(name, value)
        else:
            setattr(self.request, name, value)
