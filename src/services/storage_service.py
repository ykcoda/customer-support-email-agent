"""Storage service with FAISS semantic search."""

from typing import List, Optional
from src.core import settings


class StorageService:
    """Service for knowledge base storage using FAISS semantic search."""

    def __init__(self):
        """Initialize storage service."""
        self.kb_path = settings.knowledge_base_path
        self._faiss_index = None
        self._initialized = False

    async def _ensure_kb_loaded(self) -> None:
        """Lazy load FAISS index (production or demo mode)."""
        if self._initialized:
            return

        try:
            # Check if OpenAI API key is available
            if settings.openai_api_key:
                from src.kb.builder import build_faiss_index
                print("[STORAGE] Loading FAISS index (production mode - OpenAI embeddings)...")
                self._faiss_index = await build_faiss_index()
            else:
                # Fall back to demo mode
                from src.kb.demo import build_faiss_index_demo
                print("[STORAGE] Loading FAISS index (demo mode - mock embeddings)...")
                self._faiss_index = await build_faiss_index_demo()

            self._initialized = True
            print("[STORAGE] FAISS index loaded successfully")

        except Exception as e:
            error_msg = f"Failed to load FAISS index: {str(e)}"
            print(f"[STORAGE ERROR] {error_msg}")
            self._initialized = True  # Mark as initialized to avoid retry loops

    async def search_knowledge_base(self, query: str, k: int = 5) -> List[dict]:
        """
        Search knowledge base using semantic similarity (FAISS).

        Args:
            query: Search query string
            k: Number of results to return (default 5)

        Returns:
            List[dict]: Top k most relevant KB entries with similarity scores
        """
        await self._ensure_kb_loaded()

        if not self._faiss_index:
            print("[STORAGE] FAISS index not available, returning empty results")
            return []

        try:
            # Perform similarity search using FAISS
            # similarity_search_with_score returns (Document, score) tuples
            results_with_scores = self._faiss_index.similarity_search_with_score(
                query, k=k
            )

            # Convert results to dictionary format
            results = []
            for doc, score in results_with_scores:
                result = {
                    "id": doc.metadata.get("id", "unknown"),
                    "content": doc.page_content,
                    "category": doc.metadata.get("category", "general"),
                    "source": doc.metadata.get("source", "unknown"),
                    "_similarity_score": float(score),  # Lower is better for FAISS L2
                }
                results.append(result)

            print(f"[STORAGE] Found {len(results)} results for query: '{query}'")
            return results

        except Exception as e:
            error_msg = f"FAISS search error: {str(e)}"
            print(f"[STORAGE ERROR] {error_msg}")
            return []

    async def rebuild_index(self) -> bool:
        """
        Rebuild FAISS index from scratch.

        Returns:
            bool: Success status
        """
        try:
            from src.kb.builder import rebuild_faiss_index

            print("[STORAGE] Rebuilding FAISS index...")
            self._faiss_index = await rebuild_faiss_index()
            self._initialized = True
            print("[STORAGE] FAISS index rebuilt successfully")
            return True

        except Exception as e:
            error_msg = f"Failed to rebuild FAISS index: {str(e)}"
            print(f"[STORAGE ERROR] {error_msg}")
            return False


storage_service = StorageService()
