from typing import List, Dict, Any, Optional
from backend.repository import KnowledgeRepository

class RAGService:
    def __init__(self, repository: KnowledgeRepository):
        self.repo = repository

    def retrieve_evidence(
        self, 
        query: str, 
        biome: Optional[str] = "semi_arid", 
        limit: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Option B (pgvector / in-memory + metadata filtering).
        Searches chunks with keyword/semantic match and biome filtering.
        """
        raw_chunks = self.repo.search_chunks(query, biome=biome, limit=limit)
        results = []
        for c in raw_chunks:
            results.append({
                "chunk_id": c.get("chunk_id"),
                "source_id": c.get("source_id"),
                "title": c.get("title"),
                "publisher": c.get("publisher"),
                "year": c.get("year"),
                "doi": c.get("doi"),
                "excerpt": c.get("excerpt"),
                "topic": c.get("topic"),
                "evidence_strength": c.get("evidence_strength", "TIER_1_CONSENSUS")
            })
        return results
