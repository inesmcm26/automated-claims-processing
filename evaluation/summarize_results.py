"""
Script to create a summarized version of evaluation results.
Extracts only the key fields for easier review.
"""
import json
from pathlib import Path
from typing import Literal
from pydantic import BaseModel


class SummarizedResult(BaseModel):
    claim_id: str
    claim_description: str
    expected_decision: str
    acceptable_decision: str | None
    ground_truth_explanation: str | None
    pipeline_decision: str | None
    pipeline_explanation: str | None
    decision_match: bool
    match_type: Literal["exact", "acceptable", "mismatch", "error"] | None


def summarize_results(input_file: Path, output_file: Path):
    """
    Create a summarized version of evaluation results.
    
    Args:
        input_file: Path to full evaluation results JSON
        output_file: Path to save summarized results JSON
    """
    # Load full results
    with open(input_file, 'r') as f:
        full_results = json.load(f)
    
    # Extract key fields
    summarized = []
    for result in full_results:
        summary = SummarizedResult(
            claim_id=result["claim_id"],
            claim_description=result["claim_description"],
            expected_decision=result["expected_decision"],
            acceptable_decision=result.get("acceptable_decision"),
            ground_truth_explanation=result.get("ground_truth_explanation"),
            pipeline_decision=result.get("pipeline_decision"),
            pipeline_explanation=result.get("pipeline_explanation"),
            decision_match=result["decision_match"],
            match_type=result.get("match_type")
        )
        summarized.append(summary.model_dump())
    
    # Save summarized results
    with open(output_file, 'w') as f:
        json.dump(summarized, f, indent=2)
    
    print(f"✓ Summarized {len(summarized)} results")
    print(f"✓ Saved to: {output_file}")


def main():
    """Main function."""
    project_root = Path(__file__).parent.parent
    results_folder = project_root / "results"
    
    input_file = results_folder / "evaluation_results.json"
    output_file = results_folder / "evaluation_results_summary.json"
    
    if not input_file.exists():
        print(f"✗ Error: {input_file} not found")
        print("Run evaluate_pipeline.py first to generate results")
        return
    
    summarize_results(input_file, output_file)


if __name__ == "__main__":
    main()
