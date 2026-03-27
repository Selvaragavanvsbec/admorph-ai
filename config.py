import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AdMorph Agentic Ads Platform"
    database_url: str = "sqlite:///./admorph.db"
    
    # Generic LLM Configuration
    llm_provider: str = "openai"  # options: openai, google, grok, anthropic
    llm_api_key: str | None = None
    llm_model: str = "gpt-4o"
    
    pixabay_api_key: str | None = None
    
    output_dir: str = "generated"
    api_base_url: str = "http://127.0.0.1:8000"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()

# In deployed environments, use the RENDER_EXTERNAL_URL or PORT-based URL
if os.environ.get("RENDER_EXTERNAL_URL"):
    settings.api_base_url = os.environ["RENDER_EXTERNAL_URL"]
elif os.environ.get("PORT"):
    settings.api_base_url = f"http://0.0.0.0:{os.environ['PORT']}"
