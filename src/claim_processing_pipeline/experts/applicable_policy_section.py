import logging

from claim_processing_pipeline.prompts import IDENTIFY_POLICY_SECTION_PROMPT
from claim_processing_pipeline.constants import SCENARIO_POLICY_SECTION_MAPPING, EXCLUSIONS_SECTION
from claim_processing_pipeline.utils import call_ollama_structured
from claim_processing_pipeline.schemas import RelevantPolicySectionChoice

logger = logging.getLogger(__name__)


async def find_applicable_policy_section(claim_description: str) -> tuple[str | None, str]:
    """
    Identifies which policy section applies to the claim based on the description.
    
    Uses LLM to analyze the claim and determine which insurance policy section
    is relevant (e.g., trip cancellation, personal effects, missed departure).

    Args:
        claim_description: Text description of the insurance claim
        
    Returns:
        Tuple containing:
        - Policy section text with requirements and covered scenarios
        - Explanation of why this section was chosen
    """    
    section_choice = await call_ollama_structured(
        IDENTIFY_POLICY_SECTION_PROMPT.format(claim=claim_description),
        response_model=RelevantPolicySectionChoice,
    )
    
    covered_scenario_identifier = section_choice.identifier
    explanation = section_choice.short_explanation
    
    logger.info(f"Identified policy section: {covered_scenario_identifier}")
    logger.debug(f"Explanation: {explanation}")

    if covered_scenario_identifier == "D":
        policy = None
    else:
        policy = f"{SCENARIO_POLICY_SECTION_MAPPING[covered_scenario_identifier]}\n\n{EXCLUSIONS_SECTION}"

    return policy, explanation
