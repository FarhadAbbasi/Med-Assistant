from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_env: str = "local"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "info"

    jwt_secret: str = "change_me"
    jwt_alg: str = "HS256"

    default_tenant_id: str = "public"

    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "med_assistant"
    postgres_user: str = "med_user"
    postgres_password: str = "med_pass"

    qdrant_host: str = "qdrant"
    qdrant_port: int = 6333
    qdrant_collection: str = "guidelines_v1"

    rabbitmq_host: str = "rabbitmq"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "guest"
    rabbitmq_pass: str = "guest"
    rabbitmq_exchange: str = "llm.jobs"
    rabbitmq_queue_analyze: str = "llm.analyze"

    vllm_base_url: str = "http://vllm:8000"
    vllm_model: str = "meta-llama/Meta-Llama-3.1-8B-Instruct"
    vllm_api_key: str = "dev_stub_key"

    class Config:
        env_file = ".env", ".env.example"

_settings: Settings | None = None

def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
