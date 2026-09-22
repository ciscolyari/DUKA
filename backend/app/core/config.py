from pydantic_settings import BaseSettings




class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg://duka_user:Lyari123@localhost:5432/duka"
    DEBUG: bool = False


settings = Settings()