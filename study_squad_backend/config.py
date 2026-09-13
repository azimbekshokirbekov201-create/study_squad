from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./study_squad.db"
    secret_key: str = "CHANGE_THIS_TO_A_RANDOM_SECRET_IN_PRODUCTION"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 kun
    gemini_api_key: str = ""
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    frontend_success_url: str = "https://example.com/success"
    frontend_cancel_url: str = "https://example.com/cancel"

    class Config:
        env_file = ".env"


settings = Settings()
