from pydantic import BaseSettings


__all__ = ['settings']


class Settings(BaseSettings):
    """This settings object will load environment variables or variables in the cwd .env file."""
    SECRET: str = "Insert SECRET KEY HERE!!!!"
    HTTPS_ONLY = True
    RUN_OCR = False
    RUN_CRUD = False
    # DATABASE_URL: str = 'sqlite:///./test.db'
    # DATABASE_URL: str = 'postgresql://user:password@postgresserver/db'

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'


settings = Settings()
