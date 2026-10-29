from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    DATABASE_URL: str = Field(..., description="PostgreSQL connection string")
    OPENAI_API_KEY: str = Field(..., description="OpenAI API key for agents")
    WHATSAPP_TOKEN: str = Field(..., description="Meta Business Cloud API access token")
    WHATSAPP_PHONE_NUMBER_ID: str = Field(..., description="WhatsApp phone number ID")
    WHATSAPP_WEBHOOK_SECRET: str = Field(..., description="WhatsApp webhook verify token")
    GMAIL_IMAP_USER: str = Field(..., description="Email account for IMAP access")
    GMAIL_IMAP_PASSWORD: str = Field(..., description="App password for IMAP access")
    GMAIL_IMAP_HOST: str = Field(default="imap.gmail.com")
    GMAIL_IMAP_PORT: int = Field(default=993)
    SMTP_USER: str = Field(..., description="SMTP user for sending emails")
    SMTP_PASSWORD: str = Field(..., description="SMTP password for sending emails")
    SMTP_HOST: str = Field(default="smtp.gmail.com")
    SMTP_PORT: int = Field(default=587)

    APPROVED_CLIENT_SENDERS: str = Field(
        default="", description="Comma-separated list of approved client email addresses"
    )

    PROJECT_NAME: str = "Sorax Automation"
    DEBUG: bool = False

    @property
    def approved_senders(self) -> list[str]:
        return [s.strip() for s in self.APPROVED_CLIENT_SENDERS.split(",") if s.strip()]


settings = Settings()