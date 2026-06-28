from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_title: str = "RAG Assistance API"
    app_version: str = "0.1.0"
    debug: bool = True
    
    bot_token: str = ""
    telegram_webhook_secret: str = "dev-secret"
    telegram_admin_ids: str = ""
    upload_dir: str = "uploads"
    allowed_document_extensions: str = ""
    postgres_host: str = ""
    postgres_port: str = "5432"
    postgres_db: str = ""
    postgres_user: str = ""
    postgres_password: str = ""
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    llm_provider: str = "ollama"
    ollama_base_url: str = "http://host.docker.internal:11434"
    ollama_model: str = "hf.co/google/gemma-4-12B-it-qat-q4_0-gguf:Q4_0"
    llm_timeout_seconds: int = 120
    telegram_webhook_url: str = ""
    warmup_embedding_model: bool = True
    delete_webhook_on_shutdown: bool = True
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )
    
    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:"
            f"{self.postgres_password}@{self.postgres_host}:"
            f"{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def allowed_extensions(self) -> set[str]:
        if not self.allowed_document_extensions:
            return set()
        
        return {
            allowed_ex.strip().lower() for allowed_ex in self.allowed_document_extensions.split(",") if allowed_ex.strip()
        }
    
    @property
    def admin_ids(self) -> set[int]:
        if not self.telegram_admin_ids:
            return set()
        
        return {
            int(admin_id.strip()) for admin_id in self.telegram_admin_ids.split(",") if admin_id.strip()
        }

settings = Settings()