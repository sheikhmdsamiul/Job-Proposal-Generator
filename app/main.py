from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Swiftme Mini - Job Proposal Generator",
    description="AI-powered job proposal generator using RAG and LangChain (Ollama)",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
async def root():
    return {
        "message": "Swiftme Mini API - Job Proposal Generator",
        "status": "running",
        "endpoints": {
            "setup_profile": "POST /api/profile/setup",
            "generate_proposal": "POST /api/proposal/generate",
            "proposal_history": "GET /api/proposal/history",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
