IDENTIFY_POLICY_SECTION_PROMPT = """
Given a claim description, identify which cost the client is asking reimbursment for:

- A: Pre-booked Trip Expenses (Cancellations/Rescheduling): Costs of transportation (flights, train tickets) or accommodation lost because the traveler could no longer attend the trip as planned (e.g., due to illness, emergency, or change of plans).
- B: Personal Property: Costs for physical belongings (luggage, electronics, clothing, or jewelry) that are lost, stolen, or damaged during the trip.
- C: Missed Departure/Connection Fare: Costs of the transportation ticket itself (the fare) when the client failed to arrive on time for a departure or a connection.

When asking for reimbursment of other costs, chose "D".

Claim: {claim}

You must return the relevant identifier ("A", "B", "C" or "D) and justify.
"""

DOC_TYPE_PROMPT = """
You are an assistant that the document type for a given document.

Options:
1. Medical document
2. Police report
3. Jury summon letter
4. Documentation explaining the cause of a delay
5. Other similar official documents
6. Proof of booking (reservations, tickets, appointments, etc.)
7. None of the above

Analyze the following document:

{document}

Answer with the chosen option number. Do not provide explanations.
"""

SIGNATURE_DETECTION_PROMPT = """
Is there a handwritten signature or an official stamp/seal in this image? Answer only "SIGNATURE" or "SEAL" or "NONE". Do not guess.
"""

ANALYSE_DOCUMENTS_PROMPT = """
You are given a document and a schema in JSON format. The schema defines fields that may be present in the document.

Your task:
1. Extract all information from the document that corresponds to the fields in that schema.
2. Do not infer or guess any information. Use only what is explicitly in the document and fill as much values as you can.

Document:
{document}

Schema:
{schema}

You MUST always return the chosen schema, even if you extract none or only a few fields
"""

SUSPICIOUS_DOC_ANALYSIS_PROMPT = """
You are an insurance claim document analyst. Your task is to review a supporting document and report only clear, objective issues that could make it difficult to verify or use the document for an insurance claim.

IMPORTANT RULES:
- Do NOT treat invalid, incomplete, malformed, or ambiguously formatted dates as inconsistencies.
- If a date cannot be reliably interpreted, ignore it entirely.
- Do NOT flag OCR errors, typos, layout issues, or formatting problems.

TASK:
1. Identify all clearly stated, valid calendar dates in the document (ignore malformed or unreadable dates).
2. Determine whether the document issue date occurs before, during, or after the events it describes.
3. If the document issue date is earlier than the events it certifies, this MUST be reported as a factual inconsistency.

Only report:
- Chronological contradictions between clearly stated, valid dates
- Clear inconsistencies in claimant identity (e.g., different names for the same person).

If no such contradiction exists, say you have nothing to report

Document:
{document}

Produce a short report with you analysis (1 sentence max)
"""

POLICY_EXPERT_PROMPT = """
You are an insurance claim policy expert. You will be given three inputs:

1. Policy - the official insurance policy describing what is required for this type of covered claim, including any exclusions.
2. Claim - description of what happened provided by the claimant.
3. Supporting documents - The documents uploaded by the claimant to support the claim.

Your task is to analyze the claim against the policy and the supporting documents, and then make a decision: APPROVE, DENY, or UNCERTAIN.
References to the current date indicate the date on which the claim was submitted for analysis. Only use this information to check for late reporting

Fact-check the claim against all supporting documents:
- Verify names, dates, and reason/incident (or equivalent key details) mentioned in the claim. Pay special attention to the patient name in medical documents.
- A claim is fully verifiable only if all elements are confirmed by the documents.
- A medical report stating the person is healthy/apt does not consistute a covered reason and the claim MUST be automatically denied

Decision guidelines:
- DENY: If any required document is missing, the claim cannot be fully verified or is not covered under the policy. Do not deny solely for document validity concerns flagged as suspicious (e.g., missing signature); treat these as UNCERTAIN instead.
- APPROVE: If all required elements are present, the claim is fully verifiable, and there are no inconsistencies, ambiguities, or exclusions.
- UNCERTAIN: If all required elements are present but the fraud detection states a signature is missing signature OR it is questionable if the claim is covered under the policy (both by reason and timing)

Policy:
{policy}

Claim:
{claim}

Supporting documents analysis:
{document_analysis_report}
{metadata}
Justify your choice referencing the claim and the documents.
"""