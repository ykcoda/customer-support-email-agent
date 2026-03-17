"""Knowledge base module for semantic search using FAISS."""

from .builder import build_faiss_index, rebuild_faiss_index, load_kb_documents

__all__ = ["build_faiss_index", "rebuild_faiss_index", "load_kb_documents"]
