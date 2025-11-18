import os
from typing import List

from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import PydanticOutputParser


from app.models import JobRequirements


class JobAnalyzer:
    def __init__(self):
        model_name = os.getenv("OLLAMA_LLM_MODEL", "llama3:8b-instruct")
        self.llm = ChatOllama(model=model_name, temperature=0)
        self.parser = PydanticOutputParser(pydantic_object=JobRequirements)

    def analyze_job_posting(self, job_posting: str) -> JobRequirements:
        system_prompt = (
            "You are an expert job analyzer. Extract the following information from the job posting:\n"
            "- Required skills and technologies\n"
            "- Project scope and detailed requirements\n"
            "- Budget information if mentioned\n"
            "- Timeline/deadline if mentioned\n"
            "- Key priorities and success factors\n\n"
            "Format the output as JSON matching the specified schema."
        )
        user_prompt = f"""
Analyze this job posting and extract the key requirements:

{job_posting}

{self.parser.get_format_instructions()}
"""
        try:
            # Use the ChatOllama public invocation method
            response = self.llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
            return self.parser.parse(response.content)
        except Exception as e:
            print(f"Error analyzing job posting: {e}")
            return self._fallback_extraction(job_posting)

    def _fallback_extraction(self, job_posting: str) -> JobRequirements:
        return JobRequirements(
            required_skills=["Extracted from job posting"],
            project_scope=job_posting[:500],
            budget="Not specified",
            timeline="Not specified",
            key_priorities=["Complete project successfully"],
        )
