import os
from typing import List, Dict, Any
from datetime import datetime

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

from app.models import JobRequirements, GeneratedProposal, Tone


class ProposalGenerator:
    def __init__(self):
        model_name = os.getenv("OLLAMA_LLM_MODEL", "llama2:7b")
        self.llm = ChatOllama(model=model_name, temperature=0.7)
        self.tone_templates = {
            "formal": (
                "You are writing a formal business proposal. Use professional language, "
                "complete sentences, and maintain a respectful, corporate tone. "
                "Avoid contractions and casual expressions."
            ),
            "casual": (
                "You are writing a friendly, casual proposal. Use conversational language, "
                "contractions, and a more personal tone. Be enthusiastic but professional."
            ),
            "professional": (
                "You are writing a professional yet approachable proposal. Balance expertise "
                "with friendliness. Use clear, direct language that shows confidence."
            ),
        }

    def generate_proposal(
        self,
        job_reqs: JobRequirements,
        relevant_experience: List[Dict[str, Any]],
        tone: Tone = Tone.PROFESSIONAL,
        custom_instructions: str | None = None,
    ) -> GeneratedProposal:
        confidence_score = self._calculate_confidence_score(relevant_experience)
        experience_context = self._prepare_experience_context(relevant_experience)
        prompt = self._build_proposal_prompt(
            job_reqs, experience_context, tone, custom_instructions
        )
        # Use the ChatOllama public invocation method
        response = self.llm.invoke([HumanMessage(content=prompt)])
        proposal_content = response.content
        matched_skills = self._extract_matched_skills(
            job_reqs.required_skills, experience_context
        )
        return GeneratedProposal(
            content=proposal_content,
            confidence_score=confidence_score,
            matched_skills=matched_skills,
            timestamp=datetime.now(),
        )

    def _calculate_confidence_score(self, relevant_experience: List[Dict[str, Any]]) -> float:
        if not relevant_experience:
            return 0.0
        total_score = sum(float(exp["score"]) for exp in relevant_experience)
        avg = total_score / len(relevant_experience)
        return max(0.0, min(avg * 2, 1.0))

    def _prepare_experience_context(self, relevant_experience: List[Dict[str, Any]]) -> str:
        parts: List[str] = []
        for i, exp in enumerate(relevant_experience, 1):
            parts.append(f"Relevant Experience {i} (Relevance: {float(exp['score']):.2f}):")
            parts.append(exp["content"])
            parts.append("")
        return "\n".join(parts)

    def _build_proposal_prompt(
        self,
        job_reqs: JobRequirements,
        experience_context: str,
        tone: Tone,
        custom_instructions: str | None,
    ) -> str:
        tone_instruction = self.tone_templates.get(tone.value, self.tone_templates["professional"]) if isinstance(tone, Tone) else self.tone_templates.get(str(tone), self.tone_templates["professional"]) 
        prompt = f"""
{tone_instruction}

You are an expert freelance developer writing a job proposal. Use the following information to create a compelling, personalized proposal.

JOB REQUIREMENTS:
- Required Skills: {', '.join(job_reqs.required_skills)}
- Project Scope: {job_reqs.project_scope}
- Budget: {job_reqs.budget or 'Not specified'}
- Timeline: {job_reqs.timeline or 'Not specified'}
- Key Priorities: {', '.join(job_reqs.key_priorities)}

YOUR RELEVANT EXPERIENCE:
{experience_context}

PROPOSAL STRUCTURE:
1. Professional greeting that shows you understand their needs
2. Highlight 2-3 most relevant skills and experiences that match their requirements
3. Propose your approach/solution to their project
4. Mention timeline availability and next steps
5. Professional closing

{f"CUSTOM INSTRUCTIONS: {custom_instructions}" if custom_instructions else ""}

Generate a compelling proposal that shows why you're the perfect fit for this project:
"""
        return prompt

    def _extract_matched_skills(self, required_skills: List[str], experience_context: str) -> List[str]:
        matched: List[str] = []
        exp_lower = experience_context.lower()
        for skill in required_skills:
            if skill.lower() in exp_lower:
                matched.append(skill)
        return matched
