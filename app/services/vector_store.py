import os
from typing import List, Dict, Any

from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


from app.models import FreelancerProfile


class VectorStoreService:
    def __init__(self):
        # Ollama local embeddings 
        model_name = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
        self.embeddings = OllamaEmbeddings(model=model_name)

        # the directory will store FAISS files.
        self.collection_name = os.getenv("CHROMA_COLLECTION", "freelancer_profiles")
        self.persist_directory = os.getenv("CHROMA_DIR", "./chroma_db")
        os.makedirs(self.persist_directory, exist_ok=True)
        self.vector_store = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )

    def setup_profile(self, profile: FreelancerProfile) -> bool:
        try:
            # Create document from profile
            profile_text = self._profile_to_text(profile)
            documents = self.text_splitter.split_text(profile_text)

            # Convert to Document objects
            docs = [Document(page_content=doc, metadata={"name": profile.name}) for doc in documents]
            # Create or load FAISS vector store. If an index exists, load and append documents;
            # otherwise create a new FAISS index from the documents.
            try:
                # Try loading existing FAISS index from disk
                self.vector_store = FAISS.load_local(self.persist_directory, self.embeddings)
                self.vector_store.add_documents(docs)
            except Exception:
                # No existing index — create from documents
                self.vector_store = FAISS.from_documents(docs, self.embeddings)

            # Persist FAISS index to disk
            self.vector_store.save_local(self.persist_directory)
            return True
        except Exception as e:
            print(f"Error setting up profile: {e}")
            return False

    def _profile_to_text(self, profile: FreelancerProfile) -> str:
        skills_text = ", ".join(profile.skills)
        projects_text = "\n".join([f"- {project}" for project in profile.past_projects])
        return f"""
        Freelancer Profile: {profile.name}

        Skills: {skills_text}

        Experience: {profile.experience}

        Past Projects:
        {projects_text}

        Rates: {profile.rates or 'Not specified'}

        Specialization: {profile.specialization or 'General'}
        """

    def search_relevant_experience(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        if not self.vector_store:
            # Try to load existing store if available
            try:
                self.vector_store = FAISS.load_local(self.persist_directory, self.embeddings)
            except Exception:
                return []
        try:
            results = self.vector_store.similarity_search_with_relevance_scores(query, k=k)
            return [
                {
                    "content": doc.page_content,
                    "score": float(score),
                    "metadata": doc.metadata,
                }
                for doc, score in results
            ]
        except Exception as e:
            print(f"Error searching vector store: {e}")
            return []
