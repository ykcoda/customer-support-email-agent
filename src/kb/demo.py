"""
Demo mode for FAISS knowledge base without OpenAI API.
Uses mock embeddings to demonstrate the semantic search workflow.
"""

import json
from pathlib import Path
from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_community.vectorstores import FAISS


class MockEmbeddings(Embeddings):
    """Mock embeddings using simple hash-based similarity."""

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Create mock embeddings from text."""
        embeddings = []
        for text in texts:
            # Create a simple embedding: use text length + hash as features
            embedding = [float(len(text) % 100) / 100.0]
            # Add character frequency as features
            for char_code in text.encode()[:10]:
                embedding.append(float(char_code) / 256.0)
            # Pad to 384 dimensions (like sentence-transformers)
            while len(embedding) < 384:
                embedding.append(0.0)
            embeddings.append(embedding[:384])
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        """Create mock embedding for query."""
        return self.embed_documents([text])[0]


KB_INDEX_PATH = "./data/knowledge_base/faiss_index_demo"
KB_DOCS_PATH = "./data/knowledge_base"


async def load_kb_documents_demo() -> List[Document]:
    """Load all KB documents for demo."""
    documents = []
    kb_dir = Path(KB_DOCS_PATH)

    if not kb_dir.exists():
        return documents

    for json_file in kb_dir.glob("*.json"):
        if json_file.name.startswith("faiss"):
            continue

        try:
            with open(json_file, "r") as f:
                data = json.load(f)
                entries = data.get("entries", []) if isinstance(data, dict) else data

                for entry in entries:
                    content_parts = []
                    if "title" in entry:
                        content_parts.append(f"Title: {entry['title']}")
                    if "question" in entry:
                        content_parts.append(f"Question: {entry['question']}")
                    if "content" in entry:
                        content_parts.append(f"Content: {entry['content']}")
                    if "answer" in entry:
                        content_parts.append(f"Answer: {entry['answer']}")
                    if "solution" in entry:
                        content_parts.append(f"Solution: {entry['solution']}")
                    if "problem" in entry:
                        content_parts.append(f"Problem: {entry['problem']}")
                    if "tags" in entry:
                        content_parts.append(f"Tags: {', '.join(entry['tags'])}")

                    full_content = "\n".join(content_parts)

                    metadata = {
                        "id": entry.get("id", f"doc_{len(documents)}"),
                        "source": json_file.name,
                        "category": entry.get("category", "general"),
                    }

                    doc = Document(page_content=full_content, metadata=metadata)
                    documents.append(doc)

        except Exception as e:
            print(f"[KB DEMO] Failed to load {json_file}: {str(e)}")

    print(f"[KB DEMO] Loaded {len(documents)} documents from KB files")
    return documents


async def build_faiss_index_demo(force_rebuild: bool = False) -> FAISS:
    """
    Build FAISS index using mock embeddings (demo mode).

    Args:
        force_rebuild: Force rebuild from scratch

    Returns:
        FAISS vector store
    """
    index_path = Path(KB_INDEX_PATH)

    if index_path.exists() and not force_rebuild:
        try:
            print(f"[KB DEMO] Loading existing FAISS index from {index_path}")
            embeddings = MockEmbeddings()
            vector_store = FAISS.load_local(
                index_path,
                embeddings,
                allow_dangerous_deserialization=True,
            )
            print(f"[KB DEMO] Loaded existing FAISS index (demo mode)")
            return vector_store
        except Exception as e:
            print(f"[KB DEMO] Failed to load existing index: {str(e)}")

    print("[KB DEMO] Building new FAISS index (demo mode with mock embeddings)...")

    documents = await load_kb_documents_demo()

    if not documents:
        raise ValueError("No documents to index")

    embeddings = MockEmbeddings()

    print(f"[KB DEMO] Creating FAISS index from {len(documents)} documents...")
    vector_store = FAISS.from_documents(documents, embeddings)

    print(f"[KB DEMO] Saving FAISS index to {index_path}")
    vector_store.save_local(index_path)

    print("[KB DEMO] FAISS index created successfully (demo mode)")
    return vector_store


async def rebuild_faiss_index_demo() -> FAISS:
    """Force rebuild FAISS index in demo mode."""
    print("[KB DEMO] Force rebuilding FAISS index (demo mode)...")
    return await build_faiss_index_demo(force_rebuild=True)
