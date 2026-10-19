import os
from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ClinicalPlatformSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    ENVIRONMENT: str = Field(default="development")
    LOG_LEVEL: str = Field(default="INFO")

    SECRET_KEY: str = Field(default="medguard_clinical_secure_hmac_secret_2026_x89a0b_minimum32")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=480)

    # HIPAA Safe Harbor audit log destination
    AUDIT_LOG_STORAGE_PATH: str = Field(default="./data/audit_logs/hipaa_audit.jsonl")
    ENABLE_PHI_SCRUBBING: bool = Field(default=True)
    ANONYMIZE_IP_ADDRESSES: bool = Field(default=True)

    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///./medguard_clinical.db")

    VECTOR_STORE_PATH: str = Field(default="./data/vector_store")
    VECTOR_SIMILARITY_THRESHOLD: float = Field(default=0.45)
    MAX_RETRIEVED_CHUNKS: int = Field(default=4)

    # National Emergency Hotline Defaults
    EMERGENCY_ESCALATION_HOTLINE_US: str = Field(default="911")
    EMERGENCY_ESCALATION_HOTLINE_UK: str = Field(default="999")
    EMERGENCY_ESCALATION_HOTLINE_EU: str = Field(default="112")
    EMERGENCY_ESCALATION_HOTLINE_LK: str = Field(default="1990")
    SUICIDE_CRISIS_LIFELINE: str = Field(default="988")
    SUICIDE_CRISIS_LIFELINE_LK: str = Field(default="1926")

    # Hybrid Cloud LLM Configuration (Google Gemini 1.5 Pro, Claude 3.5 Sonnet, OpenAI GPT-4o)
    LLM_PROVIDER: str = Field(default="auto")  # 'auto' | 'gemini' | 'anthropic' | 'openai' | 'local'
    GEMINI_API_KEY: str = Field(default="")
    GEMINI_MODEL: str = Field(default="gemini-1.5-pro")
    ANTHROPIC_API_KEY: str = Field(default="")
    ANTHROPIC_MODEL: str = Field(default="claude-3-5-sonnet-20241022")
    OPENAI_API_KEY: str = Field(default="")
    OPENAI_MODEL: str = Field(default="gpt-4o")
    LLM_TEMPERATURE: float = Field(default=0.2)
    LLM_MAX_TOKENS: int = Field(default=900)
    LLM_TIMEOUT_SECONDS: float = Field(default=12.0)

    BACKEND_CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"]
    )

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, str) and v.startswith("["):
            import json
            try:
                return json.loads(v)
            except Exception:
                return ["http://localhost:3000", "http://127.0.0.1:3000"]
        return v


settings = ClinicalPlatformSettings()
