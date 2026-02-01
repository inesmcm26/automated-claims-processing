from pydantic import BaseModel
from typing import Union, Literal

# ---------------------------------
# Data extraction schemas
# ---------------------------------
class MedicalReport(BaseModel):
    patient_name: str | None = None
    hospital_or_clinic: str | None = None
    admission_date: str | None = None
    discharge_date: str | None = None
    report_issuing_date: str | None = None
    diagnosis: str | None = None
    treatment: str | None = None
    doctor_name: str | None = None

class PoliceReport(BaseModel):
    claimant_name: str | None = None
    police_institution: str | None = None
    report_date: str | None = None
    report_time: str | None = None
    incident_date: str | None = None
    incident_time: str | None = None
    report_number: str | None = None
    items_or_damage_reported: str | None = None
    officer_name_or_badge: str | None = None

class PersonalEmergencyReport(BaseModel):
    person_name: str | None = None
    emergency_type: str | None = None
    incident_date: str | None = None
    incident_time: str | None = None
    location: str | None = None
    supporting_details: str | None = None

class JurySummons(BaseModel):
    recipient_name: str | None = None
    court_name: str | None = None
    summons_date: str | None = None
    appearance_date: str | None = None
    case_number: str | None = None

class JustificationForDelay(BaseModel):
    person_name: str | None = None
    reason_for_delay: str | None = None
    date_of_incident: str | None = None
    supporting_evidence: str | None = None

class ProofOfBooking(BaseModel):
    guest_name: str | None = None
    booking_reference: str | None = None
    booking_platform: str | None = None
    price: str | None = None
    location: str | None = None
    check_in_date: str | None = None
    check_out_date: str | None = None
    number_guests: str | None = None
    booked_on: str | None = None


DocumentType = Union[None, MedicalReport, PoliceReport, PersonalEmergencyReport, JurySummons, JustificationForDelay, ProofOfBooking]

# ---------------------------------
# Structured LLM output schemas
# ---------------------------------
class RelevantPolicySectionChoice(BaseModel):
    identifier: str
    short_explanation: str

class RelevantSectionChoice(BaseModel):
    identifier_list: list[str]
    short_justification: str
    

class DecisionResults(BaseModel):
    decision: Literal["APPROVE", "DENY", "UNCERTAIN"]
    short_explanation: str


# ---------------------------------
# Document processing
# ---------------------------------
class ProcessedDoc(BaseModel):
    id: str
    name: str
    text: str
    file_ext: str

class DocReport(ProcessedDoc):
    requires_official_issuer: bool | None = None
    trustworthy: bool | None = None
    fraud_detection: str | None = None
    extracted_fields: DocumentType | None = None

