from curses import meta
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from datetime import datetime
import uuid
import json
from pathlib import Path

from claim_processing_pipeline.api.models import ClaimResponse
from claim_processing_pipeline.constants import CLAIMS_STORAGE_DIR
from claim_processing_pipeline.pipeline import run_claim_processing_pipeline

router = APIRouter(prefix="/claims", tags=["claims"])


# Supported file extensions
SUPPORTED_EXTENSIONS = {'.md', '.png', '.jpg', '.jpeg', '.webp', '.txt'}

CLAIMS_STORAGE_DIR.mkdir(exist_ok=True)


def _save_claim(claim_id: str, claim_data: dict):
    """Save a claim to disk."""
    claim_dir = CLAIMS_STORAGE_DIR / claim_id
    claim_dir.mkdir(exist_ok=True)

    claim_file = claim_dir / "claim.json"
    with open(claim_file, 'w') as f:
        json.dump(claim_data, f, indent=2)


def _load_claim(claim_id: str) -> dict | None:
    """Load a claim from disk."""
    claim_file = CLAIMS_STORAGE_DIR / claim_id / "claim.json"
    if not claim_file.exists():
        return None
    
    with open(claim_file, 'r') as f:
        return json.load(f)


def _list_all_claims() -> list[dict]:
    """List all claims from disk."""
    claims = []
    for claim_dir in CLAIMS_STORAGE_DIR.iterdir():
        if claim_dir.is_dir():
            claim_file = claim_dir / "claim.json"
            if claim_file.exists():
                try:
                    with open(claim_file, 'r') as f:
                        claims.append(json.load(f))
                except Exception as e:
                    print(f"Error loading claim from {claim_file}: {e}")
    return claims


@router.post("/", response_model=dict)
async def submit_claim(
    description: str = Form(..., description="Text description of the incident"),
    metadata: str | None = Form(None, description="General metadata as text (optional)"),
    files: list[UploadFile] = File(default=[], description="Supporting documents (.md, .png, .jpg, .jpeg, .webp)"),
):
    """
    Submit a new claim with supporting documents and metadata.
    """
    claim_id = str(uuid.uuid4())
    
    # Validate file types
    for file in files:
        if file.filename:
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in SUPPORTED_EXTENSIONS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type: {file.filename}. Supported types: .md, .png, .jpg, .jpeg, .webp, .txt"
                )
    
    # Create claim directory
    claim_dir = CLAIMS_STORAGE_DIR / claim_id
    claim_dir.mkdir(parents=True, exist_ok=True)
    print(f"Created claim directory: {claim_dir.absolute()}")
    
    # Save uploaded files to claim directory
    document_paths = []
    for file in files:
        if file.filename:
            file_path = claim_dir / file.filename
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
            document_paths.append(str(file_path))
            print(f"Saved file: {file_path}")

    # Run pipeline
    pipeline_result = await run_claim_processing_pipeline(claim_id, description, document_paths, metadata)

    # Create claim record with pipeline results
    claim = ClaimResponse(
        claim_id=claim_id,
        status="processed",
        created_at= datetime.now().isoformat(),
        description=description,
        metadata=metadata,
        documents=document_paths,
        decision=pipeline_result.decision,
        explanation=pipeline_result.explanation,
    )
    
    # Save claim result to disk
    _save_claim(claim_id, claim.model_dump())
    
    return {
        "claim_id": claim_id,
        "status": "processed",
        "message": "Claim processed successfully",
        "decision": pipeline_result.decision,
        "explanation": pipeline_result.explanation,
    }


@router.get("/{claim_id}", response_model=ClaimResponse)
async def get_claim(claim_id: str):
    """
    Retrieve a specific claim by ID.
    """
    claim_data = _load_claim(claim_id)
    if not claim_data:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    return ClaimResponse(**claim_data)


@router.get("/", response_model=list[ClaimResponse])
async def list_claims():
    """
    List all processed claims.
    """
    claims = _list_all_claims()
    return [ClaimResponse(**claim) for claim in claims]
