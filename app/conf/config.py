from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_port: int

    sqlalchemy_database_url: str

    secret_key: str
    algorithm: str

    mail_username: str
    mail_password: str
    mail_from: str
    mail_from_name: str
    mail_port: int
    mail_server: str
    mail_starttls: bool
    mail_ssl_tls: bool

    # redis_host: str = 'localhost'
    # redis_port: int = 6379

    cors_origins: str = '*'

    cloudinary_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str

    openai_api_key: str
    hf_api_access_token: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


settings = Settings()
