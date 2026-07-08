from typing import Any
from app.schemas.ai_schema import AIResponse
from app.ai_system.orchestrator.document_guard import validate_document_access
from app.ai_system.orchestrator.planner import TaskPlanner
from app.ai_system.orchestrator.orchestrator import TaskOrchestrator

class AIOrchestratorService:
    """
    Central service layer acting as the single entrypoint for all AI operations.
    Validates input permissions, generates plans, and executes pipelines.
    """
    def __init__(self) -> None:
        self.planner = TaskPlanner()
        self.orchestrator = TaskOrchestrator()

    async def execute_query(self, document_id: str, request: Any, user_id: str) -> AIResponse:
        """
        Validates access to the document, compiles the task plan,
        and routes execution through the orchestrator.
        """
        # Validate existence, ownership, and ingestion status
        await validate_document_access(document_id, user_id)
        
        # Inject document_id into the request object
        request.document_id = document_id
        
        # Build plan
        plan = self.planner.plan(request)
        
        # Execute & return merged response
        response = await self.orchestrator.execute(plan, request)
        return response

# Global process-wide singleton
ai_orchestrator_service = AIOrchestratorService()
