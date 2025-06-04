import os
from dotenv import load_dotenv

env_file = os.getenv("ENV_FILE", ".env.development")
load_dotenv(env_file)

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL")

settings = Settings()