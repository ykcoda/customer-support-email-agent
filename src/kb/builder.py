"""Knowledge base builder - creates and updates FAISS index."""

import json
import os
from pathlib import Path
from typing import List, Dict, Any
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from src.core import settings


KB_INDEX_PATH = "./data/knowledge_base/faiss_index"
KB_DOCS_PATH = "./data/knowledge_base"


async def load_kb_documents() -> List[Document]:
    """
    Load all documents from KB JSON files and convert to LangChain Documents.

    Returns:
        List[Document]: Documents ready for embedding
    """
    documents = []
    kb_dir = Path(KB_DOCS_PATH)

    if not kb_dir.exists():
        print(f"[KB BUILDER] KB directory not found: {kb_dir}")
        return documents

    # Load all JSON files except faq.json and policies.json (already in system)
    for json_file in kb_dir.glob("*.json"):
        if json_file.name.startswith("faiss"):
            continue  # Skip FAISS index files

        try:
            with open(json_file, "r") as f:
                data = json.load(f)
                entries = data.get("entries", []) if isinstance(data, dict) else data

                for entry in entries:
                    # Build content string from all text fields
                    content_parts = []

                    # Add title/question
                    if "title" in entry:
                        content_parts.append(f"Title: {entry['title']}")
                    if "question" in entry:
                        content_parts.append(f"Question: {entry['question']}")

                    # Add main content
                    if "content" in entry:
                        content_parts.append(f"Content: {entry['content']}")
                    if "answer" in entry:
                        content_parts.append(f"Answer: {entry['answer']}")
                    if "solution" in entry:
                        content_parts.append(f"Solution: {entry['solution']}")
                    if "problem" in entry:
                        content_parts.append(f"Problem: {entry['problem']}")

                    # Add tags
                    if "tags" in entry:
                        content_parts.append(f"Tags: {', '.join(entry['tags'])}")

                    full_content = "\n".join(content_parts)

                    # Create metadata
                    metadata = {
                        "id": entry.get("id", f"doc_{len(documents)}"),
                        "source": json_file.name,
                        "category": entry.get("category", "general"),
                    }

                    # Create Document
                    doc = Document(page_content=full_content, metadata=metadata)
                    documents.append(doc)

        except Exception as e:
            print(f"[KB BUILDER ERROR] Failed to load {json_file}: {str(e)}")

    print(f"[KB BUILDER] Loaded {len(documents)} documents from KB files")
    return documents


async def build_faiss_index(force_rebuild: bool = False) -> FAISS:
    """
    Build or load FAISS index from KB documents.

    Args:
        force_rebuild: If True, rebuild index from scratch

    Returns:
        FAISS: The vector store
    """
    index_path = Path(KB_INDEX_PATH)

    # Load existing index if available and not forcing rebuild
    if index_path.exists() and not force_rebuild:
        try:
            print(f"[KB BUILDER] Loading existing FAISS index from {index_path}")
            embeddings = OpenAIEmbeddings(api_key=settings.openai_api_key)
            vector_store = FAISS.load_local(
                index_path,
                embeddings,
                allow_dangerous_deserialization=True,
            )
            print(f"[KB BUILDER] Loaded existing FAISS index")
            return vector_store
        except Exception as e:
            print(f"[KB BUILDER] Failed to load existing index: {str(e)}")

    # Build new index
    print("[KB BUILDER] Building new FAISS index...")

    documents = await load_kb_documents()

    if not documents:
        raise ValueError("No documents to index")

    # Create embeddings using OpenAI
    embeddings = OpenAIEmbeddings(api_key=settings.openai_api_key)

    # Create FAISS index
    print(f"[KB BUILDER] Embedding {len(documents)} documents...")
    vector_store = FAISS.from_documents(documents, embeddings)

    # Save index to disk
    print(f"[KB BUILDER] Saving FAISS index to {index_path}")
    vector_store.save_local(index_path)

    print("[KB BUILDER] FAISS index created successfully")
    return vector_store


async def rebuild_faiss_index() -> FAISS:
    """
    Force rebuild FAISS index from scratch.

    Returns:
        FAISS: The rebuilt vector store
    """
    print("[KB BUILDER] Force rebuilding FAISS index...")
    return await build_faiss_index(force_rebuild=True)
