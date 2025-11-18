import requests

BASE_URL = "http://localhost:8000"

profile_data = {
    "profile": {
        "name": "Alex Johnson",
        "skills": [
            "Python",
            "FastAPI",
            "React",
            "Machine Learning",
            "LangChain",
            "RAG",
            "Ollama",
        ],
        "experience": "5 years of full-stack development with focus on AI applications. Built multiple chatbots and RAG systems for clients.",
        "past_projects": [
            "AI-powered document analysis system for legal firm",
            "Real-time chatbot for customer support",
            "ML pipeline for predictive analytics",
            "LangChain-based content generation tool",
        ],
        "rates": "$75-100/hour",
        "specialization": "AI/ML Applications",
    }
}

job_posting = """
Looking for an experienced developer to build a smart document processing system. 
The system should use AI to extract key information from PDFs and generate summaries.

Requirements:
- Strong Python and FastAPI experience
- Experience with LangChain and RAG systems
- Knowledge of OpenAI API and embeddings (or local alternatives)
- Ability to work with PDF processing libraries
- Experience building scalable backend systems

Budget: $5000-8000
Timeline: 4-6 weeks

Key priorities: Accuracy of information extraction, clean API design, good documentation.
"""


def test_api():
    print("Setting up profile...")
    resp = requests.post(f"{BASE_URL}/api/profile/setup", json=profile_data)
    print(resp.status_code, resp.json())

    print("Generating proposal...")
    proposal_request = {
        "job_posting": job_posting,
        "tone": "professional",
        "custom_instructions": "Emphasize experience with document processing systems",
    }
    resp = requests.post(f"{BASE_URL}/api/proposal/generate", json=proposal_request)
    print("Status:", resp.status_code)
    try:
        result = resp.json()
    except Exception:
        print("Response text:", resp.text)
        return
    if resp.status_code != 200:
        print("Error response:", result)
        return
    print(f"Confidence Score: {result['confidence_score']:.2f}")
    print(f"Matched Skills: {', '.join(result['matched_skills'])}")
    print(f"\nGenerated Proposal:\n{result['proposal']}")

    print("\nGetting proposal history...")
    resp = requests.get(f"{BASE_URL}/api/proposal/history")
    history = resp.json()
    print(f"Stored proposals: {len(history['proposals'])}")


if __name__ == "__main__":
    test_api()
