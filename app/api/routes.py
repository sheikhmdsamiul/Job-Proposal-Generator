from fastapi import APIRouter, HTTPException

from app.services.vector_store import VectorStoreService
from app.services.job_analyzer import JobAnalyzer
from app.services.proposal_generator import ProposalGenerator
from app.api.schemas import *
from app.models import ProfileSetupRequest

# In-memory storage
proposal_history: list[GeneratedProposal] = []

router = APIRouter()
vector_service = VectorStoreService()
job_analyzer = JobAnalyzer()
proposal_generator = ProposalGenerator()


@router.post("/api/profile/setup", response_model=ProfileSetupResponse)
async def setup_profile(request: ProfileSetupRequest):
    try:
        success = vector_service.setup_profile(request.profile)
        if success:
            return ProfileSetupResponse(
                success=True,
                message="Profile successfully stored in knowledge base",
            )
        raise HTTPException(status_code=500, detail="Failed to setup profile")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/api/proposal/generate", response_model=ProposalGenerationResponse)
async def generate_proposal(request: ProposalGenerationRequest):
    try:
        job_requirements = job_analyzer.analyze_job_posting(request.job_posting)
        search_query = f"{' '.join(job_requirements.required_skills)} {job_requirements.project_scope}"
        relevant_experience = vector_service.search_relevant_experience(search_query)
        proposal = proposal_generator.generate_proposal(
            job_requirements,
            relevant_experience,
            request.tone,
            request.custom_instructions,
        )
        proposal_history.append(proposal)
        if len(proposal_history) > 5:
            proposal_history.pop(0)
        return ProposalGenerationResponse(
            proposal=proposal.content,
            confidence_score=proposal.confidence_score,
            matched_skills=proposal.matched_skills,
            timestamp=proposal.timestamp.isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating proposal: {str(e)}")


@router.get("/api/proposal/history", response_model=ProposalHistoryResponse)
async def get_proposal_history():
    return ProposalHistoryResponse(proposals=proposal_history[-5:])
