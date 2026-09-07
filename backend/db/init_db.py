import json
import hashlib
import sys
import numpy as np
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from sqlalchemy import text
from backend.core.config import settings
from backend.db.database import engine, SessionLocal, Base
from backend.db.models import ScientificSource, EvidenceChunk, Intervention

def generate_embedding_vector(text_content: str, dim: int = 1536) -> list[float]:
    """
    Generates a normalized embedding vector for the given text.
    Uses OpenAI text-embedding-3-small if OPENAI_API_KEY is available and valid;
    otherwise generates a deterministic, normalized 1536-dim semantic feature vector.
    """
    if settings.openai_api_key and not settings.openai_api_key.startswith("your_"):
        try:
            import httpx
            resp = httpx.post(
                "https://api.openai.com/v1/embeddings",
                headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                json={"input": text_content, "model": settings.embedding_model},
                timeout=10.0
            )
            if resp.status_code == 200:
                return resp.json()["data"][0]["embedding"]
        except Exception as e:
            print(f"Warning: OpenAI embedding call failed ({e}); using deterministic feature vector.")

    # Deterministic normalized 1536-dim feature vector based on text token hashing
    vec = np.zeros(dim, dtype=np.float32)
    words = text_content.lower().split()
    for w in words:
        h = int(hashlib.sha256(w.encode("utf-8")).hexdigest(), 16)
        idx = h % dim
        vec[idx] += 1.0
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec.tolist()

def init_db(seed: bool = True):
    print("🚀 Initializing Darukaa.Earth PostgreSQL database...")
    print(f"   Target URL: {settings.database_url.split('@')[-1]}")

    # 1. Enable pgvector extension
    with engine.connect() as conn:
        print("   Enabling pgvector extension...")
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()

    # 2. Create tables
    print("   Creating application tables...")
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE interventions ADD COLUMN IF NOT EXISTS time_horizon JSON DEFAULT '{}'::json;"))
        conn.commit()

    # 3. Create HNSW index on evidence_chunks.embedding
    with engine.connect() as conn:
        print("   Configuring HNSW vector index on evidence_chunks...")
        try:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_evidence_chunks_hnsw 
                ON evidence_chunks 
                USING hnsw (embedding vector_cosine_ops)
                WITH (m = 16, ef_construction = 64);
            """))
            conn.commit()
            print("   ✅ HNSW index verified.")
        except Exception as e:
            print(f"   Note on vector index: {e}")

    if not seed:
        print("✅ Database initialization complete (without seed).")
        return

    # 4. Seed Data from data/scientific_corpus.json and data/interventions.json
    db = SessionLocal()
    try:
        # Seed Scientific Sources & Chunks
        corpus_path = settings.scientific_corpus_path
        if corpus_path.exists():
            with open(corpus_path, "r", encoding="utf-8") as f:
                chunks_data = json.load(f)
            
            print(f"   Seeding {len(chunks_data)} scientific evidence chunks...")
            for c in chunks_data:
                # Upsert Scientific Source
                source = db.query(ScientificSource).filter_by(source_id=c["source_id"]).first()
                if not source:
                    source = ScientificSource(
                        source_id=c["source_id"],
                        title=c["title"],
                        publisher=c["publisher"],
                        authors=c.get("authors", []),
                        year=c.get("year"),
                        doi=c.get("doi"),
                        url=c.get("url")
                    )
                    db.add(source)
                    db.flush()

                # Upsert Evidence Chunk with vector embedding
                existing_chunk = db.query(EvidenceChunk).filter_by(chunk_id=c["chunk_id"]).first()
                if not existing_chunk:
                    full_text = f"{c.get('title', '')} {c.get('section', '')} {c.get('excerpt', '')} {c.get('topic', '')}"
                    emb = generate_embedding_vector(full_text, dim=settings.embedding_dimension)
                    
                    chunk = EvidenceChunk(
                        chunk_id=c["chunk_id"],
                        source_id=c["source_id"],
                        page=c.get("page"),
                        section=c.get("section"),
                        excerpt=c["excerpt"],
                        topic=c.get("topic"),
                        metrics=c.get("metrics", []),
                        ecosystem=c.get("ecosystem"),
                        region=c.get("region"),
                        evidence_type=c.get("evidence_type"),
                        evidence_strength=c.get("evidence_strength", "TIER_1_CONSENSUS"),
                        embedding=emb
                    )
                    db.add(chunk)

            db.commit()
            print("   ✅ Scientific evidence chunks seeded successfully.")

        # Seed Interventions
        interventions_path = settings.interventions_path
        if interventions_path.exists():
            with open(interventions_path, "r", encoding="utf-8") as f:
                interventions_data = json.load(f)

            print(f"   Seeding {len(interventions_data)} ecological interventions...")
            for item in interventions_data:
                existing_item = db.query(Intervention).filter_by(slug=item["slug"]).first()
                if not existing_item:
                    interv = Intervention(
                        slug=item["slug"],
                        name=item["name"],
                        category=item["category"],
                        biome_applicability=item.get("biome_applicability", []),
                        water_requirement=item.get("water_requirement", "LOW"),
                        primary_benefits=item.get("primary_benefits", {}),
                        tradeoffs=item.get("tradeoffs", []),
                        base_feasibility=item.get("base_feasibility", 0.7),
                        biodiversity_gain=item.get("biodiversity_gain", 0.7),
                        soil_gain=item.get("soil_gain", 0.7),
                        citation_keys=item.get("citation_keys", []),
                        time_horizon=item.get("time_horizon", {})
                    )
                    db.add(interv)
                else:
                    existing_item.time_horizon = item.get("time_horizon", {})

            db.commit()
            print("   ✅ Interventions catalog seeded successfully.")

    except Exception as e:
        db.rollback()
        print(f"❌ Error during database seeding: {e}")
        raise e
    finally:
        db.close()

    print("🎉 Database initialized, tables verified, and vectors seeded in PostgreSQL!")

if __name__ == "__main__":
    init_db(seed=True)
