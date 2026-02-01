"""
Shared models for evaluation.
"""
from typing import Literal
from pydantic import BaseModel


class GroundTruth(BaseModel):
    decision: Literal["APPROVE", "DENY", "UNCERTAIN"]
    explanation: str | None = None
    acceptable_decision: Literal["APPROVE", "DENY", "UNCERTAIN"] | None = None


class ClaimEvaluationResult(BaseModel):
    claim_id: str
    claim_description: str
    
    # Ground truth
    expected_decision: str
    acceptable_decision: str | None
    ground_truth_explanation: str | None = None
    
    # Pipeline results
    pipeline_decision: str | None
    pipeline_explanation: str | None
    
    # Intermediate results
    policy_context: str | None
    processed_documents: list[dict]
    
    # Evaluation
    decision_match: bool
    match_type: Literal["exact", "acceptable", "mismatch", "error"] | None
    
    # Metadata
    processing_time_seconds: float | None
    error: str | None
