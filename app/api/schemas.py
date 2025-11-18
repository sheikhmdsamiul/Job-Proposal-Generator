from pydantic import BaseModel
from typing import List, Optional
from app.models import Tone, GeneratedProposal


class ProfileSetupResponse(BaseModel):
    success: bool
    message: str


class ProposalGenerationRequest(BaseModel):
    job_posting: str
    tone: Tone = Tone.PROFESSIONAL
    custom_instructions: Optional[str] = None


class ProposalGenerationResponse(BaseModel):
    proposal: str
    confidence_score: float
    matched_skills: List[str]
    timestamp: str


class ProposalHistoryResponse(BaseModel):
    proposals: List[GeneratedProposal]
