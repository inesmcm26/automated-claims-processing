import logging

from claim_processing_pipeline.utils import call_ollama_structured
from claim_processing_pipeline.schemas import DocReport
from claim_processing_pipeline.prompts import POLICY_EXPERT_PROMPT
from claim_processing_pipeline.schemas import DecisionResults

logger = logging.getLogger(__name__)

async def make_decision(
    claim_description: str,
    analysed_docs: list[DocReport],
    policy_context: str,
    metadata: str = "",
) -> DecisionResults:
    """
    Makes final claim decision by analyzing claim against policy and supporting documents.
    
    Uses LLM to act as a policy expert that:
    - Verifies claim details against supporting documents
    - Checks if all policy requirements are met
    - Identifies any exclusions or missing documentation
    - Makes final APPROVE/DENY/UNCERTAIN decision
    
    Args:
        claim_description: The claim description text
        analysed_docs: List of analyzed documents with extracted text and fields
        policy_context: Relevant policy text including requirements and exclusions
        metadata: Extra metadata (dates, names, etc.)
        
    Returns:
        Decision result with verdict (APPROVE/DENY/UNCERTAIN) and explanation
    """
    logger.info("Preparing document analysis report for policy expert")
    
    # Build document context from analyzed documents
    docs_ctx = []
    for doc in analysed_docs:
        doc_content = doc.extracted_fields.model_dump() if doc.extracted_fields else doc.text
        doc_ctx = f"Document name: {doc.name}\nContent: {doc_content}\nFraud detection report: {doc.fraud_detection}" 
        docs_ctx.append(doc_ctx)

    document_analysis_report = "\n\n--------\n\n".join(docs_ctx)

    decision_results = await call_ollama_structured(
        POLICY_EXPERT_PROMPT.format(
            policy=policy_context,
            claim=claim_description,
            document_analysis_report=document_analysis_report,
            metadata=f"Metadata:\n{metadata}" if metadata else "",
        ),
        response_model=DecisionResults,
    )

    logger.info(f"Policy expert decision: {decision_results.decision}")
    logger.info(f"Explanation: {decision_results.short_explanation}")
    return decision_results