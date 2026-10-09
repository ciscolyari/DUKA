from pydantic_settings import BaseSettings




class Settings(BaseSettings):
    DATABASE_URL: str ="postgresql+psycopg://posgres:HW4lRW8SEY6Y40Ps3NgBXJgXvaxnJ4wG@dpg-db49nvvlk1mc73fb7oh0-a/duka_ai_db"
    DEBUG: bool = False


settings = Settings()
