from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "ProposalCraft AI"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    MONGODB_URL: str
    DATABASE_NAME: str
    MONGODB_MAX_POOL_SIZE: int = 50
    MONGODB_MIN_POOL_SIZE: int = 10

    HF_TOKEN: str = ""

    QDRANT_URL: str = ""
    QDRANT_API_KEY: str = ""
    QDRANT_COLLECTION_PROPOSALS: str = "proposal_examples"
    QDRANT_COLLECTION_INDUSTRY: str = "industry_knowledge"
    QDRANT_COLLECTION_TECH: str = "technology_knowledge"
    QDRANT_COLLECTION_PRICING: str = "pricing_data"
    QDRANT_COLLECTION_CASE_STUDIES: str = "case_studies"
    QDRANT_COLLECTION_BEST_PRACTICES: str = "best_practices"
    QDRANT_COLLECTION_AUTOMATION: str = "automation_patterns"
    QDRANT_COLLECTION_COMPLIANCE: str = "compliance_standards"

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    PASSWORD_BCRYPT_ROUNDS: int = 12

    LLM_PROVIDER: str = "groq"
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_FAST_MODEL: str = "llama-3.1-8b-instant"

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1:8b"

    EMBEDDING_PROVIDER: str = "sentence_transformers"

    ENABLE_LLM_CACHE: bool = True
    ENABLE_EMBEDDING_CACHE: bool = True
    ENABLE_RAG_CACHE: bool = True
    REDIS_URL: str = ""

    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""

    SENDGRID_API_KEY: str = ""
    FROM_EMAIL: str = "noreply@proposalcraft.ai"

    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    RATE_LIMIT_PER_USER: int = 100
    RATE_LIMIT_PER_ORG: int = 1000
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    MAX_UPLOAD_SIZE_MB: int = 10
    STORAGE_BACKEND: str = "local"
    DEFAULT_LOGO_PATH: str = "app/assets/logo.png"
    ENABLE_DIAGRAMS_APPENDIX: bool = True
    S3_BUCKET: str = ""
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""
    S3_REGION: str = "us-east-1"
    S3_ENDPOINT: str = ""

    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    ENABLE_AUDIT_LOG: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
