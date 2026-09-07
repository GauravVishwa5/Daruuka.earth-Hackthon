import json
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path
from sqlalchemy.orm import Session
from backend.core.config import settings
from backend.db.database import SessionLocal, check_db_connection
from backend.db.models import (
    ScientificSource, 
    EvidenceChunk, 
    Intervention, 
    Conversation, 
    Message, 
    RecommendationRecord, 
    EvidenceLedgerRecord
)
from backend.db.init_db import generate_embedding_vector

class KnowledgeRepository(ABC):
    @abstractmethod
    def search_chunks(self, query: str, biome: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_chunk(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_all_interventions(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_intervention(self, slug: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def save_conversation(self, conv_id: str, profile: Dict[str, Any], messages: List[Dict[str, Any]]) -> None:
        pass

    @abstractmethod
    def get_conversation(self, conv_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def save_ledger_and_recs(self, conv_id: str, recs: List[Dict[str, Any]], ledger: List[Dict[str, Any]]) -> None:
        pass


class PostgresVectorRepository(KnowledgeRepository):
    """
    Primary Data Repository using local PostgreSQL 16/17 with native pgvector.
    Stores all conversations, messages, interventions, scientific sources, and embeddings.
    """
    def search_chunks(self, query: str, biome: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        q_vec = generate_embedding_vector(query, dim=settings.embedding_dimension)
        db: Session = SessionLocal()
        try:
            query_obj = db.query(EvidenceChunk, ScientificSource).join(
                ScientificSource, EvidenceChunk.source_id == ScientificSource.source_id
            )
            
            # If biome provided, prioritize biome applicability
            if biome:
                # Order by cosine distance via pgvector
                chunks_res = query_obj.order_by(
                    EvidenceChunk.embedding.cosine_distance(q_vec)
                ).limit(limit * 2).all()

                # Score with biome filter boost
                results = []
                for chunk, src in chunks_res:
                    is_match = (chunk.ecosystem and biome in chunk.ecosystem) or (chunk.region and "global" in chunk.region)
                    results.append((chunk, src, 1.0 if is_match else 0.8))
                
                results.sort(key=lambda x: x[2], reverse=True)
                final_chunks = results[:limit]
            else:
                chunks_res = query_obj.order_by(
                    EvidenceChunk.embedding.cosine_distance(q_vec)
                ).limit(limit).all()
                final_chunks = [(c, s, 1.0) for c, s in chunks_res]

            output = []
            for chunk, src, _ in final_chunks:
                output.append({
                    "chunk_id": chunk.chunk_id,
                    "source_id": chunk.source_id,
                    "title": src.title,
                    "publisher": src.publisher,
                    "authors": src.authors,
                    "year": src.year,
                    "doi": src.doi,
                    "url": src.url,
                    "page": chunk.page,
                    "section": chunk.section,
                    "excerpt": chunk.excerpt,
                    "topic": chunk.topic,
                    "metrics": chunk.metrics,
                    "ecosystem": chunk.ecosystem,
                    "region": chunk.region,
                    "evidence_type": chunk.evidence_type,
                    "evidence_strength": chunk.evidence_strength
                })
            return output
        finally:
            db.close()

    def get_chunk(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        db: Session = SessionLocal()
        try:
            res = db.query(EvidenceChunk, ScientificSource).join(
                ScientificSource, EvidenceChunk.source_id == ScientificSource.source_id
            ).filter(EvidenceChunk.chunk_id == chunk_id).first()

            if not res:
                return None
            chunk, src = res
            return {
                "chunk_id": chunk.chunk_id,
                "source_id": chunk.source_id,
                "title": src.title,
                "publisher": src.publisher,
                "authors": src.authors,
                "year": src.year,
                "doi": src.doi,
                "url": src.url,
                "page": chunk.page,
                "section": chunk.section,
                "excerpt": chunk.excerpt,
                "topic": chunk.topic,
                "metrics": chunk.metrics,
                "ecosystem": chunk.ecosystem,
                "region": chunk.region,
                "evidence_type": chunk.evidence_type,
                "evidence_strength": chunk.evidence_strength
            }
        finally:
            db.close()

    def get_all_interventions(self) -> List[Dict[str, Any]]:
        db: Session = SessionLocal()
        try:
            items = db.query(Intervention).all()
            return [
                {
                    "slug": i.slug,
                    "name": i.name,
                    "category": i.category,
                    "biome_applicability": i.biome_applicability,
                    "water_requirement": i.water_requirement,
                    "primary_benefits": i.primary_benefits,
                    "tradeoffs": i.tradeoffs,
                    "base_feasibility": i.base_feasibility,
                    "biodiversity_gain": i.biodiversity_gain,
                    "soil_gain": i.soil_gain,
                    "citation_keys": i.citation_keys,
                    "time_horizon": i.time_horizon or {}
                }
                for i in items
            ]
        finally:
            db.close()

    def get_intervention(self, slug: str) -> Optional[Dict[str, Any]]:
        db: Session = SessionLocal()
        try:
            i = db.query(Intervention).filter_by(slug=slug).first()
            if not i:
                return None
            return {
                "slug": i.slug,
                "name": i.name,
                "category": i.category,
                "biome_applicability": i.biome_applicability,
                "water_requirement": i.water_requirement,
                "primary_benefits": i.primary_benefits,
                "tradeoffs": i.tradeoffs,
                "base_feasibility": i.base_feasibility,
                "biodiversity_gain": i.biodiversity_gain,
                "soil_gain": i.soil_gain,
                "citation_keys": i.citation_keys,
                "time_horizon": i.time_horizon or {}
            }
        finally:
            db.close()

    def save_conversation(self, conv_id: str, profile: Dict[str, Any], messages: List[Dict[str, Any]]) -> None:
        db: Session = SessionLocal()
        try:
            conv = db.query(Conversation).filter_by(id=conv_id).first()
            if not conv:
                conv = Conversation(id=conv_id, accumulated_profile=profile)
                db.add(conv)
            else:
                conv.accumulated_profile = profile

            # Clear and re-save messages for the conversation turn
            db.query(Message).filter_by(conversation_id=conv_id).delete()
            for m in messages:
                db.add(Message(conversation_id=conv_id, role=m["role"], content=m["content"]))

            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Error saving conversation to PostgreSQL: {e}")
        finally:
            db.close()

    def get_conversation(self, conv_id: str) -> Optional[Dict[str, Any]]:
        db: Session = SessionLocal()
        try:
            conv = db.query(Conversation).filter_by(id=conv_id).first()
            if not conv:
                return None
            messages = db.query(Message).filter_by(conversation_id=conv_id).order_by(Message.created_at.asc()).all()
            return {
                "conversation_id": conv.id,
                "accumulated_profile": conv.accumulated_profile or {},
                "messages": [{"role": m.role, "content": m.content} for m in messages]
            }
        finally:
            db.close()

    def save_ledger_and_recs(self, conv_id: str, recs: List[Dict[str, Any]], ledger: List[Dict[str, Any]]) -> None:
        db: Session = SessionLocal()
        try:
            # Save recommendations
            db.query(RecommendationRecord).filter_by(conversation_id=conv_id).delete()
            for r in recs:
                db.add(RecommendationRecord(
                    conversation_id=conv_id,
                    intervention_slug=r["slug"],
                    decision_score=r["decision_score"],
                    rank=r["rank"]
                ))
            
            # Save ledger items (clear previous turn ledger for this conversation)
            db.query(EvidenceLedgerRecord).filter_by(conversation_id=conv_id).delete()
            for item in ledger:
                db.add(EvidenceLedgerRecord(
                    conversation_id=conv_id,
                    claim=item["claim"],
                    status=item["status"],
                    action=item["action"],
                    detail=item.get("detail", "")
                ))

            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Error saving ledger & recommendations: {e}")
        finally:
            db.close()


class InMemoryVectorRepository(KnowledgeRepository):
    """
    In-memory fallback repository for offline unit tests or lightweight mock environments.
    """
    def __init__(self, corpus_path: Optional[Path] = None, interventions_path: Optional[Path] = None):
        self.corpus_path = corpus_path or settings.scientific_corpus_path
        self.interventions_path = interventions_path or settings.interventions_path
        self.chunks: List[Dict[str, Any]] = []
        self.interventions: List[Dict[str, Any]] = []
        self.conversations: Dict[str, Dict[str, Any]] = {}
        self._load_data()

    def _load_data(self):
        if self.corpus_path.exists():
            with open(self.corpus_path, "r", encoding="utf-8") as f:
                self.chunks = json.load(f)
        if self.interventions_path.exists():
            with open(self.interventions_path, "r", encoding="utf-8") as f:
                self.interventions = json.load(f)

    def _compute_keyword_score(self, query: str, text: str) -> float:
        query_words = set(query.lower().split())
        target_words = text.lower().split()
        if not query_words or not target_words:
            return 0.0
        matches = sum(1 for w in query_words if any(w in tw for tw in target_words))
        return matches / len(query_words)

    def search_chunks(self, query: str, biome: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        scored_chunks = []
        for chunk in self.chunks:
            if biome and chunk.get("ecosystem") and biome not in chunk.get("ecosystem", "") and "global" not in chunk.get("region", ""):
                penalty = 0.5
            else:
                penalty = 1.0

            content = f"{chunk.get('title', '')} {chunk.get('section', '')} {chunk.get('excerpt', '')} {chunk.get('topic', '')}"
            score = self._compute_keyword_score(query, content) * penalty
            
            if any(term in query.lower() for term in chunk.get("topic", "").split("_")):
                score += 0.35

            scored_chunks.append({"chunk": chunk, "score": round(score, 3)})

        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        return [item["chunk"] for item in scored_chunks[:limit]]

    def get_chunk(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        for c in self.chunks:
            if c.get("chunk_id") == chunk_id:
                return c
        return None

    def get_all_interventions(self) -> List[Dict[str, Any]]:
        return self.interventions

    def get_intervention(self, slug: str) -> Optional[Dict[str, Any]]:
        for item in self.interventions:
            if item.get("slug") == slug:
                return item
        return None

    def save_conversation(self, conv_id: str, profile: Dict[str, Any], messages: List[Dict[str, Any]]) -> None:
        self.conversations[conv_id] = {
            "conversation_id": conv_id,
            "accumulated_profile": profile,
            "messages": messages
        }

    def get_conversation(self, conv_id: str) -> Optional[Dict[str, Any]]:
        return self.conversations.get(conv_id)

    def save_ledger_and_recs(self, conv_id: str, recs: List[Dict[str, Any]], ledger: List[Dict[str, Any]]) -> None:
        pass


_repo_instance = None

def get_repository() -> KnowledgeRepository:
    """
    Returns PostgresVectorRepository if PostgreSQL is reachable;
    falls back to InMemoryVectorRepository only if connection fails.
    """
    global _repo_instance
    if _repo_instance is None:
        db_status = check_db_connection()
        if db_status.get("connected") and db_status.get("pgvector_active"):
            _repo_instance = PostgresVectorRepository()
        else:
            print(f"Warning: PostgreSQL/pgvector not fully active ({db_status}); using InMemoryVectorRepository fallback.")
            _repo_instance = InMemoryVectorRepository()
    return _repo_instance
