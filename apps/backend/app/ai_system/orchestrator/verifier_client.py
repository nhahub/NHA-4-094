from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel
from app.schemas.ai_schema import VerificationPolicy

class VerificationResult(BaseModel):
    success: bool
    reason: Optional[str] = None
    grounding_score: float = 1.0
    relevance_score: float = 1.0
    schema_valid: bool = True

class VerifierClient(ABC):
    """Abstract Base Class defining the verifier/grounding agent contract."""
    
    @abstractmethod
    async def verify(
        self,
        context: str,
        response: str,
        policy: VerificationPolicy
    ) -> VerificationResult:
        """
        Verifies LLM response grounding, schema compliance, relevance, and completeness.
        """
        pass

class MockVerifierClient(VerifierClient):
    """Development mock implementation of LLM response validation."""
    
    async def verify(
        self,
        context: str,
        response: str,
        policy: VerificationPolicy
    ) -> VerificationResult:
        # Check if user specifically queries to simulate a failure state for testing
        if "simulate_fail" in response or "fail_verification" in response:
            return VerificationResult(
                success=False,
                reason="Simulated grounding audit failure for testing retries.",
                grounding_score=0.4,
                relevance_score=0.9,
                schema_valid=True
            )
            
        if policy.verify_schema and ("{" in response or "[" in response):
            # Basic validation of brackets if json schema is verified
            import json
            try:
                # Attempt basic JSON parse check if brackets are present
                if response.strip().startswith("{") or response.strip().startswith("["):
                    json.loads(response)
            except Exception as e:
                return VerificationResult(
                    success=False,
                    reason=f"JSON schema verification error: {str(e)}",
                    grounding_score=1.0,
                    relevance_score=1.0,
                    schema_valid=False
                )

        return VerificationResult(
            success=True,
            reason="Grounded verification passed successfully.",
            grounding_score=0.95,
            relevance_score=0.98,
            schema_valid=True
        )

# Singleton dev instance
default_verifier_client = MockVerifierClient()
