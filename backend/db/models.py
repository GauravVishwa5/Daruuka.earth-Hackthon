import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from backend.db.database import Base

class ScientificSource(Base):
    __tablename__ = "scientific_sources"

    source_id = Column(String(100), primary_key=True)
    title = Column(String(500), nullable=False)
    publisher = Column(String(200), nullable=False)
    authors = Column(JSON, default=list)
    year = Column(Integer, nullable=True)
    doi = Column(String(200), nullable=True)
    url = Column(String(500), nullable=True)

    chunks = relationship("EvidenceChunk", back_populates="source", cascade="all, delete-orphan")

class EvidenceChunk(Base):
    __tablename__ = "evidence_chunks"

    chunk_id = Column(String(100), primary_key=True)
    source_id = Column(String(100), ForeignKey("scientific_sources.source_id"), nullable=False)
    page = Column(Integer, nullable=True)
    section = Column(String(300), nullable=True)
    excerpt = Column(Text, nullable=False)
    topic = Column(String(100), nullable=True)
    metrics = Column(JSON, default=list)
    ecosystem = Column(String(100), nullable=True)
    region = Column(String(100), nullable=True)
    evidence_type = Column(String(100), nullable=True)
    evidence_strength = Column(String(50), default="TIER_1_CONSENSUS")
    embedding = Column(Vector(1536), nullable=True)

    source = relationship("ScientificSource", back_populates="chunks")

class Intervention(Base):
    __tablename__ = "interventions"

    slug = Column(String(100), primary_key=True)
    name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=False)
    biome_applicability = Column(JSON, default=list)
    water_requirement = Column(String(50), default="LOW")
    primary_benefits = Column(JSON, default=dict)
    tradeoffs = Column(JSON, default=list)
    base_feasibility = Column(Float, default=0.7)
    biodiversity_gain = Column(Float, default=0.7)
    soil_gain = Column(Float, default=0.7)
    citation_keys = Column(JSON, default=list)
    time_horizon = Column(JSON, default=dict)

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(100), primary_key=True, default=lambda: str(uuid.uuid4()))
    accumulated_profile = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    recommendations = relationship("RecommendationRecord", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"

    id = Column(String(100), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(100), ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")

class RecommendationRecord(Base):
    __tablename__ = "recommendations"

    id = Column(String(100), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(100), ForeignKey("conversations.id"), nullable=False)
    intervention_slug = Column(String(100), ForeignKey("interventions.slug"), nullable=False)
    decision_score = Column(Float, nullable=False)
    rank = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="recommendations")

class EvidenceLedgerRecord(Base):
    __tablename__ = "evidence_ledger"

    id = Column(String(100), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(100), nullable=False)
    claim = Column(Text, nullable=False)
    status = Column(String(50), nullable=False)
    action = Column(String(50), nullable=False)
    detail = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
