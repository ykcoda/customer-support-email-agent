#!/usr/bin/env python
"""
Management script for knowledge base operations.

Usage:
    uv run python manage_kb.py build      - Build FAISS index (production)
    uv run python manage_kb.py build-demo - Build FAISS index (demo mode, no API key needed)
    uv run python manage_kb.py rebuild    - Force rebuild FAISS index
    uv run python manage_kb.py search     - Test search functionality
    uv run python manage_kb.py list       - List all KB documents
"""

import asyncio
import sys
from pathlib import Path
from src.core import settings


async def build_kb(demo: bool = False):
    """Build FAISS index from KB documents."""
    try:
        print("=" * 60)
        if demo:
            print("Building FAISS Index (DEMO MODE - Mock Embeddings)")
            from src.kb.demo import build_faiss_index_demo
            index = await build_faiss_index_demo()
        else:
            print("Building FAISS Index (Production - OpenAI Embeddings)")
            if not settings.openai_api_key:
                print("\n⚠️  OPENAI_API_KEY not set in .env file")
                print("\nTo use production mode:")
                print("  1. Get your API key: https://platform.openai.com/account/api-keys")
                print("  2. Add to .env: OPENAI_API_KEY=sk-your-key-here")
                print("\nOr use demo mode: uv run python manage_kb.py build-demo")
                return False

            from src.kb.builder import build_faiss_index
            index = await build_faiss_index()

        print("=" * 60)
        print("✓ FAISS index built successfully!")
        return True
    except Exception as e:
        print(f"✗ Error building index: {str(e)}")
        if not demo:
            print("\n💡 Tip: Try demo mode instead: uv run python manage_kb.py build-demo")
        return False


async def rebuild_kb(demo: bool = False):
    """Force rebuild FAISS index."""
    try:
        print("=" * 60)
        if demo:
            print("Force Rebuilding FAISS Index (DEMO MODE)")
            from src.kb.demo import rebuild_faiss_index_demo
            index = await rebuild_faiss_index_demo()
        else:
            print("Force Rebuilding FAISS Index (Production)")
            if not settings.openai_api_key:
                print("\n⚠️  OPENAI_API_KEY not set in .env file")
                return False

            from src.kb.builder import rebuild_faiss_index
            index = await rebuild_faiss_index()

        print("=" * 60)
        print("✓ FAISS index rebuilt successfully!")
        return True
    except Exception as e:
        print(f"✗ Error rebuilding index: {str(e)}")
        return False


async def test_search(demo: bool = False):
    """Test FAISS search with sample queries."""
    if demo:
        from src.kb.demo import build_faiss_index_demo
        # Build demo index if needed
        index = await build_faiss_index_demo()

    from src.services.storage_service import storage_service

    print("=" * 60)
    print("Testing FAISS Semantic Search")
    print(f"Mode: {'DEMO (Mock)' if demo else 'Production (OpenAI)'}")
    print("=" * 60)

    test_queries = [
        "I forgot my password",
        "How do I upgrade my plan?",
        "My payment failed",
        "I can't log in",
        "Two-factor authentication setup",
        "Export my data",
        "Integration with Slack",
        "Slow performance issues",
        "Account creation",
    ]

    print("\nTesting semantic search with sample queries:\n")

    for query in test_queries:
        print(f"Query: '{query}'")
        results = await storage_service.search_knowledge_base(query, k=2)

        if results:
            for i, result in enumerate(results, 1):
                print(f"  {i}. [{result['category']}] {result['id']}")
                print(f"     Score: {result['_similarity_score']:.4f}")
                preview = result["content"][:100].replace("\n", " ")
                print(f"     Preview: {preview}...")
        else:
            print("  No results found")
        print()

    print("✓ Search test completed!")


async def list_documents():
    """List all KB documents in the index."""
    from src.kb.builder import load_kb_documents

    print("=" * 60)
    print("Knowledge Base Documents")
    print("=" * 60)

    try:
        docs = await load_kb_documents()
        print(f"\nTotal documents: {len(docs)}\n")

        by_source = {}
        for doc in docs:
            source = doc.metadata.get("source", "unknown")
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(doc)

        for source, docs_in_source in sorted(by_source.items()):
            print(f"\n{source} ({len(docs_in_source)} documents)")
            print("-" * 40)
            for doc in docs_in_source:
                doc_id = doc.metadata.get("id", "unknown")
                category = doc.metadata.get("category", "general")
                preview = doc.page_content[:80].replace("\n", " ")
                print(f"  • {doc_id} [{category}]")
                print(f"    {preview}...")

        print(f"\n✓ Listing complete!")

    except Exception as e:
        print(f"✗ Error listing documents: {str(e)}")


async def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        return

    command = sys.argv[1].lower()
    demo = "--demo" in sys.argv or command in ("build-demo", "rebuild-demo", "search-demo")

    if command == "build":
        success = await build_kb(demo=False)
        sys.exit(0 if success else 1)

    elif command == "build-demo":
        success = await build_kb(demo=True)
        sys.exit(0 if success else 1)

    elif command == "rebuild":
        success = await rebuild_kb(demo=False)
        sys.exit(0 if success else 1)

    elif command == "rebuild-demo":
        success = await rebuild_kb(demo=True)
        sys.exit(0 if success else 1)

    elif command == "search":
        await test_search(demo=demo)
        sys.exit(0)

    elif command == "search-demo":
        await test_search(demo=True)
        sys.exit(0)

    elif command == "list":
        await list_documents()
        sys.exit(0)

    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
