import re
import logging

from claim_processing_pipeline.schemas import ProcessedDoc, DocReport
from claim_processing_pipeline.utils import (
    model_to_class_string,
    call_ollama_chat,
    call_ollama_structured,
)
from claim_processing_pipeline.prompts import (
    DOC_TYPE_PROMPT,
    ANALYSE_DOCUMENTS_PROMPT
)
from claim_processing_pipeline.constants import DOC_TYPE_SCHEMA_MAPPING

logger = logging.getLogger(__name__)


async def _identify_document_type(doc: ProcessedDoc) -> int:
    """
    Identifies the type of document using LLM classification.

    Returns:
        Document type code (1-7)
    """
    response = await call_ollama_chat(
        prompt=DOC_TYPE_PROMPT.format(
            document=f"Document name:{doc.name}\nContent:{doc.text}"
        ),
    )

    match = re.search(r"\d+", response)
    if not match:
        logger.warning(f"Could not extract document type from response, defaulting to 7 (unknown)")
        return 7
    
    chosen_option = int(match.group())
    if chosen_option < 1 or chosen_option > 7:
        logger.warning(f"Invalid document type {chosen_option}, defaulting to 7 (unknown)")
        return 7
    
    logger.info(f"Identified as document type {chosen_option}")
    return chosen_option


async def _extract_structured_fields(doc: ProcessedDoc, doc_type: int):
    """
    Extracts structured fields from document using corresponding document type schema.
    If document is plain text already, do not extract fields.
    """
    # Skip extraction for unknown types or text documents
    if doc_type == 7 or doc.file_ext in [".txt", ".md"]:
        logger.info("Skipping field extraction (text document or unknown type)")
        return None
    
    chosen_schema = DOC_TYPE_SCHEMA_MAPPING[doc_type]
    logger.info(f"Extracting structured fields using schema: {chosen_schema.__name__}")
    
    extracted_fields = await call_ollama_structured(
        ANALYSE_DOCUMENTS_PROMPT.format(
            document=f"Document name: {doc.name}\nContent: {doc.text}",
            schema=model_to_class_string(chosen_schema)
        ),
        response_model=chosen_schema,
    )
    logger.info(f"Extracted fields: {extracted_fields}")
    return extracted_fields


def _assess_trustworthiness(doc: ProcessedDoc, requires_official_issuer: bool) -> bool:
    """
    Assesses document trustworthiness based on format and requirements.
    A document is not trustworthy if it requires an official issuer but is in plain text format.
    """
    # Official documents shouldn't be plain text/markdown files
    trustworthy = not (requires_official_issuer and doc.file_ext in [".txt", ".md"])
    
    if not trustworthy:
        logger.info(f"Document marked as untrustworthy (official issuer required but format is text)")
    else:
        logger.info("Document format is trustworthy")
    
    return trustworthy


async def analyse_documents(processed_docs: list[ProcessedDoc]) -> list[DocReport]:
    """
    Analyzes processed documents to identify their type, extract structured fields, and assess trustworthiness.
    
    This function performs three main steps for each document:
    1. Type classification: Uses LLM to identify document type (medical report, police report, 
       jury summons, booking proof, etc.)
    2. Field extraction: For non-text documents, extracts structured data fields using the 
       appropriate schema (e.g., patient name, diagnosis from medical reports)
    3. Trustworthiness assessment: Validates that official documents are in proper format (not plain text)
    
    Args:
        processed_docs: List of documents with extracted text content from OCR or file reading
        
    Returns:
        List of document reports containing:
        - Document type classification
        - Extracted structured fields (for image documents)
        - Trustworthiness flag based on format validation
        - Whether document requires official issuer verification (all except proof of booking)
    """
    logger.info(f"Analyzing {len(processed_docs)} document(s)")
    doc_reports = []

    for doc in processed_docs:
        logger.info(f"Analyzing document: {doc.name}")
        
        # Identify document type
        doc_type = await _identify_document_type(doc)
        
        # Determine if that type of document requires an official issuer (types 1-5)
        requires_official_issuer = doc_type not in [6, 7]
        logger.info(f"Requires official issuer: {requires_official_issuer}")

        # Extract structured fields
        extracted_fields = await _extract_structured_fields(doc, doc_type)

        # Assess trustworthiness
        trustworthy = _assess_trustworthiness(doc, requires_official_issuer)

        # Build document report
        doc_report = DocReport(**doc.model_dump())
        doc_report.requires_official_issuer = requires_official_issuer
        doc_report.extracted_fields = extracted_fields
        doc_report.trustworthy = trustworthy
        doc_reports.append(doc_report)

    logger.info(f"Document analysis complete: {len(doc_reports)} documents analyzed")
    logger.info(f"Results: {doc_reports}")
    return doc_reports
