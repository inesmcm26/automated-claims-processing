from pydantic import BaseModel
from typing import Literal

class ClaimResponse(BaseModel):
    claim_id: str
    status: str
    created_at: str
    description: str
    metadata: str | None = None
    documents: list[str] = []
    decision: Literal["APPROVE", "DENY", "UNCERTAIN"] | None = None
    explanation: str | None
