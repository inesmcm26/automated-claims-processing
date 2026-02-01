# Evaluation Scripts

Scripts for evaluating the claim processing pipeline against ground truth data.

## Scripts

### `test_single_claim.py`
Test a single claim through the pipeline.

```bash
pdm run python evaluation/test_single_claim.py <claim_number>
```

**Example:** `pdm run python evaluation/test_single_claim.py 1`

**Output:** `results/test_single_result.json` - Result for the tested claim

### `evaluate_pipeline.py`
Runs all claims through the pipeline and saves results.

```bash
pdm run evaluation
```

**Output:** `results/evaluation_results.json` - Detailed results for each claim

### `generate_report.py`
Generates performance report from evaluation results.

```bash
pdm run evaluation-report
```

**Output:** `results/evaluation_report.json` - Performance metrics and summary

### `summarize_results.py`
Creates a simplified version of results with only key fields.

```bash
pdm run summarize-results
```

**Output:** `results/evaluation_results_summary.json` - Simplified results

## Evaluation Metrics

### Match Types
- **Exact**: Pipeline decision matches expected decision
- **Acceptable**: Pipeline decision matches acceptable_decision (if provided)
- **Mismatch**: Pipeline decision doesn't match
- **Error**: Pipeline failed to process the claim

### Accuracy
```
Accuracy = (Exact + Acceptable) / Total Claims
```

## Ground Truth Format

Each claim needs an `answer.json`:

```json
{
  "decision": "APPROVE|DENY|UNCERTAIN",
  "explanation": "Optional reason",
  "acceptable_decision": "Optional alternative decision"
}
```
