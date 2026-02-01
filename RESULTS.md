# Results Analysis

## Overview

The claim processing pipeline was evaluated against a benchmark dataset of 25 insurance claims with varying complexity levels, including medical emergencies, travel cancellations, and fraud indicators.

Results can be found in the `results/` folder, including detailed per-claim results (`evaluation_results.json`), a summary of those per-claim results (`evaluation_results_summary.json`), and an evaluation report (`evaluation_report.json`).

### Performance Metrics

- **Total Claims Processed**: 25
- **Overall Accuracy**: 68% (17 correct decisions out of 25)
- **Average Processing Time**: ~2 minutes per claim (using models running locally)

### Decision Breakdown

- 10 Approved
- 14 Denied
- 1 Uncertain

**Expected APPROVE Decisions:**
- Correct: 5
- Incorrect: 2
- Precision: 71%

**Expected DENY Decisions:**
- Correct: 11
- Incorrect: 2
- Precision: 82%

**Expected UNCERTAIN Decisions:**
- Correct: 1
- Incorrect: 4
- Precision: 25%

### Main Conclusions

The pipeline correctly processed 68% of claims, performing well on the majority of the scenarios but struggling mostly with ambiguity and subtle fraud indicators. Most errors are due to a limited fraud detection step, basic OCR, and occasional LLM misinterpretations. Improving and extending fraud checks, improving document processing with better OCR, and refining policy reasoning (especially for borderline cases) would increase accuracy and allow uncertain claims to be reliably escalated to human reviewers.

## Analysis of wrong decisions

#### **Claim 11**: Severe Migraine Due to Allergic Reaction

**Expected**: APPROVE | **Pipeline**: DENY

- **What went wrong**: The "Find applicable policy section" failed, wrongly choosing _Missed Departure or Missed Connection_ as relevant policy section. Medical emergy is not covered, only ""Traffic accident en route" is a covered reason on the policy.

- **How to fix**: Use a more reliable approach to detect relevant policy sections like a semantic retrieval-based approach

#### **Claim 13**: Hospitalization with Suspicious Dating

**Expected**: UNCERTAIN/DENY | **Pipeline**: APPROVE

- **What went wrong**: Fraud detection step doesn't have a mechanism to identify the date inconsistency between the claimed hospitalization date (16/12/2023) and the document stamp (17/11/2023). This is a clear red flag that should have triggered UNCERTAIN or DENY.

- **How to fix**: I experimented having a step to detect inconsistencies in documents with a LLM call, like mismatched dates, but it failed often. A stronger model or better heuristics would likely make this check reliable.

#### **Claim 21**: Missing Medical Documentation
    
**Expected**: DENY | **Pipeline**: APPROVE

- **What went wrong**: The policy reasoner failed to detect a missing document. Only claim where this happened (in claim 1, 21, etc the missing document was detected)

- **How to fix**: Using a better LLM would probably solve the problem

#### **Claim 23**: Suspicious Document with Missing Discharge Date
    
**Expected**: UNCERTAIN | **Pipeline**: APPROVE

- **What went wrong**: The fraud detection step doesn't have a mechanism to find anomalies or inconsistencies in dates.

- **How to fix**: Improve fraud detection step to make it more robust.

#### **Claim 24**: Medical Certificate Issued After Travel Date

**Expected**: UNCERTAIN | **Pipeline**: DENY

- **What went wrong**: The pipeline treated the date mismatch (medical appointment 3 days after travel) as a definitive reason to deny the claim, instead of recognizing it as an ambiguity.

- **How to fix**: Clarify the guidelines for UNCERTAIN decisions in cases with minor date discrepancies. But the logic to choose DENY also makes sense to me.

#### **Claim 5**: Missing Patient Name in Medical Report
    
**Expected**: APPROVE | **Pipeline**: DENY

- **What went wrong**: The OCR is now powerful enough to parse the handwritten text. Seems that the claimant's name is not on the certificate.

- **How to fix**: Improve OCR

#### **Claim 6**: Future-Dated Claim (Hospitalization Ongoing)
    
**Expected**: UNCERTAIN | **Pipeline**: APPROVE

- **What went wrong**: The pipeline approved a claim for a future event that hasn't fully materialized. The hospitalization is real, but the inability to travel on August 15 is speculative at the time of claim submission (July 22).

- **How to fix**: Prompt engineering and/or a better LLM

#### **Claim 7**: Suspicious Document with Missing Discharge Date
    
**Expected**: DENY | **Pipeline**: APPROVE

- **What went wrong**: The fraud detection failed to identify visual anomalies in the document (photoshopped elements) or flag the missing discharge date as a critical omission.

- **How to fix**: Improve fraud detection with image forensics capabilities to detect manipulated documents.

### Notes on "UNCERTAIN" decisions

Escalating uncertain cases to a human reviewer is crucial in scenarios like this. In my solution, only one out of the 25 claims was marked as "UNCERTAIN." Many claims that ideally should have been flagged as uncertain were instead approved or denied, primarily due to my basic fraud detection step.

Currently, fraud detection only checks for missing signatures on documents that require a verifiable official issuer. However, much more could be done. For example, we could analyze inconsistencies in dates and names, or assess the overall veracity of documents. Implementing these checks would require more advanced techniques, but would succesfully flag situations that would require escalation to a human.