"""
Test evaluation on a single claim for debugging.

Usage:
    python scripts/test_single_claim.py 1
    python scripts/test_single_claim.py 8
"""
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from evaluate_pipeline import evaluate_single_claim


async def main():
    """Test evaluation on a single claim."""
    # Parse command line argument
    if len(sys.argv) < 2:
        print("Error: Please provide a claim number")
        print("Usage: python scripts/test_single_claim.py <claim_number>")
        print("Example: python scripts/test_single_claim.py 1")
        sys.exit(1)
    
    claim_number = sys.argv[1]
    
    project_root = Path(__file__).parent.parent
    claim_dir = project_root / "data" / "claims" / f"claim {claim_number}"
    
    if not claim_dir.exists():
        print(f"Error: Claim directory not found: {claim_dir}")
        print(f"Available claims:")
        claims_dir = project_root / "data" / "claims"
        for d in sorted(claims_dir.iterdir()):
            if d.is_dir() and d.name.startswith("claim"):
                print(f"  - {d.name}")
        sys.exit(1)
    
    results_folder = project_root / "results"
    results_file = results_folder / "test_single_result.json"

    if not results_folder.is_dir():
        results_folder.mkdir(parents=True)
    
    if results_file.exists():
        results_file.unlink()
    
    print(f"Testing evaluation on: {claim_dir}")
    
    result = await evaluate_single_claim(claim_dir, results_file)
    
    print("\n" + "="*80)
    print("RESULT")
    print("="*80)
    print(json.dumps(result.model_dump(), indent=2))
    
    print(f"\n✓ Result saved to: {results_file}")


if __name__ == "__main__":
    asyncio.run(main())
