from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.core.config import settings

Base = declarative_base()

engine = create_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_db_connection() -> dict:
    """Verifies actual connection to PostgreSQL and checks pgvector status."""
    try:
        with engine.connect() as conn:
            # Check basic connection
            res = conn.execute(text("SELECT current_database(), version();")).fetchone()
            db_name = res[0] if res else "unknown"
            
            # Check pgvector extension
            vec_check = conn.execute(text("SELECT extversion FROM pg_extension WHERE extname = 'vector';")).fetchone()
            pgvector_active = vec_check is not None
            pgvector_version = vec_check[0] if vec_check else None

            return {
                "connected": True,
                "database": db_name,
                "pgvector_active": pgvector_active,
                "pgvector_version": pgvector_version
            }
    except Exception as e:
        return {
            "connected": False,
            "error": str(e),
            "pgvector_active": False
        }
