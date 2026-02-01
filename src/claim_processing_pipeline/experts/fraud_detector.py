import logging
from pathlib import Path
from ollama import chat

from claim_processing_pipeline.schemas import DocReport
from claim_processing_pipeline.prompts import SIGNATURE_DETECTION_PROMPT

logger = logging.getLogger(__name__)


async def detect_fraud(analysed_docs: list[DocReport]) -> list[DocReport]:
    """
    Detects potential fraud indicators in analyzed documents.
    
    Checks for missing signatures in official documents that require them
    (medical certificates, police reports, jury summons, etc.). Documents in plain
    text format (.md, .txt) are skipped as they cannot contain signatures.

    Args:
        analysed_docs: List of analyzed document reports
        
    Returns:
        Updated list of document reports with fraud detection results
    """
    logger.info(f"Running fraud detection on {len(analysed_docs)} document(s)")
    
    for doc in analysed_docs:
        doc.fraud_detection = "Nothing to report"
        
        # Only check signature for official documents in image format
        if doc.requires_official_issuer and doc.file_ext not in [".md", ".txt"]:
            try:
                # Use vision LM to detect signature presence
                image_path = str(Path(doc.name).absolute())
                response = chat(
                    model="qwen2.5vl:7b-q4_K_M",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant for insurance document analysis."},
                        {"role": "user", "content": SIGNATURE_DETECTION_PROMPT, "images": [image_path]}
                    ],
                    options={"temperature": 0}
                )

                content = response.message.content
                if not content:
                    raise Exception("No content returned from model")

                logger.debug(f"Signature detection response: {content}")
                if "none" in content.lower():
                    doc.fraud_detection = "The document is missing a signature/official seal"
                logger.info(f"Fraud detection result: {doc.fraud_detection}")

            except Exception as e:
                logger.error(f"Vision LM request failed: {str(e)}")
                raise e

    return analysed_docs
