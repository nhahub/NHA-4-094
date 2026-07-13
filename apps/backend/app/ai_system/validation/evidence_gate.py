import logging
import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.ai_system.validation.schemas import (
    DocumentTaskType,
    EvidenceStatus,
    ResponseStrategy,
    RetrievedChunk,
)
from app.ai_system.validation import rules

logger = logging.getLogger(__name__)

class EvidenceValidationResult(BaseModel):
    evidence_status: EvidenceStatus
    retrieved_count: int
    usable_chunk_count: int
    top_relevance_score: float
    coverage_score: float
    has_direct_answer: bool
    has_conflicting_evidence: bool
    reason_codes: List[str] = Field(default_factory=list)
    next_action: ResponseStrategy

async def validate_evidence(
    primary_task: DocumentTaskType,
    collected_chunks: List[RetrievedChunk],
    query: str
) -> EvidenceValidationResult:
    """
    Checks if the collected chunks provide sufficient context to fulfill the user's request.

    # Applies task-specific thresholds from rules.py (provisional — see rules.py comments).
    Returns structured validation results for routing decisions.
    """
    retrieved_count = len(collected_chunks)
    query_lower = query.lower()

    # Borderline case: zero chunks collected (and not metadata query)
    if retrieved_count == 0:
        return EvidenceValidationResult(
            evidence_status=EvidenceStatus.insufficient,
            retrieved_count=0,
            usable_chunk_count=0,
            top_relevance_score=0.0,
            coverage_score=0.0,
            has_direct_answer=False,
            has_conflicting_evidence=False,
            reason_codes=["NO_CHUNKS_FOUND"],
            next_action=ResponseStrategy.generate_out_of_scope_response
        )

    # Calculate scores
    scores = [c.similarity_score for c in collected_chunks if c.similarity_score is not None]
    top_score = max(scores) if scores else 1.0
    avg_score = sum(scores) / len(scores) if scores else 1.0

    # 1. Check for conflicting evidence
    has_conflict = False
    conflict_keywords = ["\u062a\u0639\u0627\u0631\u0636", "\u062a\u0646\u0627\u0642\u0636", "\u0627\u062e\u062a\u0644\u0627\u0641", "conflict", "contradict", "disagree"]
    if any(k in query_lower for k in conflict_keywords):
        # If we have chunks from different pages with different numbers/claims, flag it
        pages = {c.page_number for c in collected_chunks if c.page_number}
        if len(pages) > 1:
            has_conflict = True

    # 2. Task-specific routing rules using calibrated thresholds from rules.py
    reason_codes = []

    # Read task-specific thresholds (provisional — see rules.py for calibration notes)
    qa_threshold = getattr(rules, "THRESHOLD_FACTUAL_QA", 0.70)
    qa_specific_threshold = getattr(rules, "THRESHOLD_FACTUAL_QA_SPECIFIC", 0.75)
    default_threshold = getattr(rules, "THRESHOLD_DEFAULT", 0.60)

    if primary_task == DocumentTaskType.document_factual_qa:
        # Check if the query asks about a specific numeric fact
        # e.g. "هل عندي خمس سنين خبرة؟"
        has_specific_fact = bool(re.search(r"\b\d+\b", query))

        if top_score < 0.55:
            evidence_status = EvidenceStatus.insufficient
            next_action = ResponseStrategy.generate_out_of_scope_response
            reason_codes.append("LOW_RELEVANCE_SCORE")
        elif has_specific_fact and top_score < qa_specific_threshold:
            # Borderline relevance on a specific factual QA requiring exact evidence
            evidence_status = EvidenceStatus.partial
            next_action = ResponseStrategy.generate_partial_evidence_response
            reason_codes.append("BORDERLINE_SPECIFIC_FACT")
        elif top_score < qa_threshold:
            evidence_status = EvidenceStatus.insufficient
            next_action = ResponseStrategy.generate_out_of_scope_response
            reason_codes.append("INSUFFICIENT_QA_SUPPORT")
        else:
            evidence_status = EvidenceStatus.sufficient
            next_action = ResponseStrategy.continue_to_executor

    elif primary_task in [DocumentTaskType.document_summary, DocumentTaskType.document_explanation]:
        # Summary/Explanation: requires representative chunks
        if retrieved_count < 2:
            evidence_status = EvidenceStatus.partial
            next_action = ResponseStrategy.generate_partial_evidence_response
            reason_codes.append("SPARSE_CONTEXT_FOR_SUMMARY")
        else:
            evidence_status = EvidenceStatus.sufficient
            next_action = ResponseStrategy.continue_to_executor

    elif primary_task == DocumentTaskType.document_structure_analysis:
        # Structure analysis must have REPRESENTATIVE SECTION COVERAGE, not just any chunk.
        # Require chunks from at least 2 distinct pages to meaningfully assess structure.
        # A single chunk cannot describe document-wide organisation.
        distinct_pages = len({c.page_number for c in collected_chunks if c.page_number})
        if distinct_pages < 2:
            evidence_status = EvidenceStatus.partial
            next_action = ResponseStrategy.generate_partial_evidence_response
            reason_codes.append("INSUFFICIENT_SECTION_COVERAGE_FOR_STRUCTURE")
        else:
            evidence_status = EvidenceStatus.sufficient
            next_action = ResponseStrategy.continue_to_executor

    elif primary_task == DocumentTaskType.document_comparison:
        # Same-document comparison: verify representative coverage across multiple sections.
        # At least 3 distinct pages required to compare different parts meaningfully.
        # Cross-document comparison is deferred until multi-document retrieval is implemented.
        distinct_pages = len({c.page_number for c in collected_chunks if c.page_number})
        if retrieved_count < 3 or distinct_pages < 2:
            evidence_status = EvidenceStatus.partial
            next_action = ResponseStrategy.generate_partial_evidence_response
            reason_codes.append("INSUFFICIENT_COVERAGE_FOR_COMPARISON")
        else:
            evidence_status = EvidenceStatus.sufficient
            next_action = ResponseStrategy.continue_to_executor

    elif primary_task in [
        DocumentTaskType.document_evaluation,
        DocumentTaskType.document_critique,
        DocumentTaskType.document_gap_analysis,
    ]:
        # Document-wide analysis: as long as we have multiple chunks we can evaluate
        if retrieved_count < 2:
            evidence_status = EvidenceStatus.partial
            next_action = ResponseStrategy.generate_partial_evidence_response
            reason_codes.append("SPARSE_CONTEXT_FOR_EVALUATION")
        else:
            evidence_status = EvidenceStatus.sufficient
            next_action = ResponseStrategy.continue_to_executor

    elif primary_task in [
        DocumentTaskType.document_transformation,
        DocumentTaskType.document_rewrite,
        DocumentTaskType.document_formatting,
        DocumentTaskType.document_targeted_improvement
    ]:
        # CV Transformation/Rewrite: check for required CV sections
        context_text = " ".join(c.text.lower() for c in collected_chunks)
        has_experience = "experience" in context_text or "خبرة" in context_text
        has_projects = "project" in context_text or "مشروع" in context_text or "مشاريع" in context_text

        if not has_experience or not has_projects:
            evidence_status = EvidenceStatus.partial
            next_action = ResponseStrategy.generate_partial_evidence_response
            reason_codes.append("MISSING_CV_SECTIONS")
        else:
            evidence_status = EvidenceStatus.sufficient
            next_action = ResponseStrategy.continue_to_executor

    else:
        # Default fallback QA routing using default_threshold
        if top_score < default_threshold:
            evidence_status = EvidenceStatus.insufficient
            next_action = ResponseStrategy.generate_out_of_scope_response
            reason_codes.append("LOW_DEFAULT_SUPPORT")
        else:
            evidence_status = EvidenceStatus.sufficient
            next_action = ResponseStrategy.continue_to_executor

    # Conflicting evidence override (only when evidence is not already insufficient)
    if has_conflict and evidence_status != EvidenceStatus.insufficient:
        evidence_status = EvidenceStatus.conflicting
        next_action = ResponseStrategy.generate_conflicting_evidence_response
        reason_codes.append("CONFLICTING_EVIDENCE_FOUND")

    return EvidenceValidationResult(
        evidence_status=evidence_status,
        retrieved_count=retrieved_count,
        usable_chunk_count=retrieved_count,
        top_relevance_score=top_score,
        coverage_score=avg_score,
        has_direct_answer=evidence_status == EvidenceStatus.sufficient,
        has_conflicting_evidence=has_conflict,
        reason_codes=reason_codes,
        next_action=next_action
    )
