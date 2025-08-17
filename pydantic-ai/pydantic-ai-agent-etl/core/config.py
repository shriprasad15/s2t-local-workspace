from enum import Enum
from typing import Optional

from pydantic import Field, BaseModel
from pydantic_settings import BaseSettings


class EnvironmentType(str, Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    STAGING = "staging"


class SASHeader(BaseModel):
    OCP_APIM_SUBSCRIPTION_KEY: str = Field(serialization_alias="ocp-apim-subscription-key", alias="ocp-apim-subscription-key")


class SASConfig(BaseModel):
    BASE_URL: str
    HEADER: SASHeader


class DocserverConfig(BaseModel):
    ES_URL: str = Field(serialization_alias="es_url")
    ES_PASSWORD: str = Field(serialization_alias="es_password")
    ES_USER: str = Field(serialization_alias="es_user")
    NEO_4J_URL: str = Field(serialization_alias="neo4j_url")
    NEO_4J_PASSWORD: str = Field(serialization_alias="neo4j_password")
    NEO_4J_USERNAME: str = Field(serialization_alias="neo4j_user")
    MINIO_ACCESS_KEY: str = Field(serialization_alias="minio_access_key")
    MINIO_SECURE: str = Field(serialization_alias="minio_secure")
    MINIO_SECRET_KEY: str = Field(serialization_alias="minio_secret_key")
    MINIO_URL: str = Field(serialization_alias="minio_url")
    ETCD_HOST: str = Field(serialization_alias="etcd_host")
    ETCD_PORT: int = Field(serialization_alias="etcd_port")


class Settings(BaseSettings):
    APP_NAME: str = "ETL AI Agent API"
    APP_DESCRIPTION: str = "Natural language interface for ETL operations"
    APP_VERSION: str = "1.0.0"

    ENVIRONMENT: str = EnvironmentType.DEVELOPMENT
    APP_PORT: int = 8080

    FASTSTREAM_PROVIDER: Optional[str] = None
    FASTSTREAM_ENABLE: bool = False

    CELERY_ENABLE: bool = False
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_BACKEND_URL: Optional[str] = None
    CELERY_DEFAULT_QUEUE: Optional[str] = "Celery"

    # SAQ Configuration
    SAQ_ENABLE: bool = Field(default=False)
    REDIS_URL: str | None = Field(default=None)
    SAQ_WEB_PORT: int = Field(default=8081)
    SAQ_WORKERS: int = Field(default=1)

    # ETL API Configuration
    ETL_API_URL: str = Field(default="http://cyber-ai-etl-microservice.cyber.svc.cluster.local")
    ETL_USER_ID: str = Field(default="system")
    
    # Custom OpenAI API Configuration (for Pydantic AI)
    API_KEY: Optional[str] = Field(default=None)
    
    # Alternative: Standard OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = Field(default=None)
    
    # Optional: Other model configurations
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None)
    GOOGLE_API_KEY: Optional[str] = Field(default=None)

    # SAS Configuration
    SAS: Optional[SASConfig] = None

    # Docserver Config
    DOCSERVER: Optional[DocserverConfig] = None

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"
        extra = "allow"


settings = Settings()
