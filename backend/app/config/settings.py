from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MONGODB_URL: str
    DATABASE_NAME: str

    HF_TOKEN: str

    QDRANT_URL: str
    QDRANT_API_KEY: str
    QDRANT_COLLECTION: str

    LLM_PROVIDER: str
    GROQ_API_KEY: str
    GROQ_MODEL: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()