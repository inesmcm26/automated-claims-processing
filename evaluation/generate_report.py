"""
Script to generate a performance report from existing evaluation results.
"""
import json
from pathlib import Path
from typing import Literal
from datetime import datetime
from pydantic import BaseModel

from evaluation_models import ClaimEvaluationResult


class PerformanceReport(BaseModel):
    total_claims: int
    successful_evaluations: int
    failed_evaluations: int
    
    # Decision accuracy
    exact_matches: int
    acceptable_matches: int
    mismatches: int
    
    accuracy: float
    exact_accuracy: float
    
    # System decision counts
    total_approved: int
    total_denied: int
    total_uncertain: int
    
    # Decision breakdown
    approve_correct: int
    approve_incorrect: int
    deny_correct: int
    deny_incorrect: int
    uncertain_correct: int
    uncertain_incorrect: int
    
    # Performance metrics
    avg_processing_time: float | None
    
    # Detailed results
    mismatched_claims: list[str]
    failed_claims: list[str]
    
    timestamp: str


def generate_performance_report(results: list[ClaimEvaluationResult]) -> PerformanceReport:
    """
    Generate a performance report from evaluation results.
    
    Args:
        results: List of ClaimEvaluationResult objects
    
    Returns:
        PerformanceReport object
    """
    total_claims = len(results)
    successful_evaluations = sum(1 for r in results if r.error is None)
    failed_evaluations = sum(1 for r in results if r.error is not None)
    
    # Decision accuracy
    exact_matches = sum(1 for r in results if r.match_type == "exact")
    acceptable_matches = sum(1 for r in results if r.match_type == "acceptable")
    mismatches = sum(1 for r in results if r.match_type == "mismatch")
    
    accuracy = (exact_matches + acceptable_matches) / total_claims if total_claims > 0 else 0.0
    exact_accuracy = exact_matches / total_claims if total_claims > 0 else 0.0
    
    # System decision counts
    total_approved = sum(1 for r in results if r.pipeline_decision == "APPROVE")
    total_denied = sum(1 for r in results if r.pipeline_decision == "DENY")
    total_uncertain = sum(1 for r in results if r.pipeline_decision == "UNCERTAIN")
    
    # Decision breakdown
    approve_correct = sum(
        1 for r in results 
        if r.expected_decision == "APPROVE" and r.decision_match
    )
    approve_incorrect = sum(
        1 for r in results 
        if r.expected_decision == "APPROVE" and not r.decision_match
    )
    deny_correct = sum(
        1 for r in results 
        if r.expected_decision == "DENY" and r.decision_match
    )
    deny_incorrect = sum(
        1 for r in results 
        if r.expected_decision == "DENY" and not r.decision_match
    )
    uncertain_correct = sum(
        1 for r in results 
        if r.expected_decision == "UNCERTAIN" and r.decision_match
    )
    uncertain_incorrect = sum(
        1 for r in results 
        if r.expected_decision == "UNCERTAIN" and not r.decision_match
    )
    
    # Performance metrics
    processing_times = [r.processing_time_seconds for r in results if r.processing_time_seconds is not None]
    avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else None
    
    # Detailed results
    mismatched_claims = [r.claim_id for r in results if r.match_type == "mismatch"]
    failed_claims = [r.claim_id for r in results if r.error is not None]
    
    report = PerformanceReport(
        total_claims=total_claims,
        successful_evaluations=successful_evaluations,
        failed_evaluations=failed_evaluations,
        exact_matches=exact_matches,
        acceptable_matches=acceptable_matches,
        mismatches=mismatches,
        accuracy=accuracy,
        exact_accuracy=exact_accuracy,
        total_approved=total_approved,
        total_denied=total_denied,
        total_uncertain=total_uncertain,
        approve_correct=approve_correct,
        approve_incorrect=approve_incorrect,
        deny_correct=deny_correct,
        deny_incorrect=deny_incorrect,
        uncertain_correct=uncertain_correct,
        uncertain_incorrect=uncertain_incorrect,
        avg_processing_time=avg_processing_time,
        mismatched_claims=mismatched_claims,
        failed_claims=failed_claims,
        timestamp=datetime.now().isoformat()
    )
    
    return report


def print_performance_report(report: PerformanceReport):
    """Print a formatted performance report to console."""
    print("\n" + "="*80)
    print("PERFORMANCE REPORT")
    print("="*80)
    print(f"\nTimestamp: {report.timestamp}")
    print(f"\nTotal Claims: {report.total_claims}")
    print(f"Successful Evaluations: {report.successful_evaluations}")
    print(f"Failed Evaluations: {report.failed_evaluations}")
    
    print(f"\n{'Decision Accuracy':-^80}")
    print(f"Overall Accuracy: {report.accuracy:.2%} ({report.exact_matches + report.acceptable_matches}/{report.total_claims})")
    print(f"Exact Match Accuracy: {report.exact_accuracy:.2%} ({report.exact_matches}/{report.total_claims})")
    print(f"  - Exact Matches: {report.exact_matches}")
    print(f"  - Acceptable Matches: {report.acceptable_matches}")
    print(f"  - Mismatches: {report.mismatches}")
    
    print(f"\n{'System Decision Counts':-^80}")
    print(f"Total APPROVED: {report.total_approved}")
    print(f"Total DENIED: {report.total_denied}")
    print(f"Total UNCERTAIN: {report.total_uncertain}")
    
    print(f"\n{'Decision Breakdown':-^80}")
    print(f"APPROVE decisions:")
    print(f"  - Correct: {report.approve_correct}")
    print(f"  - Incorrect: {report.approve_incorrect}")
    print(f"DENY decisions:")
    print(f"  - Correct: {report.deny_correct}")
    print(f"  - Incorrect: {report.deny_incorrect}")
    print(f"UNCERTAIN decisions:")
    print(f"  - Correct: {report.uncertain_correct}")
    print(f"  - Incorrect: {report.uncertain_incorrect}")
    
    if report.avg_processing_time:
        print(f"\n{'Performance Metrics':-^80}")
        print(f"Average Processing Time: {report.avg_processing_time:.2f}s")
    
    if report.mismatched_claims:
        print(f"\n{'Mismatched Claims':-^80}")
        for claim_id in report.mismatched_claims:
            print(f"  - {claim_id}")
    
    if report.failed_claims:
        print(f"\n{'Failed Claims':-^80}")
        for claim_id in report.failed_claims:
            print(f"  - {claim_id}")
    
    print("\n" + "="*80)


def main():
    """Main function."""
    project_root = Path(__file__).parent.parent
    results_folder = project_root / "results"
    
    results_file = results_folder / "evaluation_results.json"
    report_file = results_folder / "evaluation_report.json"
    
    if not results_file.exists():
        print(f"✗ Error: {results_file} not found")
        print("Run evaluate_pipeline.py first to generate results")
        return
    
    # Load results
    print(f"Loading results from: {results_file}")
    with open(results_file, 'r') as f:
        results_data = json.load(f)
    
    results = [ClaimEvaluationResult(**r) for r in results_data]
    
    # Generate report
    print(f"Generating report for {len(results)} claims...")
    report = generate_performance_report(results)
    
    # Save report
    with open(report_file, 'w') as f:
        json.dump(report.model_dump(), f, indent=2)
    
    # Print report
    print_performance_report(report)
    
    print(f"\n✓ Report saved to: {report_file}")


if __name__ == "__main__":
    main()
