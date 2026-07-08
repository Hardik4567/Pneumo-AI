from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

class Settings:
    SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_THIS_TO_A_LONG_RANDOM_SECRET")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")

    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("authToken_EXPIRE_MINUTES", 60))
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

    BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", 12))

    # MYSQL CONFIG
    MYSQL_DB_HOST = os.getenv("MYSQL_DB_HOST", "localhost")
    MYSQL_DB_PORT = os.getenv("MYSQL_DB_PORT", "3306")
    MYSQL_DB_USER = os.getenv("MYSQL_DB_USER", "root")
    MYSQL_DB_PASSWORD = os.getenv("MYSQL_DB_PASSWORD", "root")
    MYSQL_DB_NAME = os.getenv("MYSQL_DB_NAME", "new_db")
    MYSQL_DB_POOL_RECYCLE = int(os.getenv("MYSQL_DB_POOL_RECYCLE", 1800))
    
    # PG CONFIG
    PG_DB_HOST = os.getenv("PG_DB_HOST", "localhost")
    PG_DB_PORT = os.getenv("PG_DB_PORT", 5433)
    PG_DB_USER = os.getenv("PG_DB_USER", "postgres")
    PG_DB_PASSWORD = os.getenv("PG_DB_PASSWORD", "12345")
    PG_DB_NAME = os.getenv("PG_DB_NAME", "maths_care")
    PG_DB_POOL_RECYCLE = int(os.getenv("PG_DB_POOL_RECYCLE", 1800))
    
    #Google API Key -- for Gemini
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    # Email settings
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "developerwebanix@gmail.com")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "nqjy ubsa mlww yjph")
    SMTP_FROM_EMAIL = os.getenv(
        "SMTP_FROM_EMAIL", "developerwebanix@gmail.com")


settings = Settings()
