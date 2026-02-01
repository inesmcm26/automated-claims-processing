from pathlib import Path
from claim_processing_pipeline.schemas import (
    MedicalReport,
    PoliceReport,
    PersonalEmergencyReport,
    JurySummons,
    JustificationForDelay,
    ProofOfBooking,
)

CLAIMS_STORAGE_DIR = Path("in-memory-storage")

# ---------------------------------
# Policy
# ---------------------------------
TRIP_CANCELLATON_OR_RESCHEDULING_SECTION = """
If your trip is cancelled or rescheduled for a covered reason, you may be eligible for compensation.
Examples of covered reasons:
- Jury duty
- Medical emergency (must be supported by a medical report)
- Theft or criminal incident (must be supported by a police report)
- Other specified personal emergencies

What's required:
- Valid supporting documentation (e.g., medical certificate, police report, jury summon letter)
- Proof of booking and amount paid
"""

PERSONAL_EFFECTS_SECTION = """
If your trip is cancelled or rescheduled for a covered reason, you may be eligible for compensation.
Examples of covered reasons:
- Jury duty
- Medical emergency (must be supported by a medical report)
- Theft or criminal incident (must be supported by a police report)
- Other specified personal emergencies

What's required:
- Valid supporting documentation (e.g., medical certificate, police report, jury summon letter)
- Proof of booking and amount paid
"""

MISSED_DEPARTURE_OR_CONNECTION_SECTION = """
If you miss a scheduled departure or connection due to a covered reason, you may be compensated.

Examples of covered reasons: 
- Traffic accident en route

What's required:
- Incident report or documentation explaining the cause of delay
- Proof of booking
"""

EXCLUSIONS_SECTION = """
Your claim may be **rejected** in the following cases:

- Not a covered reason (e.g., voluntary changes to your travel)
- Prior knowledge of the incident or reason before purchase
- Outside policy period - e.g., incident occurred before coverage began or after it ended
- Late reporting - claim submitted more than 30 days after policy expired (usually the day after you return from your trip)
- Incomplete documentation - failure to provide necessary proof 
"""

# ---------------------------------
# Mappings
# ---------------------------------
SCENARIO_POLICY_SECTION_MAPPING = {
    "A": TRIP_CANCELLATON_OR_RESCHEDULING_SECTION,
    "B": PERSONAL_EFFECTS_SECTION,
    "C": MISSED_DEPARTURE_OR_CONNECTION_SECTION,
}


DOC_TYPE_SCHEMA_MAPPING = {
    1: MedicalReport,
    2: PoliceReport,
    3: JurySummons,
    4: JustificationForDelay,
    5: PersonalEmergencyReport,
    6: ProofOfBooking,
}