import os
from pathlib import Path
from typing import List
from pydantic import BaseModel
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# Load backend/.env
env_path = BACKEND_DIR / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv(BASE_DIR / ".env")

class Settings(BaseModel):
    app_name: str = "Darukaa.Earth AI Biodiversity Intelligence"
    app_env: str = os.getenv("APP_ENV", "development")
    host: str = os.getenv("HOST", "127.0.0.1")
    port: int = int(os.getenv("PORT", "8005"))
    database_url: str = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:root@localhost:5432/darukaa")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    cors_origins: List[str] = [
        orig.strip() for orig in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173"
        ).split(",") if orig.strip()
    ]
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    embedding_model: str = "text-embedding-3-small"
    embedding_dimension: int = 1536
    scientific_corpus_path: Path = DATA_DIR / "scientific_corpus.json"
    interventions_path: Path = DATA_DIR / "interventions.json"

settings = Settings()
