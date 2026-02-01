from typing import Literal
from pydantic import BaseModel
import logging

from claim_processing_pipeline.experts import (
    find_applicable_policy_section,
    process_documents,
    analyse_documents,
    detect_fraud,
    make_decision,
)

logger = logging.getLogger(__name__)

class ClaimDecision(BaseModel):
    decision: Literal["APPROVE", "DENY", "UNCERTAIN"] | None = None
    explanation: str | None
    policy_context: str | None = None
    processed_documents: list[dict] | None = None


async def run_claim_processing_pipeline(
    claim_id: str,
    claim_description: str,
    supporting_filenames: list[str],
    metadata: str = "",
) -> ClaimDecision:

    decision=None
    explanation=None
    
    policy_section, explanation = await find_applicable_policy_section(claim_description)
    if not policy_section:
        decision = "DENY"
        full_document_analysis = []
    else:
        processed_docs = await process_documents(supporting_filenames)
        document_analysis = await analyse_documents(processed_docs)

        for doc in document_analysis:
            if not doc.trustworthy:
                decision = "DENY"
                explanation = f"Supporting document that requires official issuer is in invalid format (free text): {doc.name}"
                full_document_analysis = document_analysis

        if not decision:
            # 3. Call fraud detection
            full_document_analysis = await detect_fraud(document_analysis)

            # for doc in full_document_analysis:
            #     if doc.missing_signature:
            #         decision = "DENY"
            #         explanation = f"Missing signature in supporting document that requires official issuer verification: {doc.name}"

            if not decision:
                # 4. Call policy expert
                decision_result = await make_decision(
                    claim_description=claim_description,
                    analysed_docs=full_document_analysis,
                    policy_context=policy_section,
                    metadata=metadata,
                )

                decision = decision_result.decision
                explanation = decision_result.short_explanation

    # Convert DocReport objects to dicts for JSON serialization
    processed_docs_dict = [doc.model_dump() for doc in full_document_analysis]

    decision = ClaimDecision(
        decision=decision, 
        explanation=explanation,
        policy_context=policy_section,
        processed_documents=processed_docs_dict
    )

    return decision

    

