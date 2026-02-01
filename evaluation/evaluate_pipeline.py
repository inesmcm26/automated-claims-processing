"""
Evaluation script for the claim processing pipeline.
Compares pipeline decisions against ground truth in answer.json files.
"""
import asyncio
import json
from pathlib import Path
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from claim_processing_pipeline.pipeline import run_claim_processing_pipeline
from claim_processing_pipeline.config import setup_logging
from evaluation_models import GroundTruth, ClaimEvaluationResult

# Set up logging for the script
setup_logging("INFO")


async def evaluate_single_claim(
    claim_dir: Path,
    results_file: Path
) -> ClaimEvaluationResult:
    """
    Evaluate a single claim and append results to the JSON file.
    
    Args:
        claim_dir: Path to the claim directory
        results_file: Path to the results JSON file
    
    Returns:
        ClaimEvaluationResult object
    """
    claim_id = claim_dir.name
    print(f"\n{'='*60}")
    print(f"Evaluating {claim_id}")
    print(f"{'='*60}")
    
    start_time = datetime.now()
    
    # Helper function to create error result
    def create_error_result(error_msg: str, ground_truth: GroundTruth | None = None) -> ClaimEvaluationResult:
        return ClaimEvaluationResult(
            claim_id=claim_id,
            claim_description="",
            expected_decision=ground_truth.decision if ground_truth else "",
            acceptable_decision=ground_truth.acceptable_decision if ground_truth else None,
            ground_truth_explanation=ground_truth.explanation if ground_truth else "",
            pipeline_decision=None,
            pipeline_explanation=None,
            policy_context=None,
            processed_documents=[],
            decision_match=False,
            match_type="error",
            processing_time_seconds=None,
            error=error_msg
        )
    
    # Load ground truth
    answer_file = claim_dir / "answer.json"
    if not answer_file.exists():
        error_result = create_error_result(f"answer.json not found in {claim_dir}")
        _append_result_to_file(results_file, error_result)
        return error_result
    
    with open(answer_file, 'r') as f:
        ground_truth_data = json.load(f)
    
    ground_truth = GroundTruth(**ground_truth_data)
    
    # Load claim description
    description_file = claim_dir / "description.txt"
    if not description_file.exists():
        error_result = create_error_result(f"description.txt not found in {claim_dir}", ground_truth)
        _append_result_to_file(results_file, error_result)
        return error_result
    
    description = description_file.read_text(encoding='utf-8').strip()
    
    # Get supporting documents
    supporting_files = []
    for file in claim_dir.iterdir():
        if file.name not in ["answer.json", "description.txt", ".DS_Store"]:
            supporting_files.append(str(file.absolute()))
    
    # Run pipeline
    try:
        pipeline_result = await run_claim_processing_pipeline(
            claim_id=claim_id,
            claim_description=description,
            supporting_filenames=supporting_files,
            metadata=""
        )
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # Extract intermediate results from pipeline
        policy_context = pipeline_result.policy_context
        processed_documents = pipeline_result.processed_documents or []
        
        # Evaluate decision
        pipeline_decision = pipeline_result.decision
        decision_match = False
        match_type = "mismatch"
        
        if pipeline_decision == ground_truth.decision:
            decision_match = True
            match_type = "exact"
        elif ground_truth.acceptable_decision and pipeline_decision == ground_truth.acceptable_decision:
            decision_match = True
            match_type = "acceptable"
        
        result = ClaimEvaluationResult(
            claim_id=claim_id,
            claim_description=description,
            expected_decision=ground_truth.decision,
            acceptable_decision=ground_truth.acceptable_decision,
            ground_truth_explanation=ground_truth.explanation,
            pipeline_decision=pipeline_decision,
            pipeline_explanation=pipeline_result.explanation,
            policy_context=policy_context,
            processed_documents=processed_documents,
            decision_match=decision_match,
            match_type=match_type,
            processing_time_seconds=processing_time,
            error=None
        )
        
        print(f"✓ Expected: {ground_truth.decision}, Got: {pipeline_decision}, Match: {match_type}")
        
    except Exception as e:
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        result = ClaimEvaluationResult(
            claim_id=claim_id,
            claim_description=description,
            expected_decision=ground_truth.decision,
            acceptable_decision=ground_truth.acceptable_decision,
            ground_truth_explanation=ground_truth.explanation,
            pipeline_decision=None,
            pipeline_explanation=None,
            policy_context=None,
            processed_documents=[],
            decision_match=False,
            match_type="error",
            processing_time_seconds=processing_time,
            error=str(e)
        )
        
        print(f"✗ Error processing claim: {e}")
    
    # Append result to file
    _append_result_to_file(results_file, result)
    
    return result


def _append_result_to_file(results_file: Path, result: ClaimEvaluationResult):
    """Append a single result to the JSON results file."""
    # Read existing results
    if results_file.exists():
        with open(results_file, 'r') as f:
            try:
                results = json.load(f)
            except json.JSONDecodeError:
                results = []
    else:
        results = []
    
    # Append new result
    results.append(result.model_dump())
    
    # Write back
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)


async def evaluate_all_claims(
    claims_dir: Path,
    results_file: Path
) -> list[ClaimEvaluationResult]:
    """
    Evaluate all claims in the claims directory.
    
    Args:
        claims_dir: Path to directory containing claim folders
        results_file: Path to save results JSON file
    
    Returns:
        List of ClaimEvaluationResult objects
    """
    # Clear existing results file
    if results_file.exists():
        results_file.unlink()
    
    # Get all claim directories
    claim_dirs = sorted([d for d in claims_dir.iterdir() if d.is_dir() and d.name.startswith("claim")])
    
    print(f"Found {len(claim_dirs)} claims to evaluate")
    
    results = []
    for claim_dir in claim_dirs:
        result = await evaluate_single_claim(claim_dir, results_file)
        results.append(result)
    
    return results


async def main():
    """Main evaluation function."""
    # Set up paths
    project_root = Path(__file__).parent.parent
    claims_dir = project_root / "data" / "claims"
    results_folder = project_root / "results"
    results_file = results_folder / "evaluation_results.json"

    if not results_folder.is_dir():
        results_folder.mkdir(parents=True)
    
    print(f"Claims directory: {claims_dir}")
    print(f"Results file: {results_file}")
    
    # Run evaluation
    results = await evaluate_all_claims(claims_dir, results_file)
    
    print(f"\n✓ Evaluation complete: {len(results)} claims processed")
    print(f"✓ Results saved to: {results_file}")
    print(f"\nRun 'python scripts/generate_report.py' to generate performance report")


if __name__ == "__main__":
    asyncio.run(main())
