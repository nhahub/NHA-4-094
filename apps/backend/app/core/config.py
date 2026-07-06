import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Application configuration settings.
    Loads environment variables from OS or .env file.
    """
    # Supabase configurations
    SUPABASE_URL: str = "http://localhost:54321"  # Default URL for local Supabase development
    SUPABASE_SERVICE_ROLE_KEY: str = ""           # Preferred backend-only service_role key
    SUPABASE_KEY: str = ""                        # Fallback key (e.g. anon key or alternate role key)
    SUPABASE_STORAGE_BUCKET: str = "study-documents"

    # Validation limits
    MAX_UPLOAD_SIZE_MB: int = 10

    # Google Gemini API Key — preserved in case it is used elsewhere
    GEMINI_API_KEY: str = ""

    # Embedding configurations
    EMBEDDING_PROVIDER: str = "cloudflare"
    EMBEDDING_MODEL_NAME: str = "@cf/baai/bge-m3"
    EMBEDDING_DIMENSIONS: int = 1024
    EMBEDDING_BATCH_SIZE: int = 32

    # Cloudflare configurations
    CLOUDFLARE_ACCOUNT_ID: str = ""
    CLOUDFLARE_API_TOKEN: str = ""
    CLOUDFLARE_AI_BASE_URL: str = "https://api.cloudflare.com/client/v4"

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }

settings = Settings()
