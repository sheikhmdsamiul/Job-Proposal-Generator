from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum


class Tone(str, Enum):
    FORMAL = "formal"
    CASUAL = "casual"
    PROFESSIONAL = "professional"


class FreelancerProfile(BaseModel):
    name: str
    skills: List[str]
    experience: str
    past_projects: List[str]
    rates: Optional[str] = None
    specialization: Optional[str] = None


class JobRequirements(BaseModel):
    required_skills: List[str]
    project_scope: str
    budget: Optional[str] = None
    timeline: Optional[str] = None
    key_priorities: List[str]


class ProposalRequest(BaseModel):
    job_posting: str
    tone: Tone = Tone.PROFESSIONAL
    custom_instructions: Optional[str] = None


class GeneratedProposal(BaseModel):
    content: str
    confidence_score: float
    matched_skills: List[str]
    timestamp: datetime


class ProfileSetupRequest(BaseModel):
    profile: FreelancerProfile
