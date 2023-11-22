from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    app_port: int = Field(..., env='APP_PORT')
    app_host: str = Field(..., env='APP_HOST')

    sqlalchemy_database_url: str = Field(..., env='SQLALCHEMY_DATABASE_URL')

    secret_key: str = Field(..., env='SECRET_KEY')
    algorithm: str = Field(..., env='ALGORITHM')

    mail_username: str = Field(..., env='MAIL_USERNAME')
    mail_password: str = Field(..., env='MAIL_PASSWORD')
    mail_from: str = Field(..., env='MAIL_FROM')
    mail_from_name: str = Field(..., env='MAIL_FROM_NAME')
    mail_port: int = Field(..., env='MAIL_PORT')
    mail_server: str = Field(..., env='MAIL_SERVER')
    mail_starttls: bool = Field(..., env='MAIL_STARTTLS')
    mail_ssl_tls: bool = Field(..., env='MAIL_SSL_TLS')

    # redis_host: str = 'localhost'
    # redis_port: int = 6379

    cors_origins: str = '*'

    # cloudinary_name: str
    # cloudinary_api_key: str
    # cloudinary_api_secret: str

    openai_api_key: str = Field(..., env='OPENAI_API_KEY')
    hf_api_access_token: str = Field(..., env='HF_API_ACCESS_TOKEN')

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


settings = Settings()
